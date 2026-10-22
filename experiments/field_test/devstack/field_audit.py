# H2 审计有效性自测：构造 20 次篡改（8 哈希 / 6 时间戳回拨 / 6 指纹漂移），否决率必须 =1.00
# 模式 generate（host 侧）：生成篡改案例定义 tamper_cases.json
# 模式 execute（容器内）：基于真实快照构造篡改文件 → auditor._verify_one 逐条校验 → 汇总

import json
import os
import shutil
import sys
import time

BRIDGE_DIR = os.environ.get("IAC_BRIDGE_DIR", "/bridge/events")
TAMPER_CASES = os.environ.get("IAC_TAMPER_CASES", "/dev/audit/tamper_cases.json")

N_HASH = 8
N_MTIME = 6
N_FP = 6


def generate_cases(out_path):
    cases = []
    base = {"seq": -1, "ts": 0.0, "mtime": 0.0,
            "env_fingerprint": {"os_release": "x"}, "metrics": {"connection_pool_active": 1},
            "state": {"fault": "none"}}
    for i in range(N_HASH):
        c = json.loads(json.dumps(base)); c.update({"kind": "hash", "name": f"tamper_hash_{i:02d}"})
        cases.append(c)
    for i in range(N_MTIME):
        c = json.loads(json.dumps(base)); c.update({"kind": "mtime", "name": f"tamper_mtime_{i:02d}"})
        cases.append(c)
    for i in range(N_FP):
        c = json.loads(json.dumps(base)); c.update({"kind": "fingerprint", "name": f"tamper_fp_{i:02d}"})
        cases.append(c)
    with open(out_path, "w") as f:
        json.dump(cases, f, ensure_ascii=False)
    print(f"generated {len(cases)} tamper cases -> {out_path}", flush=True)
    return cases


def execute():
    with open(TAMPER_CASES) as f:
        cases = json.load(f)
    import auditor
    # 清理上一轮残留篡改文件（避免污染模板选取与 auditor 主循环）
    for x in os.listdir(BRIDGE_DIR):
        if x.startswith("tamper_"):
            try:
                os.remove(os.path.join(BRIDGE_DIR, x))
            except OSError:
                pass
            try:
                os.remove(os.path.join(BRIDGE_DIR, x + ".sha256"))
            except OSError:
                pass
    real = sorted([x for x in os.listdir(BRIDGE_DIR)
                   if x.endswith(".json") and x.startswith("evt_")])
    if not real:
        print("FAIL: no real bridge events; run exporter first", flush=True)
        sys.exit(1)
    template = os.path.join(BRIDGE_DIR, real[-1])
    # 独立校验状态：避免与并发 auditor 主循环竞争污染 last_mtime
    auditor._STATE_PATH = "/dev/audit/_tamper_state.json"
    auditor._save_state({"last_mtime": 0.0})
    # 指纹基线：取真实快照的环境指纹（生产流审计器亦按此漂移判据）
    with open(template) as f:
        auditor.EXPECTED_FINGERPRINT = json.load(f).get("env_fingerprint", {})
    results = []
    last_ok_mtime = 0.0
    seq = 100000
    for i, case in enumerate(cases):
        with open(template) as f:
            rec = json.load(f)
        name = case["name"]
        # 逐类构造
        if case["kind"] == "hash":
            rec["metrics"]["connection_pool_active"] = 99  # 篡改内容
        elif case["kind"] == "mtime":
            rec["mtime"] = last_ok_mtime - 1.0  # 回拨
            rec["ts"] = rec["mtime"]
        elif case["kind"] == "fingerprint":
            rec["env_fingerprint"]["os_release"] = "Tampered OS 99"
        rec["seq"] = seq
        rec["name"] = name
        seq += 1
        path = os.path.join(BRIDGE_DIR, f"tamper_{i:02d}.json")
        data = json.dumps(rec, ensure_ascii=False, sort_keys=True).encode()
        with open(path, "wb") as f:
            f.write(data)
        if case["kind"] == "hash":
            # 保留模板原 sha256 → 内容已篡改，哈希必然不匹配（缺失 sha256 会被审计器跳过）
            with open(template + ".sha256") as f:
                tmpl_sha = f.read().strip()
            with open(path + ".sha256", "w") as f:
                f.write(tmpl_sha + "\n")
        elif case["kind"] != "hash":
            import hashlib
            with open(path + ".sha256", "w") as f:
                f.write(hashlib.sha256(data).hexdigest() + "\n")
        # 逐条校验（对 hash 类篡改，保留原模板 sha256 → 必然 mismatch）
        ok, reason = auditor._verify_one(path)
        results.append({"case": name, "kind": case["kind"], "rejected": (not ok),
                        "reason": reason})
        if ok:
            last_ok_mtime = rec["mtime"]
    rejected = sum(1 for r in results if r["rejected"])
    print(f"TAMPER RESULTS: {rejected}/{len(results)} rejected "
          f"(hash={sum(1 for r in results if r['kind']=='hash' and r['rejected'])}/"
          f"{N_HASH}, mtime={sum(1 for r in results if r['kind']=='mtime' and r['rejected'])}/"
          f"{N_MTIME}, fp={sum(1 for r in results if r['kind']=='fingerprint' and r['rejected'])}/{N_FP})", flush=True)
    with open("/dev/audit/tamper_results.json", "w") as f:
        json.dump({"total": len(results), "rejected": rejected, "results": results}, f,
                  ensure_ascii=False, indent=1)
    ok_all = rejected == len(results)
    print("H2 VERDICT: " + ("PASS (rejection rate = 1.00)" if ok_all else "FAIL"), flush=True)
    sys.exit(0 if ok_all else 2)


def main():
    mode = sys.argv[sys.argv.index("--mode") + 1] if "--mode" in sys.argv else "generate"
    if mode == "generate":
        out = TAMPER_CASES if os.name == "posix" else os.path.join(
            os.path.dirname(__file__), "tamper_cases.json")
        generate_cases(out)
    elif mode == "execute":
        execute()
    else:
        print(f"unknown mode {mode}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
