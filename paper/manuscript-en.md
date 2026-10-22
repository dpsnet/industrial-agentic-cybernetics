# Memory Poisoning in Ungated Agentic Memory Architectures: Architecture-Dependent Propagation Mechanisms, Capacity Control, and Quarantine Invariance

Long-lived language-model agents accumulate experience in persistent memory; unvalidated or malicious entries can propagate across sessions and poison downstream tasks. Existing defenses treat soft marking and hard quarantine interchangeably, and no account links the *memory architecture* to the mathematical structure of propagation. We study injection-propagation under two write protocols—selective replay and full append—through pre-registered experiments spanning three model families (DeepSeek-V4-Pro-0813 (Pro), Kimi, DeepSeek-V4.1-Flash-1017 (Flash)), two architectures, three capacity settings, and 1,264 agent-session chains, with Lean 4 machine-checked conditional theorems.

We find that the architecture, not the model, determines the propagation mechanism. Selective replay yields branching decay: a Galton-Watson process with model-specific offspring mean $\hat m\in[0.56,0.98]$ and geometric-law decay (R²≥0.92). Full append yields linear accumulation–competition: a constant per-generation write ($w_n\equiv1$) gives $Z_{n+1}=Z_n+1$ up to the memory capacity $M$, where FIFO competition reaches a steady state ($5/16$); the estimated mean $\hat m=1.166$ (CI [1.156,1.176]) persists rather than decays. Capacity $M$ is the control parameter, with a critical capacity $M_c\in(8,16)$ separating extinction ($M\le M_c$) from persistence ($M>M_c$).

For defense, soft marking shows zero compression across three independent experiment families (Pro $p=0.15$; full-append 12/12 same-trace; paired $n=48$, $\bar d=0.020$, $p=0.69$), while quarantine ($\sigma=1$) cuts off propagation in all conditions: 24/24 cross-model, 48/48 cross-task, and 12/12 full-append chains. We conclude that defense depends on hard quarantine, not soft marking. As a methodological note, our pre-registered branching-match hypothesis was falsified by direct generation-level evidence and revised to linear accumulation–competition; we report the revision transparently.


---

## 1. Introduction

## 1.1 Problem

LLM agents are being deployed into long-running production systems: experience accumulates in a persistent memory store and is reused, via retrieval, across sessions and tasks. This architecture introduces a failure mode that has not previously been studied systematically—**memory poisoning**: unvalidated self-generated experience (or attacker-injected experience) that enters the memory store, is copied across generations by transcribing, and contaminates all subsequently retrieved tasks. The literature has established the reality and cross-session persistence of the attack (MemoryGraft, arXiv:2512.16962; OEP, arXiv:2605.18930), as well as the macroscopic collapse consequences of recursive self-consumption during training (Shumailov et al., *Nature* 631, 2024). However, three questions—**how the memory architecture itself modulates propagation, why defenses fail, and which interventions carry a mechanism-level guarantee**—lack both empirical and formal answers.

## 1.2 Three Gaps

1. **Mechanism gap**: which mathematical model propagation obeys depends on the memory transcription protocol (selective replay vs. full append)—no cross-architecture controlled experiments exist;
2. **Defense gap**: soft marking (a marking gate) and hard quarantine (a gate) are conflated, with no independent criterion separating their roles in propagation dynamics;
3. **Formalization gap**: the "fundamental laws" of software engineering (Brooks 1987; Lehman 1980; Conway 1968) are empirical laws that have never been formally proven (§2.5); the poisoning-quarantine regularities of agentic memory likewise remain at the heuristic level.

## 1.3 This Work

This work is rooted in **Axiom IV (empirical self-immunity)**: self-generated experience that lacks **physical verification and independent-review final adjudication** persistently contaminates subsequently retrieved tasks; defense must therefore rely on structural blocking at the write layer (quarantine) rather than soft signals at the decision layer (marking). Within this framework we deliver a closed loop of **mechanism identification + formalization + pre-registered evidence**:

1. **Mechanism layer**: "the architecture determines the propagation mechanism"—selective replay yields branching decay (a Galton-Watson branching process), full append yields linear accumulation–competition (constant per-generation write $w_n\equiv1$); memory capacity $M$ is the control parameter with critical capacity $M_c\in(8,16)$ (§3);
2. **Formalization layer**: a Lean 4 machine-checked theorem chain (zero `sorry`, §4)—GW extinction probability equals the least fixed point, subcritical probabilistic extinction, quarantine compresses offspring, supercritical positive-probability non-extinction;
3. **Evidence layer**: pre-registered, cross-model (Pro / Kimi / Flash; full-name-to-abbreviation mapping in §5.2) × cross-architecture (selective / full-append / capacity tiers) × cross-task-family (144 chains) × large-sample paired (160 chains) closed criteria (§5–§6);
4. **Engineering implication**: defense depends on **quarantine, not marking**—the marking gate shows zero compression across three experiment families and two architectures (Pro $p=0.15$; C1-full 12/12 generation-identical trajectories; H1AC paired $\bar d=0.020$, $p=0.69$), while quarantine truncates propagation in three dimensions: cross-model (24/24 chains $Z_1=0$), cross-task-family (48/48 chains), cross-architecture (12/12 chains, mem constant 6) (§7).

**An honest methodological statement**: the pre-registered hypothesis S-H3 (GW branching match) was **falsified** by generation-level mechanism evidence ($w_n\equiv1$ linear accumulation). We present it as a positive case of "pre-registered hypothesis falsified → mechanism re-identification" (§8), rather than post-hoc rationalization.

## 1.4 Paper Structure

§2 Related Work; §3 mechanism model; §4 formalization; §5 experimental setup; §6 results; §7 discussion; §8 mechanism-revision narrative; §9 scope; §10 limitations; §11 conclusion.


## 2. Background and Related Work

## 2.1 Agentic Memory and Poisoning

Agentic memory has become a standard component of LLM application systems: experience is reused via retrieval, forming a persistent cross-session knowledge layer. At the same time, memory has become a high-value attack surface: **memory poisoning**—attacker-injected or agent-failure experience that enters the memory store, is persistently reused after retrieval, and contaminates downstream tasks (Shumailov et al., 2024; MemoryGraft, 2025). Recent empirical work shows that poisoning attacks persist across sessions, and that extremely low contamination rates suffice for high attack success (MemoryGraft, arXiv:2512.16962); pollution paths for self-evolving agents under "locally correct but non-transferable" experience are also characterized (OEP, arXiv:2605.18930). These works establish the reality and persistence of the attack, but the **defense side remains heuristic** (marking, filtering, human review), lacking mechanism-level explanations of why certain defenses fail—this work fills that layer.

