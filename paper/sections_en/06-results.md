# §6 Results (English, for manuscript-en.md)

> Status: **translated v1** (2026-10-22); tables generated directly from judgment JSONs.

---

## 6.1 Mechanism and Capacity (SUPERCRITICAL tier, Flash, full-append)

**S-H1 Mechanism-B criterion ✅ (GW formulation invalidated)**: the GW formulation of S-H1 ($\hat m>1$ with CI lower bound $>1$) is invalidated with S-H3's falsification—for a deterministic linear-accumulation process any growth statistic is necessarily $>1$, so the criterion could not, by design, fail under Mechanism B (§8). The Mechanism-B endogenous criteria are: **persistent accumulation** (linear growth before saturation; steady state $5/16$ maintained for 3 generations) and **survival 1.0**—both satisfied. Z trajectory $[1,2,2.917,3.917,3.917,4.917,4.917,4.917]$: linear accumulation g0–g3; capacity hit at g4 (mem 6→16); FIFO steady state 4.917 at g5–g7. The cross-mechanism propagation ratio $\hat m^\dagger=1.166$ ([1.156,1.176]; estimator $\hat m=\sum Z_{n+1}/\sum Z_n$, §3.1; GW “mean offspring per parent” semantics valid for Mechanism A only).

**S-H2 survival ✅**: g7 survival 1.0 (12/12 chains, no extinction).

**S-H3 GW match ✗ (falsified by mechanism evidence)**: per-generation offspring check—each generation writes 0 or 1 new P1 ($w_n\in\{0,1\}$, PMF=[0,1], chain mean $E[w_n]=0.917$; 11/12 chains write 1 every generation, about 1/12 chains skip one generation), and the write does not depend on $Z_n$—the "offspring depends on parent population" requirement of a branching process fails. Mechanism B (linear accumulation–competition) replaces GW matching; **revision narrative in §8**.

**S-H4 quarantine invariance ✅**: C3-full 12/12 chains, mem constant 6, $Z$ constant 1—quarantine truncates propagation under the full-append architecture as well (even where the branching premise fails).

**Capacity as control parameter**: at $M=8$, the propagation ratio $\hat m^\dagger=0.829$ ($[0.739,0.875]$), g7 survival 0 (extinction); at $M=32$, $\hat m^\dagger=1.25$ (degenerate CI, 6 identical chains), $Z=[1,\dots,8]$ linear growth, unsaturated. **Critical $M_c\in(8,16)$** (this protocol tier, $b=3$), capacity monotonicity holds; supplementary EXP-B shows $M_c$ is a $(b,M)$ joint function (§6.5).

**Selective control (Flash)**: 2 chains, $Z$ constant 1, memory shrinks to 3 ($\hat m=1.0$ critical boundary; H1AC large sample, 48 chains, $m\approx0.92$, supports weak subcriticality)—within the same model tier, an architecture bifurcation with C0-full (§3.4). **Supplementary EXP-C ($n=12$, 2026-10-23)**: $\hat m=0.966$ (boot95 CI $[0.911,1.000]$, contains 1), geometric law $R^2=0.833$, $Z$-means $[1,1,1,0.917,0.917,0.833]$, final-generation survival 0.83—**the CI is fully separated from C0-full ($\hat m=1.166$, CI $[1.156,1.176]$)**, confirming selective subcriticality/criticality at $n=12$; the architecture-bifurcation load-bearing wall is expanded from 2 to 12 chains (C-H1/C-H2 ✅).

## 6.2 Marking Gate and Multiplicative Law (H1AC, Flash, 160 chains)

**B-H1a marking-gate compression ✗ (confirmed by the Flash large sample)**: paired (C0 vs C1, 48 pairs) difference $\bar d=+0.020$ (mean pulled by a few large-difference pairs; only 15/48 positive—at the pair level, mostly contrary to expectation), sign-flip permutation $p=0.69$—**zero compression on the Flash tier**. The three-tier evidence is stratified: the Pro main experiment is a **large-but-non-significant effect under inadequate power** ($p=0.15$, C1/C0 ratio 0.529, 47% compression, power 0.38—not interpretable as zero compression); SUPERCRITICAL C1-full 12/12 generation-identical trajectories (the full-append write path structurally bypasses model judgment, not independent soft-signal evidence); the H1AC large-sample paired test confirms zero compression. Power side: H1AC's $n=48$ meets the sample required by the Pro-tier power analysis (power 0.848), excluding the "insufficient power" explanation.

