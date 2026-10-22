# 附录 B：形式化收敛性与稳定性证明（Lean 4 机检）
## Appendix B: Formal Proofs of Convergence and Stability (Lean 4 Mechanized)

> 本附录是全书理论主张的机检底座。所有定理均在 Lean 4（toolchain v4.34.0-rc2）+ mathlib4 中通过内核验证，工程位于 `formal_proof/IACFormalization/`，构建命令：`lake build`。
>
> 统计：86 条 [定理]（内核验证，含辅助引理）、**0 条公理**、0 个 `sorry`。
>
> 认识论三级标注贯穿本附录：
> - **[定理]**：Lean 内核完整验证，无公理依赖（或仅依赖显式假设/结构前提）；
> - **[引用公理]**：数学文献中已确立但 mathlib 尚未收录现成形式的结果（本附录不含此类依赖）；
> - **[经验公设]**：关于大模型实际行为的经验命题。形式化以条件定理呈现：前提为显式结构假设（如注意力机制的上下文质量增长律），结论由内核验证导出；"真实系统满足该前提"由实测支撑，不在形式系统内断言。

---

## B.1 模块与章节对应总表

| Lean 模块 | 对应书章节 | 数学工具 | 证明状态 |
| :--- | :--- | :--- | :--- |
| `Axiom1_Grounding` | §3.2 公理 I；第二章 | 有限联合分布代数 | 全部 [定理]，独立性为显式假设 |
| `Axiom2_AttentionDilution` | §3.2 公理 II；模式 04 | 实分析（softmax 单调性）、三通道注意力机制 + 增长律（几何/线性/幂律） | 全部 [定理] |
| `Axiom2_PhaseModel` | §3.2 公理 II 两相动力学 | 两相结构、显式相变点、不逆转上界 | 全部 [定理]，零公理 |
| `Axiom2_Axiom4_Bridge` | §3.2 公理 II ↔ 公理 IV 跨公理接口 | 注入耦合、下界合成 | 全部 [定理]，零公理 |
| `Axiom3_CausalMonotonicity` | §3.2 公理 III；模式 09 | 序理论、幂等算子 | 全部 [定理]，零公理 |
| `Axiom4_MemoryPoisoning` | §3.2 公理 IV；模式 14/15 | 分支过程、初等概率（PMF + Markov 不等式） | 全部 [定理]，零公理 |
| `Probability_Markov` | §3.2 公理 IV 概率工具 | Markov 不等式（初等证明，零测度论依赖） | 全部 [定理]，零公理 |
| `Theorem3_1_CausalInvariance` | §3.3 | Foster–Lyapunov 离散核、有限状态机反例 | 全部 [定理]，零公理 |
| `GaltonWatson` | §3.2 公理 IV 超临界强结论 | 生成函数、不动点、初等分析 | 全部 [定理]，零公理 |
| `StochasticFosterLyapunov` | §3.3 随机控制 | 随机核、停时、初等期望 | 全部 [定理]，零公理 |
| `Pattern10_LeaseLock` | 模式 10 | 离散时钟、租约状态机 | 全部 [定理]，零公理 |
| `Pattern11_PrimaryWriter` | 模式 11 | 写日志、时钟严格递增、视图过滤 | 全部 [定理]，零公理 |
| `Pattern23_24_ProductionLoop` | 模式 23/24 | 有限支撑随机核、Foster–Lyapunov 漂移 | 全部 [定理]，零公理 |

---

## B.2 公理 I：接地不可替代性（全部已证）

书中公理 I 的概率极限式表达的是工程立场；其可严格证明的核心在本模块：

- **定理 `self_verdict_zero_information`（自检零信息定理）**：在条件独立的封闭认知闭环中（无任何外部物理传感器），自检通过的后验真值率等于先验真值率：$P(V_t=1 \mid V_s=1) = P(V_t=1)$。自检证据的贝叶斯似然比恒为 1。
- **定理 `closed_loop_risk_factorizes`**：闭环内"自检声称成功且物理亦真"的概率被先验乘积结构完全锁定，任何不引入外部观测的纯反思策略无法改变它。
- **定理 `posterior_independent_of_mechanism`**：后验真值率与自检机制的复杂程度无关——形式化排除了"更强的模型可以靠自省突破"的幻想。