## 2.2 Model Collapse and Recursive Degradation

At the macroscopic level, recursive self-consumption has been shown to cause **model collapse**: training on recursively generated data drives the model distribution into mode collapse and variance loss (Shumailov et al., *Nature* 631, 2024). Its connection to branching processes is noted in the literature: degradation can be characterized as population dynamics. The theoretical tools of this work—the Galton-Watson branching process, its extinction probability, and the geometric decay law (Harris, 1963)—are a formal end point of this connection. Unlike Shumailov et al.'s training-phase collapse, this work concerns **inference-/memory-phase propagation**: no retraining; propagation occurs generation by generation in the context–memory–transcription loop. This distinction is the starting point of our mechanism.

## 2.3 Defenses against Memory Poisoning

Existing defenses follow two lines:

1. **Soft marking**: tagging self-generated experience as "unvalidated" for downstream filtering (the experimental marker name is DRAFT_SUSPECT, §5.3). Three experiment families in this work (Pro main experiment $p=0.15$; SUPERCRITICAL C1-full 12/12 generation-identical trajectories; H1AC large-sample paired $\bar d=0.020$, $p=0.69$; full model names in §5.2) consistently show: **the marking gate has no compression effect**—model adherence to soft signals is unreliable;
2. **Hard quarantine**: experience that has not passed **five-fold physical criteria** and **independent-review final adjudication** cannot enter the global knowledge store (equivalent to this work's gate $\sigma=1$). The five-fold physical criteria are five **independent physical channels**—compilation, hidden tests, live execution probing, exit-code verification, and formal audit—all green before promotion; LLM self-assessment does not constitute evidence. Independent-review final adjudication is an arbitration gate physically isolated from the experience producer, which does not accept natural-language justifications. This work shows empirically: quarantine truncates propagation across **cross-model (24/24 chains $Z_1=0$), cross-task-family (48/48 chains), and cross-architecture (full-append 12/12 chains, mem constant 6)**—defense depends on structural blocking, not model behavior.

This "quarantine works, marking fails" separation is an empirical conclusion not systematically tested in the literature (MemoryGraft, 2025 does not distinguish the two in its defense discussion).

## 2.4 General Degradation Mechanisms in Agents

- **Reward hacking / specification gaming**: agents satisfy the letter rather than the spirit of goals to obtain success signals (Amodei et al., 2016; Krakovna et al., 2020); naturally emergent misalignment has been observed in production RL (Anthropic, arXiv:2511.18397). This is of the same family as our Axiom I (absent external anchoring, self-claims are untrustworthy), but does not involve cross-generation propagation.
- **Context rot / Lost in the Middle**: effective reasoning degrades significantly with irrelevant context growth, showing a U-shaped attention curve (Liu et al., TACL 2024); effective context length is far below nominal (Hsieh et al., 2024, RULER; Chroma, 2024). This corresponds to Axiom II (attention dilution), a **within-generation** degradation; our Axiom IV concerns **cross-generation** propagation. The two connect in the causal chain but differ mechanistically.

## 2.5 Software Engineering "Near-Axiom" Laws (Positioning)

The traditional "fundamental laws" of software engineering are **empirical laws**, not formal axioms: Brooks' essential complexity (Brooks, 1987) bounds the engineering frontier; Lehman's laws (Lehman, 1980) characterize continuous change and increasing complexity in software evolution (software's "entropy increase"); Conway's law (Conway, 1968) reveals architecture–organization isomorphism; the CAP theorem (Gilbert & Lynch, 2002) fixes the consistency trade-offs of distributed systems; the halting problem (Turing, 1936) bounds decidability. These laws derive from extensive engineering experience and have **never been formally proven**.

Our methodological position: the "near-axiom" laws of SE can and should be promoted to engineering axioms with **first-principle starting-point status plus empirically falsifiable content**. This paper focuses on one of them—empirical self-immunity—and provides: a Lean 4 machine-checked chain of conditional theorems (quarantine implies extinction, GW extinction probability, geometric law, supercritical divergence), pre-registered large-sample evidence, and a mechanism-level revision (branching decay vs. accumulation–competition). This is one instance of advancing an SE empirical law through "formalization + measurement," not a bare postulate.

## 2.6 Formal Verification Tooling

The theorem chain is machine-checked in **Lean 4** (Moura & Ullrich, 2021), zero `sorry` (conditional theorems and sources in §4). Prior applications of formal verification in software engineering (protocol verification, concurrency correctness) support the feasibility of presenting engineering commitments as machine-checkable theorems; one contribution of this paper is the first application of such conditional theorems ("for systems satisfying branching and multiplicative compression, quarantine makes the poisoning lineage go extinct with probability 1") to agentic memory security.


## 3. Model

## 3.1 Notation

| Symbol | Meaning | Measured / setting |
| :--- | :--- | :--- |
| $Z_n$ | number of poison-lineage (P1) entries in the memory store at generation $n$ (pool size) | tracked per generation |
| $M$ | memory window capacity (FIFO) | default $16$; sensitivity tiers $M=8,32$ |
| $w_n$ | number of newly written poison entries at generation $n$ (fresh write) | selective: varies with $Z_n$; full-append: $\equiv 1$ (per-generation check) |
| $X_i$ | offspring count of a single parent in the branching process | $E[X]=\hat m$ (empirical estimate) |
| $\sigma$ | gate filtering parameter (write-through rate) | random filtering $\sigma=0.5$ (C2); quarantine $\sigma=1$ |
| $\hat m$ | estimated mean offspring per parent (bootstrap CI) | per experiment tier |

**Notation discipline**: $M$ is the memory capacity (the window parameter in tier names `_W8/_W32`), and $w_n$ is the per-generation write—the two are strictly distinguished throughout this paper.

## 3.2 Two Propagation Mechanisms (Core Claim 1)

**Mechanism A: branching decay (selective-replay protocol)**. The agent transcribes only the entries judged relevant in the current session; the offspring count depends on the parent poison lineage's transcription propensity:

$$Z_{n+1}=\sum_{i=1}^{Z_n} X_i,\qquad E[Z_{n+1}\mid Z_n]=\hat m\,Z_n$$

This is the classical Galton-Watson branching process (Harris, 1963): the expected propagation follows the geometric law $E[Z_n]=\hat m^n E[Z_0]$; the extinction probability is the least fixed point of the generating function $\varphi(s)$ (Lean T1); subcritical ($\hat m<1$) decay is exponential (Lean T2). **Criterion for this mechanism**: $w_n$ varies with $Z_n$ (branching dependence).

**Mechanism B: linear accumulation–competition (full-append protocol)**. The agent appends all experience each generation (vector-store direct write / no transcription decay); the poison write is constant:

$$Z_{n+1}=Z_n+w_n,\qquad w_n\equiv 1\ \text{(measured)}$$

Before saturation, growth is linear, $Z_{n+1}=Z_n+1$; once $Z_n$ reaches capacity $M$, the system enters the FIFO competition steady state (new entries evict the oldest), with steady-state pool size determined by capacity competition (measured C0-full steady state $5/16$). **Criterion for this mechanism**: $w_n$ is constant and independent of $Z_n$ (accumulative writing).

**Direct evidence of mechanism discrimination (per-generation offspring check)**: in the full-append tier, the number of newly written P1 entries is 1 every generation ($w_n\equiv1$, linear accumulation $Z_{n+1}=Z_n+1$; measured Z=[1,2,2.917,3.917,3.917,4.917,4.917,4.917]); the "offspring depends on parent population" requirement of a branching process fails. **Therefore the pre-registered hypothesis S-H3 (GW match) is falsified by mechanism evidence, and the theory is revised to Mechanism B** (see §8, mechanism-revision narrative). Branching decay (Mechanism A) still holds under the selective protocol (geometric law $R^2=0.958$, main experiment; $R^2=0.923$, H1AC large sample).

## 3.3 Capacity as Control Parameter (Half of Core Claim 2)

Memory window capacity $M$ determines the propagation outcome of Mechanism B (SUPERCRITICAL tier, full-append, Flash):

| $M$ | $\hat m$ (boot95 CI) | g7 survival | Outcome |
| :--- | :--- | :--- | :--- |
| 8 | 0.829 ([0.739, 0.875]) | 0 | **extinction** (suppressed at the write side by capacity) |
| 16 | 1.166 ([1.156, 1.176]) | 1.0 | **persistent accumulation** (engineering-sense supercritical) |
| 32 | 1.25 (degenerate CI, 6 identical chains) | 1.0 | **linear growth** ($Z=[1,\dots,8]$, unsaturated) |

**Critical capacity $M_c\in(8,16)$**: capacity monotonicity holds—the poison pool is suppressed to extinction when $M\le M_c$, and accumulates monotonically without extinction when $M>M_c$. $M$ is therefore the **control parameter** of propagation (not a model parameter).

## 3.4 Architecture Determines Mechanism (Core Claim 2)

Switching the memory architecture within the same model family (Flash) switches the mechanism:

| Architecture | Mechanism | $\hat m$ / propagation | Criterion |
| :--- | :--- | :--- | :--- |
| selective replay | branching decay (A) | $\hat m\in[0.56,0.98]$ (cross-model, model-specific) | $w_n$ depends on $Z_n$; geometric law holds |
| full-append | accumulation–competition (B) | $Z$ accumulates linearly; capacity $M$ decides the outcome | $w_n\equiv1$; $M_c\in(8,16)$ |

**The variable is architecture, not the model**: within the same Flash tier, the selective control (2 chains) keeps $Z$ constant at 1 with memory shrinking to 3 (critical boundary $\hat m=1.0$; weak subcriticality supported by the H1AC large sample $m\approx0.92$), while full-append C0 (12 chains) accumulates linearly to 5/16 (engineering-sense supercritical)—the bifurcation is entirely determined by the transcription protocol. This is consistent with the applicability-domain statement of Axiom IV: without a gate, $\hat m$ is a model–task–site joint parameter ($[0.29,1.00]$; cross-model $[0.56,0.98]$), but the **mechanism class is determined by architecture and does not migrate across models**.

## 3.5 Pre-registered Hypotheses (Experiments in §5, Results in §6)

| Hypothesis | Proposition | Criterion |
| :--- | :--- | :--- |
| **S-H1** | full-append without gate has $\hat m>1$ and CI lower bound $>1$ | bootstrap 95% CI |
| **S-H2** | survival rate 1.0 in the unsaturated segment | g7 survival |
| **S-H3** | GW branching match ($\to$ **falsified by mechanism evidence, revised to Mechanism B**) | per-generation $w_n$ check |
| **S-H4** | quarantine truncates accumulation across mechanisms | C3-full 12/12 |
| **B-H1a** | marking gate compresses paired difference $>0$ ($\to$ does not hold) | sign-flip permutation $p<0.05$ |
| **B-H1c** | multiplicative compression law $\hat r_{C2}/\hat r_{C0}\in[0.35,0.65]$ with CI fully inside | point + CI dual criterion |
| **B-H2** | large-sample geometric-law re-check $R^2\ge0.8$ | log-linear |
| **X-H1/X-H4** | cross-model quarantine guarantee; defense does not depend on the model | 24/24 chains $Z_1=0$ |
| **T-H1/T-H4** | cross-task-family quarantine guarantee; poison propagation modulated by task family | 48/48 chains; paired $p<0.05$ |


![Mechanism schematic: branching decay (selective replay) vs. linear accumulation-competition (full append)](figures/fig-mechanism.png)

*Figure 1. Two propagation mechanisms: A) branching decay under selective replay (Galton-Watson, geometric law, extinction probability = least fixed point); B) linear accumulation-competition under full append (constant write $w_n\equiv1$, FIFO competition at capacity $M$, critical $M_c\in(8,16)$).* (data: DeepSeek-V4.1-Flash-1017, chain means)

