# §10 Limitations and Future Work (English, for manuscript-en.md)

> Status: **translated v1** (2026-10-22).

---

## 10.1 Model Heterogeneity of the Marking-Gate Effect

The Pro-tier marking gate is directionally negative (C1/C0 ratio 0.529, $p=0.15$, underpowered $n=12$), while the Flash tier shows zero compression ($p=0.69$, $n=48$ adequately powered). The cause of the directional disagreement is unattributed: it may be model differences in adherence to soft signals (DRAFT_SUSPECT markers) or task-family modulation. **Future work**: cross-model paired comparison of marker-adherence rates under the same protocol.

## 10.2 Dual-Strain Event Multiplication Failure

The H1AC P2 strain barely propagates ($\mu\approx0.001$)—the model did not adopt P2's event channel, and the "event-density multiplication" design goal was not achieved. P1's 48/64 sample size already far exceeds the main experiment, but the statistical design of dual-strain interaction needs reconstruction (e.g., stronger event signals).

## 10.3 Statistical-Unit Lesson

The H1AC pooled per-parent criterion fails under C2 due to survivor bias (final-generation survival only 6%, pooled ratio 1.017 meaningless)—switched to chain mean and recorded in plan §9. Lesson: the judgment unit of propagation experiments must be fixed at pre-registration; B-H1c's CI lower bound slightly out (0.017) likewise suggests that boundary criteria need more conservative definitions or larger samples. The COMPLEMENT-EXP experiments also required two criterion corrections (EXP-A gain judged as "no accumulation propagation"; EXP-B's $W_c$ redefined as the first tier with survival ≥0.5), both recorded in plan §8—when pre-registered criteria conflict with mechanism facts, corrections must be traceable, never silently moved goalposts.

**Sensitivity of the EXP-B $W_c$ criterion (threshold 0.5 → 0.8)**: re-judging on the available data, $W_c(b)$ becomes $b{=}1\to(4,8)$, $b{=}2\to\le4$, $b{=}3\to(4,8)$, $b{=}5\to(8,12)$—the qualitative "$b$ up → $M_c$ up" conclusion is preserved at threshold 0.8; only the $b{=}1$ tier shifts from "$\le4$" to "$\in(4,8)$" ($W{=}4$ survival 0.50 sits exactly on the threshold boundary), leaving the direction conclusion unaffected. After extending the $b{=}3$ tier's $W{=}8$ to 12 chains, survival is 0.92 (passes both thresholds), and the split from the main protocol at $W{=}8$ (§6.5) persists after extension—an execution-protocol difference, not a threshold choice.

## 10.4 Residual Open Items of Quarantine Cost and Capacity Jointness

The supplementary experiments (EXP-A/B, Flash) close the quantitative gaps in quarantine cost (σ=1 utility retention 0.88) and $M_c$ jointness ($(b,M)$ joint function); after the 2026-10-23 middle-tier complement ($\sigma_{\rm eff}\in\{0.75,0.9\}$), the σ sweep covers the full measured spectrum $\sigma_{\rm eff}\in\{0.1,0.25,0.5,0.75,0.9,1.0\}$ with no sweet spot (A-H4). Residual open items remain:
- the quarantine cost is measured only on the memory-stock side (utility retention); the task-completion side (test_code_len) is not separately analyzed—the 0.88 retention does not cover the downstream-task impact of missing benign experiences under quarantine; finer σ tiers ($\sigma_{\rm eff}\in(0.9,1)$) are unmeasured;
- the $b\in\{1,2,3,5\}$ surface covers only four write-rate tiers; the retrieval-strategy dimension is unscanned ($M_c$'s drift with retrieval strategy remains open);
- the non-monotonic anomaly of the capacity surface ($b=2, W=4$ survival 1.00) is under-sampled (6 chains) and unattributed;
- **the $W{=}8$ split is attributed (2026-10-23 same-day rerun control, §6.5): it is not a protocol difference but cross-batch drift in DeepSeek-V4.1-Flash-1017's poison-transcription behavior** (the 10-22 batch transcribed significantly less, Fisher $p{=}0.0024$ vs all 10-23 data). Residual open item: no predictive model exists for the uncontrollable batch/API-session sensitivity of poison transcription rate (10-22: 2.00 poison writes/chain vs 10-23: 5.0–6.75; $W{=}8$ survival follows 0↔0.58–0.92); cross-batch absolute $M_c$ readings are marked batch-sensitive, while within-batch comparisons are unaffected.

## 10.5 Two-Layer Connection Not Theorized

The quantitative connection between the production engineering loop (promotion/blocking/leakage, five-fold physical criteria, §2.3) and the theoretical channel (purely social propagation, $\hat m$)—the coupling of the engineering-side $q$ loop to the theoretical $\hat m$—is not yet theorized; this paper does not claim the engineering loop is evidence for the theoretical channel. **First-priority future work**: a coupling model of the two-layer channels.

## 10.6 Ecological Validity

The main evidence is concentrated on the test-writing task family; across task families, only the quarantine guarantee has generalization evidence (48/48 chains); the multiplicative law and capacity criticality have not been tested across families. The vector-store direct-write architecture is not isolated as an experiment (full-append is used as a proxy).

## 10.7 Other

- Model-tier time snapshots: DeepSeek-V4.1-Flash-1017 was released on 2026-10-17, and all SUPERCRITICAL and H1AC experiments were executed within 5 days of release (2026-10-22), COMPLEMENT-EXP within 6 days (2026-10-23; per-batch run timestamps in Appendix A); drift of the conclusions to newer model generations is unverified;
- Sampling temperature 0.7 fixed; the effect of sampling temperature on $w_n$ is not scanned;
- Judgment scripts depend on deterministic reshuffle seeds; cross-platform floating-point differences are untested.
