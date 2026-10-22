# 生产现场实验编排（Windows 侧）：docker compose 拓扑 + 故障注入 + 数据收集
# 用法：
#   python production_field_test.py up            # 构建并启动全部服务（含 LLM 流水线）
#   python production_field_test.py baseline      # 预热：exporter≥5 快照 + sniffer 基线
#   python production_field_test.py h2            # H2 审计自测（20 篡改 → 否决率）
#   python production_field_test.py run --scenario F1 --reps 10
#   python production_field_test.py collect       # 收集容器内 alerts/gate/audit 到 results/
#   python production_field_test.py analyze       # 按 §5 判读
# 判读标准：F1-F3 检出率≥0.90（5 采集周期=180s 内）；F4 误报率≤0.05；H2/H3/H4/H5 见判读脚本

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")
COMPOSE = os.path.join(HERE, "compose.yaml")
RESULTS = os.path.join(HERE, "results")

APP_INJECT = "http://localhost:8000/admin/fault"
TOXIPROXY_API = "http://localhost:8474"
SCRAPE_PERIOD = 30           # prometheus 采集周期（秒）
DETECT_WINDOW = 5 * SCRAPE_PERIOD + 30   # 5 个采集周期 + 余量 = 180s
COOLDOWN = 20
SCENARIOS = ["F1", "F2", "F3", "F4"]

PY = "D:\\pyenv\\pyenv-win\\versions\\3.11.8\\python.exe"


def compose(*args, capture=True):
    cmd = ["docker", "compose", "--env-file", ENV_FILE, "-f", COMPOSE] + list(args)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"compose {' '.join(args)} failed: {r.stderr[-500:]}")
    return r.stdout