**B-H1c multiplicative compression law (partial)**: chain-mean write-rate ratio $\hat r=\mu_{C2}/\mu_{C0}=0.422/0.905=\boldsymbol{0.466}\in[0.35,0.65]$ (multiplicative prediction 0.5 matches); bootstrap CI $[0.333,0.602]$—lower bound 0.017 outside the target band. Criterion definition (point + CI dual criterion): point ✅, CI ⚠️. Survival corroboration: C2 final generation 0.062 vs C0 0.750—random filtering genuinely suppresses propagation.

**B-H2 geometric-law re-check ✅**: log-linear fit of $\log Z$ vs. generation, $R^2=0.923$, $m\approx0.92$ (Flash selective critical/weak-subcritical, consistent with main-experiment $R^2=0.958$).

**P2 event multiplication not achieved**: $\mu_{P2}\approx0.001$ (250 vs 1 entries)—the second event channel of the dual-strain design was not adopted by the model; recorded transparently (§10).

## 6.3 Cross-Model (288 sessions, selective)

**X-H1/X-H4 ✅**: without a gate, $\hat m$ is model-specific (Pro 0.560 [0.294,0.735], Kimi 0.983 [0.944,1.000], Flash 1.0 critical; heterogeneous transcription-decay tendencies; full names in §5.2), but the quarantine guarantee holds across models (24/24 chains $Z_1=0$)—defense does not depend on model behavior. Judgment summary in §6.6, Table 3.

## 6.4 Cross-Task-Family (144 chains, selective)

Quarantine: 48/48 chains extinct (T-H1 ✅); poison propagation is modulated by task family (T-H4 paired $p=0.026$ ✅); without a gate, $\hat m$ is a model–task–site joint parameter (cross-task interval $[0.29,1.00]$)—**cross-family non-transferability is a measured conclusion, not a defect** (§9).

## 6.5 Quarantine Cost and Capacity Surface (Supplementary, Flash, 396 chains)

**EXP-A quarantine cost (σ sweep × 48 chains, full-append W=16, 6 generations; σ convention in Table 5: A50/A75/A90 tiers are implemented as random pass rate $r=0.5/0.75/0.9$, equivalent interception rate $\sigma_{\rm eff}=0.5/0.25/0.1$; A100 is the quarantine tier, $\sigma_{\rm eff}=1$)**: A100 (hard quarantine): $Z$ final generation constant 1, memory non-growing (mem_growth=0.00, $n=48$)—**hard quarantine blocks all non-finalized writes; accumulation propagation is absent (A-H1 ✅, "no accumulation propagation" criterion, following §8.3 S-H4 precedent)**; $\sigma_{\rm eff}=0.1$ (A90) is insufficient ($Z_f=4.60$, propagation persists)—no $\sigma_{\rm eff}<1$ tier meets the gain criterion. Cost side: benign pass-through measured 0.488/0.754/0.908/0.000 = pass rate $r$ ($=1-\sigma_{\rm eff}$, indiscriminate random filtering, A-H2 ✅); at the quarantine tier memory utility retention is 0.88 (vs. C0 benign stock, −12%, all from lost new-experience increments; the 6-entry seed baseline is undamaged). **Unexpected capacity-competition finding**: mid-interception tiers ($\sigma_{\rm eff}=0.5/0.25/0.1$) hold *more* benign stock than gate-free C0 (utility retention 1.33/1.31/1.19)—filtering suppresses the strain, so benign entries gain larger FIFO share; false blocking ($\sigma_{\rm eff}$) is offset by share compensation. **Two-dimensional cost–benefit conclusion: no $\sigma_{\rm eff}<1$ tier both suppresses the strain and preserves new-experience increments—hard quarantine ($\sigma_{\rm eff}=1$) meets the gain criterion at −12% increments; $\sigma_{\rm eff}<1$ preserves increments but leaves the strain supercritical**.