物理 Exit 0 穿透（模式 01）因此不是"提高置信度"，而是"获得任何证据的唯一通道"。

## B.3 公理 II：注意力稀释（全部已证）

模型（结构 `AttentionMechanism`）：目标 token 的注意力质量 $a(\rho)$、**总非目标质量** $b(\rho)$ 与**残差子通道** $r(\rho)$（BOS/attention sink、指令 token 等固定占用），满足 $a,b>0$、$0\le r<b$，且增加冗余不增强目标信号（$a(\rho+1)\le a(\rho)$）、总非目标质量非减（$b(\rho)\le b(\rho+1)$）。注意力份额为 $a/(a+b)$，检索信噪比为

$$\operatorname{snr}(\rho) := \frac{a(\rho)}{b(\rho)}.$$

**口径要点（A2）**：定理前提承载在**总非目标质量** $b$ 上；实测只能统计**填充子通道** $\mathrm{filler} := b - r$。二者关系由两条定理刻画：

- **定理 `snr_le_proxy`**：实测填充口径 $a/\mathrm{filler}$ 系统性**高估**真实 $\operatorname{snr}$，偏差因子为 $b/\mathrm{filler}\ge 1$——只统计填充段会低估稀释严重程度（E3b 实测高估 35.8%–36.7%，方向一致）；
- **定理 `filler_growth_not_sufficient`**（反例）：仅填充子通道按几何膨胀**不足以**保证总量前提成立——增长前提必须施加在 $b$ 上，前提对象不可移位。

**基础稀释定理**：

- **定理 `attention_dilution_strict`**：固定目标质量 $a>0$，无关上下文总质量 $b \to b' > b$，则目标 token 的注意力份额严格下降：$\frac{a}{a+b'} < \frac{a}{a+b}$。稀释是严格不等式意义上的必然，不是"可能影响"。
- **定理 `softmax_share_strictly_decreases`**：上述结论对任意正权重函数（如 softmax 参数化 $w = \exp \circ \operatorname{logit}$）的抽象实例。
- **定理 `attention_share_dilution`**：总非目标质量严格增大（$b(\rho) < b(\rho+1)$）时，注意力份额严格下降——定性稀释是注意力公式的代数必然。

**增长律 → 衰减率的三条对应定理**（前提均为显式结构假设，实测形态由经验判别）：

- **定理 `snr_geometric_decay`**：$b$ 每步至少按因子 $(1+\gamma)$ 膨胀（$\gamma>0$）⟹ $\operatorname{snr}(\rho+1) \le c\cdot\operatorname{snr}(\rho)$，其中 $c = 1/(1+\gamma) < 1$ 为**定义**而非独立断言。前提是关于"注意力分母如何膨胀"的结构性假设（因），结论是"信噪比如何衰减"的定量界（果）。
- **定理 `snr_polynomial_decay`**：$b$ 仅线性增长（每步至少加 $\delta>0$）⟹ $\operatorname{snr}(n) \le a(0)/(b(0)+n\delta)$，即 $O(1/n)$ 多项式衰减。
- **定理 `snr_power_decay`（幂律分支，A4）**：$b$ 每步至少按**精确幂比** $((\rho+1)/\rho)^\beta$ 膨胀（$\beta>0$）⟹ $\operatorname{snr}(n)\le a_0/(b_0\,n^\beta)$ 型幂衰减。配套：`b_power_growth`（幂比连乘的伸缩积引理）、`snr_power_decay_relative`、`snr_power_decay_of_one_add`（$0<\beta\le 1$ 档经 Bernoulli 不等式桥接 $1+\beta/\rho$ 的字面写法；精确幂比写法避免 $\rho=0$ 奇异且 $\beta\ge1$ 时无常数损失）。E3 实测幂律在 33/36 cell 占优、几何 0 票，该分支由可选升为**必要**。

`DilutionDynamics` = `AttentionMechanism` + 几何增长因子 $\gamma$，单步衰减 `hdecay` 为定理。其后承：