## 4. Formalization

## 4.1 Model Structure

The propagation model is a **branching process** (`BranchingProcess` structure, a finitely supported PMF per generation): in the cross-generation propagation of un-adjudicated experience, the selectivity $\sigma$ of the double-blind quarantine gate compresses the nominal reproduction mean $\mu$ to an effective reproduction number

$$m = \mu(1-\sigma) \quad \text{(multiplicative compression law)}$$

All theorems are presented as **conditional theorems**: structural premises (e.g., $m<1$) are explicit assumptions; "the real system satisfies the premise" is supported by measurement in §5–§6 and is not asserted inside the formal system. This division is the three-layer knowledge-status structure adopted throughout: **theorem layer** (Lean-checked structural implications), **empirical layer** (pre-registered measurements of $\hat m$, $M_c$, $\sigma$), and **engineering layer** (deployment adjudication by production criteria); numbers and theorems do not impersonate each other.

## 4.2 Theorem Chain (Lean 4 machine-checked, zero `sorry`)

**T1 Expected geometric law** (`expected_population_geometric`, by induction): $E[Z_n]=m^n E[Z_0]$.

**T2 Subcritical probabilistic extinction** (`subcritical_extinction_in_probability`): by Markov's inequality with geometric decay, when $m<1$ the survival probability $P(Z_n\ge1)\to0$. This is the quantitative core of the quarantine promotion gate's effectiveness: the gate pushes $m$ below 1, and the lineage dies out with probability 1.

