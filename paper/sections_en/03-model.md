# §3 Model

> Status: **translated v1** (2026-10-22); notation defined here, consistent with judgment artifacts.

---

## 3.1 Notation

| Symbol | Meaning | Measured / setting |
| :--- | :--- | :--- |
| $Z_n$ | number of poison-lineage (P1) entries in the memory store at generation $n$ (pool size) | tracked per generation |
| $M$ | memory window capacity (FIFO) | default $16$; sensitivity tiers $M=8,32$ |
| $w_n$ | number of newly written poison entries at generation $n$ (fresh write) | selective: varies with $Z_n$; full-append: $\in\{0,1\}$ (PMF=[0,1], chain mean $E[w_n]=0.917$) |
| $X_i$ | offspring count of a single parent in the branching process | $E[X]=\hat m$ (empirical estimate) |
| $\sigma$ | gate blocking rate (write-through rate $=1-\sigma$) | random filtering $\sigma=0.5$ (blocks half); quarantine $\sigma=1$ (blocks all) |
| $\hat m$ | estimated propagation ratio $\hat m=\sum_n Z_{n+1}/\sum_n Z_n$ (generation-weighted; GW “mean offspring per parent” semantics valid for Mechanism A only, §3.2) | per experiment tier |

**Notation discipline**: $M$ is the memory capacity (the window parameter in tier names `_W8/_W32`), and $w_n$ is the per-generation write—the two are strictly distinguished throughout this paper.

## 3.2 Two Propagation Mechanisms

**Mechanism A: branching decay (selective-replay protocol)**. The agent transcribes only the entries judged relevant in the current session; the offspring count depends on the parent poison lineage's transcription propensity:

$$Z_{n+1}=\sum_{i=1}^{Z_n} X_i,\qquad E[Z_{n+1}\mid Z_n]=\hat m\,Z_n$$

This is the classical Galton-Watson branching process (Harris, 1963): the expected propagation follows the geometric law $E[Z_n]=\hat m^n E[Z_0]$; the extinction probability is the least fixed point of the generating function $\varphi(s)$ (Lean T1); subcritical ($\hat m<1$) decay is exponential (Lean T2). **Criterion for this mechanism**: $w_n$ varies with $Z_n$ (branching dependence).

**Mechanism B: linear accumulation–competition (full-append protocol)**. The agent appends all experience each generation (vector-store direct write / no transcription decay); the poison write is constant:

$$Z_{n+1}=Z_n+w_n,\qquad w_n\in\{0,1\}\ \text{(measured, PMF=[0,1])}$$

Before saturation, growth is linear, $Z_{n+1}=Z_n+1$; once $Z_n$ reaches capacity $M$, the system enters the FIFO competition steady state (new entries evict the oldest), with steady-state pool size determined by capacity competition (measured C0-full steady state $5/16$). **Criterion for this mechanism**: $w_n$ is constant and independent of $Z_n$ (accumulative writing).

**Direct evidence of mechanism discrimination (per-generation offspring check)**: in the full-append tier, the number of newly written P1 entries is 0 or 1 every generation ($w_n\in\{0,1\}$, PMF=[0,1], chain mean $E[w_n]=0.917$—11/12 chains write 1 every generation, about 1/12 chains skip one generation; $Z_{n+1}=Z_n+w_n$ linear accumulation; measured Z=[1,2,2.917,3.917,3.917,4.917,4.917,4.917]); the "offspring depends on parent population" requirement of a branching process fails. **Therefore the pre-registered hypothesis S-H3 (GW match) is falsified by mechanism evidence, and the theory is revised to Mechanism B** (see §9, mechanism-revision narrative). Branching decay (Mechanism A) still holds under the selective protocol (geometric law $R^2=0.958$, main experiment; $R^2=0.923$, H1AC large sample).

## 3.3 Capacity as Control Parameter

Memory window capacity $M$ determines the propagation outcome of Mechanism B (SUPERCRITICAL tier, full-append, Flash):

| $M$ | propagation ratio $\hat m^\dagger$ (boot95 CI) | g7 survival | Outcome |
| :--- | :--- | :--- | :--- |
| 8 | 0.829 ([0.739, 0.875]) | 0 | **extinction** (suppressed at the write side by capacity) |
| 16 | 1.166 ([1.156, 1.176]) | 1.0 | **persistent accumulation** (steady state 5/16 maintained for 3 generations; engineering-sense supercritical) |
| 32 | 1.25 (degenerate CI, 6 identical chains) | 1.0 | **linear growth** ($Z=[1,\dots,8]$, unsaturated) |