- **定理 `snr_decay_iterated`**：由单步几何衰减归纳推出 `snr(ρ+n) ≤ c^n · snr(ρ)`。
- **定理 `geometric_decay_strictly_decreases`**：当 `snr(ρ) > 0` 时几何衰减蕴含严格单调下降。
- **定理 `violation_prob_lower_bound`**：违约概率 `P_violate(ρ) = 1 - snr(ρ)/snr(0)` 满足 `P_violate(n) ≥ 1 - c^n`，与正文 §3.2 的 `P_violate(ρ) ≥ 1-e^{-αρ}` 在 $\rho \in \mathbb{N}$ 上等价（$c = e^{-\alpha}$）。

**两相动力学（`Axiom2_PhaseModel`，A1）**：`PhaseModel` = `AttentionMechanism` + 膨胀率 $\gamma$ + 显式相变点 $N^*$，稀释相膨胀律仅在 $[0,N^*)$ 内承诺：

- **定理 `snr_dilute_decay`**：稀释相内 $c^n$ 几何衰减界（定义域显式截断到 $[0,N^*)$）；
- **定理 `snr_plateau_le`**：平台相（$n\ge N^*$）衰减**不逆转**——$\operatorname{snr}(n)\le\operatorname{snr}(N^*)$：工程保证在饱和区退化为"不再恶化"，而非失效；
- **定理 `violation_prob_plateau_lower_bound`**：平台相违约概率的常数下界；
- **定理 `plateau_violates_geometric_bound`**（反例）：全域几何界确会在饱和区失效；`global_growth_recovers_decay` 表明仅补上全域增长前提即可恢复几何界。

**跨公理接口（`Axiom2_Axiom4_Bridge`，A5 / T7）**：`InjectionCoupling` 把记忆注入速率 $\mu$ 经无关量映射 $\rho(\mu)$ 与公理 IV 相接：

- **定理 `violation_lower_bound_at_injection`**：注入速率 $\mu$ 下违约概率下界 $1-c^{\lceil\rho(\mu)\rceil}$；
- **定理 `injection_strengthens_lower_bound`**：注入越快下界越紧（单调放大）；
- **定理 `violation_under_injection`**：纵向边合成形式；`violation_bound_beyond_plateau` 给出平台相校正。

这是分层公理系统中"层间无反馈"的纵向边：公理 II 的稀释动力学经注入速率驱动公理 IV 的污染传播下界，专著由此不再是若干独立模型的集合。

> 认识论要点：形式系统断言的是"对任何满足相应增长律的注意力系统，对应衰减界与违约下界成立"；"真实 Transformer 满足哪一分支"是经验命题。实测判读（E3/E3b，Qwen2.5-1.5B/7B，上下文至 131k，2026-10）：幂律分支占优（AIC 33/36 cell）、几何分支 0 票；弱前提 $a$ 非增方向性成立而"$a$ 为常数"被证伪（$\hat\beta_a<0$，CI 不含 0）——实测 SNR 衰减由分子收缩与分母膨胀共同贡献；7B YaRN 长程"下降相"经三通道补测判定为填充子通道向 sink 的质量迁移，总非目标质量 $t=b+r$ 全程非减（`hb_nondec` 总量口径实测存活）。详见附录 B.11 与 `experiments/attention_growth/EXPERIMENT_PLAN.md`。

> **衰减参数的代理探索（E8，2026-10-20，关闭）**：$\gamma$ / $\beta$ 是定理的**自由参数**，本附录不假设其可由结构量预测。三次跨模型族复验（Qwen2.5-7B / 1.5B + Llama-3.2-3B，共 486 行）后，三候选结构量（注意力熵、top-1% 集中度、key 有效秩）**无一跨 3 模型稳健复现**——erank 仅在 7B 上满足判据，top1pct 仅在 1.5B β̂ 与 7B λ̂ 上存活，Llama-3B 上四个结构量在两种口径下均未达 |Spearman|≥0.5 且 CI 不含 0。**γ 保持自由参数**，其值由实测标定。值得记录的弱信号是**方向一致性**：entropy（−β̂/+λ̂）、top1pct（+β̂/−λ̂）、erank（−β̂/+λ̂）在三模型上方向完全一致——强度跨规模/跨族不稳定，但方向可能有机制意义。单次 OOM 事故已由 `_gram_streamed` 分块永久修复（峰值 <1 GB vs 原 34 GB）。

