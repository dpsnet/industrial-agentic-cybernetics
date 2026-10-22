# 桥接导出器（模式 12 单向导出）：指标快照 → SHA-256 → bridge-volume（只写一次、只读消费）
# prod-net 侧；不具 dev-net 访问权（网络隔离由 compose 保证）

import hashlib
import json
import os
import platform
import subprocess
import time
import urllib.request

SCRAPE_INTERVAL = float(os.environ.get("IAC_SCRAPE_INTERVAL", "30"))
APP_METRICS_URL = os.environ.get("IAC_APP_METRICS_URL", "http://app:8000/metrics")
APP_STATE_URL = os.environ.get("IAC_APP_STATE_URL", "http://app:8000/state")
OUT_DIR = os.environ.get("IAC_BRIDGE_OUT", "/bridge/events")

FINGERPRINT_FIELDS = ["os_release", "kernel", "app_image_digest", "pool_cap", "cache_cap"]


def _env_fingerprint():
    fp = {}
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    fp["os_release"] = line.strip().split("=", 1)[1].strip('"')
    except Exception:
        fp["os_release"] = "unknown"
    try:
        fp["kernel"] = platform.release()
    except Exception:
        fp["kernel"] = "unknown"
    fp["app_image_digest"] = os.environ.get("IAC_APP_DIGEST", "unknown")
    fp["pool_cap"] = os.environ.get("IAC_POOL_SIZE", "20")
    fp["cache_cap"] = os.environ.get("IAC_CACHE_CAP", "500")
    return fp


def _fetch_metrics():
    with urllib.request.urlopen(APP_METRICS_URL, timeout=10) as r:
        return r.read().decode()


def _fetch_state():
    try:
        with urllib.request.urlopen(APP_STATE_URL, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception:
        return {}


def _parse_metrics(text):
    """把 prometheus 文本格式解析成 dict（仅取我们关心的指标）"""
    wanted = {
        "connection_pool_active": None,
        "memory_usage_bytes": None,
        "p99_latency_ms": None,
    }
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            continue
        for name in wanted:
            if line.startswith(name + " "):
                try:
                    wanted[name] = float(line.split()[-1])
                except ValueError:
                    pass
    return wanted


def _next_seq():
    """重启续号：scan 已有快照取最大 seq，避免序号复用导致 mtime 序与文件名序失序"""
    best = -1
    try:
        for n in os.listdir(OUT_DIR):
            if n.startswith("evt_") and n.endswith(".json"):
                try:
                    best = max(best, int(n[4:10]))
                except ValueError:
                    pass
    except Exception:
        pass
    return best + 1


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    seq = _next_seq()
    print(f"exporter resume seq={seq}", flush=True)
    while True:
        try:
            text = _fetch_metrics()
            state = _fetch_state()
            metrics = _parse_metrics(text)
            snapshot = {
                "seq": seq,
                "ts": time.time(),
                "mtime": time.time(),
                "env_fingerprint": _env_fingerprint(),
                "metrics": metrics,
                "state": {k: state.get(k) for k in ("fault", "pool_active", "cache_keys", "downstream_latency", "p99_ms")},
            }
            payload = json.dumps(snapshot, ensure_ascii=False, sort_keys=True).encode()
            digest = hashlib.sha256(payload).hexdigest()
            path = os.path.join(OUT_DIR, f"evt_{seq:06d}.json")
            with open(path, "wb") as f:
                f.write(payload)
            with open(path + ".sha256", "w") as f:
                f.write(digest + "\n")
            seq += 1
            print(f"snapshot {seq - 1} written, sha256={digest[:12]}", flush=True)
        except Exception as e:
            print(f"export error: {e!r}", flush=True)
        time.sleep(SCRAPE_INTERVAL)


if __name__ == "__main__":
    main()
