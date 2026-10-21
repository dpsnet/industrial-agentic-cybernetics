# -*- coding: utf-8 -*-
"""T8 判读（E8）：结构量 → γ/β 代理关系检验。

对应 EXPERIMENT_PLAN.md §8.2 预注册：
  假设 H_T8：存在结构量 S，使 cell 级 β̂（幂律指数）与 S 的 |Spearman| ≥ 0.5
             且 bootstrap 95% CI 不含 0。
  证伪标准：三候选结构量与 β̂ 的 Spearman 均 |ρ_S| < 0.5 或 CI 含 0
            ⟹ T8 关闭，γ 保持自由参数。
  附加要求：若仅个别层相关而层均值不相关，须按层分组报告。

分析单元：9 个 (filler × position) 单元；每单元 6 档 ρ（reps=3 取均值）。
"""
import json
import math
import random

random.seed(20261020)
PATH = r"E:\workspace\industrial-agentic-cybernetics\experiments\attention_growth\t8_7b_yarn4.json"
STRUCT_KEYS = ["entropy", "top1pct", "top10", "erank"]


def rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    rk = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            rk[order[k]] = avg
        i = j + 1
    return rk


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = math.sqrt(sum((x - ma) ** 2 for x in a))
    db = math.sqrt(sum((y - mb) ** 2 for y in b))
    if da == 0 or db == 0:
        return float("nan")
    return num / (da * db)


def spearman(a, b):
    return pearson(rank(a), rank(b))


def bootstrap_ci(xs, ys, n=10000):
    """对 (x,y) 配对做 bootstrap 重抽样，返回 Spearman 的 95% CI 与观测值。"""
    obs = spearman(xs, ys)
    vals = []
    m = len(xs)
    for _ in range(n):
        idx = [random.randrange(m) for _ in range(m)]
        xs2 = [xs[i] for i in idx]
        ys2 = [ys[i] for i in idx]
        v = spearman(xs2, ys2)
        if not math.isnan(v):
            vals.append(v)
    vals.sort()
    if not vals:
        return obs, float("nan"), float("nan")
    lo = vals[int(0.025 * len(vals))]
    hi = vals[int(0.975 * len(vals))]
    return obs, lo, hi


def perm_p(xs, ys, n=10000):
    """置换检验：H0 下 |Spearman| ≥ |观测| 的比例（双尾）。"""
    obs = abs(spearman(xs, ys))
    cnt = 0
    yy = list(ys)
    for _ in range(n):
        random.shuffle(yy)
        v = spearman(xs, yy)
        if not math.isnan(v) and abs(v) >= obs:
            cnt += 1
    return cnt / n


d = json.load(open(PATH, encoding="utf-8"))
cfg, rows, cells = d["config"], d["rows"], d["cells"]
rhos = cfg["rho"]
units = sorted(cells.keys())
print("T8 判读 | rows=%d units=%d rho=%s reps=%s model=%s"
      % (len(rows), len(units), rhos, cfg["reps"], d.get("model", "?")))

# ---------- 1. 每单元：b 序列 + 拟合口径 ----------
print("\n== 每单元幂律/几何/饱和拟合（log b ~ log rho 主口径） ==")
print(" %-12s %8s %8s %8s %8s %8s" % ("unit", "beta_b", "R2_pow", "gamma", "R2_geo", "b_best"))
beta_by_unit, gamma_by_unit, sat_by_unit = {}, {}, {}
for u in units:
    gm = cells[u]["growth_models"]
    pow_ = gm.get("power", {})
    geo = gm.get("geometric", {})
    sat = gm.get("saturating", {})
    beta_by_unit[u] = pow_.get("beta", float("nan"))
    gamma_by_unit[u] = geo.get("gamma", float("nan"))
    sat_by_unit[u] = sat.get("lambda", float("nan"))
    aic = {k: gm[k]["aic"] for k in gm if "aic" in gm[k]}
    best = min(aic, key=aic.get) if aic else "?"
    print(" %-12s %+8.5f %8.4f %+8.2e %8.4f %8s"
          % (u, beta_by_unit[u], pow_.get("r2", float("nan")),
             gamma_by_unit[u], geo.get("r2", float("nan")), best))

