"""毒株转写率漂移模型 v2：合并历史 4 批（T=8）+ 探针 8 批（T=6）重估。
支持每批不同 T 的 Beta-Binomial（链级 Binomial(T_b, p_batch)，批次级 Beta）。
"""
import json, os, glob
from math import lgamma
from scipy.optimize import minimize
from scipy.stats import beta

HERE = r"E:\workspace\industrial-agentic-cybernetics\experiments\attention_growth"
names = ["P1", "P2", "P3"]


def load_batch_pw(path, key=None, T=8):
    d = json.load(open(path, encoding="utf-8"))
    if key:
        runs = d["runs"][key]
    else:
        runs = d["runs"][list(d["runs"].keys())[0]]
    out = []
    for r in runs:
        pw = sum(sum(1 for it in g["new_experiences"] if it.get("lineage") in names)
                 for g in r["gens"])
        out.append(pw)
    return out


def bb_nll(theta, batches):
    """batches = [(T_b, [pw_i...]), ...]；负对数似然（忽略与参数无关的组合系数）。"""
    a, b = theta
    if a <= 0 or b <= 0:
        return 1e18
    nll = 0.0
    for Tb, pws in batches:
        for k in pws:
            nll -= (lgamma(a + k) + lgamma(b + Tb - k) - lgamma(a + b + Tb)
                    - (lgamma(a) + lgamma(b) - lgamma(a + b)))
    return nll


def main():
    hist = [
        (8, HERE + r"\axiom4_results_supercritical_W8.json", "A|C0"),
        (8, HERE + r"\axiom4_results_supercritical_W8_repro.json", "C0"),
        (8, HERE + r"\kimi_boost_B.json", "b3|W8"),
        (8, HERE + r"\kimi_boost_B_W8_repro.json", "b3|W8"),
    ]
    batches = []
    print("=== 历史批次 (T=8) ===")
    for T, path, key in hist:
        pws = load_batch_pw(path, key, T)
        batches.append((T, pws))
        print(f"  {os.path.basename(path)} [{key}] n={len(pws)} mean={sum(pws)/len(pws)/T:.3f}/代")

    probes = []
    for f in sorted(glob.glob(os.path.join(HERE, "probe_0*.json"))):
        pws = load_batch_pw(f, T=6)
        probes.append((f, pws))
    print("=== 探针批次 (T=6) ===")
    for f, pws in probes:
        batches.append((6, pws))
        print(f"  {os.path.basename(f)} n={len(pws)} pw={pws[0]}/6 p={pws[0]/6:.3f}")

    n_batches = len(batches)
    n_chains = sum(len(pws) for _, pws in batches)
    allk = [k for _, pws in batches for k in pws]
    n = len(allk)
    mean_p = sum(allk) / n
    Ts = [sum(len(pws) * T for T, pws in batches)][0]
    mean_pp = sum(allk) / Ts
    var_p = sum((k - mean_pp) ** 2 for k in allk) / n
    a0 = max(mean_pp * (mean_pp * (1 - mean_pp) / var_p - 1), 0.05)
    b0 = max((1 - mean_pp) * (mean_pp * (1 - mean_pp) / var_p - 1), 0.05)
    res = minimize(bb_nll, [a0, b0], args=(batches,), method="Nelder-Mead",
                   options={"maxiter": 10000, "xatol": 1e-10, "fatol": 1e-10})
    a, b = res.x
    print(f"\nMLE over {n_batches} batches / {n_chains} chains: alpha={a:.3f} beta={b:.3f} p_hat={a/(a+b):.3f}")
    lo, hi = beta.ppf([0.025, 0.975], a, b)
    print(f"批次 p_batch 后验预测 95%: [{lo:.3f}, {hi:.3f}]（每代均值）")
    print(f"对应 6 代探针毒株写入预测: [{lo*6:.2f}, {hi*6:.2f}]")
    # 与 v1（4 批）对比
    print("\n[对比] v1 (4批): alpha=0.570 beta=0.268 区间 [0.009, 1.000]")


if __name__ == "__main__":
    main()
