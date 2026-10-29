# Appendix B: Formal Proofs of Convergence and Stability (Lean 4 Mechanized)

> This appendix is the mechanized foundation of the book's theoretical claims. All theorems are kernel-verified in Lean 4 (toolchain v4.34.0-rc2) + mathlib4; the project lives at `formal_proof/IACFormalization/`, and the build command is `lake build`.
>
> Statistics: 118 [Theorem] entries (117 theorems + 1 auxiliary lemma, kernel-verified, counted by `theorem`/`lemma` in the source), **0 axioms**, 0 `sorry`.
>
> A three-tier epistemic annotation runs throughout this appendix:
> - **[Theorem]**: fully verified by the Lean kernel, with no axiom dependencies (or depending only on explicit assumptions / structural premises);
> - **[Cited Result]**: results established in the mathematical literature but for which mathlib does not yet contain a ready-made formalization (this appendix carries no such dependencies);
> - **[Empirical Postulate]**: empirical propositions about the actual behavior of large models. They are formalized as conditional theorems: the premises are explicit structural assumptions (e.g., the context-quality growth law of the attention mechanism), and the conclusions are derived by kernel verification; "real systems satisfy this premise" is supported by measurement and is not asserted within the formal system.

---

## B.1 Module–Chapter Correspondence Master Table

| Lean Module | Book Chapter | Mathematical Tools | Proof Status |
| :--- | :--- | :--- | :--- |
| `Axiom1_Grounding` | §3.2 Axiom I; Chapter 2 | Algebra of finite joint distributions | All [Theorem]; independence is an explicit assumption |
| `Axiom2_AttentionDilution` | §3.2 Axiom II; Pattern 04 | Real analysis (softmax monotonicity), three-channel attention mechanism + growth laws (geometric / linear / power-law) | All [Theorem] |
| `Axiom2_PhaseModel` | §3.2 Axiom II two-phase dynamics | Two-phase structure, explicit phase-transition point, non-reversal upper bound | All [Theorem], zero axioms |
| `Axiom2_Axiom4_Bridge` | §3.2 Axiom II ↔ Axiom IV cross-axiom interface | Injection coupling, lower-bound synthesis | All [Theorem], zero axioms |
| `Axiom3_CausalMonotonicity` | §3.2 Axiom III; Pattern 09 | Order theory, idempotent operators | All [Theorem], zero axioms |
| `Axiom4_MemoryPoisoning` | §3.2 Axiom IV; Patterns 14/15 | Branching processes, elementary probability (PMF + Markov inequality) | All [Theorem], zero axioms |
| `Probability_Markov` | §3.2 Axiom IV probability toolkit | Markov inequality (elementary proof, zero measure-theoretic dependencies) | All [Theorem], zero axioms |
| `Theorem3_1_CausalInvariance` | §3.3 | Foster–Lyapunov discrete kernel, finite-state-machine counterexamples | All [Theorem], zero axioms |
| `GaltonWatson` | §3.2 Axiom IV supercritical strong conclusions | Generating functions, fixed points, elementary analysis | All [Theorem], zero axioms |
| `StochasticFosterLyapunov` | §3.3 stochastic control | Stochastic kernels, stopping times, elementary expectations | All [Theorem], zero axioms |
| `Pattern02_RealityAudit` | Pattern 02 | Four-fold reality filter operator, veto power | All [Theorem], zero axioms |
| `Pattern04_PoLPProjection` | Pattern 04 | Task-level least-privilege projection, strict SNR improvement, violation-risk reduction, and privilege monotonicity | All [Theorem], zero axioms |
| `Pattern10_LeaseLock` | Pattern 10 | Discrete clock, lease state machine | All [Theorem], zero axioms |
| `Pattern11_PrimaryWriter` | Pattern 11 | Write journal, strictly increasing clock, view filtering | All [Theorem], zero axioms |
| `Pattern15_RevocationTombstone` | Pattern 15 | Absorbing-state transition, projection isolation, reverse auto-immunity | All [Theorem], zero axioms |
| `Pattern23_24_ProductionLoop` | Patterns 23/24 | Finite-support stochastic kernel, Foster–Lyapunov drift | All [Theorem], zero axioms |
| `Theorem3_1_LyapunovFuse` | §3.3; Appendix B.7 | Consecutive-stall energy-accumulation lemma, limit-cycle-repelling strict Lyapunov supermartingale theorem, stopping-time-fuse resource-boundedness theorem | All [Theorem], zero axioms |

---

## B.2 Axiom I: The Irreplaceability of Grounding (All Proven at the Formalization Layer)

The probabilistic-limit formulation of Axiom I in the main text states an engineering position; its rigorously provable core lives in this module:

- **Theorem `self_verdict_zero_information` (Self-Verification Zero-Information Theorem)**: in a closed cognitive loop with conditionally independent channels (no external physical sensors whatsoever), the posterior truth rate of a passed self-check equals the prior truth rate: $P(V_t=1 \mid V_s=1) = P(V_t=1)$. The Bayesian likelihood ratio of self-check evidence is identically 1.
- **Theorem `closed_loop_risk_factorizes`**: inside the closed loop, the probability of "self-check claims success and the physical state is also true" is fully locked by the prior-product structure; any pure reflection strategy that introduces no external observation cannot change it.
- **Theorem `posterior_independent_of_mechanism`**: the posterior truth rate is independent of the complexity of the self-check mechanism — the formalization rules out the fantasy that "a stronger model can break through by introspection."

