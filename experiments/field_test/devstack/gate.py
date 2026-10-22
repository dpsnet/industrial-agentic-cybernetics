# 终审晋升门禁（模式 14 / 模式 24）：仅接受 五重判据全绿 + 审计通过 的报告
# H5 判读：晋升条目中环境特定参数必须绑定 environmentFingerprint 且不得进入模式型库

import json
import os
import re
import time

REPORT_DIR = os.environ.get("IAC_REPORT_DIR", "/dev/reports")
RESULT_FILE = os.environ.get("IAC_GATE_RESULT", "/dev/audit/gate_results.jsonl")
ENV_SPECIFIC_PATTERNS = ["pool", "timeout", "limit", "thread", "cache_cap", "interval", "latency_ms"]

ENV_PARAM_KEYS = {"connection_pool_active", "p99_latency_ms", "memory_usage_bytes"}

# H5：环境特定参数 = "参数名=具体数值" 片段（pool=20、timeout_ms=300 等）
ENV_VAL_RE = re.compile(
    r"\b(?:pool|timeout|limit|capacity|threads?|interval|latency|cache)[-_]?[A-Za-z_]*\s*[=:]\s*\d+(?:\.\d+)?", re.I)


def _check_env_decoupling(entry):
    """H5：晋升条目的通用经验（knowledge）不得含环境特定参数；
    若含具体环境值，必须绑定 environmentFingerprint 字段"""
    knowledge = entry.get("knowledge") or {}
    text = json.dumps(knowledge, ensure_ascii=False)
    hits = ENV_VAL_RE.findall(text)
    if not hits:
        return True, []
    if isinstance(knowledge, dict) and knowledge.get("environmentFingerprint"):
        return True, []
    return False, hits


def _judge(entry):
    """返回 (promote, reasons, verdict_all_green)"""
    checks = entry.get("verdict", {})
    verdict_all_green = all(checks.get(k) is True for k in ("compile", "unit", "integration", "performance", "security"))
    # 1) 五重判据全绿
    if not verdict_all_green:
        return False, ["verdict_not_all_green"], verdict_all_green
    # 2) 审计通过
    if not entry.get("audit_ok", False):
        return False, ["audit_not_passed"], verdict_all_green
    # 3) H5 环境参数解耦
    ok, leaked = _check_env_decoupling(entry)
    if not ok:
        return False, [f"env_param_leak:{','.join(leaked)}"], verdict_all_green
    return True, ["ok"], verdict_all_green


def main():
    os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)
    while True:
        try:
            files = sorted(os.listdir(REPORT_DIR))
        except Exception:
            files = []
        for name in files:
            if not name.endswith(".json"):
                continue
            path = os.path.join(REPORT_DIR, name)
            try:
                with open(path) as f:
                    entry = json.load(f)
            except Exception:
                continue
            promote, reasons, verdict_all_green = _judge(entry)
            rec = {"entry": name, "promote": promote, "reasons": reasons,
                   "verdict_all_green": verdict_all_green,
                   "verdict": entry.get("verdict", {}),
                   "errors": entry.get("errors", {}),
                   "ts": time.time()}
            with open(RESULT_FILE, "a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"GATE {name} -> {'PROMOTE' if promote else 'REJECT'} ({','.join(reasons)})", flush=True)
            try:
                os.remove(path)  # 只处理一次
            except Exception:
                pass
        time.sleep(float(os.environ.get("IAC_GATE_POLL", "2")))


if __name__ == "__main__":
    main()