## B.4 公理 III：因果单调性（全部已证）

- **定理 `observability_iff_mtime_strict_mono`**：对产生真实差异的变异，**可观测 ⟺ 物理时钟（mtime / WAL LSN）严格单调跳变**。若时钟回拨或停滞（$\text{mtApplied} \le \text{lastCompiledAt}$），修改被增量编译器静默吞没（Silent Loss）。"代码已改、测试仍在跑旧字节码"获得了严格的形式化——单调性不是工程优化，而是可观测性的逻辑必要条件。
- **定理 `log_append_apply_idempotent`**：追加式日志（WAL）的回放算子幂等——同一物理时刻的重复回放中，第二次应用的校验和必然失败，且内容字段与首次应用完全一致。重试安全且不污染编译结果。

> **实测边界（E-A3，2026-10-20）**：上述两定理的工程对应在 Cargo 1.96（Windows NTFS）上获 28 项受控测量支持（`experiments/attention_growth/axiom3_results.json`）：mtime 停滞/回拨 ⟹ 静默丢失（各 5/5，产物保持旧版本）；mtime 严格正向跳变 ⟹ 重建（5/5，且纯时钟跳变即使内容不变也触发——重建触发纯由时钟通道决定，可观测性由内容差异决定，与 `hdiff` 前提划分一致）；幂等性在无变化重构建（5/5 跳过、产物 sha 不变）与 git 回退-重试场景（语义输出恢复）中成立。两点模型细化：① 判据参考时钟实测为"上次构建完成时刻" $R$，静默丢失窗口为 $(0, R]$，宽于朴素"文件旧 mtime"模型——构建进行中的并发写入天然落入丢失窗口；② Windows PE 头含编译时间戳，同源码重编译产物字节级必异，幂等性的判读须在语义层进行（对应定理承诺的是内容不变，非比特级一致）。适用域：mtime-based 增量编译器（Cargo、Make）；内容哈希型构建系统（Bazel、Nix）不依赖 mtime 跳变，本节定理的静默丢失场景在其上不适用。

## B.5 公理 IV：记忆投毒相变（全部已证）

模型：未终审经验的跨代传播为分支过程（`BranchingProcess` 结构，每代一个有限支撑 PMF）；双盲隔离门禁的选择度 $\sigma$ 将名义繁殖均值 $\mu$ 压缩为有效繁殖数 $m = \mu(1-\sigma)$。

- **定理 `expected_population_geometric`**：期望种群 $E(n) = m^n E(0)$（归纳）。
- **定理 `subcritical_expectation_vanishes`**：$0 \le m < 1$ 时 $E(n) \to 0$（压缩映射极限）。
- **定理 `markov_inequality`**（`Probability_Markov` 模块）：在有限支撑 PMF 上初等证明 $P(X \ge 1) \le E[X]$，零测度论依赖。
- **定理 `subcritical_extinction_in_probability`**：由 Markov 不等式与几何衰减，$m<1$ 时存活概率 $P(Z_n \ge 1) \to 0$——隔离晋升门禁（模式 14）有效性的定量核心。
- **定理 `quarantine_compresses_offspring`**：$\sigma$ 越严格有效繁殖数越小，完全隔离使其归零。
- **定理 `supercritical_expectation_diverges`**：$m>1$ 且 $E(0)>0$ 时 $E(n) \to +\infty$。这是 Galton-Watson 超临界爆炸定理的期望层版本。
- **定理 `galton_watson_non_extinction`**（`GaltonWatson` 模块）：后代均值 $m>1$ 时，灭绝概率 $q < 1$，即以**正概率永不灭绝**。证明采用生成函数不动点分析的初等路线：
  - 定义 `genFun(s) = Σ p_k s^k`，证明其在 $[0,1]$ 上单调、有界，`genFun(1)=1`；截断多项式 `genFun_N` 连续可导且 `genFun_N'(1) → m > 1`；
  - **核心引理 `exists_lt_sub_id`**：由 `genFun'(1)>1` 与连续性，取截断多项式 `genFun_N` 使 `genFun_N'(s₀)>1`，经 MVT 与尾部估计推出存在 $s₀<1$ 使 `genFun(s₀)<s₀`；
  - 灭绝概率迭代 $q_n = \varphi^n(0)$ 单调递增且被 $s₀$ 一致上界，故其极限 $q = \sup q_n \le s₀ < 1$。
