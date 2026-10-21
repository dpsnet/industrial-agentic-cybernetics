# -*- coding: utf-8 -*-
"""E3b 补测判读：r 通道漂移方向 + 7B YaRN 下降相性质判定.

对应 EXPERIMENT_PLAN.md §4.2 预注册证伪标准第 3 条:
  若 r(rho) 随 rho 显著单调漂移 (dr/drho>0 且 bootstrap CI 不含 0),
  则二通道模型不足, 须引入 sink 通道并重述量守恒.

下降相判定逻辑:
  - 记总非目标质量 t = b + r (= 1 - a, 若三通道归一).
    若 b 下降而 t 非减 => 质量从填充段迁移到残差通道 (sink 迁移),
      总量守恒, hb_nondec 在"总量"口径下存活;
    若 b 下降且 t 同步下降 => 真退化 (质量离开非目标通道),
      须检查 a 是否同步上升 (注意力重新集中) 或数值异常.
"""
import json
import collections
import random
import math

random.seed(20261019)

PATH = r"E:\workspace\industrial-agentic-cybernetics\experiments\attention_growth\results_e3b_qwen7b_yarn4.json"

d = json.load(open(PATH, encoding="utf-8"))
rows = d.get("rows", [])
cfg = d.get("config", {})
print("rows=%d reps=%s rope_factor=%s model=%s" % (
    len(rows), cfg.get("reps"), cfg.get("rope_factor"), cfg.get("model", "?")))

# ---------- 逐 rho 汇总表 ----------
byr = collections.defaultdict(list)
for x in rows:
    byr[x["rho"]].append(x)

rhos = sorted(byr)
print()
print(" rho      a        b        r      t=b+r    a+b+r   snr(tot) snr(fill) b/(b+r)")
for rho in rhos:
    rs = byr[rho]
    n = len(rs)
    a = sum(x["a"] for x in rs) / n
    b = sum(x["b"] for x in rs) / n
    r = sum(x["r"] for x in rs) / n
    t = b + r
    snr_tot = a / (1 - a) if a < 1 else float("nan")
    snr_fill = a / b if b else float("nan")
    fill_frac = b / t if t else float("nan")
    print(" %-8d %.5f  %.5f  %.5f  %.5f  %.5f  %.5f  %.5f  %.4f"
          % (rho, a, b, r, t, a + b + r, snr_tot, snr_fill, fill_frac))

# ---------- r(rho) 单调漂移检验 (预注册标准第 3 条) ----------
# 对每个 rho 取 cell 均值序列, 检验 r 是否随 rho 单调漂移;
# bootstrap: 按 cell (filler x pos) 重抽样, 对 spearman 斜率给 95% CI.
print()
print("== r(rho) 单调漂移检验 (Spearman 型: sign of slope of r vs log rho) ==")

# 按 cell 聚合: 每 (filler,pos) 一个 r 序列
cell_keys = sorted({(x["filler"], x["position"]) for x in rows})
cell_seq = {}
for key in cell_keys:
    seq = []
    for rho in rhos:
        vals = [x["r"] for x in rows if x["rho"] == rho and (x["filler"], x["position"]) == key]
        seq.append(sum(vals) / len(vals) if vals else None)
    if all(v is not None for v in seq):
        cell_seq[key] = seq

logs = [math.log(rho) for rho in rhos]

def slope(seq):
    n = len(seq)
    mx = sum(logs) / n
    my = sum(seq) / n
    num = sum((logs[i] - mx) * (seq[i] - my) for i in range(n))
    den = sum((logs[i] - mx) ** 2 for i in range(n))
    return num / den if den else 0.0

obs = [slope(v) for v in cell_seq.values()]
obs_mean = sum(obs) / len(obs)
# bootstrap over cells
B = 1000
boot = []
for _ in range(B):
    sample = [random.choice(obs) for _ in range(len(obs))]
    boot.append(sum(sample) / len(sample))
boot.sort()
lo, hi = boot[int(0.025 * B)], boot[int(0.975 * B)]
dr_pos = sum(1 for o in obs if o > 0) / len(obs)
print("  cells=%d  mean dr/dlog(rho) = %+.6f  95%% CI [%+.6f, %+.6f]  (cells>0: %d/%d)"
      % (len(obs), obs_mean, lo, hi, dr_pos * len(obs), len(obs)))
verdict = "TRIGGERED: 二通道不足" if (lo > 0 or hi < 0) else "NOT triggered: CI 含 0"
print("  预注册标准第 3 条:", verdict)

# ---------- 下降相判定: t=b+r 的单调性 vs b 的单调性 ----------
print()
print("== 下降相判定 (rho>=64k 区): b 下降时 t=b+r 是否守恒 ==")
for rho in rhos:
    rs = byr[rho]
    n = len(rs)
    a = sum(x["a"] for x in rs) / n
    b = sum(x["b"] for x in rs) / n
    r = sum(x["r"] for x in rs) / n
    print("  rho=%-8d b=%+.6f  r=%+.6f  t=b+r=%.6f  a=%.6f  1-a=%.6f  |t-(1-a)|=%.2e"
          % (rho, b, r, b + r, a, 1 - a, abs((b + r) - (1 - a))))

# 单步增量表
print()
print("== 单步增量 (相对前一 rho) ==")
prev = None
for rho in rhos:
    rs = byr[rho]
    n = len(rs)
    a = sum(x["a"] for x in rs) / n
    b = sum(x["b"] for x in rs) / n
    r = sum(x["r"] for x in rs) / n
    if prev is not None:
        db, dr, dt = b - prev[1], r - prev[2], (b + r) - (prev[1] + prev[2])
        print("  %8d -> %8d : db=%+.6f  dr=%+.6f  dt=%+.6f  (迁移占比 dr/(db+dr)=%.2f)"
              % (prev[0], rho, db, dr, dt,
                 (dr / (dr - db)) if (db < 0 and dr > 0) else float("nan")))
    prev = (rho, b, r)

# ---------- 逐头离散度 ----------
print()
print("== 逐头离散度 (每 cell 每层头间 pstdev 的均值) ==")
import statistics as st
print(" rho      disp_a   disp_b")
for rho in rhos:
    rs = byr[rho]
    disp_a, disp_b = [], []
    for x in rs:
        for key, acc in (("a_heads", disp_a), ("b_heads", disp_b)):
            hs = x.get(key)
            if hs:
                for hl in hs:
                    if len(hl) > 1:
                        acc.append(st.pstdev(hl))
    da = sum(disp_a) / len(disp_a) if disp_a else float("nan")
    db_ = sum(disp_b) / len(disp_b) if disp_b else float("nan")
    print(" %-8d %.4f   %.4f" % (rho, da, db_))
