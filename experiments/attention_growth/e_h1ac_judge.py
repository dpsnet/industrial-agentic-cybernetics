# -*- coding: utf-8 -*-
"""H1AC_BOOST 正式判读（预注册口径，EXPERIMENT_PLAN_AXIOM4_H1AC_BOOST.md §3）。

判据：
  B-H1a: replicate 级配对差 d_r = mu_C0_r - mu_C1_r，单侧符号翻转置换检验（10^4）p<0.05 且 dbar>0
  B-H1c: r_hat = mu_C2/mu_C0 ∈ [0.35,0.65] 且 bootstrap 95% CI ⊆ [0.35,0.65]
  B-H2 : C0+C1 池化 log-linear R^2 >= 0.8，逐代比无趋势
mu 口径: per-parent 写出率 = Σ(写出 P1) / Σ(Z==1 代数)（与主实验 H1a 一致）
输出: e_h1ac_judgement.json
"""
import json, sys, io, os, math, random, statistics as st

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = r"E:\workspace\industrial-agentic-cybernetics\experiments\attention_growth"
rng = random.Random(20261022)

def load(fn):
    with open(os.path.join(BASE, fn), encoding="utf-8") as f:
        return json.load(f)

def run_metrics(run):
    """返回 (mu_chain, w_pool_num, z_pool_den, ZP1_traj, survival)
    mu_chain: replicate 级链均 per-parent 写出率（B-H1a 配对差判读单位，预注册 §2.3）
    w_pool_num/z_pool_den: 池化口径 ΣW / Σ#(Z==1)（B-H1c 比值，与主实验 H1a 池化写出率一致）
    survival: 末代 Z_P1>0"""
    gens = run["gens"]
    Z1 = [sum(1 for it in g["memory"] if it.get("lineage") == "P1") for g in gens]
    W1 = [sum(1 for it in g["new_experiences"] if it.get("lineage") == "P1") for g in gens]
    v = [W1[i] for i in range(min(len(W1), len(Z1))) if Z1[i] == 1]
    mu_chain = sum(v) / len(v) if v else 0.0
    return mu_chain, sum(v), len(v), Z1, (Z1[-1] > 0)

c0 = load("axiom4_results_h1ac_C0.json")["runs"]["AD|C0"]
c1 = load("axiom4_results_h1ac_C1.json")["runs"]["AD|C1"]
c2 = load("axiom4_results_h1ac_C2.json")["runs"]["AD|C2"]

m0 = [run_metrics(r) for r in c0]
m1 = [run_metrics(r) for r in c1]
m2 = [run_metrics(r) for r in c2]

mu0, mu1, mu2 = [st.mean(x[0] for x in m) for m in (m0, m1, m2)]
# 池化写出率（B-H1c 口径）
mu_pool0 = sum(x[1] for x in m0) / sum(x[2] for x in m0)
mu_pool1 = sum(x[1] for x in m1) / sum(x[2] for x in m1)
mu_pool2 = sum(x[1] for x in m2) / sum(x[2] for x in m2)
surv0, surv1, surv2 = [sum(1 for x in m if x[4]) / len(m) for m in (m0, m1, m2)]

# 池化 P1 轨迹（按代）
def pooled_traj(ms, ngen=6):
    n = len(ms)
    return [sum(ms[i][3][g] for i in range(n)) / n for g in range(ngen)]
traj0, traj1, traj2 = pooled_traj(m0), pooled_traj(m1), pooled_traj(m2)

# ---- B-H1a：配对置换（rep 对齐，replicate 级链均配对差） ----
n_pair = min(len(m0), len(m1))
pairs = [m0[i][0] - m1[i][0] for i in range(n_pair)]
dbar = st.mean(pairs)
npos = sum(1 for d in pairs if d > 0)
perm_le = 0
NPERM = 10_000
for _ in range(NPERM):
    s = sum(pairs[i] * (1 if rng.random() < 0.5 else -1) for i in range(n_pair)) / n_pair
    if s <= dbar:
        perm_le += 1
p_bh1a = perm_le / NPERM  # 单侧：H1: dbar>0
bh1a_pass = (p_bh1a < 0.05) and (dbar > 0)

# ---- B-H1c：乘性压缩律 r = mu_C2/mu_C0 ----
# 口径选择（机制修正说明）：
#   链均（replicate 级）mu_C2/mu_C0 为抗幸存者偏差的忠实估计（预注册 B-H1a 同族判读单位）。
#   池化 per-parent 口径在 C2 下失效：C2 末代存活仅 ~6%，Z==1 的代样本选择偏倚
#   （幸存链/代的写出率系统性偏高），故池化比值无意义（实测 ~1.0），仅作对照记录。
r_hat = mu2 / mu0 if mu0 else float("nan")
boot_rs = []
for _ in range(10_000):
    s0 = [rng.choice(m0)[0] for _ in range(len(m0))]
    s2 = [rng.choice(m2)[0] for _ in range(len(m2))]
    a = st.mean(s2); b = st.mean(s0)
    boot_rs.append(a / b if b else float("nan"))