def container_cat(service, cmd):
    """docker exec（真 shell 语义，支持管道），容器名固定 iac-field-<service>-1"""
    r = subprocess.run(["docker", "exec", "-i", f"iac-field-{service}-1",
                        "sh", "-c", cmd], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def inject_fault(kind, prefill=None):
    body = {"fault": kind}
    if prefill is not None:
        body["prefill"] = prefill
    data = json.dumps(body).encode()
    req = urllib.request.Request(APP_INJECT, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


def reset_state():
    """清空泄漏/缓存残留，保证每 rep 干净基线（泄漏注入不可逆）"""
    body = json.dumps({"fault": "none", "reset_pool": True, "reset_cache": True}).encode()
    req = urllib.request.Request(APP_INJECT, data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            json.loads(r.read().decode())
    except Exception:
        pass


def toxiproxy_setup():
    """创建下游代理；幂等。代理监听 8475（控制端口 8474 不冲突）"""
    try:
        body = json.dumps({"name": "downstream", "listen": "0.0.0.0:8475",
                           "upstream": "downstream:9000"}).encode()
        req = urllib.request.Request(f"{TOXIPROXY_API}/proxies", data=body,
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


def toxiproxy_latency(on):
    # 注入 400ms：必须超过 sniffer 预注册 p99 阈值 300ms 才会触发告警
    # off = 删除 toxic（POST 同名 toxic 会 409，toxicity=0 不更新）
    try:
        req = urllib.request.Request(f"{TOXIPROXY_API}/proxies/downstream/toxics/latency_downstream",
                                     method="DELETE")
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass
    if not on:
        return
    body = json.dumps({"type": "latency", "attributes": {"latency": 400, "jitter": 0},
                       "toxicity": 1}).encode()
    req = urllib.request.Request(f"{TOXIPROXY_API}/proxies/downstream/toxics",
                                 data=body, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"toxiproxy update warn: {e!r}", flush=True)


def now():
    return time.time()


def cmd_up(args):
    os.makedirs(RESULTS, exist_ok=True)
    print("building & starting stack ...", flush=True)
    print(compose("up", "-d", "--build"))
    print("waiting for app health ...", flush=True)
    for _ in range(30):
        try:
            with urllib.request.urlopen("http://localhost:8000/healthz", timeout=3) as r:
                if r.status == 200:
                    break
        except Exception:
            pass
        time.sleep(2)
    toxiproxy_setup()
    print("stack ready", flush=True)


def cmd_baseline(args):
    print("waiting for exporter snapshots (>=5) ...", flush=True)
    got = 0
    while got < 5:
        time.sleep(10)
        out = container_cat("exporter", "ls /bridge/events 2>/dev/null | wc -l").strip()
        try:
            got = int(out)
        except ValueError:
            got = 0
        print(f"  snapshots: {got}", flush=True)
    wait = max(0, int(args.seconds) - 10)
    print(f"baseline window {wait}s (sniffer EWMA/3σ 基线) ...", flush=True)
    time.sleep(wait)
    print("baseline done", flush=True)


def _collect_alerts_since(t0, t1):
    """收集 [t0,t1] 窗口内的告警（按桥接事件时间戳关联）"""
    out = container_cat("sniffer", "cat /dev/audit/alerts.jsonl 2>/dev/null")
    hits = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            a = json.loads(line)
        except Exception:
            continue
        # 关联事件文件时间戳
        ev = a.get("event", "")
        if ev and t0 <= a.get("ts", 0) <= t1:
            hits.append(a)
    return hits


def cmd_run(args):
    scenario = args.scenario.upper()
    if scenario not in SCENARIOS:
        raise SystemExit(f"unknown scenario {scenario}, use {SCENARIOS}")
    reps = args.reps
    log_path = os.path.join(RESULTS, "run_log.jsonl")
    print(f"scenario {scenario} x {reps} reps (detect window {DETECT_WINDOW}s)", flush=True)
    for rep in range(1, reps + 1):
        # F3 例外：rep 间不 reset（cache 累积），注入台阶逐 rep 递增（每 rep 新增 30000 key ≈ +60MB）
        # 保证每 rep 相对前台阶都有 >3σ 的突跳；F1/F2/F4 保持每 rep 干净基线
        if scenario != "F3":
            reset_state()  # 干净基线（清泄漏/缓存残留）
        t0 = now()
        if scenario == "F1":
            inject_fault("conn_leak")
        elif scenario == "F3":
            prefill = 50000 + 30000 * (rep - 1)
            inject_fault("mem_leak", prefill=prefill)
        elif scenario == "F2":
            toxiproxy_latency(True)
        elif scenario == "F4":
            pass  # 无注入（对照）
        print(f"  [{scenario} #{rep}] injected at t0={t0:.1f}", flush=True)
        time.sleep(DETECT_WINDOW)
        alerts = _collect_alerts_since(t0, t0 + DETECT_WINDOW)
        detected = bool(alerts)
        rec = {"scenario": scenario, "rep": rep, "inject_ts": t0,
               "detected": detected, "alerts": alerts}
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"    -> detected={detected}", flush=True)
        # 重置
        if scenario in ("F1", "F3"):
            inject_fault("none")
        elif scenario == "F2":
            toxiproxy_latency(False)
        time.sleep(COOLDOWN)
    print(f"scenario {scenario} done: {reps} reps logged -> {log_path}", flush=True)


def cmd_collect(args):
    os.makedirs(RESULTS, exist_ok=True)
    for service, path, out in [
        ("sniffer", "/dev/audit/alerts.jsonl", "alerts_all.jsonl"),
        ("gate", "/dev/audit/gate_results.jsonl", "gate_results.jsonl"),
        ("auditor", "/dev/audit/audit_pass.jsonl", "audit_pass.jsonl"),
        ("auditor", "/dev/audit/tamper_results.json", "tamper_results.json"),
        ("auditor", "/dev/audit/patterns.jsonl", "patterns_all.jsonl"),
    ]:
        data = container_cat(service, f"cat {path} 2>/dev/null")
        with open(os.path.join(RESULTS, out), "w", encoding="utf-8") as f:
            f.write(data)
        print(f"collected {out}: {len(data)} bytes", flush=True)


def cmd_analyze(args):
    subprocess.run([PY, os.path.join(HERE, "field_test_analyze.py"),
                    "--results", RESULTS], check=False)


def cmd_h2(args):
    os.makedirs(RESULTS, exist_ok=True)
    print("starting tamperer (profile h2) ...", flush=True)
    compose("--profile", "h2", "up", "-d")
    print("generating tamper cases ...", flush=True)
    r = subprocess.run(["docker", "compose", "-f", COMPOSE, "exec", "-T", "tamperer",
                        "python", "field_audit.py", "--mode", "generate"], capture_output=True, text=True)
    print(r.stdout[-300:], flush=True)
    print("running H2 audit self-test ...", flush=True)
    r = subprocess.run(["docker", "compose", "-f", COMPOSE, "exec", "-T", "tamperer",
                        "python", "field_audit.py", "--mode", "execute"], capture_output=True, text=True)
    print(r.stdout[-500:], flush=True)
    if r.returncode not in (0, 2):
        raise RuntimeError(f"H2 tamperer failed: {r.stderr[-300:]}")
    # 收集结果
    data = container_cat("tamperer", "cat /dev/audit/tamper_results.json 2>/dev/null")
    with open(os.path.join(RESULTS, "tamper_results.json"), "w", encoding="utf-8") as f:
        f.write(data)
    print("H2 results -> results/tamper_results.json", flush=True)
    sys.exit(r.returncode if r.returncode == 2 else 0)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("up")
    p = sub.add_parser("baseline")
    p.add_argument("--seconds", type=int, default=140)
    p = sub.add_parser("h2")
    p = sub.add_parser("run")
    p.add_argument("--scenario", required=True)
    p.add_argument("--reps", type=int, default=10)
    sub.add_parser("collect")
    sub.add_parser("analyze")
    args = ap.parse_args()
    globals()[f"cmd_{args.cmd}"](args)


if __name__ == "__main__":
    main()
