"""
公理 IV GW 数值验证：实测繁殖核 → Galton-Watson 仿真
====================================================
计划：EXPERIMENT_PLAN_AXIOM4.md §4.4；判据 §4.2 H3-数值：
  - 超临界（m>1）：q_sim 与理论最小不动点 q* 偏差 < 0.02
  - 亚临界（m<1）：灭绝频率 >= 0.999
  - Markov 界：P(Z_n>=1) <= E[Z_n] = m^n E(0)（数值核对）

PMF 变体：
  - C0/C1：Z_n==1 会话的每亲新写条目经验分布
  - C2-thin：C0 经验 PMF 经 Bernoulli(0.5) 抽稀（m = 0.5μ 的分布层检验）
"""
import os, json, math, sys
import numpy as np
import axiom4_memory_propagation as amp
from axiom4_memory_propagation import load_results, z_series, offspring_written, CONDITIONS

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "axiom4_gw_sim.json")
GENS_SUP = 40      # 超临界代数（q 收敛）
GENS_SUB = 30      # 亚临界代数
SEED = 2026


def empirical_pmfs():
    res = load_results()
    out = {}
    for cond, runs in res["runs"].items():
        counts = []
        for r in runs:
            Z, W = z_series(r), offspring_written(r)
            counts += [W[n] for n in range(min(len(W), len(Z))) if Z[n] == 1]
        if len(counts) >= 10:
            kmax = max(counts)
            pmf = [counts.count(k) / len(counts) for k in range(kmax + 1)]
            out[cond] = {"n": len(counts), "pmf": pmf,
                         "mean": sum(k * p for k, p in enumerate(pmf))}
    return out


def thin_pmf(pmf, p):
    """Bernoulli(p) 抽稀：每名后代独立以 p 存活的 PMF。"""
    res = [0.0] * (len(pmf) + 1)
    for j, pj in enumerate(pmf):
        for k in range(j + 1):
            res[k] += pj * math.comb(j, k) * (p ** k) * ((1 - p) ** (j - k))
    return res


def gen_fun(pmf, s):
    return sum(p * s ** k for k, p in enumerate(pmf))


def q_star(pmf):
    """灭绝概率理论值：φ 的最小不动点；亚临界为 1。"""
    if sum(k * p for k, p in enumerate(pmf)) <= 1 + 1e-12:
        return 1.0
    s = 0.0
    for _ in range(100000):
        s2 = gen_fun(pmf, s)
        if abs(s2 - s) < 1e-13:
            break
        s = s2
    return s


def simulate(pmf, gens, seed):
    """向量化 Galton-Watson：返回 E[Z_n] 序列、存活率序列、灭绝代数（-1=未灭绝）。"""
    rng = np.random.default_rng(seed)
    pm = np.array(pmf, dtype=float)
    pm = pm / pm.sum()
    n_rep = 100000 if pm @ np.arange(len(pm)) <= 1 else 20000
    z = np.ones(n_rep, dtype=np.int64)
    E, surv = np.zeros(gens), np.zeros(gens)
    tau = np.full(n_rep, -1, dtype=np.int64)
    for g in range(gens):
        E[g] = z.mean()
        surv[g] = (z > 0).mean()
        alive = z > 0
        if not alive.any():
            break
        k_draws = rng.choice(len(pm), size=int(z[alive].sum()), p=pm)
        idx = np.repeat(np.arange(n_rep), np.where(alive, z, 0))
        z = np.bincount(idx, weights=k_draws, minlength=n_rep).astype(np.int64)
        newly = (z == 0) & alive & (tau < 0)
        tau[newly] = g + 1
    return n_rep, E, surv, tau


def main():
    variants = {}
    emp = empirical_pmfs()
    for cond in ("C0", "C1"):
        if cond in emp:
            variants[f"{cond}-empirical"] = emp[cond]
    if "C0" in emp:
        t = thin_pmf(emp["C0"]["pmf"], 0.5)
        variants["C2-thin(0.5)"] = {"n": emp["C0"]["n"], "pmf": t,
                                    "mean": sum(k * p for k, p in enumerate(t))}

    results = {}
    for name, v in variants.items():
        m = v["mean"]
        gens = GENS_SUP if m > 1 else GENS_SUB
        n_rep, E, surv, tau = simulate(v["pmf"], gens, SEED)
        qs = q_star(v["pmf"])
        q_sim = float((tau >= 0).mean())
        rec = {
            "mean_m": m, "pmf": v["pmf"], "n_pmf": v["n"],
            "gens": gens, "n_rep": n_rep,
            "q_star": qs, "q_sim": q_sim, "dev": abs(q_sim - qs),
            "survival_series": [round(float(s), 5) for s in surv],
            "E_series": [round(float(e), 4) for e in E],
            "tau_mean_extinct": float(tau[tau >= 0].mean()) if (tau >= 0).any() else None,
            "markov_ok": bool(np.all(surv <= E + 1e-9)),
            "surv_last": float(surv[-1]),
            "geo_law_max_dev": float(max(
                abs(E[n] - (m ** n)) for n in range(gens))) if abs(m - 1) > 1e-9 else None,
        }
        # 预注册判据（§4.2 H3-数值）：亚临界判"灭绝频率>=0.999"即 q_sim
        rec["criterion"] = ("dev<0.02" if m > 1 else "q_sim>=0.999")
        rec["pass"] = bool((rec["dev"] < 0.02) if m > 1
                           else (q_sim >= 0.999 and rec["markov_ok"]))
        results[name] = rec
        print(f"[{name}] m={m:.3f} q*={qs:.4f} q_sim={q_sim:.4f} dev={rec['dev']:.4f} "
              f"markov_ok={rec['markov_ok']} pass={rec['pass']}", flush=True)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(f"\nsaved {len(results)} variants to {OUT}")


if __name__ == "__main__":
    opts = {a[2:].split("=", 1)[0]: a[2:].split("=", 1)[1]
            for a in sys.argv[1:] if a.startswith("--") and "=" in a}
    provider = opts.get("provider", "deepseek")
    amp.configure(provider, opts.get("results"))
    if provider != "deepseek":
        OUT = os.path.join(HERE, f"axiom4_gw_sim_{provider}.json")
    main()
