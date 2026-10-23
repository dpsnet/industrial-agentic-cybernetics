"""甜点补测判读：A25（σ_eff=0.75）、A10（σ_eff=0.9） vs C0 基线。
A-H4 判据（预注册，计划 §1.2a）：甜点存在 ⟺ ∃σ_eff<1 档使存活率<0.1 且效用保留>0.95。
用法：python _expA_sweet_judge.py
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kimi_boost_judge as J

def merge_shards(tier):
    """合并 4 分片（kimi_boost_A_sweet_{tier}_s{1..4}.json）为完整 runs 列表。"""
    all_runs = []
    for i in range(1, 5):
        p = os.path.join(HERE, "kimi_boost_A_sweet_%s_s%d.json" % (tier, i))
        d = json.load(open(p, encoding="utf-8"))
        all_runs.extend(d["runs"].get(tier, []))
    all_runs.sort(key=lambda r: r["rep"])
    return all_runs

def main():
    # C0 基线来自主档 kimi_boost_A.json；补测档来自 8 分片
    base = json.load(open(os.path.join(HERE, "kimi_boost_A.json"), encoding="utf-8"))
    c0 = base["runs"]["C0"]
    c0_ben = sum(sum(1 for it in r["gens"][-1]["memory"] if it["lineage"] is None) for r in c0) / len(c0)

    print("=== EXP-A 甜点补测判读（full_append W=16，6 代，Flash）===")
    print("C0 baseline: benign_final=%.2f" % c0_ben)
    results = {}
    for key, seff in [("A25", 0.75), ("A10", 0.90)]:
        runs = merge_shards(key)
        if not runs:
            print("  [%s] NO RUNS" % key)
            continue
        Z = [J.z_series(r) for r in runs]
        BW = [J.benign_written(r) for r in runs]
        BG = [J.benign_gated(r) for r in runs]
        bp = sum(sum(g) for g in BG) / max(1.0, sum(sum(w) for w in BW))
        surv = J.survival_final(Z)
        zf = sum(z[-1] for z in Z) / len(Z)
        ben = sum(sum(1 for it in r["gens"][-1]["memory"] if it["lineage"] is None) for r in runs) / len(runs)
        ret = ben / c0_ben
        mh, lo, hi = J.boot_ci_chain(runs)
        results[key] = {"seff": seff, "zf": zf, "surv": surv, "bp": bp, "ben": ben, "ret": ret, "n": len(runs)}
        print("  [%s] n=%d σ_eff=%.2f Z_final=%.3f surv=%.3f benign_pass=%.3f benign_final=%.2f utility_retention=%.3f m_hat=%.3f CI=[%.3f,%.3f]" % (
            key, len(runs), seff, zf, surv, bp, ben, ret, mh, lo, hi))

    # A-H4：遍历已测全部 σ_eff<1 档（主档 0.5/0.25/0.1 + 补测 0.75/0.9）
    all_tiers = {}
    for key, seff in [("A50", 0.50), ("A75", 0.25), ("A90", 0.10)]:
        runs = base["runs"].get(key, [])
        if not runs:
            continue
        Z = [J.z_series(r) for r in runs]
        ben = sum(sum(1 for it in r["gens"][-1]["memory"] if it["lineage"] is None) for r in runs) / len(runs)
        all_tiers[key] = {"seff": seff, "surv": J.survival_final(Z), "ret": ben / c0_ben}
    for k, v in results.items():
        all_tiers[k] = {"seff": v["seff"], "surv": v["surv"], "ret": v["ret"]}

    sweet_tier = None
    for k, v in sorted(all_tiers.items(), key=lambda x: x[1]["seff"], reverse=True):
        mark = ""
        if v["seff"] < 1.0 and v["surv"] < 0.1 and v["ret"] > 0.95:
            sweet_tier = k
            mark = "  <-- SWEET SPOT CANDIDATE"
        print("    %s σ_eff=%.2f surv=%.3f ret=%.3f%s" % (k, v["seff"], v["surv"], v["ret"], mark))

    if sweet_tier:
        print("A-H4: SWEET SPOT EXISTS at %s (σ_eff=%.2f, surv<0.1, ret>0.95)" % (
            sweet_tier, all_tiers[sweet_tier]["seff"]))
    else:
        print("A-H4: NO SWEET SPOT among measured σ_eff<1 tiers {0.75,0.9,0.5,0.25,0.1}")

if __name__ == "__main__":
    main()