Physical Exit 0 penetration (Pattern 01) is therefore not a matter of "raising confidence," but of "the sole channel through which any evidence can be obtained."

## B.3 Axiom II: Attention Dilution (All Proven at the Formalization Layer)

Model (structure `AttentionMechanism`): the attention mass on the target token $a(\rho)$, the **total non-target mass** $b(\rho)$, and the **residual subchannel** $r(\rho)$ (fixed occupancies such as BOS / attention sink, instruction tokens, etc.), satisfying $a,b>0$, $0\le r<b$, with added redundancy not strengthening the target signal ($a(\rho+1)\le a(\rho)$) and the total non-target mass non-decreasing ($b(\rho)\le b(\rho+1)$). The attention share is $a/(a+b)$, and the retrieval signal-to-noise ratio is

$$\operatorname{snr}(\rho) := \frac{a(\rho)}{b(\rho)}.$$

**Calibration note (A2)**: the theorem premises are borne on the **total non-target mass** $b$; measurements can only tally the **filler subchannel** $\mathrm{filler} := b - r$. The relation between the two is characterized by two theorems:

- **Theorem `snr_le_proxy`**: the measured filler-caliber $a/\mathrm{filler}$ systematically **overestimates** the true $\operatorname{snr}$, by a bias factor $b/\mathrm{filler}\ge 1$ — tallying only the filler segment underestimates the severity of dilution (E3b measured overestimation of 35.8%–36.7%, in the same direction);
- **Theorem `filler_growth_not_sufficient`** (counterexample): that only the filler subchannel expands geometrically is **not sufficient** to guarantee the total-mass premise — the growth premise must be imposed on $b$; the object of the premise cannot be shifted.

**Basic dilution theorems**:

- **Theorem `attention_dilution_strict`**: fixing the target mass $a>0$, if the total mass of irrelevant context grows $b \to b' > b$, then the attention share on the target token strictly decreases: $\frac{a}{a+b'} < \frac{a}{a+b}$. Dilution is inevitable in the strict-inequality sense, not merely "may be affected."
- **Theorem `softmax_share_strictly_decreases`**: the above conclusion as an abstract instance for an arbitrary positive weight function (e.g., the softmax parameterization $w = \exp \circ \operatorname{logit}$).
- **Theorem `attention_share_dilution`**: when the total non-target mass strictly increases ($b(\rho) < b(\rho+1)$), the attention share strictly decreases — qualitative dilution is an algebraic necessity of the attention formula.

**Three corresponding theorems mapping growth laws to decay rates** (all premises are explicit structural assumptions; the measured shape is determined empirically):

- **Theorem `snr_geometric_decay`**: $b$ expands by at least a factor $(1+\gamma)$ per step ($\gamma>0$) ⟹ $\operatorname{snr}(\rho+1) \le c\cdot\operatorname{snr}(\rho)$, where $c = 1/(1+\gamma) < 1$ is a **definition**, not an independent assertion. The premise is a structural assumption about "how the attention denominator expands" (the cause); the conclusion is a quantitative bound on "how the signal-to-noise ratio decays" (the effect).
- **Theorem `snr_polynomial_decay`**: $b$ grows only linearly (increasing by at least $\delta>0$ per step) ⟹ $\operatorname{snr}(n) \le a(0)/(b(0)+n\delta)$, i.e., $O(1/n)$ polynomial decay.
- **Theorem `snr_power_decay` (power-law branch, A4)**: $b$ expands per step by at least the **exact power ratio** $((\rho+1)/\rho)^\beta$ ($\beta>0$) ⟹ power decay of the form $\operatorname{snr}(n)\le a_0/(b_0\,n^\beta)$. Supporting lemmas: `b_power_growth` (telescoping-product lemma for the chained power ratios), `snr_power_decay_relative`, `snr_power_decay_of_one_add` (the $0<\beta\le 1$ bridge via the Bernoulli inequality to the literal form $1+\beta/\rho$; the exact-power-ratio form avoids the $\rho=0$ singularity and has no constant loss when $\beta\ge1$). E3 measurements show the power-law branch dominating in 33/36 cells and the geometric branch receiving 0 votes; this branch is thereby promoted from optional to **necessary**.

`DilutionDynamics` = `AttentionMechanism` + geometric growth factor $\gamma$; the one-step decay `hdecay` is a theorem. Its consequences:

- **Theorem `snr_decay_iterated`**: by induction from the one-step geometric decay, `snr(ρ+n) ≤ c^n · snr(ρ)`.
- **Theorem `geometric_decay_strictly_decreases`**: when `snr(ρ) > 0`, geometric decay implies strict monotone decrease.
- **Theorem `violation_prob_lower_bound`**: the violation probability `P_violate(ρ) = 1 - snr(ρ)/snr(0)` satisfies `P_violate(n) ≥ 1 - c^n`, which is equivalent on $\rho \in \mathbb{N}$ to the main-text `P_violate(ρ) ≥ 1-e^{-αρ}` ($c = e^{-\alpha}$).

**Two-phase dynamics (`Axiom2_PhaseModel`, A1)**: `PhaseModel` = `AttentionMechanism` + expansion rate $\gamma$ + explicit phase-transition point $N^*$; the dilution-phase expansion law is promised only within $[0,N^*)$:

