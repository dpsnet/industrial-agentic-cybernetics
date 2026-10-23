# §9 Mechanism Revision Narrative (English, for manuscript-en.md)

> Status: **translated v1** (2026-10-22).

---

## 9.1 Pre-registered Hypothesis

The experimental plan pre-registered: poison propagation under full-append without a gate follows a **Galton-Watson branching process** (S-H3): offspring counts expand with the parent population, $E[Z_{n+1}\mid Z_n]=\hat m Z_n$, and in the supercritical case ($\hat m>1$) non-extinction occurs with positive probability (Lean T4); lineage-multiplication-type growth was expected.

## 9.2 Mechanism Evidence and Falsification

Per-generation offspring checking (`e_supercritical_sh3.py`) found structural facts contradicting a branching process:

1. **Write in {0,1}, independent of the population**: exactly 0 or 1 new P1 entries per generation ($w_n\in\{0,1\}$, PMF=[0,1], chain mean $E[w_n]=0.917$—11/12 chains write 1 every generation), and the write is independent of $Z_n$;
2. **Linear accumulation**: $Z_{n+1}=Z_n+1$ (unsaturated segment); measured Z=[1,2,2.917,3.917,3.917,4.917,4.917,4.917] (all generations g0–g7)—no multiplication, no superlinear growth;
3. **Capacity saturation**: after hitting $M=16$, the system enters the FIFO competition steady state ($5/16$), rather than the random extinction path of a branching process.

Conclusion: **S-H3 is falsified by mechanism evidence**. Full-append propagation is **linear accumulation–competition** (Mechanism B); "supercritical" is retained as engineering semantics (persistent accumulation without extinction), and the precise mechanism is no longer GW branching.

## 9.3 Revised Theory

- Mechanism A (branching decay) still applies to the selective architecture (geometric law $R^2=0.958$ / $0.923$; Lean T1/T2 premises hold);
- Mechanism B (accumulation–competition) applies to full-append: $Z_{n+1}=Z_n+w_n$ ($w_n\in\{0,1\}$, chain mean 0.917), outcome decided by capacity $M$ (under the current protocol, $M_c\in(8,16)$);
- Quarantine invariance (S-H4) is mechanism-independent—C3-full 12/12 still truncates propagation where the branching premise fails, showing the quarantine commitment is more robust than its formalization premises.

## 9.4 Paper-Handling Principles

- **No hiding**: the falsification appears in full in Results (§6.1) and here;
- **No conflation**: Mechanism B's "persistent accumulation" and GW's "supercriticality" are distinct mathematical objects; the notational discipline throughout ($w_n$ vs $M$ vs $\hat m$) prevents misreading;
- **Methodological asset**: this case demonstrates how a pre-registered hypothesis is falsified by structural evidence rather than by significance testing—mechanism identification precedes statistical inference.
