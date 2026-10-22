# -*- coding: utf-8 -*-
"""功效分析（修正版）：标记门压缩（C0 vs C1，pro 档）达到 α=0.05、功效 0.8 所需样本量。

数据：axiom4_results.json（主实验 pro 档）C0/C1 各 12 链；per-parent 后代均值口径。
功效模型：配对检验（H1AC_BOOST 同族），单侧 α=0.05。
  统计量 T = d_hat/(sd_pair/sqrt(n))，H0 下近似 N(0,1)，H1 下 N(delta,1)，delta = d*sqrt(n)/sd_pair。
  功效(n) = Phi(delta - z_{1-alpha})；并附置换核对（正确方向：mean(flip) >= obs 计 p）。
输出: e_power_markgate.json
"""
import json, sys, io, math, random, statistics as st

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = r"E:\workspace\industrial-agentic-cybernetics\experiments\attention_growth"
P1_SIG = "isolated_env"
rng = random.Random(2026)

def sig_of(c):
    return "P1" if P1_SIG.lower() in (c or "").lower() else None

def per_parent_means(runs):
    out = []
    for r in runs:
        Z = [sum(1 for it in g["memory"] if sig_of(it["content"]) == "P1") for g in r["gens"]]
        W = [sum(1 for it in g["new_experiences"] if sig_of(it["content"]) == "P1") for g in r["gens"]]
        vals = [W[n] for n in range(min(len(W), len(Z))) if Z[n] == 1]
        out.append(sum(vals) / len(vals) if vals else 0.0)
    return out

def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

with open(BASE + "\\axiom4_results.json", "r", encoding="utf-8") as f:
    runs = json.load(f)["runs"]
c0 = per_parent_means(runs.get("C0", []))
c1 = per_parent_means(runs.get("C1", []))
pairs = [a - b for a, b in zip(c0, c1)]
d, sd = st.mean(pairs), st.stdev(pairs)
effect_ratio = st.mean(c1) / st.mean(c0) if st.mean(c0) else float("nan")
print(f"n0={len(pairs)}  配对差 mean={d:.3f} sd={sd:.3f}  C1/C0 比值={effect_ratio:.3f}")

ns = [12, 24, 48, 96, 192, 384, 480, 960]
z = 1.6448536269514722
powers = {}
for n in ns:
    delta = d * math.sqrt(n) / sd
    powers[n] = phi(delta - z)

# 置换核对（正确方向）：真实效应下拒绝率
for n in (12, 48):
    rej = 0
    n_outer, n_inner = 800, 240
    for _ in range(n_outer):
        diffs = [rng.choice(pairs) for _ in range(n)]
        obs = sum(diffs) / n
        cnt = 0
        for _ in range(n_inner):
            flips = [x * (1 if rng.random() < 0.5 else -1) for x in diffs]
            if sum(flips) / n >= obs:
                cnt += 1
        if cnt / n_inner <= 0.05:
            rej += 1
    print(f"置换核对 n={n}: power={rej/n_outer:.3f}")

print("\n解析功效（配对检验，单侧 α=0.05）:")
for n in ns:
    print(f"  n={n:5d}  power={powers[n]:.3f}")
min_n = next((n for n in ns if powers[n] >= 0.8), None)
print(f"达到功效 0.8 所需配对样本量: {min_n if min_n else '>960'}")
print(f"当前 n=12 功效: {powers[12]:.3f}（不充分）")

out = {
    "n0": len(pairs),
    "pair_diff_mean": round(d, 3), "pair_diff_sd": round(sd, 3),
    "C1_C0_ratio": round(effect_ratio, 3),
    "method": "paired test, one-sided alpha=0.05, normal approx; permutation check at n=12/48",
    "power_by_n": {str(n): round(p, 3) for n, p in powers.items()},
    "min_n_for_power_0_8": min_n,
    "power_at_n12": round(powers[12], 3),
    "note": "效应量来自主实验 pro 档 per-parent 口径（C0=0.354, C1=0.188）；960 配对（H1AC_BOOST）远超所需",
}
with open(BASE + "\\e_power_markgate.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("saved e_power_markgate.json")