- **Theorem `snr_dilute_decay`**: the $c^n$ geometric decay bound within the dilution phase (the domain is explicitly truncated to $[0,N^*)$);
- **Theorem `snr_plateau_le`**: in the plateau phase ($n\ge N^*$), the decay does **not reverse** — $\operatorname{snr}(n)\le\operatorname{snr}(N^*)$: the engineering guarantee degrades in the saturated region to "no longer worsening," rather than to failure;
- **Theorem `violation_prob_plateau_lower_bound`**: a constant lower bound on the plateau-phase violation probability;
- **Theorem `plateau_violates_geometric_bound`** (counterexample): the global geometric bound indeed fails in the saturated region; `global_growth_recovers_decay` shows that merely restoring the global growth premise recovers the geometric bound.

**Cross-axiom interface (`Axiom2_Axiom4_Bridge`, A5 / T7)**: `InjectionCoupling` connects the memory-injection rate $\mu$ to Axiom IV through the irrelevance-to-mapping $\rho(\mu)$:

- **Theorem `violation_lower_bound_at_injection`**: at injection rate $\mu$, the lower bound on the violation probability is $1-c^{\lceil\rho(\mu)\rceil}$;
- **Theorem `injection_strengthens_lower_bound`**: the faster the injection, the tighter the lower bound (monotone amplification);
- **Theorem `violation_under_injection`**: the longitudinal-edge synthesized form; `violation_bound_beyond_plateau` gives the plateau-phase correction.

This is the longitudinal edge of the layered axiom system in which "there is no feedback between layers": the dilution dynamics of Axiom II drive the contamination-propagation lower bound of Axiom IV through the injection rate, so that the monograph is no longer a mere collection of independent models.

> Epistemological note: the formal system asserts that "for any attention system satisfying the corresponding growth law, the corresponding decay bound and violation lower bound hold"; "which branch a real Transformer satisfies" is an empirical proposition. Measurement interpretation (E3/E3b, Qwen2.5-1.5B/7B, context up to 131k, 2026-10): the power-law branch dominates (AIC 33/36 cells), the geometric branch gets 0 votes; the weak premise that $a$ is non-increasing holds directionally, while "$a$ is constant" is falsified ($\hat\beta_a<0$, CI excludes 0) — measured SNR decay is contributed jointly by numerator shrinkage and denominator expansion; the long-range "declining phase" of 7B YaRN, retested via the three-channel decomposition, is judged to be mass migration from the filler subchannel to the sink, with the total non-target mass $t=b+r$ non-decreasing throughout (the `hb_nondec` total-mass calibration survives). See Appendix B.15 and `experiments/attention_growth/EXPERIMENT_PLAN.md`.

> **Proxy exploration of decay parameters (E8, 2026-10-20, closed)**: $\gamma$ / $\beta$ are **free parameters** of the theorems; this appendix does not assume they can be predicted from structural quantities. After three cross-model-family replications (Qwen2.5-7B / 1.5B + Llama-3.2-3B, 486 rows total), none of the three candidate structural quantities (attention entropy, top-1% concentration, key effective rank) **reproduced robustly across all 3 models** — erank satisfies the criterion only on 7B, top1pct survives only on the 1.5B β̂ and 7B λ̂ estimates, and on Llama-3B none of the four structural quantities reaches |Spearman|≥0.5 with CI excluding 0 under either calibration. **γ remains a free parameter**, its value calibrated by measurement. The weak signal worth recording is **directional consistency**: entropy (−β̂/+λ̂), top1pct (+β̂/−λ̂), erank (−β̂/+λ̂) have perfectly consistent directions across the three models — the strength is unstable across scale and family, but the direction may carry mechanistic meaning. A one-off OOM incident was permanently fixed by chunking in `_gram_streamed` (peak <1 GB vs. the original 34 GB).

## B.4 Axiom III: Causal Monotonicity (All Proven at the Formalization Layer)

- **Theorem `observability_iff_mtime_strict_mono`**: for a mutation that produces a real diff, **observability ⟺ the physical clock (mtime / WAL LSN) jumps strictly monotonically**. If the clock is rolled back or stalled ($\text{mtApplied} \le \text{lastCompiledAt}$), the modification is silently swallowed by the incremental compiler (Silent Loss). "The code has changed but the tests still run on old bytecode" receives a rigorous formalization — monotonicity is not an engineering optimization but a logically necessary condition for observability.
- **Theorem `log_append_apply_idempotent`**: the replay operator of an append-only log (WAL) is idempotent — on repeated replay at the same physical instant, the second application's checksum necessarily fails, and the content fields are identical to the first application. Retries are safe and do not pollute the compiled result.

> **Measurement boundary (E-A3, 2026-10-20)**: the engineering counterparts of the two theorems above are supported by 28 controlled measurements on Cargo 1.96 (Windows NTFS) (`experiments/attention_growth/axiom3_results.json`): mtime stall / rollback ⟹ silent loss (5/5 each, artifacts retained at the old version); strict forward mtime jump ⟹ rebuild (5/5, and a pure clock jump triggers a rebuild even when the content is unchanged — rebuild triggering is determined purely by the clock channel, observability by the content diff, consistent with the split of the `hdiff` premise); idempotency holds in unchanged rebuilds (5/5 skipped, artifact sha unchanged) and in the git-rollback-retry scenario (semantic output recovered). Two model refinements: ① the criterion reference clock is measured as the "last build completion instant" $R$, and the silent-loss window is $(0, R]$, wider than the naive "file's old mtime" model — concurrent writes while a build is in progress fall naturally into the loss window; ② the Windows PE header carries a compile timestamp, so recompilation from identical source necessarily differs at the byte level, and idempotency must be interpreted at the semantic layer (the theorem promises content invariance, not bit-level equality). Applicability domain: mtime-based incremental compilers (Cargo, Make); content-hash build systems (Bazel, Nix) do not rely on mtime jumps, and the silent-loss scenario of this section does not apply to them.