# ---------- 2. 每单元结构量（层均值，6 档 ρ 平均） ----------
def unit_struct(u, key):
    """单元 u 在 key 结构量上的 6 档 ρ 均值（先对 reps 与 ρ 平均，逐层再平均）。"""
    per_rho = []
    for rho in rhos:
        vals, cnt = 0.0, 0
        for r in rows:
            if r["filler"] + "@pos%.1f" % r["position"] != u or r["rho"] != rho:
                continue
            seq = r["struct"][key]
            vals += sum(seq) / len(seq)
            cnt += 1
        if cnt:
            per_rho.append(vals / cnt)
    return sum(per_rho) / len(per_rho) if per_rho else float("nan")


def unit_struct_per_layer(u, key, layer):
    per_rho = []
    for rho in rhos:
        vals, cnt = 0.0, 0
        for r in rows:
            if r["filler"] + "@pos%.1f" % r["position"] != u or r["rho"] != rho:
                continue
            vals += r["struct"][key][layer]
            cnt += 1
        if cnt:
            per_rho.append(vals / cnt)
    return sum(per_rho) / len(per_rho) if per_rho else float("nan")


print("\n== 单元级结构量均值 ==")
print(" %-12s %8s %8s %8s %8s" % ("unit", "entropy", "top1pct", "top10", "erank"))
S_unit = {k: [unit_struct(u, k) for u in units] for k in STRUCT_KEYS}
for i, u in enumerate(units):
    print(" %-12s %8.4f %8.4f %8.4f %8.2f"
          % (u, S_unit["entropy"][i], S_unit["top1pct"][i],
             S_unit["top10"][i], S_unit["erank"][i]))

# ---------- 3. 主检验：Spearman(beta_b, S) over 9 单元 ----------
print("\n== 主检验：Spearman(beta_b, S_unit)，n=9，bootstrap 95%% CI + 置换 p ==")
print(" %-10s %10s %20s %10s %10s" % ("metric", "rho_S", "CI95", "p_perm", "verdict"))
n_layer = len(rows[0]["struct"]["entropy"])
beta_list = [beta_by_unit[u] for u in units]
gamma_list = [gamma_by_unit[u] for u in units]
sat_list = [sat_by_unit[u] for u in units]
results = {}
for k in STRUCT_KEYS:
    obs, lo, hi = bootstrap_ci(beta_list, S_unit[k])
    p = perm_p(beta_list, S_unit[k])
    sig = (abs(obs) >= 0.5) and (lo > 0 or hi < 0)
    results[k] = (obs, lo, hi, p, sig)
    print(" %-10s %+10.4f  [%+.3f, %+.3f]      %8.4f   %s"
          % (k, obs, lo, hi, p, "SIGNAL" if sig else "null"))

# 同样对几何 gamma 与饱和 lambda 做（补充口径）
print("\n== 补充口径：Spearman(gamma_geo, S) 与 Spearman(lambda_sat, S) ==")
for name, yb in (("gamma", gamma_list), ("lambda", sat_list)):
    for k in STRUCT_KEYS:
        obs, lo, hi = bootstrap_ci(yb, S_unit[k])
        print(" %-10s x %-8s rho_S=%+.4f  CI[%+.3f,%+.3f]" % (k, name, obs, lo, hi))

# ---------- 4. 逐层分组（§8.2：不得聚合掩盖） ----------
print("\n== 逐层分组检验：每层 Spearman(beta_b, S_layer)，n=9 ==")
for k in STRUCT_KEYS:
    obs_list = []
    for l in range(n_layer):
        Sl = [unit_struct_per_layer(u, k, l) for u in units]
        v = spearman(beta_list, Sl)
        if not math.isnan(v):
            obs_list.append((l, v))
    strong = [(l, v) for l, v in obs_list if abs(v) >= 0.5]
    if obs_list:
        vs = [v for _, v in obs_list]
        print(" %-10s 层数=%d  |rho|>=0.5 层数=%d  min=%+.3f max=%+.3f mean=%+.3f"
              % (k, len(vs), len(strong), min(vs), max(vs), sum(vs) / len(vs)))
        if strong:
            print("            强相关层:", ", ".join("L%d(%+.3f)" % (l, v) for l, v in strong[:8]))

# ---------- 5. 结构量自身的 rho 依赖 ----------
print("\n== 结构量随 rho 的幂律斜率（log S ~ log rho，逐单元） ==")
def log_slope(xs, ys):
    lx = [math.log(x) for x in xs]
    ly = [math.log(y) for y in ys]
    n = len(lx)
    mx, my = sum(lx) / n, sum(ly) / n
    num = sum((a - mx) * (b - my) for a, b in zip(lx, ly))
    den = sum((a - mx) ** 2 for a in lx)
    return num / den if den else float("nan")


