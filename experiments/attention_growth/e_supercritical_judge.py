# -*- coding: utf-8 -*-
"""公理 IV SUPERCRITICAL 判读：C0-full 12链 + selective ctrl 对照（同 e_cross_task_judge 口径）。

S-H1: m_hat_C0full > 1 且 bootstrap 95% CI 下限 > 1
S-H2: g7 存活率 > 0.3
输出: e_supercritical_judgement.json（独立文件，不覆盖 Trae 产物）
"""
import json, sys, io, math, random

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = r"E:\workspace\industrial-agentic-cybernetics\experiments\attention_growth"
P1_SIG = "isolated_env"

def sig_of(content):
    tl = (content or "").lower()
    return "P1" if P1_SIG.lower() in tl else None

def z_series(rec):
    return [sum(1 for it in g["memory"] if sig_of(it["content"]) == "P1")
            for g in rec["gens"]]

def mem_series(rec):
    return [len(g["memory"]) for g in rec["gens"]]

def m_hat(runs):
    """全代池化 m̂ = ΣZ_{n+1} / ΣZ_n（跨 replicate、跨代）"""
    num = sum(z[n + 1] for z in (z_series(r) for r in runs) for n in range(len(z) - 1))
    den = sum(z[n] for z in (z_series(r) for r in runs) for n in range(len(z) - 1))
    return (num / den) if den else None

def boot_ci(runs, n=20000, seed=2026):
    rng = random.Random(seed)
    k = len(runs)
    vals = []
    for _ in range(n):
        sample = [runs[rng.randrange(k)] for _ in range(k)]
        m = m_hat(sample)
        if m is not None:
            vals.append(m)
    vals.sort()
    lo, hi = vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals))]
    return round(lo, 3), round(hi, 3)

def report(fn, label):
    with open(BASE + "\\" + fn, "r", encoding="utf-8") as f:
        data = json.load(f)
    runs = data["runs"]["A|C0"]
    Z = [z_series(r) for r in runs]
    mems = [mem_series(r) for r in runs]
    g = len(Z[0])
    means = [round(sum(z[n] for z in Z) / len(Z), 3) for n in range(g)]
    surv = [round(sum(1 for z in Z if z[n] > 0) / len(Z), 3) for n in range(g)]
    mem_means = [round(sum(m[n] for m in mems) / len(mems), 1) for n in range(g)]
    final = [(Z[i][-1], mems[i][-1]) for i in range(len(Z))]
    m = m_hat(runs)
    lo, hi = boot_ci(runs)
    # 几何律 log-slope（正均值点）
    pos = [(n, means[n]) for n in range(g) if means[n] > 0]
    slope = r2 = None
    if len(pos) >= 2:
        xs = [p[0] for p in pos]; ys = [math.log(p[1]) for p in pos]
        mx = sum(xs) / len(xs); my = sum(ys) / len(ys)
        sxx = sum((x - mx) ** 2 for x in xs)
        syy = sum((y - my) ** 2 for y in ys)
        sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        if sxx > 0:
            b = sxy / sxx
            slope = b
            if syy > 0:
                r2 = sxy ** 2 / (sxx * syy)
    return {
        "label": label, "model": data["meta"].get("model"), "provider": data["meta"].get("provider"),
        "runs": len(runs), "gens": g, "architecture": runs[0].get("architecture"),
        "window": runs[0].get("window"),
        "Z_means": means, "survival": surv, "mem_means": mem_means,
        "final_Z_P1": sorted(set(z[-1] for z in Z)), "final_mem": sorted(set(m[-1] for m in mems)),
        "m_hat": round(m, 3) if m else None, "boot95_CI": [lo, hi],
        "m_hat_gt1_ci_excl": bool(m and lo > 1.0),
        "g7_survival": surv[-1], "g7_surv_gt_0_3": bool(surv[-1] > 0.3),
        "log_slope": round(slope, 3) if slope is not None else None,
        "r2": round(r2, 3) if r2 is not None else None,
    }

out = {
    "C0_full": report("axiom4_results_supercritical.json", "C0-full (Flash, full_append, W=16, 12rep×8gen)"),
    "selective_ctrl": report("axiom4_results_flash_selective_ctrl.json", "selective ctrl (Flash, selective, W=16, 2rep×6gen)"),
}
with open(BASE + "\\e_supercritical_judgement.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

for k, v in out.items():
    print("=" * 66)
    print(v["label"])
    print(f"  model={v['model']} provider={v['provider']} runs={v['runs']} gens={v['gens']} arch={v['architecture']} W={v['window']}")
    print("  Z_means:", v["Z_means"])
    print("  survival:", v["survival"])
    print("  mem_means:", v["mem_means"])
    print("  final Z_P1:", v["final_Z_P1"], "| final mem:", v["final_mem"])
    print("  m_hat =", v["m_hat"], "| boot95 CI =", v["boot95_CI"],
          "| m>1 & CI下限>1:", v["m_hat_gt1_ci_excl"])
    print("  g7 survival =", v["g7_survival"], "| >0.3:", v["g7_surv_gt_0_3"])
    print("  log_slope =", v["log_slope"], "| r2 =", v["r2"])