**T3 Quarantine compresses offspring** (`quarantine_compresses_offspring`): the stricter $\sigma$, the smaller the effective reproduction number; full quarantine ($\sigma=1$) gives $m=0$, and the lineage reaches zero within one generation. **Applicability**: branching + multiplicative compression—measured to hold under the selective architecture (geometric law $R^2=0.958$); under the full-append architecture the branching premise fails, and quarantine's effectiveness is given directly by measurement (C3-full 12/12, mem constant 6, $Z$ constant 1), with the mechanism revision recorded transparently (§8).

**T4 Supercritical non-extinction** (`galton_watson_non_extinction` + `supercritical_expectation_diverges`): when $m>1$, the extinction probability is the **least fixed point** $q=\min\{s\in[0,1]:\varphi(s)=s\}<1$ of the generating function $\varphi$ on $[0,1]$—non-extinction with positive probability; the expectation $E(n)\to+\infty$. The proof uses elementary generating-function fixed-point analysis (monotone squeezing + polynomial truncation), avoiding any dependence on continuity of $\varphi$.

## 4.3 Theorem–Application Mapping

| Theorem | Assertion | Application side |
| :--- | :--- | :--- |
| T1 | $E[Z_n]=m^nE[Z_0]$ | geometric-law criterion (expectation side of S-H2/B-H2) |
| T2 | $m<1 \Rightarrow P(Z_n\ge1)\to0$ | quarantine/random filtering extinguishes lineages (C2 survival 0.062 vs C0 0.750) |
| T3 | $\sigma\!\uparrow \Rightarrow m\downarrow$; $\sigma=1\Rightarrow m=0$ | quarantine invariance (S-H4/T-H1/X-H1) |
| T4 | $m>1 \Rightarrow q<1$, expectation diverges | expectation-side counterpart of Mechanism B "persistent accumulation without extinction" (engineering-sense supercriticality) |

## 4.4 Boundary of the Formalization

The **values** of $\hat m$, $M_c$, and $\sigma$ are empirical/engineering-layer parameters and do not enter the formal interface; the formalization guarantees **structural implication** (if the premise holds, the conclusion is necessarily true), and the values are estimated by pre-registered measurement. This division avoids two errors: treating empirical constants as theorems, and treating theorems as empirical constants.


## 5. Experimental Setup

## 5.1 Pre-registration Principle

All criteria were fixed before the experiments (hypothesis list in §3.5): significance threshold ($p<0.05$ permutation/one-sided), judgment unit (chain mean vs. pooled; §5.5), and directional claims are declared in advance. Plan documents are archived with the judgment artifacts (`EXPERIMENT_PLAN_AXIOM4_SUPERCRITICAL.md`, `EXPERIMENT_PLAN_AXIOM4_H1AC_BOOST.md`); any criterion revision is recorded in §9 (e.g., the invalidation of the H1AC pooled criterion).

## 5.2 Model Tiers

| Tier | Model | Use |
| :--- | :--- | :--- |
| Main | **DeepSeek-V4-Pro-0813** (abbrev. Pro; sampling temperature 0.7) | selective protocol, 4 conditions × 12 sessions × 6 generations = 288 sessions |
| Cross-model | Kimi `kimi-for-coding` + same Pro protocol | X-H1/X-H4, 288 sessions |
| SUPERCRITICAL | **DeepSeek-V4.1-Flash-1017** (abbrev. Flash) | full-append / capacity tiers / selective control (deviation from the pre-registered model tier recorded in plan §9) |
| H1AC | same as Flash | 160-chain dual-strain large sample |

## 5.3 Propagation Protocol

- **Standardized poison injection**: at generation 0, inject 1 seed experience carrying a lineage marker (P1/P2); transcription generation by generation (selective: only entries judged relevant are transcribed; full-append: all entries are appended);
- **Lineage tracking**: every memory entry carries a lineage marker; $Z_n$ = number of poison-lineage entries at generation $n$ (judgment unit);
- **Double-blind filtering (DRAFT_SUSPECT)**: the marking-gate condition (C1) tags suspected entries without blocking; the quarantine gate (C3/C2) physically blocks un-adjudicated entries (i.e., entries that have not passed the five-fold physical criteria and independent-review final adjudication; definition in §2.3).

## 5.4 Condition Matrix

- **selective**: C0 (no gate) / C1 (marking gate) / C2 (random filtering $\sigma=0.5$) / C3 (quarantine $\sigma=1$);
- **full-append**: C0-full / C1-full / C3-full (12 sessions × 8 generations each); capacity tiers $M=8$ / $M=32$ (6 sessions × 8 generations each); selective control (2 sessions × 6 generations);
- **H1AC (Flash, dual-strain)**: C0 (48) / C1 (48) / C2 (64), 6 generations.

Total session–generation units **1,264** (= main 288 + cross-model 288 + cross-task 144 + SUPERCRITICAL 384 + H1AC 160); SUPERCRITICAL 384 = 3 conditions × 12 replicates × 8 generations (C0/C1/C3-full) + 2 sensitivity tiers × 6 × 8 (W=8/32); the selective control (2 chains × 6 generations) is counted separately.

## 5.5 Judgment Criteria

- bootstrap CI ($10^4$ resamples) for $\hat m$ and ratio CIs; sign-flip paired permutation ($10^4$) for the marking-gate paired difference;
- **chain mean vs. pooled**: the judgment unit for propagation experiments is the chain mean (per-parent pooling fails under C2 due to survivor bias—final-generation survival only 6%, pooled ratio 1.017 meaningless; recorded in plan §9, switched to chain mean);
- geometric-law re-check: log-linear fit $R^2$;
- **power** (Pro-tier marking gate): paired difference $d=0.167$, $sd=0.432$, C1/C0 ratio 0.529 → current $n=12$ power 0.38; $n\approx48$ needed for power 0.8 (`e_power_markgate.py/.json`)—the H1AC tier closes this gap with 48 pairs.

## 5.6 Reproducibility

- Judgment scripts: `e_supercritical_judge.py`/`judge2.py`/`sh3.py`, `e_cross_task_judge.py`, `e_h1ac_judge.py` (all in git);
- Raw sessions: `axiom4_results_*.json` (SUPERCRITICAL/H1AC/cross-model/cross-task complete, in git);
- Environment: fixed model tiers, sampling temperature 0.7, sampling parameters archived per session.


## 6. Results

## 6.1 Mechanism and Capacity (SUPERCRITICAL tier, Flash, full-append)