## B.5 Axiom IV: The Memory-Poisoning Phase Transition (All Proven at the Formalization Layer)

Model: the cross-generation transmission of not-yet-finally-reviewed empirical assets is a branching process (structure `BranchingProcess`, one finite-support PMF per generation); the selectivity $\sigma$ of the double-blind quarantine gate compresses the nominal reproduction mean $\mu$ into the effective reproduction number $m = \mu(1-\sigma)$.

- **Theorem `expected_population_geometric`**: the expected population $E(n) = m^n E(0)$ (by induction).
- **Theorem `subcritical_expectation_vanishes`**: when $0 \le m < 1$, $E(n) \to 0$ (contraction-mapping limit).
- **Theorem `markov_inequality`** (`Probability_Markov` module): an elementary proof on finite-support PMFs that $P(X \ge 1) \le E[X]$, with zero measure-theoretic dependencies.
- **Theorem `subcritical_extinction_in_probability`**: by the Markov inequality and geometric decay, when $m<1$ the survival probability $P(Z_n \ge 1) \to 0$ — the quantitative core of the effectiveness of the quarantine promotion gate (Pattern 14).
- **Theorem `quarantine_compresses_offspring`**: the stricter the $\sigma$, the smaller the effective reproduction number; full quarantine drives it to zero.
- **Theorem `supercritical_expectation_diverges`**: when $m>1$ and $E(0)>0$, $E(n) \to +\infty$. This is the expectation-layer version of the Galton–Watson supercritical explosion theorem.
- **Theorem `galton_watson_non_extinction`** (`GaltonWatson` module): when the offspring mean $m>1$, the extinction probability $q < 1$, i.e., the lineage survives forever **with positive probability**. The proof takes the elementary route of generating-function fixed-point analysis:
  - define `genFun(s) = Σ p_k s^k`, prove it is monotone and bounded on $[0,1]$, with `genFun(1)=1`; the truncated polynomial `genFun_N` is continuously differentiable and `genFun_N'(1) → m > 1`;
  - **core lemma `exists_lt_sub_id`**: from `genFun'(1)>1` and continuity, choose a truncated polynomial `genFun_N` such that `genFun_N'(s₀)>1`; via the mean-value theorem and tail estimates, deduce the existence of $s₀<1$ with `genFun(s₀)<s₀`;
  - the extinction-probability iteration $q_n = \varphi^n(0)$ is monotonically increasing and uniformly upper-bounded by $s₀$, so its limit $q = \sup q_n \le s₀ < 1$.
- **Theorems `genFun_extinctProb_fixed` / `extinctProb_le_of_fixed` / `galton_watson_extinctProb_exact`** (exact characterization of the extinction probability): $q$ is not merely an upper bound but the **least fixed point** of $\varphi$ on $[0,1]$: $q = \varphi(q)$, and any fixed point $s\in[0,1]$ satisfies $q \le s$. The proof uses monotonicity squeezing ($q_{n+1}=\varphi(q_n)\le\varphi(q)$, taking the limit gives $q\le\varphi(q)$; polynomial truncation $\varphi_N$ is continuous, giving $\varphi_N(q)\le q$, then take $N\to\infty$), avoiding reliance on the continuity of $\varphi$ itself. In the supercritical regime $q$ is therefore fully characterized: $q = \min\{s\in[0,1] : \varphi(s)=s\} < 1$.
  With no gate ($\sigma=0$) and $\mu>1$, contaminated empirical assets not only have unbounded expected load but persist forever with positive probability — the strong-dynamics counterpart of model collapse.

> **Measurement boundary (E-A4, 2026-10-21)**: the model–reality mapping of the above theorem chain was tested in the DeepSeek-V4-Pro-0813 multi-generation memory-propagation experiment (4 conditions × 12 replicates × 6 generations = 288 sessions, with preregistered interpretation preceding the experiment): the full-quarantine case ($\sigma=1$) of `quarantine_compresses_offspring` measuredly drives the cross-generation propagation of contaminated lineages strictly to zero (all replicates $Z_1=0$, no de novo rediscovery); the geometric law of `expected_population_geometric` matches the pooled population sequence in the unquarantined condition (log-linear $R^2=0.958$, no generation-to-generation trend, branching assumption holds in the small-population regime); Galton–Watson simulations parameterized by the measured reproduction kernel (per-parent offspring PMF) agree with the theorem chain with no free parameters — the three subcritical variants (C0 measured $m=0.538$, C1 measured $m=0.333$, C0 PMF thinned by Bernoulli(0.5) to $m=0.269$) have extinction frequency $q_{sim}=1.0000=q^*$, and the `markov_inequality` bound holds numerically throughout. Two mapping boundaries are recorded faithfully: ① the compression direction of the DRAFT_SUSPECT marker gate on per-entry reproduction agrees with theory ($-38\%$) but is not statistically significant (permutation test $p=0.15$); the intermediate-$\sigma$ case of `quarantine_compresses_offspring` (the engineering counterpart of marking rather than quarantining) did not receive significant support at this sample size; ② the direct LLM-layer test of $m=\mu(1-\sigma)$ is undecidable due to write-layer fluctuations and an effective filtered-layer sample $n=1$, receiving only indirect support at the distribution layer (the thinned variant); the direct LLM-layer test of this mapping requires replicates on the order of $\ge 10^2$. Applicability domain: a single model (DeepSeek-V4-Pro-0813), the pytest test-writing task family, a selective generation-by-generation transcription protocol, and no substrate feedback ($\mathrm{SubstratePass}$ channel disabled, purely social transmission); under this protocol the no-gate condition measured $m=0.56<1$ (the transcription mechanism is itself subcritical). **Supercritical case (closed on 2026-10-22)**: the empirical counterpart of `supercritical_expectation_diverges` / `galton_watson_non_extinction` was confirmed in a memory architecture with no transcription decay (full append-only memory store, direct vector-store writes, SUPERCRITICAL plan Flash tier) — propagation in that architecture is of the **linear accumulation–capacity competition** type (per generation $W\equiv1$, $Z_{n+1}=Z_n+W$), with C0-full $\hat m=1.166$ (CI $[1.156,1.176]$) and a capacity threshold $W_c\in(8,16)$; "supercritical" here is engineering semantics (the strain pool keeps accumulating and does not go extinct), and the precise mechanism is accumulation–competition rather than the $m>1$ multiplication of branching processes; the GW theorem chain's characterization of the selective-transcription regime is unchanged. Data and interpretation: `experiments/attention_growth/axiom4_results.json`, `axiom4_gw_sim.json`, `EXPERIMENT_PLAN_AXIOM4.md` §9, `EXPERIMENT_PLAN_AXIOM4_SUPERCRITICAL.md` §8.

