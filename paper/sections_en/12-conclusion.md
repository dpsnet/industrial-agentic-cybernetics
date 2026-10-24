# §12 Conclusion

> Status: **translated v1** (2026-10-22).

---

## 12.1 Conclusions

1. **Mechanism**: under the ungated accumulative (full-append) agentic memory architecture, injected poison persists and accumulates without extinction—the mechanism is **linear accumulation–competition** (per-generation write $w_n\in\{0,1\}$, $Z_{n+1}=Z_n+w_n$), measured chain-mean write $E[w_n]=0.917$, FIFO competition steady state $5/16$ after capacity saturation (cross-mechanism propagation ratio $\hat m^\dagger=1.166$; estimator and GW-semantics qualification in the §6.1 table note);
2. **Architecture effect**: the propagation mechanism is determined by architecture, not model—selective replay = branching decay (GW, cross-model $\hat m\in[0.56,0.98]$), full-append = accumulation–competition; memory capacity $M$ is the control parameter, critical $M_c\in(8,16)$ is a **low-transcription-state** reading (this protocol tier; consistent with the COMPLEMENT-EXP surface at $W=16$, split at the boundary grid point $W=8$—cross-state readings in §6.5, **$M_c$ is a conditional quantity of $(b,M,\text{strain transcription state})$: the probe-gated high-state rescan measures $W{=}8$ survival 0.75 with $M_c\in(4,8)$, so shrinking the memory window cannot reliably prevent poisoning; same-day dual-script reruns show no difference at $p{=}0.155$, and the split is attributed to a sub-hourly state transition in poison-transcription behavior rather than a protocol difference, §6.5/§11.4**);
3. **Quarantine invariance**: quarantine ($\sigma=1$) truncates propagation across mechanisms—Lean 4 machine-checked conditional theorem (T3) + measured cross-model 24/24, cross-task-family 48/48, full-append 12/12; the marking-gate effect is model-heterogeneous and unreliable (Pro 47% compression non-significant / C1-full structural same-trace / Flash large-sample zero compression, $p=0.69$)—**defense depends on quarantine, not marking**.

## 12.2 Contributions

1. Mechanism layer: the architecture-decides-mechanism dichotomy + capacity control parameter (§3);
2. Formalization layer: Lean 4 machine-checked theorem chain, zero `sorry` (§4);
3. Evidence layer: pre-registered, closed criteria across models × architectures × task families × large samples (§5–§6);
4. Engineering implication: quarantine-first defense design principle (§8.1) + honest mechanism-revision case (§9).

## 12.3 Disciplinary Implication

The empirical laws of software engineering can and should be promoted to an engineering-axiom structure of "conditional theorem + measured support" (a methodological claim; the machine-checked object is the probabilistic conditional theorem, qualification in §2.5); this work provides a complete instance (formalization + pre-registration + mechanism revision) and a transferable methodological template (three-layer knowledge status + pre-registered criteria + mechanism identification first).