- **定理 `genFun_extinctProb_fixed` / `extinctProb_le_of_fixed` / `galton_watson_extinctProb_exact`**（灭绝概率的精确刻画）：$q$ 不仅是上界，而且是 $\varphi$ 在 $[0,1]$ 上的**最小不动点**：$q = \varphi(q)$，且任何不动点 $s\in[0,1]$ 满足 $q \le s$。证明用单调性夹逼（$q_{n+1}=\varphi(q_n)\le\varphi(q)$ 取极限得 $q\le\varphi(q)$；多项式截断 $\varphi_N$ 连续给出 $\varphi_N(q)\le q$ 再取 $N\to\infty$），避免了对 $\varphi$ 自身连续性的依赖。超临界时 $q$ 因此被完全刻画：$q = \min\{s\in[0,1] : \varphi(s)=s\} < 1$。
  无门禁（$\sigma=0$）且 $\mu>1$ 时，投毒经验不仅期望载荷无界，且以正概率永久存续——模型坍缩的强动力学对应。

> **实测边界（E-A4，2026-10-21）**：上述定理链的模型–现实映射在 DeepSeek v4-pro 多代记忆传播实验（4 条件 × 12 replicate × 6 代 = 288 会话，预注册判读先于实验）中获检验：`quarantine_compresses_offspring` 的完全隔离情形（$\sigma=1$）实测使投毒谱系跨代传播严格为零（全部 replicate $Z_1=0$，无 de novo 再发现）；`expected_population_geometric` 的几何律与未隔离条件池化种群序列吻合（log-linear $R^2=0.958$，逐代比无趋势，分支性假设在小种群区成立）；实测繁殖核（per-parent offspring PMF）参数化的 Galton-Watson 仿真与定理链无自由参数吻合——三个亚临界变体（C0 实测 $m=0.538$、C1 实测 $m=0.333$、C0 PMF 经 Bernoulli(0.5) 抽稀 $m=0.269$）灭绝频率 $q_{sim}=1.0000=q^*$，`markov_inequality` 界全程数值成立。两点映射边界如实记录：① DRAFT_SUSPECT 标记门对每条目繁殖的压缩方向符合理论（$-38\%$）但统计不显著（置换检验 $p=0.15$），`quarantine_compresses_offspring` 的中间 $\sigma$ 情形（标记而非隔离的工程对应物）在本样本量下未获显著性支持；② $m=\mu(1-\sigma)$ 的 LLM 层直接检验因写出层涨落与过滤层有效样本 $n=1$ 而不可判定，仅获分布层（抽稀变体）间接支撑——该映射的 LLM 层直接检验需 $\ge 10^2$ 量级 replicate。适用域：单模型（DeepSeek v4-pro）、pytest 测试编写任务族、选择性逐代转写协议、无基质反馈（$\mathrm{SubstratePass}$ 通道关闭，纯社会传播）；本协议下无门禁条件实测 $m=0.56<1$（转写机制本身亚临界），超临界情形（`supercritical_expectation_diverges` / `galton_watson_non_extinction` 的经验对应）适用于无转写衰减的记忆架构（全量追加式记忆库、向量库直写），本实验未覆盖。数据与判读：`experiments/attention_growth/axiom4_results.json`、`axiom4_gw_sim.json`、`EXPERIMENT_PLAN_AXIOM4.md` §9。

## B.6 定理 3.1：收敛因果不变性（全部已证）

