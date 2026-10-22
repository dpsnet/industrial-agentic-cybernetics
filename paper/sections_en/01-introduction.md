# §1 Introduction (English, for manuscript-en.md)

> Status: **translated v1** (2026-10-22); single source of facts: `experiments/attention_growth/*_judgement*.json`.

---

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