**EXP-B capacity surface ($b\times M$, 24 tiers × 6 chains, 8 generations, executed by `kimi_boost.py`)**: critical capacity $W_c(b)$ moves up with benign write rate $b$—$W_c\le4$ at $b=1/2$; $W_c\in(4,8)$ at $b=3$; $W_c\in(8,12)$ at $b=5$ (drift span ≥2 tiers, B-H2 ✅)—**$M_c$ is a $(b,M)$ joint function** (the main protocol's $M_c\in(8,16)$ is reported as a parallel reading of the same $b{=}3$ write cap under a different execution script, not merged as "one instance"; grid-point reconciliation in the note below Table 6). Mechanism: benign writes compete with the strain for FIFO capacity—at $b=5, W=4$ the strain goes extinct ($Z$ final 0, $\hat m=0.143$); **high $b$ + low $M$ is a natural subcritical regime of capacity competition**. Non-monotonic anomaly recorded transparently: $b=2, W=4$ survival 1.00 (above $b=1$'s 0.50), retained unexplained under 6-chain randomness.

## 6.6 Engineering Side (Production Field, Associated Evidence)

Production-field closed-loop experiment (agent autonomous submission → five-fold physical criteria promotion/blocking → audit archival): 18 reports, 14 promoted, 4 blocked; promotion ratio 1.00, false-block 1.00, leakage 0. **Definition note**: promotion ratio 1.00 = all 14/14 promoted reports verified correct; false-block 1.00 = all 4/4 blocked reports were indeed erroneous (blocking accuracy); leakage 0 = no erroneous experience in the promoted set. This table is associated production-field evidence ($n=18$); a formal estimate of the cost side (benign false-block rate) requires a larger sample (open item, §10.4), and the connection between the engineering loop and the theoretical channel is likewise an open item—it does not constitute a cross-channel causal claim.

---

## 6.7 Formal Judgment Tables (directly from judgment JSONs)

**Table 1: Mechanism and Capacity (SUPERCRITICAL tier, Flash, full-append, chain mean)**

| Condition | Capacity $M$ | $n$ | propagation ratio $\hat m^\dagger$ (boot95 CI) | Final Z (g7) | g7 survival | Criterion |
| :--- | :---: | :---: | :--- | :---: | :---: | :---: |
| selective ctrl | 16 | 12 (EXP-C extension) | 0.966 ([0.911,1.000]) | 1.0 | 1.0 | critical boundary (weak subcriticality) |
| C0-full | 16 | 12 | **1.166** ([1.156,1.176]) | 4.917 (steady 5/16) | 1.0 | **S-H1 ✅ S-H2 ✅** |
| C1-full | 16 | 12 | 1.165 ([1.163,1.167]) | 4.917 | 1.0 | generation-identical to C0 (≤0.083) |
| C3-full | 16 | 12 | 1.0 ([1.0,1.0]) | 1.0 | 1.0 | **S-H4 ✅** (mem constant 6) |
| W=8 | 8 | 6 | 0.829 ([0.739,0.875]) | 0.0 | 0.0 | **extinction** ($M\le M_c$) |
| W=32 | 32 | 6 | 1.25 (degenerate CI) | 8.0 | 1.0 | linear growth, unsaturated ($M>M_c$) |

Critical capacity (this protocol tier, $b=3$): $M_c\in(8,16)$, capacity monotonicity holds (`capacity_monotone=True`); EXP-B shows $M_c$ is a $(b,M)$ joint function (§6.5), and the cross-experiment grid-point check with its protocol-difference note is in §6.5/§3.3. $\dagger$: $\hat m=\sum_n Z_{n+1}/\sum_n Z_n$ (generation-weighted; source `e_supercritical_judge2.py`, openly reproducible); GW “mean offspring per parent” semantics valid for Mechanism A (selective) only; Mechanism B is judged on occupancy and survival. $\hat m^\dagger$ is sensitive to the saturated segment (zero increments dilute the numerator), so cross-experiment comparisons must use the same generation length. The C0/C1 difference in $\hat m^\dagger$ (0.001) is a between-chain micro-difference of near-deterministic data, not statistically meaningful, and is not used as a marking-gate criterion.

**Table 2: Marking Gate and Multiplicative Law (H1AC tier, Flash, 160 chains, chain mean)**

