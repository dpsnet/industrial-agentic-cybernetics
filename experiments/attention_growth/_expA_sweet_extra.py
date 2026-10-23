"""甜点补测（分片版）：EXP-A 中间两档 A25（放行 0.25，σ_eff=0.75）、A10（放行 0.1，σ_eff=0.9）。
预注册判据见 EXPERIMENT_PLAN_AXIOM4_KIMI_BOOST.md §1.2a（A-H4，写死）。
协议与 kimi_boost.py expA 逐字一致：full_append、FIFO W=16、max_exps=3、6 代、Flash 档。
分片用法（4 进程并行）：
  python _expA_sweet_extra.py --tier A25 --rep-start 0 --rep-end 12 --out kimi_boost_A_sweet_A25_s1.json
  python _expA_sweet_extra.py --tier A25 --rep-start 12 --rep-end 24 --out kimi_boost_A_sweet_A25_s2.json
  python _expA_sweet_extra.py --tier A25 --rep-start 24 --rep-end 36 --out kimi_boost_A_sweet_A25_s3.json
  python _expA_sweet_extra.py --tier A25 --rep-start 36 --rep-end 48 --out kimi_boost_A_sweet_A25_s4.json
  （A10 同四份）
"""
import argparse, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kimi_boost as KB

SIGMA = {"A25": 0.25, "A10": 0.10}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tier", choices=["A25", "A10"], required=True)
    ap.add_argument("--rep-start", type=int, default=0)
    ap.add_argument("--rep-end", type=int, default=48)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    KB.M.configure("scnet-flash")
    print("provider=%s model=%s tier=%s reps=%d-%d" % (
        KB.M.PROVIDER, KB.M.API_MODEL, args.tier, args.rep_start, args.rep_end), flush=True)
    out = os.path.join(HERE, args.out)
    cond_specs = [(args.tier, SIGMA[args.tier], 3, "full_append", 16)]
    reps_list = list(range(args.rep_start, args.rep_end))
    KB.run_mode(out, cond_specs, 48, 6, reps_list)
    print("SWEET %s DONE -> %s" % (args.tier, args.out), flush=True)

if __name__ == "__main__":
    main()