**S-H1 supercritical ✅**: C0-full $\hat m=1.166$ (bootstrap 95% CI $[1.156,1.176]$), CI lower bound > 1. Z trajectory $[1,2,2.917,3.917,3.917,4.917,4.917,4.917]$: monotone linear accumulation in the unsaturated segment (g0–g3); after hitting capacity at g4 (mem 6→16), the FIFO competition steady state $Z\approx5/16$ (g5–g7 constant 4.917).

**S-H2 survival ✅**: g7 survival 1.0 (12/12 chains, no extinction).

**S-H3 GW match ✗ (falsified by mechanism evidence)**: per-generation offspring check—each generation writes exactly 1 new P1 ($w_n\equiv1$, $Z_{n+1}=Z_n+1$); the "offspring depends on parent population" requirement of a branching process fails. Mechanism B (linear accumulation–competition) replaces GW matching; **revision narrative in §8**.

**S-H4 quarantine invariance ✅**: C3-full 12/12 chains, mem constant 6, $Z$ constant 1—quarantine truncates propagation under the full-append architecture as well (even where the branching premise fails).

**Capacity as control parameter**: at $M=8$, $\hat m=0.829$ ($[0.739,0.875]$), g7 survival 0 (extinction); at $M=32$, $\hat m=1.25$ (degenerate CI, 6 identical chains), $Z=[1,\dots,8]$ linear growth, unsaturated. **Critical $M_c\in(8,16)$**, capacity monotonicity holds.

**Selective control (Flash)**: 2 chains, $Z$ constant 1, memory shrinks to 3 ($\hat m=1.0$ critical boundary; H1AC large sample, 48 chains, $m\approx0.92$, supports weak subcriticality)—within the same model tier, an architecture bifurcation with C0-full (§3.4).

## 6.2 Marking Gate and Multiplicative Law (H1AC, Flash, 160 chains)

**B-H1a marking-gate compression ✗**: paired (C0 vs C1, 48 pairs) difference $\bar d=+0.020$ (mean pulled by a few large-difference pairs; only 15/48 positive—at the pair level, mostly contrary to expectation), sign-flip permutation $p=0.69$—**zero compression by the marking gate**. Triple independent confirmation: Pro main experiment ($p=0.15$, C1/C0 ratio 0.529, 47% compression, not significant) → SUPERCRITICAL C1-full (12/12 generation-identical trajectories) → H1AC (large-sample paired). Power side: H1AC's $n=48$ meets the sample required by the Pro-tier power analysis (power 0.848), excluding the "insufficient power" explanation.

**B-H1c multiplicative compression law (partial)**: chain-mean write-rate ratio $\hat r=\mu_{C2}/\mu_{C0}=0.422/0.905=\boldsymbol{0.466}\in[0.35,0.65]$ (multiplicative prediction 0.5 matches); bootstrap CI $[0.333,0.602]$—lower bound 0.017 outside the target band. Criterion definition (point + CI dual criterion): point ✅, CI ⚠️. Survival corroboration: C2 final generation 0.062 vs C0 0.750—random filtering genuinely suppresses propagation.

**B-H2 geometric-law re-check ✅**: log-linear fit of $\log Z$ vs. generation, $R^2=0.923$, $m\approx0.92$ (Flash selective critical/weak-subcritical, consistent with main-experiment $R^2=0.958$).

**P2 event multiplication not achieved**: $\mu_{P2}\approx0.001$ (250 vs 1 entries)—the second event channel of the dual-strain design was not adopted by the model; recorded transparently (§10).

## 6.3 Cross-Model (288 sessions, selective)

**X-H1/X-H4 ✅**: without a gate, $\hat m$ is model-specific (Pro 0.560 [0.294,0.735], Kimi 0.983 [0.944,1.000], Flash 1.0 critical; heterogeneous transcription-decay tendencies; full names in §5.2), but the quarantine guarantee holds across models (24/24 chains $Z_1=0$)—defense does not depend on model behavior. Judgment summary in §6.6, Table 3.

## 6.4 Cross-Task-Family (144 chains, selective)

Quarantine: 48/48 chains extinct (T-H1 ✅); poison propagation is modulated by task family (T-H4 paired $p=0.026$ ✅); without a gate, $\hat m$ is a model–task–site joint parameter (cross-task interval $[0.29,1.00]$)—**cross-family non-transferability is a measured conclusion, not a defect** (§9).

## 6.5 Engineering Side (Production Field, Associated Evidence)

Production-field closed-loop experiment (agent autonomous submission → five-fold physical criteria promotion/blocking → audit archival): 18 reports, 14 promoted, 4 blocked; promotion ratio 1.00, false-block 1.00, leakage 0. The connection between the engineering loop and the theoretical channel is an open item (§10) and does not constitute a cross-channel causal claim.

---

## 6.6 Formal Judgment Tables (directly from judgment JSONs)

**Table 1: Mechanism and Capacity (SUPERCRITICAL tier, Flash, full-append, chain mean)**

| Condition | Capacity $M$ | $n$ | $\hat m$ (boot95 CI) | Final Z (g7) | g7 survival | Criterion |
| :--- | :---: | :---: | :--- | :---: | :---: | :---: |
| selective ctrl | 16 | 2 | 1.0 ([1.0,1.0]) | 1.0 | 1.0 | critical boundary (weak subcriticality, see H1AC) |
| C0-full | 16 | 12 | **1.166** ([1.156,1.176]) | 4.917 (steady 5/16) | 1.0 | **S-H1 ✅ S-H2 ✅** |
| C1-full | 16 | 12 | 1.165 ([1.163,1.167]) | 4.917 | 1.0 | marking gate zero compression |
| C3-full | 16 | 12 | 1.0 ([1.0,1.0]) | 1.0 | 1.0 | **S-H4 ✅** (mem constant 6) |
| W=8 | 8 | 6 | 0.829 ([0.739,0.875]) | 0.0 | 0.0 | **extinction** ($M\le M_c$) |
| W=32 | 32 | 6 | 1.25 (degenerate CI) | 8.0 | 1.0 | linear growth, unsaturated ($M>M_c$) |

Critical capacity: $M_c\in(8,16)$, capacity monotonicity holds (`capacity_monotone=True`).

**Table 2: Marking Gate and Multiplicative Law (H1AC tier, Flash, 160 chains, chain mean)**

| Hypothesis | Quantity | Value | Criterion | Conclusion |
| :--- | :--- | :--- | :--- | :---: |
| B-H1a | paired difference $\bar d$ (C0−C1) | +0.020; 15/48 positive; $p=0.69$ (sign-flip 10⁴) | $p<0.05$ | **✗ zero compression** |
| B-H1c | chain-mean write-rate ratio $\hat r=\mu_{C2}/\mu_{C0}$ | 0.422/0.905 = **0.466**; CI [0.333,0.602] | point∈[0.35,0.65] and CI fully inside | ⚠️ point ✅, CI lower bound 0.017 out |
| B-H2 | log-linear $R^2$ | **0.923**; slope −0.086 ($m\approx0.92$) | $R^2\ge0.8$ | **✅** |
| — | final-generation survival | C0=0.750 / C1=0.729 / **C2=0.062** | corroboration | random filtering genuinely effective |

