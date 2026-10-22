# -*- coding: utf-8 -*-
"""S-H3：以 SUPERCRITICAL 实测繁殖核（full_append）参数化 GW 仿真。

PMF 提取口径（与主实验 H3 一致）：Z_n==1 代 → 每亲新写 P1 条目数 W_{n+1}。
C0-full: n=0 处 12 观测（Z_0≡1）；W32: n=0 处 6 观测（W_1≡2）。
判据（预注册 §3 S-H3）：超临界变体 q_sim 与理论最小不动点 q* 偏差 < 0.02。
输出: e_supercritical_sh3.json（独立文件）
"""
import json, sys, io, math
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = r"E:\workspace\industrial-agentic-cybernetics\experiments\attention_growth"
P1_SIG = "isolated_env"
GENS = 40
SEED = 2026

def sig_of(c):
    tl = (c or "").lower()
    return "P1" if P1_SIG.lower() in tl else None

def load(fn, key):
    with open(BASE + "\\" + fn, "r", encoding="utf-8") as f:
        d = json.load(f)
    return d["runs"][key]

def pmf_from(fn, key):
    """Z_n==1 代的每亲新写 P1 后代数经验分布。"""
    runs = load(fn, key)
    counts = []
    for r in runs:
        Z = [sum(1 for it in g["memory"] if sig_of(it["content"]) == "P1") for g in r["gens"]]
        W = [sum(1 for it in g["new_experiences"] if sig_of(it["content"]) == "P1") for g in r["gens"]]
        counts += [W[n] for n in range(min(len(W), len(Z))) if Z[n] == 1]
    kmax = max(counts)
    pmf = [counts.count(k) / len(counts) for k in range(kmax + 1)]
    return {"n": len(counts), "pmf": pmf, "mean": sum(k * p for k, p in enumerate(pmf))}

def gen_fun(pmf, s):
    return sum(p * s ** k for k, p in enumerate(pmf))

def q_star(pmf):
    if sum(k * p for k, p in enumerate(pmf)) <= 1 + 1e-12:
        return 1.0
    s = 0.0
    for _ in range(100000):
        s2 = gen_fun(pmf, s)
        if abs(s2 - s) < 1e-13:
            break
        s = s2
    return s

def simulate(pmf, gens, seed, n_rep=100000):
    rng = np.random.default_rng(seed)
    pm = np.array(pmf, dtype=float); pm = pm / pm.sum()
    z = np.ones(n_rep, dtype=np.int64)
    E, surv = np.zeros(gens), np.zeros(gens)
    tau = np.full(n_rep, -1, dtype=np.int64)
    for g in range(gens):
        E[g] = z.mean(); surv[g] = (z > 0).mean()
        alive = z > 0
        if not alive.any():
            break
        k_draws = rng.choice(len(pm), size=int(z[alive].sum()), p=pm)
        idx = np.repeat(np.arange(n_rep), np.where(alive, z, 0))
        z = np.bincount(idx, weights=k_draws, minlength=n_rep).astype(np.int64)
        newly = (z == 0) & alive & (tau < 0)
        tau[newly] = g + 1
    return E, surv, tau

out = {}
for name, (fn, key) in {"C0_full": ("axiom4_results_supercritical.json", "A|C0"),
                        "W32": ("axiom4_results_supercritical_W32.json", "A|C0")}.items():
    v = pmf_from(fn, key)
    m = v["mean"]
    n_rep = 100000 if m > 1 else 20000
    E, surv, tau = simulate(v["pmf"], GENS, SEED, n_rep)
    qs = q_star(v["pmf"])
    q_sim = float((tau >= 0).mean())
    rec = {
        "mean_m": round(m, 4), "pmf": v["pmf"], "n_pmf": v["n"],
        "n_rep": n_rep, "q_star": round(qs, 5), "q_sim": round(q_sim, 5),
        "dev": round(abs(q_sim - qs), 5),
        "survival_last": float(surv[-1]),
        "markov_ok": bool(np.all(surv <= E + 1e-9)),
        "criterion": "dev<0.02", "pass": bool(abs(q_sim - qs) < 0.02),
    }
    out[name] = rec
    print(f"[{name}] n_pmf={v['n']} pmf={v['pmf']} m={rec['mean_m']} "
          f"q*={rec['q_star']} q_sim={rec['q_sim']} dev={rec['dev']} "
          f"markov_ok={rec['markov_ok']} pass={rec['pass']} surv_last={rec['survival_last']}")

with open(BASE + "\\e_supercritical_sh3.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("saved e_supercritical_sh3.json")
