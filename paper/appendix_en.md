# Appendix (English, for manuscript-en.md)

> Status: **translated v1** (2026-10-22); single source of facts: `experiments/attention_growth/` judgment artifacts.

---

## A. Judgment Scripts and Data Inventory

**Judgment scripts** (all in git):

| Script | Output | Use |
| :--- | :--- | :--- |
| `e_supercritical_judge.py` / `judge2.py` | `e_supercritical_judgement2.json` | SUPERCRITICAL tier: propagation ratio $\hat m=\sum Z_{n+1}/\sum Z_n$/CI, Z trajectory, survival, capacity sensitivity |
| `e_supercritical_sh3.py` | `e_supercritical_sh3.json` | per-generation offspring check (S-H3 falsification mechanism evidence) |
| `e_cross_task_judge.py` | cross-task-family judgment JSON | T-H1/T-H4 |
| `e_h1ac_judge.py` | `e_h1ac_judgement.json` | H1AC: B-H1a/B-H1c/B-H2 (bootstrap/sign-flip 10⁴) |
| `e_power_markgate.py` | `e_power_markgate.json` | power analysis (min_n=48) |

**Raw sessions** (all in git): `axiom4_results_supercritical*.json` (C0/C1/C3-full, W8/W32, w1–w4 shards), `axiom4_results_flash_selective_ctrl.json`, `axiom4_results_h1ac_*.json` (C0/C1/C2/smoke), cross-model/cross-task-family session JSONs.

**Pre-registration plans**: `EXPERIMENT_PLAN_AXIOM4_SUPERCRITICAL.md`, `EXPERIMENT_PLAN_AXIOM4_H1AC_BOOST.md` (judgment back-fill and criterion-revision records in §10).

**Execution environment**: DeepSeek-V4.1-Flash-1017 (abbrev. Flash; scnet-flash gateway, sampling temperature 0.7); the deviation of the model tier from the pre-registered DeepSeek-V4-Pro-0813 (Pro) tier is recorded in SUPERCRITICAL plan §10.

**Run timestamps** (result-file mtime): 2026-10-22 batch—selective control 15:24, **C0-full 15:30 (poison writes 0.917/gen, high-transcription state)**, W32 15:52, **W8 16:02 (poison writes 0.25/gen, low-transcription state)**, C3-full 16:18, C1-full 16:20, H1AC C1 19:45/C0 19:49/C2 20:09; 2026-10-23 batch—COMPLEMENT-EXP (kimi_boost A/B/C shards) 2:05–10:40, σ sweet-spot complement 12:26–12:35, W8 attribution reruns (main protocol 13:46 / EXP-B 13:43), probe calibration 15:02–15:30 (8/8 $p_{\rm probe}{=}1.000$). **Key pair (sub-hourly state-flip evidence, §6.5)**: C0-full (15:30, high-transcription state) and the W8 original batch (16:02, low-transcription state) flip within ~32 minutes on the same calendar day—a fixed checkpoint's poison-transcription propensity drifts bimodally at sub-hourly scale rather than as a day-level batch difference; all within 6 days of the V4.1-Flash-1017 release (10-17).

## B. Key Values from Judgment JSONs (same source as the main text)

| Quantity | Value | Source |
| :--- | :--- | :--- |
| C0-full propagation ratio $\hat m^\dagger$ | 1.166, boot95 [1.156,1.176] (GW semantics for Mechanism A only) | e_supercritical_judgement2 |
| C0-full Z trajectory | [1,2,2.917,3.917,3.917,4.917,4.917,4.917] | same |
| C0-full mem trajectory | [6,9,12,15,16,16,16,16] (saturated at g4) | same |
| C1-full propagation ratio $\hat m^\dagger$ | 1.165 ([1.163,1.167]) | same |
| C3-full | mem constant 6, Z constant 1 (12/12) | same |
| W=8 | $\hat m^\dagger$=0.829 ([0.739,0.875]), g7 survival 0 | same |
| W=32 | $\hat m^\dagger$=1.25, Z=[1..8], mem→27 | same |
| S-H3 mechanism evidence | $w_n\in\{0,1\}$, pmf=[0,1], chain mean $E[w_n]$=0.917, criterion pass=False | e_supercritical_sh3 |
| B-H1a | $\bar d$=+0.0201, 15/48 positive, p=0.6918 | e_h1ac_judgement |
| B-H1c | $\hat r$=0.4661, CI [0.3331,0.6017], point ✅ CI ⚠️ | same |
| B-H2 | R²=0.9233, slope −0.086 | same |
| μ chain mean | C0=0.905 / C1=0.885 / C2=0.422 | same |
| Final-generation survival | C0=0.750 / C1=0.729 / C2=0.062 | same |
| Power | n=12→0.379, n=48→0.848, min_n=48 | e_power_markgate |
| Main-experiment effect size | pair_diff=0.167, sd=0.432, C1/C0=0.529 | same |

## C. Judgment Unit and Criterion Statement

- Judgment unit: **chain mean** (H1AC); SUPERCRITICAL uses chain-mean Z/survival;
- The pooled criterion fails under C2 due to survivor bias (final-generation survival only 6%, pooled ratio 1.017 meaningless)—switched to chain mean and recorded in plan §10;
- Bootstrap / sign-flip permutations 10⁴ each; B-H1a is judged on replicate-level chain-mean paired differences (§5.5 judgment criteria).