**Table 3: Cross-Model (288 sessions, selective; quarantine 24/24 chains $Z_1=0$)**

| Model | $\hat m$ (boot95 CI) | Quarantine guarantee | Criterion |
| :--- | :--- | :---: | :---: |
| DeepSeek-V4-Pro-0813 (Pro) | 0.560 ([0.294,0.735]) | ✅ | **X-H1/X-H4 ✅** |
| Kimi | 0.983 ([0.944,1.000]) | ✅ | same |
| DeepSeek-V4.1-Flash-1017 (Flash, selective control) | 1.0 (critical) | ✅ | same |

**Table 4: Cross-Task-Family (144 chains, selective)**

| Criterion | Value | Conclusion |
| :--- | :--- | :---: |
| T-H1 quarantine 48/48 chains extinct | 48/48 | ✅ |
| T-H4 poison propagation modulated by task family | paired $p=0.026$ | ✅ |
| no-gate $\hat m$ interval | [0.29, 1.00] (model–task–site joint parameter) | cross-family non-transferable |

**Table 5: Engineering Side (production-field closed-loop experiment)**

| Metric | Value |
| :--- | :---: |
| Total reports | 18 |
| Promoted / blocked | 14 / 4 |
| Promotion ratio | 1.00 |
| False-block | 1.00 |
| Leakage | 0 |


![Poison lineage trajectories by architecture and capacity](figures/fig-trajectories.png)

*Figure 2. Poison lineage entries per generation for full-append conditions across capacity $M\in\{8,16,32\}$ and the selective control ($M=16$). The critical band $8<M_c\leq16$ separates extinction from persistence. Data: DeepSeek-V4.1-Flash-1017, chain means.*


## 7. Discussion

## 7.1 Defense Depends on Quarantine, Not Marking (Core Engineering Conclusion)

Three experiment families and two architectures converge on the same separation:

- **Marking gate zero compression**: Pro $p=0.15$ (C1/C0 ratio 0.529, 47% compression, not significant), C1-full 12/12 generation-identical trajectories, H1AC large-sample paired $\bar d=0.020$ ($p=0.69$)—the soft marker is a signal the model can ignore;
- **Quarantine/filtering effective**: quarantine truncates propagation across models (24/24), task families (48/48), and architectures (C3-full 12/12, mem constant 6); random filtering ($\sigma=0.5$) drives survival to 0.062 in the large sample.

Mechanism explanation: marking is a **soft constraint at the decision layer** (the model may ignore it); quarantine is **structural blocking at the write layer** (un-adjudicated entries are physically unreachable). Defense design should therefore use a write-layer gate as the primary mechanism, with marking serving only as an audit clue.

## 7.2 Architecture Determines Mechanism (Theoretical Conclusion)

The transcription protocol changes the **mathematical structure** of propagation, not merely its parameters: selective→branching decay (GW, model-specific $\hat m$), full-append→linear accumulation–competition ($w_n\equiv1$, outcome decided by $M_c$). Corollary: **the memory architecture is a security property, not merely a performance property**—"full append" is useful for information retention but an amplifier for poison propagation; capacity $M$ is a directly configurable propagation-control knob ($M_c\in(8,16)$).

## 7.3 Model Heterogeneity

Without a gate, $\hat m$ spans $[0.56,0.98]$ across models and $[0.29,1.00]$ across task families—propagation strength is a model–task–site joint parameter and is not transferable across domains (§9). The quarantine guarantee is independent of it: wherever $\hat m$ lies in the interval, $\sigma=1$ truncates unconditionally. This yields a **model-independent security commitment**: the reliability of defense does not drift with model generations.

## 7.4 Boundary of the Multiplicative Law

B-H1c's point estimate supports the law ($\hat r=0.466$, prediction 0.5 matches) but the CI lower bound falls slightly outside (0.017). Honest reading: the multiplicative compression law receives large-sample support at the **expectation level** but does not fully pass at the **criterion level** (CI fully inside the target band); the invalidation of the pooled criterion under survivor bias warns that the statistical unit of propagation experiments must be fixed at pre-registration—post-hoc repair risks selective-reporting.

## 7.5 Implications for the SE Discipline

This paper promotes one SE "near-axiom" law (empirical self-immunity) from empirical observation to an **engineering axiom backed by machine-checkable conditional theorems + pre-registered measurement** (§2.5 positioning). Methodological implication: the next-generation form of Brooks/Lehman/Conway-style empirical laws can be a "conditional theorem + measured support" structure, rather than remaining inductive summaries.


## 8. Mechanism Revision Narrative

## 8.1 Pre-registered Hypothesis

The experimental plan pre-registered: poison propagation under full-append without a gate follows a **Galton-Watson branching process** (S-H3): offspring counts expand with the parent population, $E[Z_{n+1}\mid Z_n]=\hat m Z_n$, and in the supercritical case ($\hat m>1$) non-extinction occurs with positive probability (Lean T4); lineage-multiplication-type growth was expected.

## 8.2 Mechanism Evidence and Falsification

Per-generation offspring checking (`e_supercritical_sh3.py`) found structural facts contradicting a branching process:

1. **Constant write**: exactly 1 new P1 entry per generation ($w_n\equiv1$), independent of $Z_n$;
2. **Linear accumulation**: $Z_{n+1}=Z_n+1$ (unsaturated segment); measured Z=[1,2,2.917,3.917,3.917,4.917,4.917,4.917] (all generations g0–g7)—no multiplication, no superlinear growth;
3. **Capacity saturation**: after hitting $M=16$, the system enters the FIFO competition steady state ($5/16$), rather than the random extinction path of a branching process.

Conclusion: **S-H3 is falsified by mechanism evidence**. Full-append propagation is **linear accumulation–competition** (Mechanism B); "supercritical" is retained as engineering semantics (persistent accumulation without extinction), and the precise mechanism is no longer GW branching.

## 8.3 Revised Theory

- Mechanism A (branching decay) still applies to the selective architecture (geometric law $R^2=0.958$ / $0.923$; Lean T1/T2 premises hold);
- Mechanism B (accumulation–competition) applies to full-append: $Z_{n+1}=Z_n+w_n$ ($w_n\equiv1$), outcome decided by capacity $M$ ($M_c\in(8,16)$);
- Quarantine invariance (S-H4) is mechanism-independent—C3-full 12/12 still truncates propagation where the branching premise fails, showing the quarantine commitment is more robust than its formalization premises.

