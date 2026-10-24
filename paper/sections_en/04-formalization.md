# §4 Formalization

> Status: **translated v1** (2026-10-22); Lean 4 sources in the project repo; single source of facts: judgment artifacts.

---

## 4.1 Model Structure

The propagation model is a **branching process** (`BranchingProcess` structure, a finitely supported PMF per generation): in the cross-generation propagation of un-adjudicated experience, the selectivity $\sigma$ of the double-blind quarantine gate compresses the nominal reproduction mean $\mu$ to an effective reproduction number

$$m = \mu(1-\sigma) \quad \text{(multiplicative compression law)}$$

All theorems are presented as **conditional theorems**: structural premises (e.g., $m<1$) are explicit assumptions; "the real system satisfies the premise" is supported by measurement in §5–§6 and is not asserted inside the formal system. This division is the three-layer knowledge-status structure adopted throughout: **theorem layer** (Lean-checked structural implications), **empirical layer** (pre-registered measurements of $\hat m$, $M_c$, $\sigma$), and **engineering layer** (deployment adjudication by production criteria); numbers and theorems do not impersonate each other. The convention for $\sigma$ is consistent with §3.1 (interception rate; write-through rate $=1-\sigma$); the EXP-A random-filter tiers are implemented as a pass rate $r=1-\sigma$ (Table 5 annotation, §6.5).

## 4.2 Theorem Chain

All theorems in this chain are machine-checked with Lean 4 (zero `sorry`). Formalization sources: `formal_proof/IACFormalization` (this repository, commit `4825137`; Lean 4, mathlib version in `lakefile.lean`). The repository is currently **kept private**: the commit hash pins the file tree and build record for verification, and the full sources are available from the authors upon request.

**T1 Expected geometric law** (`expected_population_geometric`, by induction): $E[Z_n]=m^n E[Z_0]$.

**T2 Subcritical probabilistic extinction** (`subcritical_extinction_in_probability`): by Markov's inequality with geometric decay, when $m<1$ the survival probability $P(Z_n\ge1)\to0$. This is the quantitative core of the quarantine promotion gate's effectiveness: the gate pushes $m$ below 1, and the long-run survival probability $P(Z_n\ge1)\to0$ (convergence in probability)—strictly, the application-side statement is “the survival probability tends to 0,” not “dies out with probability 1.”

**T3 Quarantine compresses offspring** (`quarantine_compresses_offspring`): the stricter $\sigma$, the smaller the effective reproduction number; full quarantine ($\sigma=1$) gives $m=0$, and the lineage reaches zero within one generation. **Applicability**: branching + multiplicative compression—measured to hold under the selective architecture (geometric law $R^2=0.958$); under the full-append architecture the branching premise fails, and quarantine's effectiveness is given directly by measurement (C3-full 12/12, mem constant 6, $Z$ constant 1), with the mechanism revision recorded transparently (§9).

**T4 Supercritical non-extinction** (`galton_watson_non_extinction` + `supercritical_expectation_diverges`): when $m>1$, the extinction probability is the **least fixed point** $q=\min\{s\in[0,1]:\varphi(s)=s\}<1$ of the generating function $\varphi$ on $[0,1]$—non-extinction with positive probability; the expectation $E[Z_n]\to+\infty$. The proof uses elementary generating-function fixed-point analysis (monotone squeezing + polynomial truncation), avoiding any dependence on continuity of $\varphi$.

## 4.3 Theorem–Application Mapping

| Theorem | Assertion | Application side |
| :--- | :--- | :--- |
| T1 | $E[Z_n]=m^nE[Z_0]$ | geometric-law criterion (expectation side of S-H2/B-H2) |
| T2 | $m<1 \Rightarrow P(Z_n\ge1)\to0$ | quarantine/random filtering extinguishes lineages (C2 survival 0.062 vs C0 0.750) |
| T3 | $\sigma\!\uparrow \Rightarrow m\downarrow$; $\sigma=1\Rightarrow m=0$ | quarantine invariance (S-H4/T-H1/X-H1) |
| T4 | $m>1 \Rightarrow q<1$, $E[Z_n]\to+\infty$ | supercritical-side counterpart of Mechanism A; Mechanism B persistence is given by measured occupancy (engineering semantics) |

## 4.5 Mechanism-B Steady-State Occupancy

This proposition is an ordinary mathematical derivation, not Lean-checked. **Proposition (Mechanism-B steady-state occupancy)**: under full-append architecture, FIFO capacity $M$, $b$ benign entries written per generation, and chain-mean poison write $\bar w$ ($0<\bar w\le1$), the steady-state poison occupancy under the approximation that poison entries mix uniformly within the capacity is

$$Z^* = \frac{M\,\bar w}{b+\bar w}$$

**Proof**: the expected per-generation write volume is $b+\bar w$ entries ($\bar w$ poison); FIFO evicts an equal number of the oldest entries per generation. If poison is uniformly distributed over the $M$ slots, the expected number of evicted poison entries per generation is $(b+\bar w)\cdot Z/M$. Steady state requires inflow equals outflow: $(b+\bar w)\cdot Z^*/M = \bar w$, hence $Z^*=M\bar w/(b+\bar w)$. $\blacksquare$

**Measured validation**: C0-full ($b=2$, $\bar w=0.917$, $M=16$) predicts $Z^*=16\times0.917/2.917=5.03$; the measured steady state is 4.917 (stable across g5–g7), a relative deviation of 2.3%.

**Caveat**: uniform mixing is an approximation—under FIFO the poison-entry position distribution is non-uniform with inter-generation correlations, and the exact solution depends on the concrete write sequence; this closed form serves as the **endogenous steady-state descriptor** of Mechanism B (the endogenization replacing GW parameters, §9).

## 4.6 Boundary of the Formalization

The **values** of $\hat m$ (Mechanism A), $M_c$, and $\sigma$ are empirical/engineering-layer parameters and do not enter the formal interface (Mechanism B has no GW-semantics $\hat m$; its propagation ratio is reported in the §6.1 table note); the formalization guarantees **structural implication** (if the premise holds, the conclusion is necessarily true), and the values are estimated by pre-registered measurement. This division avoids two errors: treating empirical constants as theorems, and treating theorems as empirical constants.