**充分性（已证）**：
- **定理 `lyapunov_finite_hitting`**：能量函数 $V : S \to \mathbb{N}$ 处处严格负漂移 ⟹ 至多 $V(s_0)$ 步命中零点（全部物理契约满足）。这是 Foster–Lyapunov 准则的离散决定论核心，归纳法完成。
- **定理 `foster_lyapunov_deterministic_bound`**：实值能量 $V : S \to \mathbb{R}_{\ge 0}$，当 $V \ge \delta$ 时每步至少下降 $\delta$（强漂移 $V(\text{step}\,s) \le V(s)-\delta$），则命中 $\delta$-邻域的步数 $t$ 满足 $t \cdot \delta \le V(s_0)$，即 $t \le V(s_0)/\delta$。
- **定理 `zero_energy_is_fixed`**：零能量不动点 ⟹ 收敛态永久保持。

**必要性（三个已证反例）**：
1. **破坏可观测性**（`no_observability_absorbs_falsified`）：系统一步进入虚假通过吸收态并永久停留；
2. **破坏局部性**（`no_locality_two_cycle` + `no_locality_defeats_lyapunov`）：系统进入 2-周期轨道，且**任何**能量函数都不可能处处严格下降——震荡不可被李雅普诺夫方法驯服；
3. **破坏评估解耦性**（`coupled_evaluation_tautological_fixed_point`）：评价者复制解题者输出，形成自指不动点，收敛于退化平庸解。

**汇合陈述 `causal_invariance_abstract`**：充分性与三个必要性反例的合取。

> **实测边界（E-B6，2026-10-21）**：充分性经 12 组受控仿真验证（$V_0 \in \{10,50,100,500\}$，$\delta \in \{0.5,1,2\}$），强漂移条件下收敛步数全程满足 $t \le V_0/\delta$；三个必要性反例各经 $10^4$ 次仿真复现：破坏可观测性 $\Rightarrow$ 虚假通过吸收态（100%）、破坏局部性 $\Rightarrow$ 2-周期震荡且 Lyapunov 不可能（100%）、破坏评估解耦 $\Rightarrow$ 自指退化不动点（100%）。数据：`experiments/attention_growth/b6_causal_invariance_sim.json`。

> 随机情形的期望停时界见 B.7。

---

## B.7 随机 Foster-Lyapunov 期望停时界（全部已证）

`StochasticFosterLyapunov` 模块以**初等方法**（随机核 + 停时截断 + 单调归纳，无测度论/鞅可选停止定理依赖）给出随机控制器的期望命中时间界。

模型：`StochasticKernel S` 为状态空间 $S$ 上的随机转移核（`k x A` 表从 $x$ 一步落入集合 $A$ 的概率，有限支撑）；`HasStrongDrift` 结构给出 Lyapunov 函数 $V:S\to\mathbb{R}_{\ge0}$ 与漂移常数 $\delta>0$、阈值 $b\ge0$，满足当 $V(x)\ge b$ 时 $\mathbb{E}_{k(x)}[V] \le V(x)-\delta$。

- **定理 `stoppedValue_le_V` / `stoppedTime_le_value`**：截断停时过程的价值与停时被初始能量一致控制（归纳核心）。
- **定理 `stoppedTime_uniform_bound`**：截断停时 $\tau_N$ 的期望满足 $\mathbb{E}[\tau_N] \le V(x_0)/\delta$，对所有截断水平 $N$ 一致成立。
- **定理 `foster_lyapunov_expected_hitting`**（主定理）：取截断极限，随机命中 $\{V<b\}$ 的期望停时满足 $\mathbb{E}[\tau] \le V(x_0)/\delta$。

由此，决定论 `foster_lyapunov_deterministic_bound` 成为本随机定理的特例；§3.3 的收敛因果不变性在随机控制层获得完整的期望停时定量界。

> **实测边界（E-B7，2026-10-21）**：主界 $\mathbb{E}[\tau] \le V(x_0)/\delta$ 经 27 组蒙特卡洛仿真验证（$V_0 \in \{10,50,100\}$，$\delta \in \{0.5,1,2\}$，噪声 $\sigma \in \{0,0.1,0.3\}$，每组 $10^5$ 次），全部满足；截断停时 $\tau_N$ 的期望对 $N \in \{10,50,100,500\}$ 一致有界性成立。数据：`experiments/attention_growth/b7_foster_lyapunov_sim.json`。

---

## B.8 模式级形式锚点：租约锁（全部已证）

