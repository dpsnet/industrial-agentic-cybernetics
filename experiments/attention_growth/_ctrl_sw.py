# -*- coding: utf-8 -*-
"""v2 反馈控制实验执行器（跨翻转窗口捕捉版，2026-10-24 上午窗口）。
协议（判据预注册，与 §7.4 同构，追加切换动力学判据）：
- 动态臂 24 链，1:2 平行随动探针配比：rep 0/2/4/... 前各跑 1 条探针（C0-full W=16 6 代），
  探针 p_probe>=0.83 -> 该 2 链窗口 W4；p_probe<0.83 -> W8（链间切换，探针读数翻转即窗口切换）。
- 静态臂 12 链 W8（同协议对照，无门禁）。
- 切换动力学判据（N1 实验修复）：
  SW1 切换行使：probe_log 窗口序列出现 >=1 次 4<->8 切换；
  SW2 切换结局：切换点前后区段毒丸存活/记忆效用差分如实记录；
  SW3 零切换退路：全程同态则如实报告零切换（复现高态分支，并入跨窗口合并读数）。
用法：
  python _ctrl_sw.py --out-prefix _ctrl_sw
"""
import os, subprocess, json, time, argparse

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
    ts = runs[0]["gens"][-1].get("timestamp") if runs[0]["gens"] else None
    return pw, ts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-dynamic", type=int, default=24)
    ap.add_argument("--n-static", type=int, default=12)
    ap.add_argument("--probe-ratio", type=int, default=2, help="探针间隔链数")
    ap.add_argument("--out-prefix", default="_ctrl_sw")
    args = ap.parse_args()
    prefix = os.path.join(HERE, args.out_prefix)

    dyn_runs = {"runs": {"C0": []}}
    probe_log = []
    t0 = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[dyn] start {t0} n={args.n_dynamic} probe-every={args.probe_ratio}", flush=True)
    for rep in range(args.n_dynamic):
        if rep % args.probe_ratio == 0:
            pi = rep // args.probe_ratio
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
            print(f"[dyn rep{rep}] probe{pi} pw={pw}/6 p={p_probe:.3f} -> W{w} "
                  f"(probe_log[{len(probe_log)}])", flush=True)
        else:
            w = probe_log[-1]["window"]
        sub = f"{prefix}_r{rep}.json"
        rc, err = run_chain(w, sub)
        if rc != 0 or not os.path.exists(sub):
            print(f"[dyn rep{rep}] CHAIN FAILED rc={rc} tail={err}", flush=True)
            raise SystemExit(1)
        d = json.load(open(sub, encoding="utf-8"))
        dyn_runs["runs"]["C0"].extend(d["runs"][list(d["runs"].keys())[0]])
        print(f"[dyn rep{rep}] W{w} done {time.strftime('%H:%M:%S')}", flush=True)
    with open(f"{prefix}.json", "w", encoding="utf-8") as f:
        json.dump({"runs": dyn_runs["runs"], "probe_log": probe_log}, f,
                  ensure_ascii=False, indent=1)
    print(f"[dyn] DONE -> {os.path.basename(prefix)}.json ({args.n_dynamic} chains, "
          f"{len(probe_log)} probes)", flush=True)

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