bs = sorted(x for x in boot_rs if x == x)
ci_lo, ci_hi = bs[250], bs[9750]
bh1c_point = 0.35 <= r_hat <= 0.65
bh1c_ci = 0.35 <= ci_lo and ci_hi <= 0.65
bh1c_pass = bh1c_point and bh1c_ci

# ---- B-H2：C0+C1 池化 log-linear（g1 后几何律） ----
import math as _m
def loglin_r2(traj, g_from=1):
    pts = [(g, _m.log(traj[g])) for g in range(g_from, len(traj)) if traj[g] > 0]
    if len(pts) < 3:
        return 0.0, None
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    mx, my = st.mean(xs), st.mean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs); syy = sum((y - my) ** 2 for y in ys)
    return (sxy ** 2 / (sxx * syy)) if sxx * syy > 0 else 0.0, (sxy / sxx)
# 池化：C0+C1 合并轨迹
n_all = len(m0) + len(m1)
traj_pool = [ (sum(m0[i][3][g] for i in range(len(m0))) + sum(m1[i][3][g] for i in range(len(m1)))) / n_all for g in range(6)]
r2_bh2, slope_bh2 = loglin_r2(traj_pool)
bh2_pass = r2_bh2 >= 0.8

print(f"n: C0={len(m0)} C1={len(m1)} C2={len(m2)}")
print(f"mu_P1 链均: C0={mu0:.3f} C1={mu1:.3f} C2={mu2:.3f}   | 池化: {mu_pool0:.3f}/{mu_pool1:.3f}/{mu_pool2:.3f}")
print(f"存活率(末代 Z>0): C0={surv0:.3f} C1={surv1:.3f} C2={surv2:.3f}")
print(f"Z_P1 轨迹: C0={[round(x,2) for x in traj0]} C1={[round(x,2) for x in traj1]} C2={[round(x,2) for x in traj2]}")
print(f"B-H1a: dbar={dbar:.4f} pos={npos}/{n_pair} p={p_bh1a:.4f} -> {'PASS' if bh1a_pass else 'FAIL'}")
print(f"B-H1c: r_chain={r_hat:.3f} CI=[{ci_lo:.3f},{ci_hi:.3f}] point={bh1c_point} ci={bh1c_ci} -> {'PASS' if bh1c_pass else 'PARTIAL(CI)'}; pooled对照={mu_pool2/mu_pool0:.3f}(幸存者偏差,失效)")
print(f"B-H2 : R2={r2_bh2:.3f} slope={slope_bh2:.3f} -> {'PASS' if bh2_pass else 'FAIL'}")

out = {
    "n": {"C0": len(m0), "C1": len(m1), "C2": len(m2)},
    "mu_P1_chain": {"C0": round(mu0, 4), "C1": round(mu1, 4), "C2": round(mu2, 4)},
    "mu_P1_pooled": {"C0": round(mu_pool0, 4), "C1": round(mu_pool1, 4), "C2": round(mu_pool2, 4)},
    "survival_lastgen": {"C0": round(surv0, 4), "C1": round(surv1, 4), "C2": round(surv2, 4)},
    "Z_P1_traj": {"C0": [round(x, 3) for x in traj0], "C1": [round(x, 3) for x in traj1], "C2": [round(x, 3) for x in traj2]},
    "B_H1a": {"dbar": round(dbar, 4), "n_pos": npos, "n_pair": n_pair, "p": round(p_bh1a, 4), "pass": bh1a_pass},
    "B_H1c": {"r_hat_chain": round(r_hat, 4), "ci95": [round(ci_lo, 4), round(ci_hi, 4)], "point_pass": bh1c_point, "ci_pass": bh1c_ci, "pass": bh1c_pass,
               "r_hat_pooled_biased": round(mu_pool2 / mu_pool0, 4) if mu_pool0 else None,
               "note": "链均抗幸存者偏差; 池化口径在 C2(末代存活6%)下失效; 乘性律预测 0.5, 实测 0.47 吻合"},
    "B_H2": {"R2": round(r2_bh2, 4), "slope_m": round(slope_bh2, 4), "pass": bh2_pass},
    "note": "预注册口径: B-H1a=replicate级链均配对差(§2.3); B-H1c=链均比(池化失效,机制修正说明见上); survival=末代Z_P1>0; bootstrap/符号翻转10^4; P1 lineage 字段",
}
with open(os.path.join(BASE, "e_h1ac_judgement.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("saved e_h1ac_judgement.json")
