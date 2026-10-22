# -*- coding: utf-8 -*-
"""SUPERCRITICAL 阶段判读 v2：C0-full / C1-full(部分) / C3-full(部分) / W8 / W32 / selective。

输出: e_supercritical_judgement2.json（独立文件，不覆盖 Trae 产物）
"""
import json, sys, io, math, random

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = r"E:\workspace\industrial-agentic-cybernetics\experiments\attention_growth"
P1_SIG = "isolated_env"

def sig_of(content):
    tl = (content or "").lower()
    return "P1" if P1_SIG.lower() in tl else None

def z_series(rec):
    return [sum(1 for it in g["memory"] if sig_of(it["content"]) == "P1") for g in rec["gens"]]

def mem_series(rec):
    return [len(g["memory"]) for g in rec["gens"]]

def m_hat(runs):
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

def report(fn, label, expected, key="A|C0"):
    with open(BASE + "\\" + fn, "r", encoding="utf-8") as f:
        data = json.load(f)
    runs = data["runs"].get(key) or []
    Z = [z_series(r) for r in runs]
    mems = [mem_series(r) for r in runs]
    g = len(Z[0]) if Z else 0
    means = [round(sum(z[n] for z in Z) / len(Z), 3) for n in range(g)] if Z else []
    surv = [round(sum(1 for z in Z if z[n] > 0) / len(Z), 3) for n in range(g)] if Z else []
    mem_means = [round(sum(m[n] for m in mems) / len(mems), 1) for n in range(g)] if mems else []
    final_z = sorted(set(z[-1] for z in Z)) if Z else []
    final_mem = sorted(set(m[-1] for m in mems)) if mems else []
    m = m_hat(runs)
    lo, hi = boot_ci(runs) if runs else (None, None)
    return {
        "label": label, "model": data["meta"].get("model"), "runs_done": len(runs),
        "expected": expected, "gens": g,
        "architecture": runs[0].get("architecture") if runs else None,
        "window": runs[0].get("window") if runs else None,
        "Z_means": means, "survival": surv, "mem_means": mem_means,
        "final_Z_P1": final_z, "final_mem": final_mem,
        "m_hat": round(m, 3) if m else None, "boot95_CI": [lo, hi],
        "m_hat_gt1_ci_excl": bool(m and lo and lo > 1.0),
    }

out = {
    "C0_full": report("axiom4_results_supercritical.json", "C0-full", 12),
    "C1_full_partial": report("axiom4_results_supercritical_C1_full.json", "C1-full(部分)", 12, "A|C1"),
    "C3_full_partial": report("axiom4_results_supercritical_C3_full.json", "C3-full(部分)", 12, "A|C3"),
    "W8": report("axiom4_results_supercritical_W8.json", "W=8 (C0)", 6),
    "W32": report("axiom4_results_supercritical_W32.json", "W=32 (C0)", 6),
    "selective_ctrl": report("axiom4_results_flash_selective_ctrl.json", "selective ctrl", 2),
}

# 容量敏感性：W=8/16/32 的最终代 Z 与 m̂
sens = {
    "W8":  {"Z": out["W8"]["final_Z_P1"], "m": out["W8"]["m_hat"]},
    "W16": {"Z": out["C0_full"]["final_Z_P1"], "m": out["C0_full"]["m_hat"]},
    "W32": {"Z": out["W32"]["final_Z_P1"], "m": out["W32"]["m_hat"]},
}
out["capacity_sensitivity"] = sens
out["capacity_monotone"] = bool(sens["W8"]["Z"][-1] <= sens["W16"]["Z"][-1] <= sens["W32"]["Z"][-1]
                                and sens["W8"]["Z"][-1] < sens["W32"]["Z"][-1])

with open(BASE + "\\e_supercritical_judgement2.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

for k, v in out.items():
    if k in ("capacity_sensitivity", "capacity_monotone"):
        continue
    print("=" * 66)
    print(v["label"], f"(runs {v['runs_done']}/{v['expected']}, gens {v['gens']}, "
          f"arch={v['architecture']}, W={v['window']})")
    print("  Z_means:", v["Z_means"])
    print("  survival:", v["survival"])
    print("  mem_means:", v["mem_means"])
    print("  final Z_P1:", v["final_Z_P1"], "| final mem:", v["final_mem"],
          "| m_hat =", v["m_hat"], "| CI =", v["boot95_CI"],
          "| m>1&CI下限>1:", v["m_hat_gt1_ci_excl"])
print("=" * 66)
print("capacity_sensitivity (final Z / m_hat):")
for w in ["W8", "W16", "W32"]:
    print(f"  {w}: Z={sens[w]['Z']}, m={sens[w]['m']}")
print("capacity monotone:", out["capacity_monotone"])