`Pattern10_LeaseLock` 模块将模式 10（分布式物理底座租约锁与看门狗）的并发主张形式化。模型：物理时钟为离散 tick；锁状态 `LockState = Option Lease`（Option 结构本身编码"至多一个租约"）；`acquire`/`heartbeat` 为带前置条件的纯函数。

- **定理 `canWrite_unique`（互斥安全性）**：同一时刻至多一个智能体持有写权限——两个可写者必为同一人，并发写写冲突（失效场景 A）在协议内不可能。
- **定理 `acquire_rejected_of_live` / `acquire_succeeds_only_when_dead`**：租约存活时申请必被拒绝；授予仅当无存活租约。
- **定理 `no_permanent_lockout`（看门狗活性）**：对任意锁状态存在时刻 $T$（$=$ 到期时刻 $+1$），其后任何 `acquire` 都成功——崩溃持有者的孤儿租约必然在 TTL 到期后回收，工程不可能被永久锁死（失效场景 B 的形式否定）；不可用时长有界。
- **定理 `not_canWrite_of_expired`**：到期后原持有者写权限消灭，租约不因历史持有残留特权。
- **定理 `heartbeat_by_nonholder_unchanged` / `heartbeat_by_holder_extends`**：非持有者心跳被拒绝且状态不变；持有者续约不缩短租约（失效场景 C 的续约侧防护）。

> **实测边界（E-B8，2026-10-21）**：五项核心性质经离散时钟状态机仿真各 $10^4$ 次验证全部通过——互斥安全性（同一时刻至多一个写者）、看门狗活性（崩溃持有者租约 TTL+1 后必回收）、到期写权限消灭、心跳防护（非持有者拒绝、持有者续约不缩短）、并发写写冲突不可能（5 智能体 100 tick 随机竞争）。数据：`experiments/attention_growth/b8_lease_lock_sim.json`。

---

## B.9 模式级形式锚点：主写从读的单写者因果序（全部已证）

`Pattern11_PrimaryWriter` 模块将模式 11（主写入者 / 从属读取者降级互斥）的并发主张形式化。模型：写日志为 `List (Write Agent)`，元素携带写入者与物理刻度；`ChainValid` 要求相邻刻度严格递增；读取视图 `viewAt l t` 是日志按 `tick ≤ t` 过滤得到的前缀。

- **定理 `eq_of_mem_of_tick_eq`**：合法日志中不存在两个刻度相同的不同事件——同刻度即同一事件。
- **定理 `writer_unique_per_tick`**：同刻度的写事件写入者相同，故并发写写冲突在主写从读协议下不可能。
- **定理 `writer_unique_of_lease`**：该结论直接由 `Pattern10.canWrite_unique` 给出——"单写者"不是额外约定，而是租约互斥的推论。
- **定理 `view_mono` / `no_lost_write`**：较晚读取包含较早读取的全部事件；任何已提交且刻度不晚于读取时刻的写事件必然可见。故从读者读到的是**完整前缀**，不会出现"跳过中间提交"的视图。

---

## B.10 模式级形式锚点：观测–学习回路的稳定性（全部已证）

`Pattern23_24_ProductionLoop` 模块把验证报告 §7 遗留的"模式 23→24→23 负反馈回路"闭合。模型：缺陷存量 $x\in\mathbb N$，每周期以概率 $q$ 检出并修复一个（$x\mapsto x-1$），否则注入一个（$x\mapsto x+1$）；转移核 `loopKernel q` 为有限支撑随机核，直接复用 B.7 的 Foster–Lyapunov 框架。

