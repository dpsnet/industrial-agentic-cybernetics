# 附录 B：形式化收敛性与稳定性证明（Lean 4 机检）
## Appendix B: Formal Proofs of Convergence and Stability (Lean 4 Mechanized)

> 本附录是全书理论主张的机检底座。所有定理均在 Lean 4（toolchain v4.34.0-rc2）+ mathlib4 中通过内核验证，工程位于 `formal_proof/IACFormalization/`，构建命令：`lake build`。
>
> 认识论三级标注贯穿本附录：
> - **[定理]**：Lean 内核完整验证，无公理依赖（或仅依赖显式假设）；
> - **[引用公理]**：数学文献中已确立但 mathlib 尚未收录现成形式的结果，以 `axiom` 显式声明并附标准引用，绝不伪装成已证定理；
> - **[经验公设]**：关于大模型实际行为的经验刻画，本质上不可形式化推导，以 `axiom`/`opaque` 显式隔离，是全书中**唯一**的外源输入点。

---

## B.1 模块与章节对应总表

| Lean 模块 | 对应书章节 | 数学工具 | 证明状态 |
| :--- | :--- | :--- | :--- |
| `Axiom1_Grounding` | §3.2 公理 I；第二章 | 有限联合分布代数 | 全部 [定理]，独立性为显式假设 |
| `Axiom2_AttentionDilution` | §3.2 公理 II；模式 04 | 实分析（softmax 单调性） | 核心 [定理] + 1 条 [经验公设] |
| `Axiom3_CausalMonotonicity` | §3.2 公理 III；模式 09 | 序理论、幂等算子 | 全部 [定理]，零公理 |
| `Axiom4_MemoryPoisoning` | §3.2 公理 IV；模式 14/15 | 分支过程、压缩映射极限 | 核心 [定理] + 2 条 [引用公理] |
| `Theorem3_1_CausalInvariance` | §3.3 | Foster–Lyapunov 离散核、有限状态机反例 | 核心 [定理] + 1 条 [引用公理] |

---

## B.2 公理 I：接地不可替代性（全部已证）

书中公理 I 的概率极限式表达的是工程立场；其可严格证明的核心在本模块：

- **定理 `self_verdict_zero_information`（自检零信息定理）**：在条件独立的封闭认知闭环中（无任何外部物理传感器），自检通过的后验真值率等于先验真值率：$P(V_t=1 \mid V_s=1) = P(V_t=1)$。自检证据的贝叶斯似然比恒为 1。
- **定理 `closed_loop_risk_factorizes`**：闭环内"自检声称成功且物理亦真"的概率被先验乘积结构完全锁定，任何不引入外部观测的纯反思策略无法改变它。
- **定理 `posterior_independent_of_mechanism`**：后验真值率与自检机制的复杂程度无关——形式化排除了"更强的模型可以靠自省突破"的幻想。

物理 Exit 0 穿透（模式 01）因此不是"提高置信度"，而是"获得任何证据的唯一通道"。

## B.3 公理 II：注意力稀释（核心已证 + 1 条经验公设）

- **定理 `attention_dilution_strict`**：固定目标质量 $a>0$，无关上下文总质量 $b \to b' > b$，则目标 token 的注意力份额严格下降：$\frac{a}{a+b'} < \frac{a}{a+b}$。稀释是严格不等式意义上的必然，不是"可能影响"。
- **定理 `softmax_share_strictly_decreases`**：上述结论对任意正权重函数（如 softmax 参数化 $w = \exp \circ \operatorname{logit}$）的抽象实例。
- **[经验公设] `attention_snr_decay`**：存在衰减因子 $c \in (0,1)$，使每增加一单位冗余上下文，目标检索信噪比至少按比例 $c$ 衰减（几何/指数衰减的离散形式）：$\mathrm{snr}(\rho+1) \le c \cdot \mathrm{snr}(\rho)$。归纳即得 $\mathrm{snr}(\rho+n) \le c^n \cdot \mathrm{snr}(\rho)$，与书中 §3.2 的越界下界 $P_{violate}(\rho) \ge 1-e^{-\alpha\rho}$ 在 $\rho \in \mathbb{N}$ 上等价（$c = e^{-\alpha}$）。$c$ 的具体值依赖 Transformer 内部动力学，不可抽象推出；实证支撑为 Liu et al. (TACL 2024) 与 RULER (2024)。该公设是全书唯一的外源输入。

## B.4 公理 III：因果单调性（全部已证）

