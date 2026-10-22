# 独立审计器（模式 02 探针 4 / 模式 23）：校验哈希 + 环境指纹 + mtime 单调性
# dev-net 侧；只读消费 bridge-volume；审计通过的事件写入 dev-volume/audit_pass.jsonl

import hashlib
import json
import os
import time

BRIDGE_DIR = os.environ.get("IAC_BRIDGE_DIR", "/bridge/events")
OUT_DIR = os.environ.get("IAC_AUDIT_OUT", "/dev/audit")
POLL_INTERVAL = float(os.environ.get("IAC_AUDIT_POLL", "5"))
EXPECTED_FINGERPRINT = json.loads(os.environ.get("IAC_EXPECTED_FP", "{}"))


def _verify_one(path):
    """返回 (ok, reason)。篡改构造：sha256 不符 / mtime 回拨 / 指纹漂移"""
    rec = None
    try:
        with open(path, "rb") as f:
            data = f.read()
        rec = json.loads(data.decode())
    except Exception as e:
        return False, f"unreadable: {e!r}"

    # 1) 哈希校验（若 .sha256 存在）
    sha_path = path + ".sha256"
    if os.path.exists(sha_path):
        with open(sha_path) as f:
            expect = f.read().strip()
        if expect != hashlib.sha256(data).hexdigest():
            return False, "hash_mismatch"

    # 2) mtime 单调性（与上一事件比较，记录于审计器状态文件）
    st = _get_state()
    last_mtime = st.get("last_mtime", None)
    cur_mtime = rec.get("mtime", rec.get("ts", 0.0))
    if last_mtime is not None and cur_mtime <= last_mtime:
        return False, f"mtime_not_strict_increasing: {cur_mtime} <= {last_mtime}"
    st["last_mtime"] = cur_mtime
    _save_state(st)

    # 3) 环境指纹一致性（未显式配置时，以首个含指纹的事件自动确立基线）
    fp = rec.get("env_fingerprint", {})
    global EXPECTED_FINGERPRINT
    if not EXPECTED_FINGERPRINT and fp:
        EXPECTED_FINGERPRINT = dict(fp)
        return True, "ok"  # 基线事件本身接受
    for k, v in EXPECTED_FINGERPRINT.items():
        if fp.get(k) != v:
            return False, f"fingerprint_drift:{k}"

    return True, "ok"


_STATE_PATH = os.environ.get("IAC_AUDIT_STATE", "/dev/audit/audit_state.json")


def _get_state():
    try:
        with open(_STATE_PATH) as f:
            return json.load(f)
    except Exception:
        return {"last_mtime": None}


def _save_state(st):
    os.makedirs(os.path.dirname(_STATE_PATH), exist_ok=True)
    with open(_STATE_PATH, "w") as f:
        json.dump(st, f)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    seen = set()
    while True:
        try:
            files = sorted(os.listdir(BRIDGE_DIR),
                           key=lambda n: os.path.getmtime(os.path.join(BRIDGE_DIR, n)))
        except Exception:
            files = []
        for name in files:
            if not name.endswith(".json"):
                continue
            if name.startswith("tamper_"):
                continue  # H2 自测构造，不进入生产审计流
            if name in seen:
                continue
            seen.add(name)
            path = os.path.join(BRIDGE_DIR, name)
            ok, reason = _verify_one(path)
            record = {"event": name, "ok": ok, "reason": reason, "audited_at": time.time()}
            with open(os.path.join(OUT_DIR, "audit_pass.jsonl"), "a") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"audit {name} -> {'PASS' if ok else 'REJECT'} ({reason})", flush=True)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