for k in STRUCT_KEYS:
    sl = []
    for i, u in enumerate(units):
        per_rho = []
        for rho in rhos:
            vals, cnt = 0.0, 0
            for r in rows:
                if r["filler"] + "@pos%.1f" % r["position"] != u or r["rho"] != rho:
                    continue
                seq = r["struct"][k]
                vals += sum(seq) / len(seq)
                cnt += 1
            per_rho.append(vals / cnt)
        sl.append(log_slope(rhos, per_rho))
    print(" %-10s slope mean=%+.5f  min=%+.5f  max=%+.5f"
          % (k, sum(sl) / len(sl), min(sl), max(sl)))
    obs, lo, hi = bootstrap_ci(beta_list, sl)
    print("            Spearman(beta_b, slope_%s) = %+.4f  CI[%+.3f, %+.3f]"
          % (k, obs, lo, hi))

# ---------- 6. 判读 ----------
print("\n== 判读（§8.2 预注册标准） ==")
any_sig = any(results[k][4] for k in STRUCT_KEYS)
for k in STRUCT_KEYS:
    obs, lo, hi, p, sig = results[k]
    print("  %-10s |rho_S|=%.3f  CI[%+.3f,%+.3f]  p=%.4f  -> %s"
          % (k, abs(obs), lo, hi, p, "触发强信号" if sig else "不满足 |rho|>=0.5 且 CI 不含 0"))
print("  综合: %s" % ("至少一个结构量满足 H_T8 判据 -> 进入 F 侧参数化"
                    if any_sig else
                    "三候选结构量均不满足 -> T8 关闭，gamma 保持自由参数（如实记录负结果）"))

# ---------- 7. 稳健性：LOO + 簇结构披露 ----------
print("\n== 稳健性检查 ==")
# (a) 单元差异的簇结构：β 与结构量的方差有多少来自 filler / position
print(" (a) 方差分解（9 单元）:")
for name, series in (("beta_b", beta_list),
                     ("entropy", S_unit["entropy"]),
                     ("top1pct", S_unit["top1pct"]),
                     ("erank", S_unit["erank"])):
    fillers = [u.split("@")[0] for u in units]
    grp = {}
    for f, v in zip(fillers, series):
        grp.setdefault(f, []).append(v)
    grand = sum(series) / len(series)
    ss_tot = sum((v - grand) ** 2 for v in series)
    ss_within = sum((v - sum(g) / len(g)) ** 2 for g in grp.values() for v in g)
    print("   %-8s SS_filler/SS_tot = %.3f   (position 内残差占 %.3f)"
          % (name, 1 - ss_within / ss_tot if ss_tot else float("nan"),
             ss_within / ss_tot if ss_tot else float("nan")))

# (b) LOO：逐次剔除一个单元，重算 |Spearman|
print(" (b) LOO（剔除 1 单元后）:|rho_S| 范围:")
for k in STRUCT_KEYS:
    vals = []
    for drop in range(len(units)):
        xs = [beta_list[i] for i in range(len(units)) if i != drop]
        ys = [S_unit[k][i] for i in range(len(units)) if i != drop]
        vals.append(abs(spearman(xs, ys)))
    print("   %-8s min=%.3f  max=%.3f  median=%.3f"
          % (k, min(vals), max(vals), sorted(vals)[len(vals) // 2]))

# (c) 饱和口径（该矩阵 7/9 cell AIC 最优为 saturating）的 erank 相关稳健性
print(" (c) 饱和口径 Spearman(lambda_sat, erank) LOO 范围:")
vals = []
for drop in range(len(units)):
    xs = [sat_list[i] for i in range(len(units)) if i != drop]
    ys = [S_unit["erank"][i] for i in range(len(units)) if i != drop]
    vals.append(spearman(xs, ys))
print("   min=%+.3f  max=%+.3f  median=%+.3f" % (min(vals), max(vals), sorted(vals)[len(vals) // 2]))

# (d) 位置效应：S 不解释的 β 变化
print(" (d) 位置维度残差（同 filler 内 rho 档 位置间 β 极差 对 S 极差）:")
for f in sorted({u.split("@")[0] for u in units}):
    idxs = [i for i, u in enumerate(units) if u.startswith(f)]
    bspan = max(beta_list[i] for i in idxs) - min(beta_list[i] for i in idxs)
    espan = max(S_unit["erank"][i] for i in idxs) - min(S_unit["erank"][i] for i in idxs)
    print("   %s: Δbeta=%.5f  Δerank=%.3f" % (f, bspan, espan))
