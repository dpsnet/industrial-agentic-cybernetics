"""§7.6.4 动态容量控制实验执行器（2026-10-24，凌晨窗口）。
协议（论文 §7.6.4，判据写死）：
- 动态臂 12 链，1:3 平行随动探针配比：rep 0/3/6/9 前各跑 1 条探针（C0-full W=16 6 代），
  探针 p_probe>=0.83 -> 该 3 链窗口 W4；p_probe<0.83 -> W8（链间切换）。
  首条探针即启动门控（判当前毒株转写状态）。
- 静态臂 12 链 W8（同协议对照，无门禁）。
- 判据 C1：动态存活率 <=0.5（vs 静态高态 W8 0.750，Fisher 单侧 p<0.05）；
  C2：动态记忆效用保留率 >=0.275（静态 W=4 同态基线 0.305 x 0.9）；
  C3：探针区段分层判读与整批混读方向一致；敏感性 0.5->0.8。
用法：
  python _s76_control.py --n-dynamic 12 --n-static 12 --out-prefix _ctrl_dyn
输出：
  <prefix>_r{rep}.json（动态实验链）/<prefix>_probe{idx}.json（随动探针）
  <prefix>_static_r{rep}.json（静态臂 W8）/<prefix>_static.json（静态合并）
  <prefix>.json（动态合并：runs + probe_log）
"""
import argparse, os, subprocess, json, time

HERE = os.path.dirname(os.path.abspath(__file__))
PY = r"D:\pyenv\pyenv-win\versions\3.11.8\python.exe"
MAIN = os.path.join(HERE, "axiom4_memory_propagation.py")
NAMES = ["P1", "P2", "P3"]
THRESH = 0.83


def run_chain(window, out):
    cmd = [PY, MAIN, "main", "--provider=scnet-flash",
           "--architecture=full_append", f"--window={window}",
           "--reps=1", "--gens=6", "--conds=C0", f"--out={out}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=480)
    return r.returncode, r.stderr[-300:]


def probe_pw(path):
    d = json.load(open(path, encoding="utf-8"))
    runs = d["runs"][list(d["runs"].keys())[0]]
    pw = sum(sum(1 for it in g["new_experiences"] if it.get("lineage") in NAMES)
             for g in runs[0]["gens"])
    return pw, runs[0]["gens"][-1]["timestamp"] if "timestamp" in runs[0]["gens"][-1] else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-dynamic", type=int, default=12)
    ap.add_argument("--n-static", type=int, default=12)
    ap.add_argument("--out-prefix", default="_ctrl_dyn")
    args = ap.parse_args()
    prefix = os.path.join(HERE, args.out_prefix)

    # ---- 动态臂：1:3 随动探针，链间切换 ----
    dyn_runs = {"runs": {"C0": []}}
    probe_log = []
    t0 = time.strftime("%H:%M:%S")
    print(f"[dyn] start {t0} n={args.n_dynamic}", flush=True)
    for rep in range(args.n_dynamic):
        if rep % 3 == 0:
            pi = rep // 3
            pf = f"{prefix}_probe{pi}.json"
            rc, err = run_chain(16, pf)
            if rc != 0 or not os.path.exists(pf):
                print(f"[dyn rep{rep}] PROBE FAILED rc={rc} tail={err}", flush=True)
                raise SystemExit(1)
            pw, ts = probe_pw(pf)
            p_probe = pw / 6
            w = 4 if p_probe >= THRESH else 8
            probe_log.append({"probe_idx": pi, "rep": rep, "pw": pw,
                              "p_probe": p_probe, "window": w,
                              "ts": ts or time.strftime("%H:%M:%S")})
            print(f"[dyn rep{rep}] probe{pi} pw={pw}/6 p={p_probe:.3f} -> W{w}", flush=True)
        else:
            w = probe_log[-1]["window"]
        sub = f"{prefix}_r{rep}.json"
        rc, err = run_chain(w, sub)
        if rc != 0 or not os.path.exists(sub):
            print(f"[dyn rep{rep}] CHAIN FAILED rc={rc} tail={err}", flush=True)
            raise SystemExit(1)
        d = json.load(open(sub, encoding="utf-8"))
        dyn_runs["runs"]["C0"].extend(d["runs"][list(d["runs"].keys())[0]])
        print(f"[dyn rep{rep}] W{w} done", flush=True)
    with open(f"{prefix}.json", "w", encoding="utf-8") as f:
        json.dump({"runs": dyn_runs["runs"], "probe_log": probe_log}, f,
                  ensure_ascii=False, indent=1)
    print(f"[dyn] DONE -> {os.path.basename(prefix)}.json ({args.n_dynamic} chains, "
          f"{len(probe_log)} probes)", flush=True)

    # ---- 静态臂：W8 12 链对照（同协议、无门禁） ----
    static_runs = {"runs": {"C0": []}}
    print(f"[static] start W8 n={args.n_static}", flush=True)
    for rep in range(args.n_static):
        sub = f"{prefix}_static_r{rep}.json"
        rc, err = run_chain(8, sub)
        if rc != 0 or not os.path.exists(sub):
            print(f"[static rep{rep}] FAILED rc={rc} tail={err}", flush=True)
            raise SystemExit(1)
        d = json.load(open(sub, encoding="utf-8"))
        static_runs["runs"]["C0"].extend(d["runs"][list(d["runs"].keys())[0]])
    with open(f"{prefix}_static.json", "w", encoding="utf-8") as f:
        json.dump(static_runs, f, ensure_ascii=False, indent=1)
    print(f"[static] DONE -> {os.path.basename(prefix)}_static.json ({args.n_static} chains)", flush=True)


if __name__ == "__main__":
    main()