## B.6 Theorem 3.1: Convergent Causal Invariance (All Proven at the Formalization Layer)

**Sufficiency (proven)**:

- **Theorem `lyapunov_finite_hitting`**: if the energy function $V : S \to \mathbb{N}$ has strictly negative drift everywhere ⟹ the zero point is hit in at most $V(s_0)$ steps (all physical contracts satisfied). This is the discrete-deterministic core of the Foster–Lyapunov criterion, completed by induction.
- **Theorem `foster_lyapunov_deterministic_bound`**: for a real-valued energy $V : S \to \mathbb{R}_{\ge 0}$, if every step drops by at least $\delta$ whenever $V \ge \delta$ (strong drift $V(\text{step}\,s) \le V(s)-\delta$), then the number of steps $t$ to hit the $\delta$-neighborhood satisfies $t \cdot \delta \le V(s_0)$, i.e., $t \le V(s_0)/\delta$.
- **Theorem `zero_energy_is_fixed`**: a zero-energy fixed point ⟹ the converged state is preserved forever.

**Necessity (three proven counterexamples)**:

1. **Breaking observability** (`no_observability_absorbs_falsified`): the system enters a falsified-pass absorbing state in one step and stays there forever;
2. **Breaking locality** (`no_locality_two_cycle` + `no_locality_defeats_lyapunov`): the system enters a 2-cycle orbit, and **no** energy function can be strictly decreasing everywhere — oscillation cannot be tamed by Lyapunov methods;
3. **Breaking evaluation decoupling** (`coupled_evaluation_tautological_fixed_point`): the evaluator copies the solver's output, forming a self-referential fixed point that converges to a degenerate trivial solution.

**Confluent statement `causal_invariance_abstract`**: the conjunction of sufficiency and the three necessity counterexamples.

> **Measurement boundary (E-B6, 2026-10-21)**: sufficiency was verified across 12 controlled simulations ($V_0 \in \{10,50,100,500\}$, $\delta \in \{0.5,1,2\}$); under the strong-drift condition the convergence steps satisfied $t \le V_0/\delta$ throughout; the three necessity counterexamples were each reproduced in $10^4$ simulations: breaking observability $\Rightarrow$ falsified-pass absorbing state (100%), breaking locality $\Rightarrow$ 2-cycle oscillation with Lyapunov impossibility (100%), breaking evaluation decoupling $\Rightarrow$ self-referential degenerate fixed point (100%). Data: `experiments/attention_growth/b6_causal_invariance_sim.json`.

> The expected stopping-time bound for the stochastic case is in B.7.

---

## B.7 Stochastic Foster–Lyapunov Expected Stopping-Time Bounds (All Proven at the Formalization Layer)

The `StochasticFosterLyapunov` module gives expected hitting-time bounds for stochastic controllers by **elementary methods** (stochastic kernel + stopping-time truncation + monotone induction, with no measure theory / martingale optional-stopping-theorem dependencies).

Model: `StochasticKernel S` is a stochastic transition kernel on state space $S$ (`k x A` denotes the probability of landing in set $A$ in one step from $x$, finite support); the `HasStrongDrift` structure supplies a Lyapunov function $V:S\to\mathbb{R}_{\ge0}$, a drift constant $\delta>0$, and a threshold $b\ge0$, satisfying $\mathbb{E}_{k(x)}[V] \le V(x)-\delta$ whenever $V(x)\ge b$.

- **Theorems `stoppedValue_le_V` / `stoppedTime_le_value`**: the value and stopping time of the truncated stopping-time process are uniformly controlled by the initial energy (induction core).
- **Theorem `stoppedTime_uniform_bound`**: the expectation of the truncated stopping time $\tau_N$ satisfies $\mathbb{E}[\tau_N] \le V(x_0)/\delta$, uniformly over all truncation levels $N$.
- **Theorem `foster_lyapunov_expected_hitting`** (main theorem): taking the truncation limit, the expected stopping time to stochastically hit $\{V<b\}$ satisfies $\mathbb{E}[\tau] \le V(x_0)/\delta$.

