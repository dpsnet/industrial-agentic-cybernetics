# -*- coding: utf-8 -*-
"""Axiom IV paper figures (academic vector output).

Data source: e_supercritical_judgement2.json (judged values, chain-mean).
Outputs: paper/figures/fig-mechanism.{png,svg}, fig-trajectories.{png,svg}
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle, FancyBboxPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)))
plt.rcParams.update({
    "font.size": 9.5, "axes.labelsize": 10, "axes.titlesize": 10.5,
    "legend.fontsize": 8.5, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "axes.linewidth": 0.8, "lines.linewidth": 1.4,
})

# ---------------- Fig 1: mechanism schematic ----------------
def fig_mechanism():
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.2, 2.9))
    for ax in (axa, axb):
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

    def box(ax, x, y, w, h, text, fc="#eef3fb", ec="#2c5f8a", fs=8.6):
        b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                           fc=fc, ec=ec, lw=0.9)
        ax.add_patch(b)
        ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs)

    def arrow(ax, x1, y1, x2, y2, color="#444", style="-|>", lw=1.1, ls="-"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                     color=color, lw=lw, linestyle=ls,
                                     mutation_scale=11))

    # --- Panel A: branching decay (selective) ---
    axa.set_title("A  Branching decay (selective replay)", fontsize=10)
    box(axa, 0.4, 6.2, 2.6, 1.7, "Poison pool\n$Z_n$ entries")
    box(axa, 4.1, 6.2, 2.6, 1.7, "Offspring\ndrawn per entry")
    box(axa, 7.8, 6.2, 1.9, 1.7, "$Z_{n+1}$")
    arrow(axa, 3.0, 7.0, 4.1, 7.0)
    arrow(axa, 6.7, 7.0, 7.8, 7.0)
    axa.text(0.5, 5.2, "$Z_{n+1}=\\sum_{i=1}^{Z_n} X_i,\\ \\mathbb{E}[X]=\\hat m$",
             fontsize=8.8)
    axa.text(0.5, 3.9, "GW process  \u2022  geometric law $\\mathbb{E}[Z_n]=\\hat m^n$\n"
                        "extinction prob. $q=\\min\\{s:\\varphi(s)=s\\}$  \u2022  R\u00b2\u22650.92",
             fontsize=8.2, color="#444")
    box(axa, 0.4, 0.7, 4.6, 1.6, "Subcritical $\\hat m<1$: exponential decay",
        fc="#eaf6ec", ec="#2c7a3f")
    box(axa, 5.6, 0.7, 4.0, 1.6, "Critical $\\hat m\\approx1$: flat / weak decay",
        fc="#fdf6e3", ec="#a08c00")

    # --- Panel B: linear accumulation-competition (full append) ---
    axb.set_title("B  Linear accumulation\u2013competition (full append)", fontsize=10)
    box(axb, 0.4, 6.2, 2.6, 1.7, "Poison pool\n$Z_n$ entries")
    box(axb, 4.1, 6.2, 2.6, 1.7, "Constant write\n$w_n \\equiv 1$")
    box(axb, 7.8, 6.2, 1.9, 1.7, "$Z_{n+1}$")
    arrow(axb, 3.0, 7.0, 4.1, 7.0)
    arrow(axb, 6.7, 7.0, 7.8, 7.0)
    axb.text(0.5, 5.2, "$Z_{n+1}=Z_n+w_n,\\ \\ w_n\\equiv1\\ \\Rightarrow\\ Z_{n+1}=Z_n+1$",
             fontsize=8.8)
    axb.text(0.5, 3.9, "Linear accumulation until capacity $M$;\nthen FIFO competition "
                       "(steady state $Z\\approx5/16$)\n$\\hat m=1.166$ [1.156, 1.176]",
             fontsize=8.2, color="#444")
    box(axb, 0.4, 0.7, 4.6, 1.6, "$M \\leq M_c$: extinction  ($\\hat m<1$)",
        fc="#eaf6ec", ec="#2c7a3f")
    box(axb, 5.6, 0.7, 4.0, 1.6, "$M > M_c$: persistence  ($\\hat m>1$)",
        fc="#fbeaec", ec="#b03a2e")
    axb.text(8.2, 0.15, "critical capacity $M_c\\in(8,16)$", fontsize=8.4,
             ha="center", style="italic")

    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(OUT, f"fig-mechanism.{ext}"), dpi=300,
                    bbox_inches="tight")
    plt.close(fig)
    print("fig-mechanism ok")

# ---------------- Fig 2: trajectories & capacity ----------------
def fig_trajectories():
    gens = np.arange(8)
    c0  = [1.0, 2.0, 2.917, 3.917, 3.917, 4.917, 4.917, 4.917]
    w8  = [1.0, 1.0, 1.333, 0.833, 1.0, 0.5, 0.167, 0.0]
    w32 = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    sel = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]          # 6 generations
    sel_g = np.arange(6)

    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    ax.axvspan(8, 16, alpha=0.07, color="#b03a2e")
    ax.text(11.9, 8.2, "critical band\n$8<M_c\\leq16$", fontsize=8,
            ha="center", color="#b03a2e", style="italic")

    ax.plot(gens, c0,  "-o", ms=3.5, color="#1f5fa8", label="C0-full (M=16), $\\hat m$=1.166")
    ax.plot(gens, w8,  "--s", ms=3.5, color="#2c7a3f", label="M=8, $\\hat m$=0.829 (extinct)")
    ax.plot(gens, w32, "-.^", ms=3.5, color="#a06b10", label="M=32, $\\hat m$=1.25 (linear)")
    ax.plot(sel_g, sel, ":D", ms=3, color="#7a7a7a", label="selective ctrl, $\\hat m$=1.0")
    ax.axhline(1, color="#999", lw=0.7, ls=":")

    ax.set_xlabel("Generation $g$")
    ax.set_ylabel("Poison lineage entries $Z_g$")
    ax.set_xticks(gens)
    ax.set_ylim(-0.4, 8.8)
    ax.grid(alpha=0.3, lw=0.5)
    ax.legend(loc="upper left", frameon=True, framealpha=0.95)
    ax.set_title("Poison propagation by architecture and capacity\n"
                 "(full append, DeepSeek-V4.1-Flash-1017, chain means)",
                 fontsize=9.5)

    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(OUT, f"fig-trajectories.{ext}"), dpi=300,
                    bbox_inches="tight")
    plt.close(fig)
    print("fig-trajectories ok")

if __name__ == "__main__":
    fig_mechanism()
    fig_trajectories()
    print("figures written to", OUT)