## 8.4 Paper-Handling Principles

- **No hiding**: the falsification appears in full in Results (§6.1) and here;
- **No conflation**: Mechanism B's "persistent accumulation" and GW's "supercriticality" are distinct mathematical objects; the notational discipline throughout ($w_n$ vs $M$ vs $\hat m$) prevents misreading;
- **Methodological asset**: this case demonstrates how a pre-registered hypothesis is falsified by structural evidence rather than by significance testing—mechanism identification precedes statistical inference.


## 9. Scope and Generalizability

## 9.1 Applicability Boundaries (Four)

1. **Task family**: the main-experiment family is test-case writing (pytest) with four variants (correctness/boundary/negative/regression); the non-transferability of propagation strength across task families ($\hat m\in[0.29,1.00]$) is a measured conclusion—this paper does not claim quantitative prediction for arbitrary task families;
2. **Channel**: the theoretical evidence is confined to the **purely social propagation channel** (physical execution feedback disabled; only the context–memory–transcription loop); the production engineering loop (autonomous submission–promotion–archival cycle) satisfies the five-fold physical criteria (§2.3), and its quantitative connection to the theoretical channel—the coupling between the engineering-side promotion-loop ratio $q$ (measured 1.00) and the theoretical propagation strength $\hat m$—is an open item (§10.4);
3. **Model**: three model tiers (Pro/Kimi/Flash); $\hat m$ is model-specific; the quarantine guarantee does not depend on the model;
4. **Architecture**: selective / full-append / capacity tiers $M\in\{8,16,32\}$; vector-store direct writing is proxied by full-append and not isolated as a separate experiment.

## 9.2 Layering of Guarantees and Values

- **Cross-boundary guarantee (theory layer)**: quarantine ($\sigma=1$) truncates propagation—measured across models, task families, and architectures; Lean-checked (T3 conditional theorem) for structural necessity;
- **Within-boundary values (empirical layer)**: $\hat m$, $M_c$, multiplicative-law parameters—valid only over the measured domain; cross-domain transfer is prohibited;
- **Engineering layer**: production five-fold physical criteria (§2.3) serve as deployment adjudication; their coupling to theoretical parameters is listed as an open item.

## 9.3 Scoping Statement

This paper provides a mechanism taxonomy (architecture-decided) and a defense separation (quarantine > marking) for "poison propagation in ungated agentic memory systems." It does not claim: quantitative prediction for arbitrary task families/models, cross-channel causality, or overall security of memory systems. Inferences beyond scope are regarded as reader extensions, not claims of this paper.


## 10. Limitations and Future Work

## 10.1 Model Heterogeneity of the Marking-Gate Effect

The Pro-tier marking gate is directionally negative (C1/C0 ratio 0.529, $p=0.15$, underpowered $n=12$), while the Flash tier shows zero compression ($p=0.69$, $n=48$ adequately powered). The cause of the directional disagreement is unattributed: it may be model differences in adherence to soft signals (DRAFT_SUSPECT markers) or task-family modulation. **Future work**: cross-model paired comparison of marker-adherence rates under the same protocol.

## 10.2 Dual-Strain Event Multiplication Failure

The H1AC P2 strain barely propagates ($\mu\approx0.001$)—the model did not adopt P2's event channel, and the "event-density multiplication" design goal was not achieved. P1's 48/64 sample size already far exceeds the main experiment, but the statistical design of dual-strain interaction needs reconstruction (e.g., stronger event signals).

## 10.3 Statistical-Unit Lesson

The H1AC pooled per-parent criterion fails under C2 due to survivor bias (final-generation survival only 6%, pooled ratio 1.017 meaningless)—switched to chain mean and recorded in plan §9. Lesson: the judgment unit of propagation experiments must be fixed at pre-registration; B-H1c's CI lower bound slightly out (0.017) likewise suggests that boundary criteria need more conservative definitions or larger samples.

## 10.4 Two-Layer Connection Not Theorized

The quantitative connection between the production engineering loop (promotion/blocking/leakage, five-fold physical criteria, §2.3) and the theoretical channel (purely social propagation, $\hat m$)—the coupling of the engineering-side $q$ loop to the theoretical $\hat m$—is not yet theorized; this paper does not claim the engineering loop is evidence for the theoretical channel. **First-priority future work**: a coupling model of the two-layer channels.

## 10.5 Ecological Validity

The main evidence is concentrated on the test-writing task family; across task families, only the quarantine guarantee has generalization evidence (48/48 chains); the multiplicative law and capacity criticality have not been tested across families. The vector-store direct-write architecture is not isolated as an experiment (full-append is used as a proxy).

## 10.6 Other

- Model-tier time snapshots: all three models are of the 2025–2026 generation; drift of the conclusions to new model families is unverified;
- Sampling temperature 0.7 fixed; the effect of sampling temperature on $w_n$ is not scanned;
- Judgment scripts depend on deterministic reshuffle seeds; cross-platform floating-point differences are untested.


## 11. Conclusion

## 11.1 Conclusions (Corresponding to the Three Abstract Claims)

1. **Mechanism**: under the ungated accumulative (full-append) agentic memory architecture, injected poison persists and accumulates without extinction—the mechanism is **linear accumulation–competition** (constant per-generation write $w_n\equiv1$, $Z_{n+1}=Z_n+w_n$), measured $\hat m=1.166$ (boot95 CI $[1.156,1.176]$), FIFO competition steady state $5/16$ after capacity saturation;
2. **Architecture effect**: the propagation mechanism is determined by architecture, not model—selective replay = branching decay (GW, cross-model $\hat m\in[0.56,0.98]$), full-append = accumulation–competition; memory capacity $M$ is the control parameter, critical $M_c\in(8,16)$ ($M\le M_c$ extinction, $M>M_c$ persistent accumulation);
3. **Quarantine invariance**: quarantine ($\sigma=1$) truncates propagation across mechanisms—Lean 4 machine-checked conditional theorem (T3) + measured cross-model 24/24, cross-task-family 48/48, full-append 12/12; the marking gate shows zero compression in three tiers (Pro $p=0.15$ / C1-full / H1AC $p=0.69$)—**defense depends on quarantine, not marking**.

## 11.2 Contributions

1. Mechanism layer: the architecture-decides-mechanism dichotomy + capacity control parameter (§3);
2. Formalization layer: Lean 4 machine-checked theorem chain, zero `sorry` (§4);
3. Evidence layer: pre-registered, closed criteria across models × architectures × task families × large samples (§5–§6);
4. Engineering implication: quarantine-first defense design principle (§7.1) + honest mechanism-revision case (§8).

