# Abstract & Title (English, for manuscript-en.md)

> Status: **final v1** (2026-10-22); Chinese counterpart in abstract.md.

---

## Title (final)

**Memory Poisoning in Ungated Agentic Memory Architectures: Architecture-Dependent Propagation Mechanisms, Capacity Control, and Quarantine Invariance**

## Abstract (final)

Long-lived language-model agents accumulate experience in persistent memory; unvalidated or malicious entries can propagate across sessions and poison downstream tasks. Existing defenses treat soft marking and hard quarantine interchangeably, and no account links the *memory architecture* to the mathematical structure of propagation. We study injection-propagation under two write protocols—selective replay and full append—through pre-registered experiments spanning three model families (DeepSeek-V4-Pro-0813 (Pro), Kimi, DeepSeek-V4.1-Flash-1017 (Flash)), two architectures, three capacity settings, and 450 agent-session chains (2,796 session-generation units), with Lean 4 machine-checked conditional theorems.

We find that the architecture, not the model, determines the propagation mechanism. Selective replay yields branching decay: a Galton-Watson process with model-specific offspring mean $\hat m\in[0.56,0.98]$ and geometric-law decay (R²≥0.92). Full append yields linear accumulation–competition: a per-generation write $w_n\in\{0,1\}$ (chain mean $E[w_n]=0.917$) gives $Z_{n+1}=Z_n+w_n$ up to the memory capacity $M$, where FIFO competition reaches and maintains a steady state ($5/16$) (engineering-semantics persistence; the cross-mechanism propagation ratio is reported in §6.1). Capacity $M$ is the control parameter, with a critical capacity $M_c\in(8,16)$ separating extinction ($M\le M_c$) from persistence ($M>M_c$).

For defense, soft-marking effects are model-heterogeneous and unreliable: the Pro tier shows a large but non-significant 47% compression under inadequate power, the full-append tier shows 12/12 same-trace trajectories (structural write-path bypass), and the Flash large-sample paired test ($n=48$, $\bar d=0.020$, $p=0.69$) confirms zero compression, while quarantine ($\sigma=1$) cuts off propagation in all conditions: 24/24 cross-model, 48/48 cross-task, and 12/12 full-append chains. We conclude that defense depends on hard quarantine, not soft marking. As a methodological note, our pre-registered branching-match hypothesis was falsified by direct generation-level evidence and revised to linear accumulation–competition; we report the revision transparently.
