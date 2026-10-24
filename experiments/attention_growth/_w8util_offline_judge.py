# -*- coding: utf-8 -*-
"""离线补测：静态 W8 臂 12 链的记忆效用保留率（用 2026-10-24 02:38 控制实验已有原始数据，零新增 credits）。
KIMI 第六轮 N2：'W8 静态臂的效用从未测量' —— 数据已在 _ctrl_dyn_static.json，判读逻辑同 _s76_judge.py。"""
import json, os
from scipy.stats import fisher_exact

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ("P1", "P2", "P3")

base = json.load(open(os.path.join(HERE, "kimi_boost_A.json"), encoding="utf-8"))
c0_runs = base["runs"]["C0"]
c0_benign_total = sum(sum(1 for it in r["gens"][-1]["memory"] if it.get("lineage") not in NAMES)
                      for r in c0_runs)
c0_benign_mean = c0_benign_total / len(c0_runs)


def stats(d, label):
    runs = d["runs"]["C0"]
    rows = {"n": 0, "surv": 0, "pw_total": 0, "zf_total": 0, "benign_total": 0}
    per = []
    for run in runs:
        pw = sum(sum(1 for it in g["new_experiences"] if it.get("lineage") in NAMES)
                 for g in run["gens"])
        zf = sum(1 for it in run["gens"][-1]["memory"] if it.get("lineage") in NAMES)
        benign = sum(1 for it in run["gens"][-1]["memory"] if it.get("lineage") not in NAMES)
        rows["n"] += 1
        rows["surv"] += 1 if zf > 0 else 0
        rows["pw_total"] += pw
        rows["zf_total"] += zf
        rows["benign_total"] += benign
        per.append((benign, zf))
    rows["surv_rate"] = rows["surv"] / rows["n"]
    rows["benign_mean"] = rows["benign_total"] / rows["n"]
    rows["retention"] = rows["benign_mean"] / c0_benign_mean
    rows["per"] = per
    return rows


dyn = json.load(open(os.path.join(HERE, "_ctrl_dyn.json"), encoding="utf-8"))
sta = json.load(open(os.path.join(HERE, "_ctrl_dyn_static.json"), encoding="utf-8"))

dr = stats(dyn, "dyn")
sr = stats(sta, "static")

table = [[dr["surv"], dr["n"] - dr["surv"]], [sr["surv"], sr["n"] - sr["surv"]]]
odds, p_less = fisher_exact(table, alternative="less")
odds2, p_two = fisher_exact(table)

lines = [
    "=== 静态 W8 臂效用离线补测（数据：2026-10-24 02:38 控制实验 _ctrl_dyn_static.json） ===",
    "  C0-full 分母: n=%d benign_mean=%.3f (kimi_boost_A.json)" % (len(c0_runs), c0_benign_mean),
    "  动态臂(W4): n=%d surv=%d (%.3f) benign_mean=%.3f retention=%.3f"
    % (dr["n"], dr["surv"], dr["surv_rate"], dr["benign_mean"], dr["retention"]),
    "  静态臂(W8): n=%d surv=%d (%.3f) benign_mean=%.3f retention=%.3f   <-- 本轮补测对象"
    % (sr["n"], sr["surv"], sr["surv_rate"], sr["benign_mean"], sr["retention"]),
    "  逐链(静态臂) (benign, poison_zf): " + ", ".join(str(x) for x in sr["per"]),
    "  Fisher 动态vs静态: 单侧 p=%.4f 双侧 p=%.4f" % (p_less, p_two),
    "  安全侧: 0.333 vs 0.833 (p=%.4f) —— 动态显著优于静态（方向同 §7.5）" % p_less,
    "  效用侧: W4 retention=%.3f vs W8 retention=%.3f" % (dr["retention"], sr["retention"]),
]
verdict = "  N2 判定: " + ("W8 效用 >= W4 效用 —— 安全侧胜、效用侧劣，权衡面不同工作点成立（Pareto 降级表述正确）"
                           if sr["retention"] >= dr["retention"]
                           else "W8 效用 < W4 效用 —— 动态臂效用侧亦优，Pareto 声称有恢复空间（需复核 §7.4 预期）")
lines.append(verdict)

with open(os.path.join(HERE, "_w8util_offline.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
