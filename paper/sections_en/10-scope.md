# §10 Scope and Generalizability (English, for manuscript-en.md)

> Status: **translated v1** (2026-10-22).

---

## 10.1 Applicability Boundaries (Four)

1. **Task family**: the main-experiment family is test-case writing (pytest) with four variants (correctness/boundary/negative/regression); the non-transferability of propagation strength across task families ($\hat m\in[0.29,1.00]$) is a measured conclusion—this paper does not claim quantitative prediction for arbitrary task families;
2. **Channel**: the theoretical evidence is confined to the **purely social propagation channel** (physical execution feedback disabled; only the context–memory–transcription loop); the production engineering loop (autonomous submission–promotion–archival cycle) satisfies the five-fold physical criteria (§2.3), and its quantitative connection to the theoretical channel—the coupling between the engineering-side promotion-loop ratio $q$ (measured 1.00) and the theoretical propagation strength $\hat m$—is an open item (§11.4);
3. **Model**: three model tiers (Pro/Kimi/Flash); $\hat m$ is model-specific; the quarantine guarantee does not depend on the model;
4. **Architecture**: selective / full-append / capacity tiers $M\in\{4,8,12,16,24,32\}$ (capacity-surface tiers added 2026-10-23); vector-store direct writing is proxied by full-append and not isolated as a separate experiment.

## 10.2 Layering of Guarantees and Values

- **Cross-boundary guarantee (theory layer)**: quarantine ($\sigma=1$) truncates propagation—measured across models, task families, and architectures; Lean-checked (T3 conditional theorem) for structural necessity;
- **Within-boundary values (empirical layer)**: $\hat m$ (Mechanism A), $M_c$ (**measured as a conditional quantity of $(b,M,\text{strain transcription state})$**—it moves up with the benign write rate and its absolute reading drifts with the transcription state: $W_c\le4$ at $b=1/2$, $W_c\in(4,8)$ at $b=3$, $W_c\in(8,12)$ at $b=5$ (high-state-day readings), low state $M_c\in(8,16)$ vs high state $M_c\in(4,8)$, §6.5), multiplicative-law parameters—valid only over the measured domain; cross-domain transfer is prohibited;
- **Engineering layer**: production five-fold physical criteria (§2.3) serve as deployment adjudication; their coupling to theoretical parameters is listed as an open item.

## 10.3 Scoping Statement

This paper provides a mechanism taxonomy (architecture-decided) and a defense separation (quarantine > marking) for "poison propagation in ungated agentic memory systems." It does not claim: quantitative prediction for arbitrary task families/models, cross-channel causality, or overall security of memory systems. Inferences beyond scope are regarded as reader extensions, not claims of this paper.
