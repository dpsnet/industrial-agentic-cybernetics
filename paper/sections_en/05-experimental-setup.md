# §5 Experimental Setup (English, for manuscript-en.md)

> Status: **translated v1** (2026-10-22); single source of facts: `experiments/attention_growth/*_judgement*.json`, `EXPERIMENT_PLAN_AXIOM4_*.md`.

---

## 5.1 Pre-registration Principle

All criteria were fixed before the experiments (hypothesis list in §3.5): significance threshold ($p<0.05$ permutation/one-sided), judgment unit (chain mean vs. pooled; §5.5), and directional claims are declared in advance. Plan documents are archived with the judgment artifacts (`EXPERIMENT_PLAN_AXIOM4_SUPERCRITICAL.md`, `EXPERIMENT_PLAN_AXIOM4_H1AC_BOOST.md`); any criterion revision is recorded in §9 (e.g., the invalidation of the H1AC pooled criterion).

## 5.2 Model Tiers

| Tier | Model | Use |
| :--- | :--- | :--- |
| Main | **DeepSeek-V4-Pro-0813** (abbrev. Pro; sampling temperature 0.7) | selective protocol, 4 conditions × 12 sessions × 6 generations = 288 sessions |
| Cross-model | Kimi `kimi-for-coding` + same Pro protocol | X-H1/X-H4, 288 sessions |
| SUPERCRITICAL | **DeepSeek-V4.1-Flash-1017** (abbrev. Flash) | full-append / capacity tiers / selective control (deviation from the pre-registered model tier recorded in plan §9) |
| H1AC | same as Flash | 160-chain dual-strain large sample |
| COMPLEMENT-EXP | same as Flash | quarantine-cost σ sweep (EXP-A 240) / $b\times M$ capacity surface (EXP-B 144) / selective extension n=12 (EXP-C) |

## 5.3 Propagation Protocol

- **Standardized poison injection**: at generation 0, inject 1 seed experience carrying a lineage marker (P1/P2); transcription generation by generation (selective: only entries judged relevant are transcribed; full-append: all entries are appended);
- **Lineage tracking**: every memory entry carries a lineage marker; $Z_n$ = number of poison-lineage entries at generation $n$ (judgment unit);
- **Double-blind filtering (DRAFT_SUSPECT)**: the marking-gate condition (C1) tags suspected entries without blocking; the quarantine gate (C3/C2) physically blocks un-adjudicated entries (i.e., entries that have not passed the five-fold physical criteria and independent-review final adjudication; definition in §2.3).

## 5.4 Condition Matrix

- **selective**: C0 (no gate) / C1 (marking gate) / C2 (random filtering $\sigma=0.5$) / C3 (quarantine $\sigma=1$);
- **full-append**: C0-full / C1-full / C3-full (12 sessions × 8 generations each); capacity tiers $M=8$ / $M=32$ (6 sessions × 8 generations each); selective control (2 sessions × 6 generations);
- **H1AC (Flash, dual-strain)**: C0 (48) / C1 (48) / C2 (64), 6 generations.

**846 agent-session chains in total** (= main 48 + cross-model 48 + cross-task-family 144 + SUPERCRITICAL 50 + H1AC 160 + COMPLEMENT-EXP 396; session-generation units 5,448 = 288 + 288 + 864 + 384 + 960 + 2,664; the selective control, 2 chains × 6 generations = 12 units, is excluded from and additional to the total). Of these, SUPERCRITICAL 50 chains = 3 conditions × 12 chains × 8 generations (C0/C1/C3-full) + 2 sensitivity tiers × 6 chains × 8 generations (W=8/32); H1AC 160 chains = C0 48 + C1 48 + C2 64, × 6 generations; cross-task-family 144 chains × 6 generations; COMPLEMENT-EXP 396 chains = EXP-A 240 (σ sweep, 5 tiers × 48 chains, × 6 generations) + EXP-B 144 ($b\times M$ surface, 24 tiers × 6 chains, × 8 generations) + EXP-C 12 (selective extension, × 6 generations), reproducible via `kimi_boost_judge.py`. **Timeline**: DeepSeek-V4.1-Flash-1017 was released on 2026-10-17; all SUPERCRITICAL and H1AC experiments were executed and judged within 5 days of release (2026-10-22), and the COMPLEMENT-EXP experiments within 6 days (2026-10-23; per-batch run timestamps in Appendix A).

## 5.5 Judgment Criteria

- bootstrap CI ($10^4$ resamples) for $\hat m$ and ratio CIs; sign-flip paired permutation ($10^4$) for the marking-gate paired difference;
- **chain mean vs. pooled**: the judgment unit for propagation experiments is the chain mean (per-parent pooling fails under C2 due to survivor bias—final-generation survival only 6%, pooled ratio 1.017 meaningless; recorded in plan §9, switched to chain mean);
- geometric-law re-check: log-linear fit $R^2$;
- **power** (Pro-tier marking gate): paired difference $d=0.167$, $sd=0.432$, C1/C0 ratio 0.529 → current $n=12$ power 0.38; $n\approx48$ needed for power 0.8 (`e_power_markgate.py/.json`)—the H1AC tier closes this gap with 48 pairs.

## 5.6 Reproducibility

- Judgment scripts: `e_supercritical_judge.py`/`judge2.py`/`sh3.py`, `e_cross_task_judge.py`, `e_h1ac_judge.py` (all in git);
- Raw sessions: `axiom4_results_*.json` (SUPERCRITICAL/H1AC/cross-model/cross-task complete, in git);
- Environment: fixed model tiers, sampling temperature 0.7, sampling parameters archived per session.
