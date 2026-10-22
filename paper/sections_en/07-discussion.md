# §7 Discussion (English, for manuscript-en.md)

> Status: **translated v1** (2026-10-22).

---

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