**Critical capacity is a $(b,M)$ joint function (measured by EXP-B, §6.5)**: capacity monotonicity holds—the poison pool is suppressed to extinction when $M\le M_c$, and accumulates monotonically without extinction when $M>M_c$. $M_c$ moves up with the benign write rate $b$ (under the EXP-B protocol, $W_c\le4$ at $b=1/2$; $W_c\in(4,8)$ at $b=3$; $W_c\in(8,12)$ at $b=5$). **Cross-experiment grid-point check**: the main-protocol tier (write rule "1~3 entries", $b{\approx}3$ total cap including the strain, executed by `axiom4_memory_propagation.py`) gives $M_c\in(8,16)$, consistent with the EXP-B $b{=}3$ row (executed by `kimi_boost.py`; $b$ = benign-experience cap with the strain consuming quota; measured total writes 3.00 in both tiers—flow-isomorphic) at the shared grid point $W=16$ (EXP-A C0 6-generation $Z=5.06$ vs 4.917 at the same generation in the main protocol, 2.9% difference) but split at the boundary grid point $W=8$ (main protocol: 6/6 chains extinct, surv=0; EXP-B: surv=0.92 at 12 chains, persisting after extension). **The attribution audit (§6.5) locates the split in a sub-hourly state transition of DeepSeek-V4.1-Flash-1017 strain transcription behavior** (high/low transcription states flip within ~32 minutes on the same calendar day; same-day dual-protocol reruns show no difference, Fisher $p{=}0.155$, and the 10-22 original batch is significantly low at $p{=}0.0024$—not a protocol difference); **$M_c$ is therefore a conditional quantity of $(b,M,\text{strain transcription state})$**: under the low state $M_c\in(8,16)$ with $W{=}8$ extinct, while under the high state $W{=}8$ survives at more than half (§11.4 probe-calibration protocol). Both readings reproduce within their own batches and are reported side by side (§6.5). $M_c$ drifts with $b$ and the retrieval strategy (§10/§11 open items). $M$ is therefore the **control parameter** of propagation (not a model parameter).

## 3.4 Architecture Determines Mechanism

Switching the memory architecture within the same model family (Flash) switches the mechanism:

| Architecture | Mechanism | $\hat m$ / propagation | Criterion |
| :--- | :--- | :--- | :--- |
| selective replay | branching decay (A) | $\hat m\in[0.56,0.98]$ (cross-model, model-specific) | $w_n$ depends on $Z_n$; geometric law holds |
| full-append | accumulation–competition (B) | $Z$ accumulates linearly; capacity $M$ decides the outcome | $w_n\in\{0,1\}$; $M_c\in(8,16)$ (low-transcription-state reading; $W{=}8$ survives at more than half under the high state, §6.5) |

**The variable is architecture, not the model**: within the same Flash tier, the selective control (2 chains, main experiment; **extended to 12 chains, EXP-C**) keeps $Z$ constant at 1 with memory shrinking to 3 (critical boundary $\hat m=1.0$; after extension $\hat m=0.966$, CI $[0.911,1.000]$ containing 1, weak-subcritical/critical confirmed statistically), while full-append C0 (12 chains) accumulates linearly to 5/16 (engineering-sense supercritical, $\hat m=1.166$, CI $[1.156,1.176]$)—the two $\hat m$ CIs are fully separated, and the bifurcation is entirely determined by the transcription protocol. This is consistent with the applicability-domain statement of Axiom IV: without a gate, $\hat m$ is a model–task–site joint parameter ($[0.29,1.00]$; cross-model $[0.56,0.98]$), but the **mechanism class is determined by architecture and does not migrate across models**.

## 3.5 Pre-registered Hypotheses

Experiments for these hypotheses are in §5 and the judgment results in §6.

| Hypothesis | Proposition | Criterion |
| :--- | :--- | :--- |
| **S-H1** | full-append without gate sustains accumulation (steady-state occupancy $>0$ and survival 1.0) | occupancy/survival (GW formulation invalidated with S-H3) |
| **S-H2** | survival rate 1.0 in the unsaturated segment | g7 survival |
| **S-H3** | GW branching match ($w_n$ varies with $Z_n$; $\to$ **falsified by mechanism evidence—measured $w_n\in\{0,1\}$—revised to Mechanism B**) | per-generation $w_n$ check |
| **S-H4** | quarantine truncates accumulation across mechanisms | C3-full 12/12 |
| **B-H1a** | marking gate compresses paired difference $>0$ ($\to$ does not hold) | sign-flip permutation $p<0.05$ |
| **B-H1c** | multiplicative compression law $\hat r_{C2}/\hat r_{C0}\in[0.35,0.65]$ with CI fully inside | point + CI dual criterion |
| **B-H2** | large-sample geometric-law re-check $R^2\ge0.8$ | log-linear |
| **X-H1/X-H4** | cross-model quarantine guarantee; defense does not depend on the model | 24/24 chains $Z_1=0$ |
| **T-H1/T-H4** | cross-task-family quarantine guarantee; poison propagation modulated by task family | 48/48 chains; paired $p<0.05$ |