| Hypothesis | Quantity | Value | Criterion | Conclusion |
| :--- | :--- | :--- | :--- | :---: |
| B-H1a | paired difference $\bar d$ (C0−C1) | +0.020; 15/48 positive; $p=0.69$ (sign-flip 10⁴) | $p<0.05$ | **✗ Flash large-sample zero compression** (Pro 47% non-significant) |
| B-H1c | chain-mean write-rate ratio $\hat r=\mu_{C2}/\mu_{C0}$ | 0.422/0.905 = **0.466**; CI [0.333,0.602] | point∈[0.35,0.65] and CI fully inside | ⚠️ point ✅, CI lower bound 0.017 out |
| B-H2 | log-linear $R^2$ | **0.923**; slope −0.086 ($m\approx0.92$) | $R^2\ge0.8$ | **✅** |
| — | final-generation survival | C0=0.750 / C1=0.729 / **C2=0.062** | corroboration | random filtering genuinely effective |

**Table 3: Cross-Model (288 sessions, selective; quarantine 24/24 chains $Z_1=0$)**

| Model | $\hat m$ (boot95 CI) | Quarantine guarantee | Criterion |
| :--- | :--- | :---: | :---: |
| DeepSeek-V4-Pro-0813 (Pro) | 0.560 ([0.294,0.735]) | ✅ | **X-H1/X-H4 ✅** |
| Kimi | 0.983 ([0.944,1.000]) | ✅ | same |
| DeepSeek-V4.1-Flash-1017 (Flash, selective control) | 0.966 ([0.911,1.000]) | ✅ | same (EXP-C n=12 extension) |

**Table 4: Cross-Task-Family (144 chains, selective)**

| Criterion | Value | Conclusion |
| :--- | :--- | :---: |
| T-H1 quarantine 48/48 chains extinct | 48/48 | ✅ |
| T-H4 poison propagation modulated by task family | paired $p=0.026$ | ✅ |
| no-gate $\hat m$ interval | [0.29, 1.00] (model–task–site joint parameter) | cross-family non-transferable |

**Table 5: Quarantine Cost (EXP-A, Flash, σ sweep × 48 chains, full-append W=16)**

> Annotation: A50/A75/A90 tiers are implemented as a **random pass rate $r$** (an entry passes with probability $r$), equivalent to interception rate $\sigma_{\rm eff}=1-r$ (§3.1 defines $\sigma$ as interception rate); A100 is the **quarantine tier** ($\sigma_{\rm eff}=1$, all blocked). Benign pass-through $=1-\sigma_{\rm eff}=r$.

| Condition | Pass rate $r$ ($\sigma_{\rm eff}=1-r$) | Final Z | Survival | Benign pass-through ($=r$) | Memory utility retention | Criterion |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| C0 | — (no gate) | 5.06 | 1.00 | 1.000 | 1.00 | supercritical baseline |
| A50 | 0.5 (0.5) | 3.50 | 1.00 | 0.488 | 1.33 | partial suppression; benign share rises |
| A75 | 0.75 (0.25) | 4.04 | 1.00 | 0.754 | 1.31 | same |
| A90 | 0.9 (0.1) | 4.60 | 1.00 | 0.908 | 1.19 | insufficient suppression (A-H1 ✗) |
| A100 | 0 (quarantine, $\sigma_{\rm eff}=1$) | 1.00 | 1.00 (seed persists) | 0.000 | **0.88** | **A-H1 ✅** (no accumulation propagation) |

**Table 6: Capacity Surface (EXP-B, $b\times M$, 24 tiers × 6 chains, 8 generations; $W_c$ = smallest W tier with survival first ≥0.5)**

| Benign write rate $b$ | $W_c$ | Key row ($W=4$ tier) |
| :---: | :---: | :--- |
| 1 | ≤4 | surv=0.50, $\hat m=1.071$ |
| 2 | ≤4 | surv=1.00, $\hat m=1.086$ (non-monotonic anomaly, recorded) |
| 3 | (4,8) | surv=0.17, $\hat m=0.844$ |
| 5 | (8,12) | surv=0.00, $\hat m=0.143$ (extinction) |

