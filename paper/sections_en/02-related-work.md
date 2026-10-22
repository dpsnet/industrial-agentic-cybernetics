# §2 Background and Related Work (English, for manuscript-en.md)

> Status: **translated v1** (2026-10-22); citations consistent with `docs/terminology-mapping.md` plus classical SE-law sources.

---

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