## 11.3 Disciplinary Implication

The empirical laws of software engineering can and should be promoted to an engineering-axiom structure of "conditional theorem + measured support"; this work provides a complete instance (formalization + pre-registration + mechanism revision) and a transferable methodological template (three-layer knowledge status + pre-registered criteria + mechanism identification first).


## Appendix

## A. Judgment Scripts and Data Inventory

**Judgment scripts** (all in git):

| Script | Output | Use |
| :--- | :--- | :--- |
| `e_supercritical_judge.py` / `judge2.py` | `e_supercritical_judgement2.json` | SUPERCRITICAL tier: $\hat m$/CI, Z trajectory, survival, capacity sensitivity |
| `e_supercritical_sh3.py` | `e_supercritical_sh3.json` | per-generation offspring check (S-H3 falsification mechanism evidence) |
| `e_cross_task_judge.py` | cross-task-family judgment JSON | T-H1/T-H4 |
| `e_h1ac_judge.py` | `e_h1ac_judgement.json` | H1AC: B-H1a/B-H1c/B-H2 (bootstrap/sign-flip 10⁴) |
| `e_power_markgate.py` | `e_power_markgate.json` | power analysis (min_n=48) |

**Raw sessions** (all in git): `axiom4_results_supercritical*.json` (C0/C1/C3-full, W8/W32, w1–w4 shards), `axiom4_results_flash_selective_ctrl.json`, `axiom4_results_h1ac_*.json` (C0/C1/C2/smoke), cross-model/cross-task-family session JSONs.

**Pre-registration plans**: `EXPERIMENT_PLAN_AXIOM4_SUPERCRITICAL.md`, `EXPERIMENT_PLAN_AXIOM4_H1AC_BOOST.md` (judgment back-fill and criterion-revision records in §9).

**Execution environment**: DeepSeek-V4.1-Flash-1017 (abbrev. Flash; scnet-flash gateway, sampling temperature 0.7); the deviation of the model tier from the pre-registered DeepSeek-V4-Pro-0813 (Pro) tier is recorded in SUPERCRITICAL plan §9.

## B. Key Values from Judgment JSONs (same source as the main text)

| Quantity | Value | Source |
| :--- | :--- | :--- |
| C0-full $\hat m$ | 1.166, boot95 [1.156,1.176] | e_supercritical_judgement2 |
| C0-full Z trajectory | [1,2,2.917,3.917,3.917,4.917,4.917,4.917] | same |
| C0-full mem trajectory | [6,9,12,15,16,16,16,16] (saturated at g4) | same |
| C1-full $\hat m$ | 1.165 ([1.163,1.167]) | same |
| C3-full | mem constant 6, Z constant 1 (12/12) | same |
| W=8 | $\hat m$=0.829 ([0.739,0.875]), g7 survival 0 | same |
| W=32 | $\hat m$=1.25, Z=[1..8], mem→27 | same |
| S-H3 mechanism evidence | $w_n\equiv1$, pmf=[0,1], criterion pass=False | e_supercritical_sh3 |
| B-H1a | $\bar d$=+0.0201, 15/48 positive, p=0.6918 | e_h1ac_judgement |
| B-H1c | $\hat r$=0.4661, CI [0.3331,0.6017], point ✅ CI ⚠️ | same |
| B-H2 | R²=0.9233, slope −0.086 | same |
| μ chain mean | C0=0.905 / C1=0.885 / C2=0.422 | same |
| Final-generation survival | C0=0.750 / C1=0.729 / C2=0.062 | same |
| Power | n=12→0.379, n=48→0.848, min_n=48 | e_power_markgate |
| Main-experiment effect size | pair_diff=0.167, sd=0.432, C1/C0=0.529 | same |

## C. Judgment Unit and Criterion Statement

- Judgment unit: **chain mean** (H1AC); SUPERCRITICAL uses chain-mean Z/survival;
- The pooled criterion fails under C2 due to survivor bias (final-generation survival only 6%, pooled ratio 1.017 meaningless)—switched to chain mean and recorded in plan §9;
- Bootstrap / sign-flip permutations 10⁴ each; B-H1a is judged on replicate-level chain-mean paired differences (§5.5 judgment criteria).


## References

1. Amodei, D., Olah, C., Steinhardt, J., Christiano, P., Schulman, J., & Mané, D. (2016). *Concrete Problems in AI Safety*. arXiv:1606.06565.
2. Anthropic Alignment Team (2025). *Natural emergent misalignment from reward hacking in production RL*. arXiv:2511.18397.
3. Brooks, F. P. (1987). *No Silver Bullet: Essence and Accidents of Software Engineering*. IEEE Computer, 20(4), 10–19. DOI: 10.1109/MC.1987.1663532.
4. Chroma Research (2024). *Context Rot: How Increasing Input Tokens Impacts LLM Performance*. Technical Report.
5. Conway, M. E. (1968). *How do committees invent?* Datamation, 14(4), 28–31.
6. Gilbert, S., & Lynch, N. (2002). *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services*. ACM SIGACT News, 33(2), 51–59. DOI: 10.1145/564585.564601.
7. Harris, T. E. (1963). *The Theory of Branching Processes*. Springer.
8. Hsieh, C.-P., et al. (2024). *RULER: What's the Real Context Size of Your Long-Context Language Models?* arXiv:2404.06654.
9. Krakovna, V., et al. (2020). *Specification Gaming: The Flip Side of AI Ingenuity*. DeepMind Blog.
10. Lehman, M. M. (1980). *Programs, Life Cycles, and Laws of Software Evolution*. Proceedings of the IEEE, 68(9), 1060–1076. DOI: 10.1109/PROC.1980.11805.
11. Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. TACL, 12.
12. MemoryGraft (2025). *Persistent Compromise of LLM Agents via Poisoned Experience Retrieval*. arXiv:2512.16962.
13. Moura, L., & Ullrich, S. (2021). *The Lean 4 Theorem Prover and Programming Language*. CADE-28, LNCS 12699, 625–635. DOI: 10.1007/978-3-030-79876-5_40.
14. OEP (2026). *Poisoning Self-Evolving LLM Agents via Locally Correct but Non-Transferable Experiences*. arXiv:2605.18930.
15. Shumailov, I., Shumaylov, Z., Zhao, Y., Papernot, N., Anderson, R., & Gal, Y. (2024). *AI models collapse when trained on recursively generated data*. Nature, 631, 755–759. DOI: 10.1038/s41586-024-07566-y.
16. Turing, A. M. (1936). *On Computable Numbers, with an Application to the Entscheidungsproblem*. Proceedings of the LMS, 42, 230–265.