> Protocol note: EXP-B executed by `kimi_boost.py`; grid-point reconciliation with the main protocol (`axiom4_memory_propagation.py`) in the note above. The $b{=}3$ tier's boundary grid point $W=8$ was extended to 12 chains by a supplementary run of the same script (2026-10-23): surv=**0.92**, $\hat m=1.074$ (CI $[1.039,1.101]$), $Z_f=1.92$—the split from the main protocol's $W=8$ extinction (surv=0) **persists after extension**, confirming a systematic execution-protocol difference rather than small-sample noise. $W_c$-criterion sensitivity (threshold 0.5→0.8): the "$b$ up → $M_c$ up" direction is unchanged (§10.3).

**B-H2 ✅ drift confirmed** → $M_c$ is a $(b,M)$ joint function; EXP-C (§6.1) C-H1/C-H2 ✅.

> **Cross-experiment grid-point check (EXP-B vs SUPERCRITICAL main protocol)**: EXP-B is executed by `kimi_boost.py` (write cap parameterized as $b$—**$b$ is the benign-experience cap, with strain entries consuming that quota**); the main protocol by `axiom4_memory_propagation.py` (write rule fixed at "1~3 entries", **3 being the total cap including the strain**). The two scripts' session templates are verbatim identical beyond the write-quota text (rest of the prompt, task sequence `task_for`, seed memory, strain signatures, FIFO capacity logic; $rng$ plays no role in the ungated tiers). **Measured write flow (chain-generation pooled)**: the main protocol's C0-full writes 3.00 entries per generation (benign 2.02, strain 0.98); EXP-B $b{=}3$ writes 3.00 (benign 2.16, strain 0.84)—**the two compared tiers are flow-isomorphic in total writes** (the quota texts differ but the actual output coincides); EXP-B $b{=}2$ writes 2.00 (benign 1.02, strain 0.98), a different flow from the main protocol, so mapping the main protocol onto the $b{=}2$ row does not hold ($b$ semantics = benign cap with strain consuming quota, vs. the main protocol's total cap). Grid-point reconciliation (flow-matched tiers): at the shared $W=16$ grid point the readings agree—EXP-A C0 (6 generations, same `kimi_boost.py`) gives final $Z=5.06$ vs. the main protocol's C0-full 4.917 at the same generation (g5), a 2.9% difference; at the boundary grid point $W=8$ they split—the main protocol gives 6/6 chains extinct (surv=0) while EXP-B $b{=}3$ gives survival 0.92 (12 chains, Table 6 note). $W=8$ sits in the critical regime (the $b{=}3$ tier's $M_c\in(4,8)$ and the main protocol's $M_c\in(8,16)$ share this boundary), where small samples are sensitive; both readings reproduce within their own batches (main protocol 6/6, EXP-B 11/12). **Attribution audit**: the located difference is the write-quota text (total cap 1~3 vs benign cap 1~$b$); residual candidates are model sampling and API runtime drift (10-22 vs 10-23, uncontrollable and unlocated)—the split persists after excluding the flow difference, and the joint probability of 11/12 survival vs 0/6 extinction under a shared survival probability $p$ is of order $10^{-4}$, rejecting a pure sampling-noise account; recorded as a **protocol-sensitive** open item. **Accordingly, the "one instance" merging is withdrawn**: the main protocol's $M_c\in(8,16)$ and the EXP-B surface $W_c(b)$ are reported as parallel readings of two execution protocols—consistent at $W=16$, split at $W=8$ (recorded); the $b{=}3$ tier was extended by 6 further chains (12 in total; result in Table 6 note).

**Table 7: Engineering Side (production-field closed-loop experiment)**

| Metric | Value |
| :--- | :---: |
| Total reports | 18 |
| Promoted / blocked | 14 / 4 |
| Promotion ratio | 1.00 |
| False-block | 1.00 |
| Leakage | 0 |


![Poison lineage trajectories by architecture and capacity](figures/fig-trajectories.png)

*Figure 2. Poison lineage entries per generation for full-append conditions across capacity $M\in\{8,16,32\}$ and the selective control ($M=16$). The critical band $8<M_c\leq16$ separates extinction from persistence. Data: DeepSeek-V4.1-Flash-1017, chain means.*