- **定理 `T_id_pos`**：当 $x\ge 1$ 时，一步期望存量满足 $\mathbb E[x'\mid x]=x+1-2q$。
- **定理 `hasStrongDrift`**：若 $q>1/2$，取 $V(x)=x$、$b=1$、$\delta=2q-1>0$，强漂移条件成立。
- **定理 `loop_return_bound`**：回路命中"存量 $<1$"的期望时间满足 $\mathbb E[\tau]\le x_0/(2q-1)$——观测–学习闭环在 $q>1/2$ 时指数可回收。
- **定理 `no_drift_below_half`（临界负结果）**：若 $q\le 1/2$，则 $\mathbb E[x'\mid x]\ge x$，$V=\mathrm{id}$ 不构成 Lyapunov 函数。故 $q>1/2$ 是模型内的**必要门槛**，模式 23 文档中的"检出率 $\ge0.90$"应被理解为该门槛的工程余量，而非可选性能指标。

> **结论地位**：本模块给出的是**模型内**的稳定性判据（单缺陷类、单步注入/修复、独立同分布检出）。它不覆盖多缺陷类耦合、批量注入或检出率随存量变化的场景，这些仍属 §7 声明的未验证外推。同时，$q$ 的实测取值（`EXPERIMENT_PLAN_PRODUCTION_FIELD_TEST.md` 的 H1）尚未执行。

---

## B.11 与正文的经验边界声明

形式化覆盖的是**抽象控制模型的动力学性质**。全工程 Lean 代码中 **0 公理、0 sorry**。

以下内容本质上不可形式化，作为条件定理的前提或经验命题存在，全书不伪装其为已证：

1. Transformer 注意力机制的无关质量增长律与前提强度（B.3 各增长分支的前提）——"真实系统满足哪一分支"是经验命题。实测边界（E3/E3b，Qwen2.5-1.5B/7B，ρ≤131k，2026-10）：幂律分支占优、几何分支被否；弱前提 `ha_nonincr`（$a$ 非增）方向性成立、强假设"$a$ 为常数"被证伪；总非目标质量 $t=b+r$ 全程非减（`hb_nondec` 存活），填充子通道长程回落判定为 sink 迁移；正文引用实测 SNR 时须用三通道口径（目标/填充/sink），填充口径 SNR 系统性高估 35.8%–36.7%（`snr_le_proxy`）。**违约概率的传导边界（E4，2026-10-20）**：`violation_prob(ρ) = 1 - snr(ρ)/snr(0)` 是信噪比相对损失，**不是**任务失败概率。E4 端到端实验（Qwen2.5-1.5B/7B needle 检索正确率与 E3 SNR 对齐）表明两者之间存在补偿阈值 $W^*$：7B 在 131k 处 SNR 已损失 44% 但任务正确率仍 100%；1.5B 在 ρ∈[32k,64k] 正确率从 100% 陡降至 70%。违约下界 $P_{\text{violate}} \ge 1 - c^n$ 只在 $\rho > W^*$ 时传导为可观测的任务失败。$W^*$ 与模型能力正相关（$W^*_{1.5\text{B}} \approx 32\text{k–64k} < W^*_{7\text{B}} > 131\text{k} < W^*_{\text{Kimi}} \ge 1\text{M}$），为经验参数，不写入形式化接口。适用域：Qwen2.5 系模型、needle 型检索任务、F1–F3 填充；跨模型族与真实工程工作负载的外推未验证；
2. **模型–现实的口径映射**（B.3 全部定理的经验引用都经过它）：定理的 $a$ 是**单目标 token** 的注意力质量，实验的 $a$ 是 **needle 整段**总质量；定理的 $b$ 是**全部非目标质量**，实验的 $b$ 是**填充段**总质量（$\mathrm{filler}=b-r$）。这两条映射是未经证明的假设——其成立性由 E3b 的残差通道漂移检验部分背书（$r$ 显著漂移已触发预注册第 3 条，故三通道口径为必需而非可选），但"整段质量近似单 token 行为"尚无独立检验，引用实测数据支持定理叙事时须连同本声明一起给出；
3. 具体大模型在具体任务上的奖励欺骗发生率（第二章博弈论分析给出的是策略存在性，非发生率）；
4. 工业工程中契约违规的实测分布。

形式化证明保证的是：**在给定前提（独立性假设、增长律等）下，四大公理与定理 3.1 所断定的因果结构在逻辑上成立**。

---

## B.12 复现方式

```powershell
cd formal_proof/IACFormalization
lake build        # 全量内核验证
lean src/IACFormalization/Axiom1_Grounding.lean   # 单文件检查
```

依赖：本机共享 mathlib4 预编译包（`lakefile.lean` 中以绝对路径引用）；零 sorry 政策——任何 `sorry` 出现即视为构建缺陷。
