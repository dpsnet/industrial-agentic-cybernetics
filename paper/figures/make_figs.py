# -*- coding: utf-8 -*-
"""Axiom IV paper figures v2 (academic vector output).

Fixes vs v1: fixed axis limits (no autoscale blowout), legends outside plot,
two-row mechanism panels with dedicated whitespace per text line.

Data source: e_supercritical_judgement2.json (judged values, chain-mean).
Outputs: paper/figures/fig-mechanism.{png,svg}, fig-trajectories.{png,svg}
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({
    "font.size": 9, "axes.labelsize": 10, "axes.titlesize": 10,
    "legend.fontsize": 8, "xtick.labelsize": 9, "ytick.labelsize": 9,
    "axes.linewidth": 0.8, "lines.linewidth": 1.4,
})


def _box(ax, x, y, w, h, text, fc="#eef3fb", ec="#2c5f8a", fs=8.5):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06",
                       fc=fc, ec=ec, lw=0.9)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def _arrow(ax, x1, y1, x2, y2, color="#444", lw=1.1):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 color=color, lw=lw, mutation_scale=12))


def fig_mechanism():
    fig, (axa, axb) = plt.subplots(2, 1, figsize=(7.0, 6.2))
    for ax in (axa, axb):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")

    # ---------- Panel A: branching decay (selective) ----------
    axa.set_title("A   Branching decay (selective replay)",
                  fontsize=10.5, loc="left", pad=6)
    _box(axa, 0.3, 6.6, 2.4, 1.9, "Poison pool\n$Z_n$ entries")
    _box(axa, 3.7, 6.6, 2.9, 1.9, "Offspring\n$X_i$ drawn per entry")
    _box(axa, 7.7, 6.6, 2.0, 1.9, "$Z_{n+1}$")
    _arrow(axa, 2.7, 7.55, 3.7, 7.55)
    _arrow(axa, 6.6, 7.55, 7.7, 7.55)

    axa.text(0.3, 5.35,
             r"$Z_{n+1}=\sum_{i=1}^{Z_n} X_i,\qquad \mathbb{E}[X]=\hat m$",
             fontsize=10)
    axa.text(0.3, 4.45,
             r"Galton-Watson: $\mathbb{E}[Z_n]=\hat m^{n}$;  "
             r"extinction probability $q=\min\{s\in[0,1]:\varphi(s)=s\}$",
             fontsize=9)
    axa.text(0.3, 3.75,
             r"geometric-law decay confirmed: $R^2\geq0.92$ (pro / Kimi / H1AC)",
             fontsize=8.5, color="#444")

    _box(axa, 0.3, 1.0, 4.7, 1.9,
         r"subcritical $\hat m<1$: exponential decay" + "\n"
         r"(pro 0.56 [0.29,0.74]; Flash H1AC $m\approx0.92$)",
         fc="#eaf6ec", ec="#2c7a3f")
    _box(axa, 5.3, 1.0, 4.4, 1.9,
         r"critical $\hat m\approx1$: flat / weak decay" + "\n"
         r"(Flash selective ctrl $Z\equiv1$)",
         fc="#fdf6e3", ec="#a08c00")

    # ---------- Panel B: linear accumulation-competition (full append) ----------
    axb.set_title("B   Linear accumulation\u2013competition (full append)",
                  fontsize=10.5, loc="left", pad=6)
    _box(axb, 0.3, 6.6, 2.4, 1.9, "Poison pool\n$Z_n$ entries")
    _box(axb, 3.7, 6.6, 2.9, 1.9, "Constant write\n$w_n \\equiv 1$")
    _box(axb, 7.7, 6.6, 2.0, 1.9, "$Z_{n+1}$")
    _arrow(axb, 2.7, 7.55, 3.7, 7.55)
    _arrow(axb, 6.6, 7.55, 7.7, 7.55)

    axb.text(0.3, 5.35,
             r"$Z_{n+1}=Z_n+w_n,\quad w_n\equiv1\ \Rightarrow\ Z_{n+1}=Z_n+1$ "
             r"(measured)", fontsize=10)
    axb.text(0.3, 4.45,
             r"capacity $M$: linear growth until saturation, then FIFO "
             r"competition; steady state $Z\approx5/16$", fontsize=9)
    axb.text(0.3, 3.75,
             r"$\hat m=1.166$  [1.156, 1.176]  (12/12 chains, survival 1.0)",
             fontsize=8.5, color="#444")

    _box(axb, 0.3, 1.0, 4.7, 1.9,
         r"$M\leq M_c$: extinction" + "\n" + r"($\hat m=0.829$ at $M=8$, "
         r"g7 survival 0)", fc="#eaf6ec", ec="#2c7a3f")
    _box(axb, 5.3, 1.0, 4.4, 1.9,
         r"$M>M_c$: persistence" + "\n" + r"($\hat m=1.25$ at $M=32$, "
         r"linear $Z=[1,\dots,8]$)", fc="#fbeaec", ec="#b03a2e")
    axb.text(5.0, 0.15,
             r"critical capacity $M_c\in(8,16)$  (capacity monotone)",
             fontsize=9, ha="center", style="italic", color="#b03a2e")

    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(OUT, f"fig-mechanism.{ext}"), dpi=300,
                    bbox_inches="tight")
    plt.close(fig)
    print("fig-mechanism v2 ok")


def fig_trajectories():
    gens = np.arange(8)
    c0 = [1.0, 2.0, 2.917, 3.917, 3.917, 4.917, 4.917, 4.917]
    w8 = [1.0, 1.0, 1.333, 0.833, 1.0, 0.5, 0.167, 0.0]
    w32 = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    sel = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    sel_g = np.arange(6)

    fig, ax = plt.subplots(figsize=(5.6, 3.9))
    ax.set_xlim(-0.35, 7.7)
    ax.set_ylim(-0.5, 9.4)

    ax.plot(gens, c0, "-o", ms=4, color="#1f5fa8",
            label="C0-full (M=16), $\\hat m$=1.166")
    ax.plot(gens, w8, "--s", ms=4, color="#2c7a3f",
            label="M=8, $\\hat m$=0.829 (extinct)")
    ax.plot(gens, w32, "-.^", ms=4, color="#a06b10",
            label="M=32, $\\hat m$=1.25 (linear)")
    ax.plot(sel_g, sel, ":D", ms=3.5, color="#7a7a7a",
            label="selective ctrl, $\\hat m$=1.0")
    ax.axhline(1, color="#bbbbbb", lw=0.8, ls=":")

    ax.text(3.7, 8.85,
            "critical capacity  $8 < M_c \\leq 16$",
            fontsize=9, ha="center", style="italic", color="#b03a2e")

    ax.set_xlabel("Generation $g$")
    ax.set_ylabel("Poison lineage entries $Z_g$")
    ax.set_xticks(gens)
    ax.grid(alpha=0.25, lw=0.5)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16),
              ncol=2, frameon=False)
    ax.set_title("Poison propagation by architecture and capacity\n"
                 "(full append, DeepSeek-V4.1-Flash-1017, chain means)",
                 fontsize=9.5)

    fig.tight_layout()
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(OUT, f"fig-trajectories.{ext}"), dpi=300,
                    bbox_inches="tight")
    plt.close(fig)
    print("fig-trajectories v2 ok")


if __name__ == "__main__":
    fig_mechanism()
    fig_trajectories()
    print("figures v2 written to", OUT)
