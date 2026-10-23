"""探针门控重扫（KIMI 第四轮作业 2 执行版）：当前探针确认高转写态下，重跑主协议 SUPERCRITICAL 档 W∈{4,8,12} 各 12 链。
协议与 axiom4_memory_propagation.py main 逐字一致：full_append、FIFO window、C0 无门禁、6 代、scnet-flash、temp 0.7。
判据（预写死）：高转写态下 W=8 存活率 >=0.5 ⟹ M_c 改述为状态条件量（正文已按此修改）。
分片用法（6 进程并行，每片 6 链）：
  python _mc_state_rescan.py --window 4 --rep-start 0 --rep-end 6  --out _mc_state_rescan_W4_s1.json
  python _mc_state_rescan.py --window 4 --rep-start 6 --rep-end 12 --out _mc_state_rescan_W4_s2.json
  ... (W8, W12 同)
"""
import argparse, os, subprocess, json

HERE = os.path.dirname(os.path.abspath(__file__))
PY = r"D:\pyenv\pyenv-win\versions\3.11.8\python.exe"
MAIN = os.path.join(HERE, "axiom4_memory_propagation.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, required=True)
    ap.add_argument("--rep-start", type=int, default=0)
    ap.add_argument("--rep-end", type=int, default=12)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = os.path.join(HERE, args.out)
    shards = []
    for rep in range(args.rep_start, args.rep_end):
        sub = out[:-5] + f"_r{rep}.json"
        cmd = [PY, MAIN, "main", "--provider=scnet-flash",
               "--architecture=full_append", f"--window={args.window}",
               "--reps=1", "--gens=6", "--conds=C0", f"--out={sub}"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=480)
        if os.path.exists(sub):
            shards.append(sub)
        else:
            print(f"[mc_rescan W{args.window} r{rep}] FAILED rc={r.returncode} tail={r.stderr[-300:]}",
                  flush=True)
    merged = {"runs": {}}
    for fp in shards:
        d = json.load(open(fp, encoding="utf-8"))
        for k, v in d.get("runs", {}).items():
            merged["runs"].setdefault(k, []).extend(v)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    print(f"=== DONE W{args.window} reps {args.rep_start}-{args.rep_end} "
          f"-> {os.path.basename(out)} ({len(shards)} chains) ===", flush=True)


if __name__ == "__main__":
    main()