- **定理 `observability_iff_mtime_strict_mono`**：对产生真实差异的变异，**可观测 ⟺ 物理时钟（mtime / WAL LSN）严格单调跳变**。若时钟回拨或停滞（$\text{mtApplied} \le \text{lastCompiledAt}$），修改被增量编译器静默吞没（Silent Loss）。"代码已改、测试仍在跑旧字节码"获得了严格的形式化——单调性不是工程优化，而是可观测性的逻辑必要条件。
- **定理 `log_append_apply_idempotent`**：追加式日志（WAL）的回放算子幂等——同一物理时刻的重复回放中，第二次应用的校验和必然失败，且内容字段与首次应用完全一致。重试安全且不污染编译结果。

## B.5 公理 IV：记忆投毒相变（核心已证 + 2 条引用公理）

模型：未终审经验的跨代传播为分支过程；双盲隔离门禁的选择度 $\sigma$ 将名义繁殖均值 $\mu$ 压缩为有效繁殖数 $m = \mu(1-\sigma)$。

- **定理 `expected_population_geometric`**：期望种群 $E(n) = m^n E(0)$（归纳）。
- **定理 `subcritical_expectation_vanishes`**：$0 \le m < 1$ 时 $E(n) \to 0$（压缩映射极限）。
- **定理 `subcritical_extinction_in_probability`**：结合 Markov 界（见下），$m<1$ 时存活概率 $P(Z_n \ge 1) \to 0$——隔离晋升门禁（模式 14）有效性的定量核心。
- **定理 `quarantine_compresses_offspring`**：$\sigma$ 越严格有效繁殖数越小，完全隔离使其归零。
- **[引用公理] `markov_extinction_bound`**：非负整值随机变量的 Markov 尾界 $P(Z\ge1)\le E[Z]$（Durrett）。
- **[引用公理] `galton_watson_supercritical_explosion`**：$m>1$ 时种群以正概率永不灭绝（Athreya & Ney, 1972）。无门禁（$\sigma=0$）且 $\mu>1$ 时投毒经验以正概率永久存续——模型坍缩的种群动力学对应。

## B.6 定理 3.1：收敛因果不变性（核心已证 + 1 条引用公理）

**充分性（已证）**：
- **定理 `lyapunov_finite_hitting`**：能量函数 $V : S \to \mathbb{N}$ 处处严格负漂移 ⟹ 至多 $V(s_0)$ 步命中零点（全部物理契约满足）。这是 Foster–Lyapunov 准则的离散决定论核心，归纳法完成。
- **定理 `zero_energy_is_fixed`**：零能量不动点 ⟹ 收敛态永久保持。

**必要性（三个已证反例）**：
1. **破坏可观测性**（`no_observability_absorbs_falsified`）：系统一步进入虚假通过吸收态并永久停留；
2. **破坏局部性**（`no_locality_two_cycle` + `no_locality_defeats_lyapunov`）：系统进入 2-周期轨道，且**任何**能量函数都不可能处处严格下降——震荡不可被李雅普诺夫方法驯服；
3. **破坏评估解耦性**（`coupled_evaluation_tautological_fixed_point`）：评价者复制解题者输出，形成自指不动点，收敛于退化平庸解。

**汇合陈述 `causal_invariance_abstract`**：充分性与三个必要性反例的合取。

**[引用公理] `foster_lyapunov_expected_hitting`**：随机情形的期望停时界 $\mathbb{E}[\tau] \le V(s_0)/\delta$（Foster 1953；Meyn & Tweedie 1993, Ch. 11）。mathlib 暂无现成形式，其完整随机化（鞅可选停止定理的接入）列为后续里程碑。

---

## B.7 与正文的经验边界声明

形式化覆盖的是**抽象控制模型的动力学性质**；以下内容本质上不可形式化，全书维持其经验主张地位：

1. Transformer 注意力机制的衰减因子 $c$（B.3 公设）；
2. 具体大模型在具体任务上的奖励欺骗发生率（第二章博弈论分析给出的是策略存在性，非发生率）；
3. 工业工程中契约违规的实测分布。

形式化证明保证的是：**在这些经验参数给定的前提下，四大公理与定理 3.1 所断定的因果结构在逻辑上成立**。

---

## B.8 复现方式

```powershell
cd formal_proof/IACFormalization
lake build        # 全量内核验证
lean src/IACFormalization/Axiom1_Grounding.lean   # 单文件检查
```

依赖：本机共享 mathlib4 预编译包（`lakefile.lean` 中以绝对路径引用）；零 sorry 政策——任何 `sorry` 出现即视为构建缺陷。