Hence the deterministic `foster_lyapunov_deterministic_bound` becomes a special case of this stochastic theorem; the convergent causal invariance of §3.3 acquires a complete expected-stopping-time quantitative bound at the stochastic-control layer.

> **Measurement boundary (E-B7, 2026-10-21)**: the main bound $\mathbb{E}[\tau] \le V(x_0)/\delta$ was verified across 27 Monte Carlo simulations ($V_0 \in \{10,50,100\}$, $\delta \in \{0.5,1,2\}$, noise $\sigma \in \{0,0.1,0.3\}$, $10^5$ runs each), all satisfied; the uniform boundedness of the expected truncated stopping time $\tau_N$ holds for $N \in \{10,50,100,500\}$. Data: `experiments/attention_growth/b7_foster_lyapunov_sim.json`.

---

## B.8 Pattern-Level Formal Anchor: The Lease Lock (All Proven at the Formalization Layer)

The `Pattern10_LeaseLock` module formalizes the concurrency claims of Pattern 10 (distributed substrate lease lock and watchdog). Model: the physical clock is a discrete tick; the lock state is `LockState = Option Lease` (the `Option` structure itself encodes "at most one lease"); `acquire`/`heartbeat` are pure functions with preconditions.

- **Theorem `canWrite_unique`** (mutual-exclusion safety): at any instant at most one agent holds write permission — two writers must be the same agent, so concurrent write-write conflicts (failure scenario A) are impossible within the protocol.
- **Theorems `acquire_rejected_of_live` / `acquire_succeeds_only_when_dead`**: an acquire while a lease is alive is necessarily rejected; grant occurs only when no lease is alive.
- **Theorem `no_permanent_lockout`** (watchdog liveness): for any lock state there exists a time $T$ ($=$ expiry instant $+1$) after which any `acquire` succeeds — the orphan lease of a crashed holder is necessarily reclaimed after TTL expiry, so permanent lockout is engineering-impossible (formal negation of failure scenario B); downtime is bounded.
- **Theorem `not_canWrite_of_expired`**: after expiry, the original holder's write permission is extinguished; a lease does not retain residual privilege from historical holding.
- **Theorems `heartbeat_by_nonholder_unchanged` / `heartbeat_by_holder_extends`**: a heartbeat by a non-holder is rejected and the state is unchanged; a holder's renewal does not shorten the lease (renewal-side protection against failure scenario C).

