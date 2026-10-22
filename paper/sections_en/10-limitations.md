# §10 Limitations and Future Work (English, for manuscript-en.md)

> Status: **translated v1** (2026-10-22).

---

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

- Model-tier time snapshots: DeepSeek-V4.1-Flash-1017 was released on 2026-10-17, and all SUPERCRITICAL and H1AC experiments were executed within 5 days of release (2026-10-22; per-batch run timestamps in Appendix A); drift of the conclusions to newer model generations is unverified;
- Sampling temperature 0.7 fixed; the effect of sampling temperature on $w_n$ is not scanned;
- Judgment scripts depend on deterministic reshuffle seeds; cross-platform floating-point differences are untested.
