# 异常模式嗅探器（模式 23）：EWMA(λ=0.3) + 固定阈值 + 3-sigma；阈值预注册后冻结
# 基线期（IAC_BASELINE_SEC）内积累 EWMA 与 sigma；之后逐事件判定并输出告警事件

import json
import math
import os
import time

AUDIT_FILE = os.environ.get("IAC_AUDIT_FILE", "/dev/audit/audit_pass.jsonl")
ALERT_FILE = os.environ.get("IAC_ALERT_FILE", "/dev/audit/alerts.jsonl")
BASELINE_SEC = float(os.environ.get("IAC_BASELINE_SEC", "120"))
LAMBDA = float(os.environ.get("IAC_EWMA_LAMBDA", "0.3"))
# 预注册阈值（冻结）：
THRESHOLD_POOL_ACTIVE = float(os.environ.get("IAC_TH_POOL", "10"))     # 连接池活跃数固定阈值（池 20）
THRESHOLD_P99_MS = float(os.environ.get("IAC_TH_P99", "300"))          # p99 固定阈值（正常 <100ms）
THRESHOLD_MEM_SIGMA = float(os.environ.get("IAC_TH_MEM_SIGMA", "3"))   # 内存 3-sigma

TRACKED = ["connection_pool_active", "p99_latency_ms", "memory_usage_bytes"]

_baseline_end = time.monotonic() + BASELINE_SEC
_ewma = {k: None for k in TRACKED}
_var = {k: 0.0 for k in TRACKED}
_n = 0


def _update_ewma(metrics):
    global _n
    _n += 1
    for k in TRACKED:
        v = metrics.get(k)
        if v is None:
            continue
        if _ewma[k] is None:
            _ewma[k] = v
        else:
            prev = _ewma[k]
            _ewma[k] = LAMBDA * v + (1 - LAMBDA) * prev
            # 用 EWMA 与瞬时值的偏差做漂移方差估计（EWMA 自协方差近似）
            delta = v - prev
            _var[k] = (1 - LAMBDA) * _var[k] + LAMBDA * delta * delta


def _alert_for(metrics, state):
    """返回告警原因列表（空 = 无告警）"""
    reasons = []
    pa = metrics.get("connection_pool_active")
    p99 = metrics.get("p99_latency_ms")
    mem = metrics.get("memory_usage_bytes")

    # 固定阈值（预注册）：连接池活跃爬升 / p99 阶跃
    if pa is not None and pa >= THRESHOLD_POOL_ACTIVE:
        reasons.append(f"pool_active>{THRESHOLD_POOL_ACTIVE} ({pa:.0f})")
    if p99 is not None and p99 >= THRESHOLD_P99_MS:
        reasons.append(f"p99>{THRESHOLD_P99_MS} ({p99:.0f}ms)")

    # 3-sigma（内存线性增长）：基线后逐事件
    if _ewma["memory_usage_bytes"] is not None and mem is not None:
        sig = math.sqrt(max(_var["memory_usage_bytes"], 1e-9))
        if sig > 0 and (mem - _ewma["memory_usage_bytes"]) > THRESHOLD_MEM_SIGMA * sig:
            reasons.append(f"mem>3sigma (dev {(mem - _ewma['memory_usage_bytes']) / sig:.1f}σ)")
    return reasons


def main():
    os.makedirs(os.path.dirname(ALERT_FILE), exist_ok=True)
    offset = 0
    last_fault = None
    while True:
        # 从审计通过流读取（增量）
        try:
            with open(AUDIT_FILE) as f:
                lines = f.readlines()
        except Exception:
            lines = []
        new_lines = lines[offset:]
        offset = len(lines)
        for line in new_lines:
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if not rec.get("ok"):
                continue
            ev = rec.get("event", "")
            # 从审计记录定位原始快照
            snap_path = os.path.join("/bridge/events", ev)
            try:
                with open(snap_path) as f:
                    snap = json.load(f)
            except Exception:
                continue
            metrics = snap.get("metrics", {})
            state = snap.get("state", {})
            in_baseline = time.monotonic() < _baseline_end
            if in_baseline:
                _update_ewma(metrics)
                continue
            # 先判定后更新：跳变信号用旧基线 σ 判定（先更后判会令方差膨胀、3σ 吸收突变）
            reasons = _alert_for(metrics, state)
            _update_ewma(metrics)
            if os.environ.get("IAC_SNIFF_DEBUG") == "1":
                mem = metrics.get("memory_usage_bytes")
                sig = math.sqrt(max(_var["memory_usage_bytes"], 1e-9))
                print(f"DBG {ev} mem={mem} ewma={_ewma['memory_usage_bytes']:.0f} sig={sig:.2f} "
                      f"th={THRESHOLD_MEM_SIGMA * sig:.2f} reasons={reasons}", flush=True)
            if reasons:
                alert = {"ts": time.time(), "event": ev, "reasons": reasons,
                         "fault": state.get("fault")}
                with open(ALERT_FILE, "a") as f:
                    f.write(json.dumps(alert, ensure_ascii=False) + "\n")
                print(f"ALERT {ev}: {','.join(reasons)}", flush=True)
        time.sleep(float(os.environ.get("IAC_SNIFF_POLL", "2")))


if __name__ == "__main__":
    main()