> **Measurement boundary (E-B8, 2026-10-21)**: the five core properties were each verified in $10^4$ discrete-clock state-machine simulations, all passing — mutual-exclusion safety (at most one writer at any instant), watchdog liveness (a crashed holder's lease is necessarily reclaimed at TTL+1), post-expiry write-permission extinction, heartbeat protection (non-holder rejection, holder renewal does not shorten), and impossibility of concurrent write-write conflicts (5 agents, 100 ticks, random contention). Data: `experiments/attention_growth/b8_lease_lock_sim.json`.

---

## B.9 Pattern-Level Formal Anchor: Single-Writer Causal Order in Primary-Writer/Replica-Reader (All Proven at the Formalization Layer)

The `Pattern11_PrimaryWriter` module formalizes the concurrency claims of Pattern 11 (primary-writer / replica-reader degraded mutual exclusion). Model: the write journal is `List (Write Agent)`, each element carrying its writer and physical tick; `ChainValid` requires adjacent ticks to be strictly increasing; the read view `viewAt l t` is the prefix of the journal filtered by `tick ≤ t`.

- **Theorem `eq_of_mem_of_tick_eq`**: no two distinct events in a valid journal share the same tick — equal ticks mean the same event.
- **Theorem `writer_unique_per_tick`**: write events at the same tick have the same writer, so concurrent write-write conflicts are impossible under the primary-writer/replica-reader protocol.
- **Theorem `writer_unique_of_lease`**: this conclusion follows directly from `Pattern10.canWrite_unique` — "single writer" is not an additional convention but a corollary of lease mutual exclusion.
- **Theorems `view_mono` / `no_lost_write`**: a later read contains all events of an earlier read; any committed write event whose tick is no later than the read instant is necessarily visible. The replica reader therefore reads a **complete prefix**, with no "skipping middle commits" view.

---

## B.10 Pattern-Level Formal Anchor: Stability of the Observation–Learning Loop (All Proven at the Formalization Layer)

The `Pattern23_24_ProductionLoop` module closes the "Pattern 23→24→23 negative-feedback loop" left open in §7 of the validation report. Model: a defect stock $x\in\mathbb N$; each cycle one defect is detected and repaired with probability $q$ ($x\mapsto x-1$), otherwise one is injected ($x\mapsto x+1$); the transition kernel `loopKernel q` is a finite-support stochastic kernel that directly reuses the Foster–Lyapunov framework of B.7.

- **Theorem `T_id_pos`**: when $x\ge 1$, the one-step expected stock satisfies $\mathbb E[x'\mid x]=x+1-2q$.
- **Theorem `hasStrongDrift`**: if $q>1/2$, taking $V(x)=x$, $b=1$, $\delta=2q-1>0$, the strong-drift condition holds.
- **Theorem `loop_return_bound`**: the expected time for the loop to hit "stock $<1$" satisfies $\mathbb E[\tau]\le x_0/(2q-1)$ — the observation–learning closed loop is exponentially recoverable when $q>1/2$.
- **Theorem `no_drift_below_half`** (critical negative result): if $q\le 1/2$, then $\mathbb E[x'\mid x]\ge x$, and $V=\mathrm{id}$ does not constitute a Lyapunov function. Hence $q>1/2$ is a **necessary threshold within the model**; the "detection rate $\ge0.90$" in the Pattern 23 document should be read as engineering margin above this threshold, not as an optional performance metric.

> **Status of the conclusion**: this module gives a stability criterion **within the model** (single defect class, single-step injection/repair, i.i.d. detection). It does not cover multi-defect-class coupling, batch injection, or detection-rate variation with stock, which remain the unverified extrapolations declared in §7. Meanwhile, the measured value of $q$ is supplied by production field experiment H1 (2026-10-22): fixed-threshold defects (pool/p99) have $q=1.00$, satisfying the $q>1/2$ threshold; the mem adaptive-σ criterion does not satisfy it due to threshold drift, which is a criterion-shape boundary.

---

## B.11 Pattern-Level Formal Anchor: The Reviewer Reality-Audit Veto Power (All Proven at the Formalization Layer)

The `Pattern02_RealityAudit` module rigorously implements the formalization claims of Pattern 02 (the reviewer reality-audit veto pattern). Model: the deliverable `Deliverable` contains four physical Boolean criteria (physical source diff, compile-time physical plausibility, anti-self-reference mock check, isolated-environment homogeneity); the reality auditor `realityAudit` constructs a four-fold conjunction filter; the admission function `admissionVerdict` requires both that the reality audit passes and that the Rubric score reaches a threshold.

- **Theorem `veto_overrides_high_score`** (absoluteness of the veto power): if the reality audit fails, no matter how high the subjective or Rubric score (even as high as the full 9 points), the admission verdict is necessarily false.
- **Theorem `tautology_vetoed`** (hard block against self-referential cheating): if a test assertion is self-referential echo-cheating (`isTautological = true`), the reality audit necessarily fails and the deliverable is necessarily vetoed.
- **Theorem `substrate_missing_vetoed`** (hard block against missing physical substance): if no substantive business-code change is produced (`hasPhysicalDiff = false`), the deliverable is necessarily vetoed.
- **Theorem `four_pillars_soundness_and_completeness`** (full sufficiency-and-necessity of the four pillars): admission holds if and only if all four physical hard criteria and the score threshold hold simultaneously.

---

## B.12 Pattern-Level Formal Anchor: Tainted-Contamination Defense and Lineage Tombstoning (All Proven at the Formalization Layer)

The `Pattern15_RevocationTombstone` module formalizes the dynamic auto-immunity claims of Pattern 15 (tainted-contamination defense and anti-degradation). Model: the pattern lifecycle is a three-state machine (draft `draft`, promoted `promoted`, tombstone `tombstone`); the knowledge base is a list of patterns; the retrieval projection operator admits only patterns in the `promoted` state; a revoke operation automatically synthesizes a reverse auto-immunity rule set.

- **Theorem `tombstone_absorbing`** (terminal absorbing nature of the tombstone state): the tombstone state is a terminal absorbing state of the state machine; no subsequent state transition can escape it.
- **Theorem `tombstone_never_projectable`** (safety of dynamic projection isolation): a pattern in the tombstone state can never appear in any context retrieval projection slice.
- **Theorem `immunity_blocks_taint`** (reverse auto-immunity blocking theorem): the reverse auto-immunity rule set automatically synthesized from a tombstoned pattern blocks, 100% mechanically, any candidate-pattern generation carrying the same taint signature.
- **Theorem `revoke_produces_tombstone`** (revoke necessarily enters the tombstone state): after a revoke operation, the target pattern is necessarily in the tombstone state in the knowledge base.
- **Theorem `revoked_excluded_from_projection`** (atomic immediate invalidation on revoke): after executing `revokePatternInKB`, the target pattern is atomically set to tombstone and immediately disappears from all task projection views.
- **Theorem `tombstone_offspring_zero`** (generation-propagation cutoff): the effective reproduction mean of a tombstoned pattern is strictly zero, and branching-process offspring are immediately zero in the next generation.

---

## B.13 Pattern-Level Formal Anchor: Task-Level Least-Privilege Context Projection (All Proven at the Formalization Layer)

The `Pattern04_PoLPProjection` module rigorously implements the formalization claims of Pattern 04 (task-level least-privilege context projection pattern).

Model: the task-context environment partitions the effective target mass $a>0$, the task-necessary background mass $b_T>0$, and the external global redundancy mass $b_{ext}\ge0$; the projection operator $\mathrm{projectPoLP}$ truncates away the external redundancy mass ($b_{ext}\mapsto 0$). The signal-to-noise ratio is defined as $\mathrm{snr}(a, b) = a/b$, and the out-of-bounds-code violation probability as $P_{\mathrm{violate}}(a, b) = 1 - a/(a+b)$.

- **Theorem `polp_preserves_snr_strictly`** (least-privilege projection fidelity theorem): if non-zero external redundant context exists ($b_{ext}>0$), then after least-privilege projection the task retrieval signal-to-noise ratio is strictly greater than the full unprojected SNR: $\mathrm{snr}(a, b_T) > \mathrm{snr}(a, b_T + b_{ext})$.
- **Theorem `polp_strictly_reduces_violation_risk`** (out-of-bounds violation-probability reduction theorem): least-privilege projection strictly reduces the model's attention degradation and out-of-bounds code-tampering risk: $P_{\mathrm{violate}}(a, b_T) < P_{\mathrm{violate}}(a, b_T + b_{ext})$.
- **Theorem `polp_monotone_nesting`** (privilege-nesting monotonicity theorem): the tighter the projection slice ($b_1 \le b_2$), the monotonically lower its violation-risk upper bound.

---

## B.14 Supplement to Theorem 3.1: Limit-Cycle Oscillation and Lyapunov-Contract Residual Stopping-Time Fuse (All Proven at the Formalization Layer)

The `Theorem3_1_LyapunovFuse` module supplements Theorem 3.1 with the stopping-time bounds of Appendix B.7.

Model: an energy-residual trajectory $V: \mathbb{N} \to \mathbb{R}_{\ge 0}$, one-step drift $\Delta V(t) = V(t+1) - V(t)$; the stall criterion is $\Delta V(t) \ge 0$. The Lyapunov-contract residual stopping-time fuse hard-trips after $k$ consecutive steps with no negative drift (consecutive stall).

- **Theorem `consecutive_stalls_accumulate`** (consecutive-stall energy-accumulation lemma): if from time $t$ onward the drift is non-negative for $k$ consecutive steps, then the energy at time $t+k$ is necessarily no lower than the energy at time $t$: $V(t+k) \ge V(t)$.
- **Theorem `cycle_defeats_strict_lyapunov`** (nonexistence of a strict Lyapunov energy function excluding periodic limit cycles): for any nontrivial limit cycle $s_{t+k} = s_t$ of period $k\ge 1$, there exists no Lyapunov supermartingale energy function that is strictly decreasing everywhere; eliminating oscillation must rely on an external fuse to break the limit cycle.
- **Theorem `fuse_halts_divergence_at_k`** (stopping-time-fuse resource-boundedness theorem): the Lyapunov-contract residual fuse strictly truncates the number of consecutive ineffective self-healing retries to within a constant upper bound $k$, thoroughly eliminating infinite loops and token black holes.

---

## B.15 Empirical Boundary Declarations Relative to the Main Text

The formalization covers the **dynamical properties of the abstract control model**. Across the entire Lean codebase of the project: **0 axioms, 0 sorry**.

The following are intrinsically non-formalizable; they exist as premises of conditional theorems or as empirical propositions, and the book does not dress them up as proven:

1. The irrelevance-mass growth law of the Transformer attention mechanism and the strength of its premises (the premises of the growth branches in B.3) — "which branch a real system satisfies" is an empirical proposition. Measurement boundary (E3/E3b, Qwen2.5-1.5B/7B, ρ≤131k, 2026-10): the power-law branch dominates and the geometric branch is rejected; the weak premise `ha_nonincr` ($a$ non-increasing) holds directionally, while the strong hypothesis "$a$ is constant" is falsified; the total non-target mass $t=b+r$ is non-decreasing throughout (`hb_nondec` survives), and the long-range fallback of the filler subchannel is judged to be sink migration; when the main text cites measured SNR, the three-channel calibration (target / filler / sink) must be used, and the filler-caliber SNR systematically overestimates by 35.8%–36.7% (`snr_le_proxy`). **Transmission boundary of the violation probability (E4, 2026-10-20)**: `violation_prob(ρ) = 1 - snr(ρ)/snr(0)` is the relative loss of the signal-to-noise ratio, **not** the task-failure probability. The E4 end-to-end experiment (Qwen2.5-1.5B/7B needle-retrieval accuracy aligned with E3 SNR) shows a compensation threshold $W^*$ between the two: at 7B the SNR has already lost 44% at 131k while task accuracy remains 100%; at 1.5B accuracy drops steeply from 100% to 70% over ρ∈[32k,64k]. The violation lower bound $P_{\text{violate}} \ge 1 - c^n$ transmits to an observable task failure only when $\rho > W^*$. $W^*$ is positively correlated with model capability ($W^*_{1.5\text{B}} \approx 32\text{k–64k} < W^*_{7\text{B}} > 131\text{k} < W^*_{\text{Kimi}} \ge 1\text{M}$); it is an empirical parameter and is not written into the formal interface. Applicability domain: Qwen2.5-family models, needle-type retrieval tasks, F1–F3 filler; extrapolation across model families and to real engineering workloads is unverified;
2. **The model–reality calibration mapping** (through which all empirical citations of the B.3 theorems pass): the theorem's $a$ is the attention mass on a **single target token**, while the experiment's $a$ is the total mass of the **entire needle segment**; the theorem's $b$ is the **total non-target mass**, while the experiment's $b$ is the total mass of the **filler segment** ($\mathrm{filler}=b-r$). These two mappings are unproven assumptions — their validity is partially endorsed by the residual-channel drift test of E3b (significant drift in $r$ has triggered preregistered item 3, so the three-channel calibration is required, not optional), but "whole-segment mass approximating single-token behavior" has no independent test; when citing measured data in support of the theorem narrative, this declaration must be given alongside it;
3. The incidence rate of reward hacking by a specific large model on a specific task (the Chapter 2 game-theoretic analysis gives strategy existence, not incidence);
4. The measured distribution of contract violations in industrial engineering.

What the formal proofs guarantee is this: **under the given premises (independence assumptions, growth laws, etc.), the causal structure asserted by the four axioms and by Theorem 3.1 holds logically**.

---

## B.16 Reproduction Instructions

```powershell
cd formal_proof/IACFormalization
lake build        # full kernel verification
lean src/IACFormalization/Axiom1_Grounding.lean   # single-file check
```

Dependencies: the machine's shared prebuilt mathlib4 package (referenced by absolute path in `lakefile.lean`); zero-sorry policy — any occurrence of `sorry` is treated as a build defect.
