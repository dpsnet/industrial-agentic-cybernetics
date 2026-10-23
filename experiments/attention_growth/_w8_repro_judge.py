"""W=8 分裂归因判读：同日重跑对照（KIMI 三轮作业 2 执行结果）。
四批数据 Fisher 精确检验 + 毒株写入率对比。
"""
import json
from math import comb

HERE = r"E:\workspace\industrial-agentic-cybernetics\experiments\attention_growth"


def z_series(rec):
    names = ["P1", "P2", "P3"]
    return [sum(1 for it in g["memory"] if it.get("lineage") in names) for g in rec["gens"]]


def pw_series(rec):
    names = ["P1", "P2", "P3"]
    return [sum(1 for it in g["new_experiences"] if it.get("lineage") in names) for g in rec["gens"]]


def surv_count(runs):
    return sum(1 for r in runs if z_series(r)[-1] > 0)


def fisher_exact(a, b, c, d):
    """2x2 [[a,b],[c,d]] 双侧 Fisher 精确检验。"""
    col1, col2 = a + c, b + d
    row1, row2 = a + b, c + d
    n = row1 + row2

    def hyper(k):
        return comb(col1, k) * comb(col2, row1 - k) / comb(n, row1)

    lo = max(0, row1 - col2)
    hi = min(row1, col1)
    p_obs = hyper(a)
    p = 0.0
    for k in range(lo, hi + 1):
        if hyper(k) <= p_obs + 1e-15:
            p += hyper(k)
    return p


def main():
    d8 = json.load(open(HERE + r"\axiom4_results_supercritical_W8.json", encoding="utf-8"))
    d8r = json.load(open(HERE + r"\axiom4_results_supercritical_W8_repro.json", encoding="utf-8"))
    db = json.load(open(HERE + r"\kimi_boost_B.json", encoding="utf-8"))
    dbr = json.load(open(HERE + r"\kimi_boost_B_W8_repro.json", encoding="utf-8"))

    batches = [
        ("MAIN W8 10-22 (orig)", d8["runs"]["A|C0"]),
        ("MAIN W8 10-23 (repro)", d8r["runs"]["C0"]),
        ("EXP-B b3|W8 10-23 (orig)", db["runs"]["b3|W8"]),
        ("EXP-B b3|W8 10-23 (repro)", dbr["runs"]["b3|W8"]),
    ]
    print("=== W=8 分裂归因：同日重跑对照判读 ===")
    for label, runs in batches:
        n = len(runs)
        s = surv_count(runs)
        pw = [sum(pw_series(r)) for r in runs]
        print("  %s n=%d surv=%d/%d (%.3f) avg_pw_total=%.2f" % (
            label, n, s, n, s / n, sum(pw) / n))

    # 汇总
    m22 = batches[0][1]; m23 = batches[1][1]; e23o = batches[2][1]; e23r = batches[3][1]
    all23 = m23 + e23o + e23r
    pairs = [
        ("MAIN 10-22 vs MAIN 10-23", surv_count(m22), len(m22) - surv_count(m22),
         surv_count(m23), len(m23) - surv_count(m23)),
        ("MAIN 10-22 vs EXP-B 10-23 orig", surv_count(m22), len(m22) - surv_count(m22),
         surv_count(e23o), len(e23o) - surv_count(e23o)),
        ("MAIN 10-22 vs ALL 10-23 (n=36)", surv_count(m22), len(m22) - surv_count(m22),
         surv_count(all23), len(all23) - surv_count(all23)),
        ("EXP-B 10-23 orig vs repro (同日)", surv_count(e23o), len(e23o) - surv_count(e23o),
         surv_count(e23r), len(e23r) - surv_count(e23r)),
        ("MAIN 10-23 repro vs EXP-B 10-23 orig", surv_count(m23), len(m23) - surv_count(m23),
         surv_count(e23o), len(e23o) - surv_count(e23o)),
    ]
    print("=== Fisher 精确检验（存活, 灭绝）===")
    for label, a, b, c, d in pairs:
        print("  %s: p=%.4g" % (label, fisher_exact(a, b, c, d)))


if __name__ == "__main__":
    main()
