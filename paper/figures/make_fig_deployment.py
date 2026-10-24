# -*- coding: utf-8 -*-
"""Generate fig-deployment.png: deployment cost-benefit of dynamic capacity control.

Data: 12-chain controlled batch; Flash 1 token = 0.19 credits, one chain ~14,000
tokens ~ 2,660 credits. Survival/utility: high-state three-window merged readings
(W4 13/32 vs W8 19/24, one-sided Fisher p=0.0040). Quarantine column: zero probe
increment; its cost is the unquantified availability loss (memory frozen), noted
in caption, not plotted.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

CONFIGS = ["Static W8", "Gated +W4", "Companion 1:3", "Companion 1:2", "Quarantine \u03c3=1"]
COST = [31920, 34580, 42560, 50540, 31920]
SURV = [0.833, 0.333, 0.333, 0.333, 0.0]
UTIL = [0.541, 0.328, 0.328, 0.328, 0.88]

fig, ax1 = plt.subplots(figsize=(8.2, 4.6), dpi=300)
x = range(len(CONFIGS))

bars = ax1.bar(x, [c / 1000.0 for c in COST], width=0.55, color="#5b7fa6", alpha=0.9, label="Batch cost (k credits)")
ax1.set_ylabel("Batch cost (k credits)", fontsize=10)
ax1.set_ylim(0, 62)
ax1.set_xticks(list(x))
ax1.set_xticklabels(CONFIGS, fontsize=9)
for i, c in enumerate(COST):
    ax1.text(i, c / 1000.0 + 0.8, "%dk" % (c // 1000), ha="center", va="bottom", fontsize=9)

ax2 = ax1.twinx()
ax2.plot(x, SURV, "o-", color="#c0392b", lw=2.2, ms=7, label="Poison survival")
ax2.plot(x, UTIL, "d-", color="#1e8449", lw=2.2, ms=7, label="Utility retention")
ax2.set_ylabel("Ratio", fontsize=10)
ax2.set_ylim(-0.05, 1.05)
ax2.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
for i, v in enumerate(SURV):
    ax2.text(i, v + 0.035, ("%.0f%%" % (v * 100)) if v > 0 else "0%", ha="center", fontsize=8.5, color="#c0392b")
for i, v in enumerate(UTIL):
    ax2.text(i, v - 0.055, "%.0f%%" % (v * 100), ha="center", fontsize=8.5, color="#1e8449")

h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=9, frameon=True)
ax1.grid(axis="y", ls=":", alpha=0.4)
plt.tight_layout()
plt.savefig(r"E:\workspace\industrial-agentic-cybernetics\paper\figures\fig-deployment.png", dpi=300)
print("fig-deployment.png written")
