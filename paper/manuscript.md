# Memory Poisoning in Ungated Agentic Memory Architectures: Architecture-Dependent Propagation Mechanisms, Capacity Control, and Quarantine Invariance

Long-lived language-model agents accumulate experience in persistent memory; unvalidated or malicious entries can propagate across sessions and poison downstream tasks. Existing defenses treat soft marking and hard quarantine interchangeably, and no account links the *memory architecture* to the mathematical structure of propagation. We study injection-propagation under two write protocols—selective replay and full append—through pre-registered experiments spanning three model families (DeepSeek v4-pro, Kimi, Flash), two architectures, three capacity settings, and 1,264 agent-session chains, with Lean 4 machine-checked conditional theorems.

We find that the architecture, not the model, determines the propagation mechanism. Selective replay yields branching decay: a Galton-Watson process with model-specific offspring mean $\hat m\in[0.56,0.98]$ and geometric-law decay (R²≥0.92). Full append yields linear accumulation–competition: a constant per-generation write ($w_n\equiv1$) gives $Z_{n+1}=Z_n+1$ up to the memory capacity $M$, where FIFO competition reaches a steady state ($5/16$); the estimated mean $\hat m=1.166$ (CI [1.156,1.176]) persists rather than decays. Capacity $M$ is the control parameter, with a critical capacity $M_c\in(8,16)$ separating extinction ($M\le M_c$) from persistence ($M>M_c$).

For defense, soft marking shows zero compression across three independent experiment families (pro $p=0.15$; full-append 12/12 same-trace; paired $n=48$, $\bar d=0.020$, $p=0.69$), while quarantine ($\sigma=1$) cuts off propagation in all conditions: 24/24 cross-model, 48/48 cross-task, and 12/12 full-append chains. We conclude that defense depends on hard quarantine, not soft marking. As a methodological note, our pre-registered branching-match hypothesis was falsified by direct generation-level evidence and revised to linear accumulation–competition; we report the revision transparently.


---

## 1. Introduction

## 1.1 问题

LLM 智能体（agent）正被部署到长期运行的生产系统：经验沉淀进持久记忆库，经检索在跨会话任务间复用。这一架构引入了一类此前未被系统研究的失效模式——**记忆投毒（memory poisoning）**：未经验证的自生经验（或攻击者注入的经验）进入记忆库后，经代际转写被持续复制，污染后续所有相关任务。文献已确立攻击的现实性与跨会话持久性（MemoryGraft, arXiv:2512.16962；OEP, arXiv:2605.18930），以及递归自我消费在训练期的宏观坍缩后果（Shumailov et al., *Nature* 631, 2024）。然而，**记忆架构本身如何调节传播、防御为何失败、何种干预有机制层保证**——这三问缺少实证与形式化的回答。

## 1.2 三个空白

1. **机制空白**：传播究竟服从何种数学模型，取决于记忆的转写协议（选择性转写 vs 全量追加）——此前没有跨架构的对照实验；
2. **防御空白**：软标记（标记门）与硬隔离（门禁）被混为一谈，没有独立判据区分二者在传播动力学上的作用；
3. **形式化空白**：软件工程学科的"根本规律"（Brooks 1987；Lehman 1980；Conway 1968）历来是经验定律，从未被形式化证明（§2.5 定位）；智能体记忆的投毒-隔离规律同样停留在启发式层面。

## 1.3 本工作

在公理 IV（经验自免疫）框架下，本文给出**机制识别 + 形式化 + 预注册实证**的完整闭环：

1. **机制层**：识别"架构决定传播机制"——选择性转写产生分支衰减（Galton-Watson 分支过程），全量追加产生线性累积-容量竞争（每代恒定写入 $w_n\equiv1$）；记忆容量 $M$ 为控制参量，临界 $M_c\in(8,16)$（§3）；
2. **形式化层**：Lean 4 机检定理链——GW 灭绝概率=最小不动点、亚临界概率灭绝、隔离压缩后代、超临界正概率不灭绝（§4；专著附录 B.5，零 `sorry`）；
3. **实证层**：预注册、跨模型（DeepSeek v4-pro / Kimi / Flash）× 跨架构（selective / full-append / 容量档）× 跨任务族（144 链）× 大样本配对（160 链）闭合判据（§5–§6）；
4. **工程含义**：防御依赖**隔离而非标记**——标记门在三档实验、两架构下零压缩（pro $p=0.15$；C1-full 12/12 逐代同轨；H1AC 配对 $\bar d=0.020$，$p=0.69$），隔离在跨模型（24/24 链 $Z_1=0$）、跨任务族（48/48 链）、跨架构（12/12 链 mem 恒 6）三维截断传播（§7）。

**一项诚实的方法论声明**：预注册假说 S-H3（GW 分支匹配）被逐代机制证据（$w_n\equiv1$ 线性累积）**证伪**。我们将其作为"预注册假说被证伪→机制重新识别"的正面案例完整呈现（§8），而非事后合理化。

## 1.4 论文结构

§2 Related Work；§3 机制模型；§4 形式化；§5 实验设置；§6 结果；§7 讨论；§8 机制修正叙事；§9 适用域；§10 局限；§11 结论。


## 2. Background and Related Work

## 2.1 Agentic Memory and Poisoning

智能体长期记忆（agentic memory）已成为 LLM 应用系统的标准组件：经验经检索（retrieval）复用，构成跨会话的持续知识层。与此同时，记忆已成为一类高价值攻击面：**记忆投毒（memory poisoning）**——攻击者或智能体自身的失效经验注入记忆库后，经后续检索被持久复用，污染后续任务（Shumailov et al., 2024；MemoryGraft, 2025）。近期实证表明，投毒攻击可跨会话持久生效，且极低污染率即可造成高攻击成功率（MemoryGraft, arXiv:2512.16962）；自进化智能体在"局部正确但不可迁移"经验下的污染路径亦有刻画（OEP, arXiv:2605.18930）。这些工作确立了攻击的现实性与持续性，但**防御侧停留在启发式**（标记、过滤、人工审查），缺乏对"为什么某些防御失效"的机制层解释——本工作补上这一层。

## 2.2 Model Collapse and Recursive Degradation

宏观层面的递归自我消费已被证明导致**模型坍缩（model collapse）**：用递归生成的数据训练，模型分布退化为模式坍缩与方差消失（Shumailov et al., *Nature* 631, 2024）。其与分支过程（branching process）的联系在文献中已有提及：退化可刻画为种群动态（population dynamics）。本工作的理论工具——Galton-Watson 分支过程及其灭绝概率、几何衰减律（Harris, 1963）——正是这一联系的形式化端点之一。与 Shumailov 等的训练期坍缩不同，本工作关注**推理期/记忆期的传播**：不经过重训练，仅在上下文-记忆-转写回路中逐代传播。这一区分是本文机制的出发点。

## 2.3 Defenses against Memory Poisoning

既有防御沿两条思路：

1. **软标记（soft marking）**：对自生经验打上"未验证"标记，供下游过滤（如 DRAFT_SUSPECT）。本工作三档实验（pro 主实验 $p=0.15$；SUPERCRITICAL C1-full 12/12 逐代同轨；H1AC 大样本配对 $\bar d=0.020$，$p=0.69$）一致显示：**标记门无压缩效应**——模型对软信号的采纳不可靠；
2. **硬隔离（hard quarantine）**：未经五重物理判据与独立审查终审的经验不得进入全局知识库（等价于本工作的门禁 $\sigma=1$）。本工作实测：隔离在**跨模型（24/24 链 $Z_1=0$）、跨任务族（48/48 链）、跨架构（full-append 12/12 链 mem 恒 6）**三个维度上截断传播——防御依赖结构阻断而非模型行为。

这一"隔离有效、标记失效"的分离，是文献中未系统检验的实证结论（2512.16962 的防御讨论未区分二者）。

## 2.4 General Degradation Mechanisms in Agents

- **Reward hacking / specification gaming**：智能体满足目标的字面而非精神以骗取成功信号（Amodei et al., 2016；Krakovna et al., 2020）；生产级 RL 中已观察到自然涌现的失对齐（Anthropic, arXiv:2511.18397）。这与本文公理 I（外部锚定缺失→自我宣称不可信）同族，但未涉及代际传播。
- **Context rot / Lost in the Middle**：随无关上下文增长，模型有效推理显著衰减，呈现 U 型注意力曲线（Liu et al., TACL 2024）；有效上下文长度远低于标称（Hsieh et al., 2024, RULER；Chroma, 2024）。这对应公理 II（注意力稀释），是**代内**退化；本文公理 IV 关注**代际**传播，两者在因果链上衔接但机制不同。

## 2.5 Software Engineering "Near-Axiom" Laws（定位节）

软件工程学科的传统"根本规律"是**经验定律**而非形式公理：Brooks 的本质复杂性（Brooks, 1987）界定了工程极限；Lehman 定律（Lehman, 1980）刻画软件演化的持续变更与递增复杂性（软件的"熵增"）；Conway 定律（Conway, 1968）揭示架构-组织同构；CAP 定理（Gilbert & Lynch, 2002）锁定分布式一致性的取舍；停机问题（Turing, 1936）界定可判定性边界。这些规律源自大量工程实践的经验总结，**从未被形式化证明**。

本工作的方法论立场（专著 §1.4.1 同口径）：SE 的"近公理"规律可以且应当提升为**推理起点地位 + 经验可证伪内容**的工程公理。本文聚焦其中一支——经验自免疫——给出：Lean 4 机检的条件定理链（隔离⟹灭绝、GW 灭绝概率、几何律、超临界发散）、预注册的大样本实证、以及机制层修正（分支衰减 vs 累积-竞争）。这是把 SE 经验定律"形式化-实测化推进"的一次实例，而非凭空提出公设。

## 2.6 Formal Verification Tooling

定理链在 **Lean 4**（Moura & Ullrich, 2021）中机检，零 `sorry`（专著附录 B.2–B.5）。软件工程中形式化验证的应用先例（协议验证、并发正确性）支撑了"工程承诺以可机检定理呈现"的可行性；本文的贡献之一是此类条件定理（"对满足分支性与乘性压缩的系统，隔离使投毒谱系以概率 1 灭绝"）在智能体记忆安全问题上的首次应用。

---

## 参考文献（本节约用）

1. Amodei, D., Olah, C., Steinhardt, J., Christiano, P., Schulman, J., & Mané, D. (2016). *Concrete Problems in AI Safety*. arXiv:1606.06565.
2. Anthropic Alignment Team (2025). *Natural emergent misalignment from reward hacking in production RL*. arXiv:2511.18397.
3. Brooks, F. P. (1987). *No Silver Bullet: Essence and Accidents of Software Engineering*. IEEE Computer, 20(4), 10–19. DOI: 10.1109/MC.1987.1663532.
4. Chroma Research (2024). *Context Rot: How Increasing Input Tokens Impacts LLM Performance*. Technical Report.
5. Conway, M. E. (1968). *How do committees invent?* Datamation, 14(4), 28–31.
6. Gilbert, S., & Lynch, N. (2002). *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services*. ACM SIGACT News, 33(2), 51–59. DOI: 10.1145/564585.564601.
7. Harris, T. E. (1963). *The Theory of Branching Processes*. Springer.
8. Hsieh, C.-P., et al. (2024). *RULER: What's the Real Context Size of Your Long-Context Language Models?* arXiv:2404.06654.
9. Krakovna, V., et al. (2020). *Specification Gaming: The Flip Side of AI Ingenuity*. DeepMind Blog.
10. Lehman, M. M. (1980). *Programs, Life Cycles, and Laws of Software Evolution*. Proceedings of the IEEE, 68(9), 1060–1076. DOI: 10.1109/PROC.1980.11805.
11. Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. TACL, 12.
12. MemoryGraft (2025). *Persistent Compromise of LLM Agents via Poisoned Experience Retrieval*. arXiv:2512.16962.
13. Moura, L., & Ullrich, S. (2021). *The Lean 4 Theorem Prover and Programming Language*. CADE-28, LNCS 12699, 625–635. DOI: 10.1007/978-3-030-79876-5_40.
14. OEP (2026). *Poisoning Self-Evolving LLM Agents via Locally Correct but Non-Transferable Experiences*. arXiv:2605.18930.
15. Shumailov, I., Shumaylov, Z., Zhao, Y., Papernot, N., Anderson, R., & Gal, Y. (2024). *AI models collapse when trained on recursively generated data*. Nature, 631, 755–759. DOI: 10.1038/s41586-024-07566-y.
16. Turing, A. M. (1936). *On Computable Numbers, with an Application to the Entscheidungsproblem*. Proceedings of the LMS, 42, 230–265.


## 3. Model

## 3.1 记号（Notation）

| 符号 | 含义 | 实测/设定 |
| :--- | :--- | :--- |
| $Z_n$ | 第 $n$ 代记忆库中毒株（P1 谱系）条目数（池大小） | 逐代追踪 |
| $M$ | 记忆窗口容量（FIFO） | 默认 $16$；敏感性档 $M=8,32$ |
| $w_n$ | 第 $n$ 代新写入的毒株条目数（fresh write） | selective：随 $Z_n$ 变化；full-append：$\equiv 1$（逐代核对） |
| $X_i$ | 分支过程的单亲后代数 | $E[X]=\hat m$（经验估计） |
| $\sigma$ | 门禁过滤参数（写出通过率） | 随机过滤 $\sigma=0.5$（C2）；隔离 $\sigma=1$ |
| $\hat m$ | 每亲繁殖数估计（bootstrap CI） | 见各实验档 |

**符号纪律**：$M$ 为记忆容量（实验档名 `_W8/_W32` 中的窗口参数），$w_n$ 为每代写入——两者在本文中严格区分。

## 3.2 两个传播机制（核心主张 1）

**机制 A：分支衰减（selective 转写协议）**。智能体仅将当前会话中被判定相关的条目转写进记忆，后代数依赖亲代毒株的转写倾向：

$$Z_{n+1}=\sum_{i=1}^{Z_n} X_i,\qquad E[Z_{n+1}\mid Z_n]=\hat m\,Z_n$$

经典 Galton-Watson 分支过程（Harris, 1963）：期望传播按几何律 $E[Z_n]=\hat m^n E[Z_0]$ 演化；灭绝概率为生成函数 $\varphi(s)$ 的最小不动点（Lean T1）；亚临界（$\hat m<1$）指数衰减（Lean T2）。**该机制的判据**：$w_n$ 随 $Z_n$ 变化（分支依赖）。

**机制 B：线性累积-容量竞争（full-append 转写协议）**。智能体将每代经验全量追加进记忆库（向量库直写/无转写衰减），毒株写入恒定：

$$Z_{n+1}=Z_n+w_n,\qquad w_n\equiv 1\ \text{(实测)}$$

未饱和段线性增长 $Z_{n+1}=Z_n+1$；当 $Z_n$ 触及容量 $M$ 后进入 FIFO 竞争稳态（新写条目挤占最旧条目），稳态池大小由容量竞争决定（实测 C0-full 稳态 $5/16$）。**该机制的判据**：$w_n$ 恒定、不依赖 $Z_n$（累积写入）。

**机制判别的直接证据（逐代 offspring 核对）**：full-append 档每代新写 P1 恒为 1（$w_n\equiv1$、$Z_{n+1}=Z_n+1$ 线性累积，实测 Z=[1,2,2.917,3.917,3.917,4.917,4.917,4.917]）；分支过程要求的"后代数依赖亲代种群"不成立。**由此，预注册假说 S-H3（GW 匹配）被机制证据证伪，理论修订为机制 B**（见 §8 机制修正叙事）。分支衰减（机制 A）仍在 selective 协议下成立（几何律 $R^2=0.958$，主实验；$R^2=0.923$，H1AC 大样本）。

## 3.3 容量控制参量（核心主张 2 之半）

记忆窗口容量 $M$ 决定机制 B 的传播结局（SUPERCRITICAL 档，full-append，Flash）：

| $M$ | $\hat m$（boot95 CI） | g7 存活率 | 结局 |
| :--- | :--- | :--- | :--- |
| 8 | 0.829（[0.739, 0.875]） | 0 | **灭绝**（写入侧即被容量压制） |
| 16 | 1.166（[1.156, 1.176]） | 1.0 | **持续累积**（工程语义的超临界） |
| 32 | 1.25（退化 CI，6 链全同） | 1.0 | **线性增长**（$Z=[1,\dots,8]$，未饱和） |

**临界容量 $M_c\in(8,16)$**：容量单调性成立——$M\le M_c$ 时毒株池被压制至灭绝，$M>M_c$ 时单调累积不灭绝。$M$ 因此是传播的**控制参量**（而非模型参数）。

## 3.4 架构决定机制（核心主张 2）

同一模型族（Flash）下切换记忆架构即切换机制：

| 架构 | 机制 | $\hat m$ / 传播 | 判据 |
| :--- | :--- | :--- | :--- |
| selective 转写 | 分支衰减（A） | $\hat m\in[0.56,0.98]$（跨模型，模型特定） | $w_n$ 依赖 $Z_n$；几何律成立 |
| full-append | 累积-竞争（B） | $Z$ 线性累积，容量 $M$ 定结局 | $w_n\equiv1$；$M_c\in(8,16)$ |

**变量是架构，不是模型**：同一 Flash 档，selective 对照（2 链）$Z$ 恒 1、记忆收缩至 3（亚临界），full-append C0（12 链）$Z$ 线性累积至 5/16（超临界）——分叉完全由转写协议决定。这一结论与公理 IV 适用域口径一致：无门禁下 $\hat m$ 是模型-任务-位点联合参数（$[0.29,1.00]$，跨模型 $[0.56,0.98]$），但**机制类别由架构决定，不随模型迁移**。

## 3.5 预注册假说清单（实验在 §5，结果在 §6）

| 假说 | 命题 | 判据 |
| :--- | :--- | :--- |
| **S-H1** | full-append 无门禁下 $\hat m>1$ 且 CI 下限 $>1$ | bootstrap 95% CI |
| **S-H2** | 未饱和段存活率 1.0 | g7 存活率 |
| **S-H3** | GW 分支匹配（$\to$ **被机制证据证伪，修订为机制 B**） | 逐代 $w_n$ 核对 |
| **S-H4** | 隔离跨机制截断累积 | C3-full 12/12 |
| **B-H1a** | 标记门压缩配对差 $>0$（$\to$ 不成立） | 符号翻转置换 $p<0.05$ |
| **B-H1c** | 乘性压缩律 $\hat r_{C2}/\hat r_{C0}\in[0.35,0.65]$ 且 CI 完全落入 | 点+CI 双判据 |
| **B-H2** | 大样本几何律复验 $R^2\ge0.8$ | log-linear |
| **X-H1/X-H4** | 跨模型隔离保证；防御不依赖模型 | 24/24 链 $Z_1=0$ |
| **T-H1/T-H4** | 跨任务族隔离保证；毒株传播受任务族调节 | 48/48 链；配对 $p<0.05$ |


![Mechanism schematic: branching decay (selective replay) vs. linear accumulation-competition (full append)](figures/fig-mechanism.png)

*Figure 1. Two propagation mechanisms: A) branching decay under selective replay (Galton-Watson, geometric law, extinction probability = least fixed point); B) linear accumulation-competition under full append (constant write $w_n\equiv1$, FIFO competition at capacity $M$, critical $M_c\in(8,16)$).* (data: DeepSeek-V4.1-Flash-1017, chain means)

## 4. Formalization

## 4.1 模型结构

传播模型为**分支过程**（`BranchingProcess` 结构，每代一个有限支撑 PMF）：未终审经验的跨代传播中，双盲隔离门禁的选择度 $\sigma$ 将名义繁殖均值 $\mu$ 压缩为有效繁殖数

$$m = \mu(1-\sigma) \quad \text{(乘性压缩律)}$$

所有定理以**条件定理**呈现：结构前提（如 $m<1$）为显式假设，"真实系统满足该前提"由 §5–§6 实测支撑，不在形式系统内断言——这是三层知识地位（定理层/经验层/工程层）在本文的执行（专著 §1.4.2 同口径）。

## 4.2 定理链（Lean 4 机检，零 `sorry`）

**T1 期望几何律**（`expected_population_geometric`，归纳证明）：$E[Z_n]=m^n E[Z_0]$。

**T2 亚临界概率灭绝**（`subcritical_extinction_in_probability`）：由 Markov 不等式与几何衰减，$m<1$ 时存活概率 $P(Z_n\ge1)\to0$。这是隔离晋升门禁有效性的定量核心：门禁把 $m$ 压到 $<1$，谱系以概率 1 消亡。

**T3 隔离压缩后代**（`quarantine_compresses_offspring`）：$\sigma$ 越严格，有效繁殖数越小；完全隔离（$\sigma=1$）使 $m=0$，谱系单代内归零。**应用条件**：分支性 + 乘性压缩——在 selective 架构下实测满足（几何律 $R^2=0.958$）；在 full-append 架构下分支前提不成立，隔离的有效性由实测直接给出（C3-full 12/12，mem 恒 6、$Z$ 恒 1），机制修正如实记录（§8）。

**T4 超临界不灭绝**（`galton_watson_non_extinction` + `supercritical_expectation_diverges`）：$m>1$ 时，灭绝概率为生成函数 $\varphi$ 在 $[0,1]$ 上的**最小不动点** $q=\min\{s\in[0,1]:\varphi(s)=s\}<1$——以正概率永不灭绝；期望 $E(n)\to+\infty$。证明采用初等生成函数不动点分析（单调夹逼 + 多项式截断），避免对 $\varphi$ 连续性的依赖。

## 4.3 定理-应用映射

| 定理 | 断言 | 应用侧 |
| :--- | :--- | :--- |
| T1 | $E[Z_n]=m^nE[Z_0]$ | 几何律判据（S-H2/B-H2 的期望侧） |
| T2 | $m<1 \Rightarrow P(Z_n\ge1)\to0$ | 隔离/随机过滤压灭谱系（C2 存活率 0.062 vs C0 0.750） |
| T3 | $\sigma\!\uparrow \Rightarrow m\downarrow$；$\sigma=1\Rightarrow m=0$ | 隔离不变性（S-H4/T-H1/X-H1） |
| T4 | $m>1 \Rightarrow q<1$，期望发散 | 机制 B"持续累积不灭绝"的期望侧对照（工程语义超临界） |

## 4.4 形式化的边界

$\hat m$、$M_c$、$\sigma$ 的**数值**为经验/工程层参数，不入形式化接口；形式化保证的是**结构蕴含**（若前提成立则结论必真），数值由预注册实测估计。这一分工避免了两类错误：把经验常数当定理、把定理当经验常数。


## 5. Experimental Setup

## 5.1 预注册原则

全部判据先于实验固定（假说清单见 §3.5）：显著性门槛（$p<0.05$ 置换/单侧）、判读单位（链均 vs 池化，见 5.5）、方向性命题一律预先声明。实验计划文档随判读产物存档（`EXPERIMENT_PLAN_AXIOM4_SUPERCRITICAL.md`、`EXPERIMENT_PLAN_AXIOM4_H1AC_BOOST.md`），任何口径修订在 §9 如实记录（如 H1AC 池化口径失效）。

## 5.2 模型档

| 档 | 模型 | 用途 |
| :--- | :--- | :--- |
| 主实验 | DeepSeek v4-pro（temperature 0.7） | selective 协议，4 条件 × 12 会话 × 6 代 = 288 会话 |
| 跨模型 | Kimi `kimi-for-coding` + 同 pro 协议 | X-H1/X-H4，288 会话 |
| SUPERCRITICAL | DeepSeek-V4.1-Flash-1017 | full-append/容量档/selective 对照（与预注册模型档的偏离已在计划 §9 记录） |
| H1AC | 同 Flash | 160 链双毒株大样本 |

## 5.3 传播协议

- **毒株规范注入**：第 0 代注入 1 条携带谱系标记（P1/P2）的种子经验；逐代转写（selective：仅被判定相关者转写；full-append：全量追加）；
- **谱系追踪**：每条记忆条目携带 lineage 标记，$Z_n$=第 $n$ 代毒株谱系条目数（判读单位）；
- **双盲过滤（DRAFT_SUSPECT）**：标记门条件（C1）对疑似条目打标但不阻断；隔离门禁（C3/C2）物理阻断未终审条目（五重机械判据）。

## 5.4 条件矩阵

- **selective**：C0（无门禁）/ C1（标记门）/ C2（随机过滤 $\sigma=0.5$）/ C3（隔离 $\sigma=1$）；
- **full-append**：C0-full / C1-full / C3-full（各 12 会话 × 8 代）；容量档 $M=8$ / $M=32$（各 6 会话 × 8 代）；selective 对照（2 会话 × 6 代）；
- **H1AC（Flash 双毒株）**：C0（48）/ C1（48）/ C2（64），6 代。

## 5.5 判读口径

- bootstrap CI（$10^4$ 重采样）估计 $\hat m$ 及比值 CI；符号翻转配对置换（$10^4$）检验标记门配对差；
- **链均 vs 池化**：传播实验的判读单位取链均（per-parent 池化在 C2 下因幸存者偏差失效——末代存活率仅 6%，池化比值 1.017 无意义；已在计划 §9 记录并改用链均）；
- 几何律复验：log-linear 拟合 $R^2$；
- **功效**（pro 档标记门）：配对差 $d=0.167$、$sd=0.432$、C1/C0 比值 0.529 → 当前 $n=12$ 功效仅 0.38，达 0.8 需 $n\approx48$（`e_power_markgate.py/.json`）——H1AC 档以 48 配对补齐该缺口。

## 5.6 可复现性

- 判读脚本：`e_supercritical_judge.py`/`judge2.py`/`sh3.py`、`e_cross_task_judge.py`、`e_h1ac_judge.py`（全部入 git）；
- 原始会话：`axiom4_results_*.json`（SUPERCRITICAL/H1AC/跨模型/跨任务族全套入 git）；
- 环境：模型档固定、temperature 0.7、温度与采样参数随会话归档。


## 6. Results

## 6.1 机制与容量（SUPERCRITICAL 档，Flash，full-append）

**S-H1 超临界 ✅**：C0-full $\hat m=1.166$（bootstrap 95% CI $[1.156,1.176]$），CI 下限 > 1。Z 轨迹 $[1,2,2.917,3.917,3.917,4.917,4.917,4.917]$：未饱和段单调线性累积（g0–g3），g4 触及容量（mem 6→16）后 FIFO 竞争稳态 $Z\approx5/16$（g5–g7 恒 4.917）。

**S-H2 存活率 ✅**：g7 存活率 1.0（12/12 链无灭绝）。

**S-H3 GW 匹配 ✗（被机制证据证伪）**：逐代 offspring 核对——每代新写 P1 恒为 1（$w_n\equiv1$，$Z_{n+1}=Z_n+1$），分支过程要求的"后代数依赖亲代种群"不成立。机制 B（线性累积-容量竞争）取代 GW 匹配；**修订叙事见 §8**。

**S-H4 隔离不变性 ✅**：C3-full 12/12 链 mem 恒 6、$Z$ 恒 1——隔离在 full-append 架构下同样截断传播（即使分支前提不成立）。

**容量控制参量**：$M=8$ 时 $\hat m=0.829$（$[0.739,0.875]$），g7 存活率 0（灭绝）；$M=32$ 时 $\hat m=1.25$（退化 CI，6 链全同），$Z=[1,\dots,8]$ 线性增长未饱和。**临界 $M_c\in(8,16)$**，容量单调性成立。

**selective 对照（Flash）**：2 链 $Z$ 恒 1、记忆收缩至 3（$\hat m=1.0$ 临界边界；H1AC 大样本 48 链 $m\approx0.92$ 支持弱亚临界）——同一模型档下与 C0-full 构成架构分叉（§3.4）。

## 6.2 标记门与乘性律（H1AC，Flash，160 链）

**B-H1a 标记门压缩 ✗**：配对（C0 vs C1，48 对）差值 $\bar d=+0.020$（均值被少数大差对拉动；正差仅 15/48，配对层面多数反预期）、符号翻转置换 $p=0.69$——**标记门零压缩**。三重独立确认：pro 主实验（$p=0.15$，C1/C0 比值 0.529、压缩 47%，不显著）→ SUPERCRITICAL C1-full（12/12 逐代同轨）→ H1AC（大样本配对）。功效侧：H1AC 的 $n=48$ 已达 pro 档功效分析所需样本（功效 0.848），排除"功效不足"解释。

**B-H1c 乘性压缩律（部分）**：链均写入率比 $\hat r=\mu_{C2}/\mu_{C0}=0.422/0.905=\boldsymbol{0.466}\in[0.35,0.65]$（乘性预测 0.5 吻合）；bootstrap CI $[0.333,0.602]$——下界微出目标带 0.017。判据定义（点估计+CI 双判据）：点估计 ✅、CI ⚠️。存活率佐证：C2 末代 0.062 vs C0 0.750——随机过滤真实压低传播。

**B-H2 几何律复验 ✅**：C0/C1 的 $\log Z$ 对代际线性拟合 $R^2=0.923$、$m\approx0.92$（Flash selective 临界/弱亚临界，与主实验 $R^2=0.958$ 一致）。

**P2 事件倍增未达成**：$\mu_{P2}\approx0.001$（250 vs 1 条）——双毒株设计的第二事件通道未被模型采纳，如实记录（§10）。

## 6.3 跨模型（288 会话，selective）

| 模型 | $\hat m$（boot95） | 隔离 24/24 链 $Z_1=0$ |
| :--- | :--- | :--- |
| DeepSeek v4-pro | 0.560（[0.294, 0.735]） | ✅ |
| Kimi | 0.983（[0.944, 1.000]） | ✅ |
| Flash（selective 对照） | 1.0（临界） | ✅ |

**X-H1/X-H4 ✅**：无门禁下 $\hat m$ 模型特定（转写衰减倾向异质），但隔离保证跨模型成立——防御不依赖模型行为。

## 6.4 跨任务族（144 链，selective）

隔离 48/48 链灭绝（T-H1 ✅）；毒株传播受任务族调节（T-H4 配对 $p=0.026$ ✅）；无门禁 $\hat m$ 为模型-任务-位点联合参数（跨任务族区间 $[0.29,1.00]$）——**跨族不可迁移是实测结论而非缺陷**（§9）。

## 6.5 工程侧（生产现场，关联实证）

模式 23/24 生产闭环：18 份报告晋升 14、拦截 4；晋升比例 1.00、错误拦截 1.00、泄漏 0。工程闭环与理论通道的连接为开放项（§10），不构成跨通道因果声称。

---

## 6.6 正式判读表（数据直出判读 JSON）

**表 1：机制与容量（SUPERCRITICAL 档，Flash，full-append，链均）**

| 条件 | 容量 $M$ | $n$ | $\hat m$（boot95 CI） | Z 末代（g7） | 存活率 g7 | 判据 |
| :--- | :---: | :---: | :--- | :---: | :---: | :---: |
| selective ctrl | 16 | 2 | 1.0（[1.0,1.0]） | 1.0 | 1.0 | 临界边界（弱亚临界，见 H1AC） |
| C0-full | 16 | 12 | **1.166**（[1.156,1.176]） | 4.917（稳态 5/16） | 1.0 | **S-H1 ✅ S-H2 ✅** |
| C1-full | 16 | 12 | 1.165（[1.163,1.167]） | 4.917 | 1.0 | 标记门零压缩 |
| C3-full | 16 | 12 | 1.0（[1.0,1.0]） | 1.0 | 1.0 | **S-H4 ✅**（mem 恒 6） |
| W=8 | 8 | 6 | 0.829（[0.739,0.875]） | 0.0 | 0.0 | **灭绝**（$M\le M_c$） |
| W=32 | 32 | 6 | 1.25（退化 CI） | 8.0 | 1.0 | 线性增长未饱和（$M>M_c$） |

临界容量：$M_c\in(8,16)$，容量单调性成立（`capacity_monotone=True`）。

**表 2：标记门与乘性律（H1AC 档，Flash，160 链，链均）**

| 假说 | 判读量 | 数值 | 判据 | 结论 |
| :--- | :--- | :--- | :--- | :---: |
| B-H1a | 配对差 $\bar d$（C0−C1） | +0.020；正差 15/48；$p=0.69$（符号翻转 10⁴） | $p<0.05$ | **✗ 零压缩** |
| B-H1c | 链均写入率比 $\hat r=\mu_{C2}/\mu_{C0}$ | 0.422/0.905 = **0.466**；CI [0.333,0.602] | 点∈[0.35,0.65] 且 CI 全落入 | ⚠️ 点 ✅ CI 下界微出（0.017） |
| B-H2 | log-linear $R^2$ | **0.923**；slope −0.086（$m\approx0.92$） | $R^2\ge0.8$ | **✅** |
| — | 存活率末代 | C0=0.750 / C1=0.729 / **C2=0.062** | 佐证 | 随机过滤真实有效 |

**表 3：跨模型（288 会话，selective；隔离 24/24 链 $Z_1=0$）**

| 模型 | $\hat m$（boot95 CI） | 隔离保证 | 判据 |
| :--- | :--- | :---: | :---: |
| DeepSeek v4-pro | 0.560（[0.294,0.735]） | ✅ | **X-H1/X-H4 ✅** |
| Kimi | 0.983（[0.944,1.000]） | ✅ | 同上 |
| Flash（selective 对照） | 1.0（临界） | ✅ | 同上 |

**表 4：跨任务族（144 链，selective）**

| 判据 | 数值 | 结论 |
| :--- | :--- | :---: |
| T-H1 隔离 48/48 链灭绝 | 48/48 | ✅ |
| T-H4 毒株传播受任务族调节 | 配对 $p=0.026$ | ✅ |
| 无门禁 $\hat m$ 区间 | [0.29, 1.00]（模型-任务-位点联合参数） | 跨族不可迁移 |

**表 5：工程侧（生产现场，模式 23/24）**

| 指标 | 数值 |
| :--- | :---: |
| 报告总数 | 18 |
| 晋升 / 拦截 | 14 / 4 |
| 晋升比例 | 1.00 |
| 错误拦截 | 1.00 |
| 泄漏 | 0 |


![Poison lineage trajectories by architecture and capacity](figures/fig-trajectories.png)

*Figure 2. Poison lineage entries per generation for full-append conditions across capacity $M\in\{8,16,32\}$ and the selective control ($M=16$). The critical band $8<M_c\leq16$ separates extinction from persistence. Data: DeepSeek-V4.1-Flash-1017, chain means.*

## 7. Discussion

## 7.1 防御依赖隔离而非标记（核心工程结论）

三档实验、两架构收敛到同一分离：

- **标记门零压缩**：pro $p=0.15$（C1/C0 比值 0.529、压缩 47%，不显著）、C1-full 12/12 逐代同轨、H1AC 大样本配对 $\bar d=0.020$（$p=0.69$）——软标记是可被模型忽略的信号；
- **隔离/过滤有效**：隔离跨模型（24/24）、跨任务族（48/48）、跨架构（C3-full 12/12 mem 恒 6）截断传播；随机过滤（$\sigma=0.5$）大样本下把存活率压到 0.062。

机制解释：标记是**决策层的软约束**（模型可无视），隔离是**写入层的结构阻断**（未终审条目物理不可达）。防御设计因此应以写入层门禁为主体，标记仅作审计线索。

## 7.2 架构决定机制（理论结论）

转写协议改变传播的**数学结构**而非仅其参数：selective→分支衰减（GW，$\hat m$ 模型特定），full-append→线性累积-容量竞争（$w_n\equiv1$，$M_c$ 定结局）。推论：**记忆架构是安全属性而非性能属性**——"全量追加"在信息保留上有用，在投毒传播上是放大器；容量 $M$ 是可直接配置的传播控制旋钮（$M_c\in(8,16)$）。

## 7.3 模型异质性

无门禁 $\hat m$ 跨模型 $[0.56,0.98]$、跨任务族 $[0.29,1.00]$——传播强度是模型-任务-位点联合参数，不可跨域迁移（§9）。隔离保证与之无关：无论 $\hat m$ 在区间何处，$\sigma=1$ 一律截断。这给出了一条**与模型无关的安全承诺**：防御的可靠性不随模型换代漂移。

## 7.4 乘性律的边界

B-H1c 点估计支持（$\hat r=0.466$，预测 0.5 吻合）但 CI 下界微出（0.017）。诚实判读：乘性压缩律在**期望层**获得大样本支持，在**判据层**（CI 完全落入目标带）未完全通过；池化口径的幸存者偏差失效提醒——传播实验的统计口径必须在预注册阶段固定，事后补救会引入选择性报告风险。

## 7.5 对 SE 学科的含义

本文把一条 SE"近公理"规律（经验自免疫）从经验观察提升为**可机检条件定理 + 预注册实测**的工程公理（§2.5 定位）。方法论含义：Brooks/Lehman/Conway 式经验定律的下一代形式，可以是"条件定理+实测支撑"结构，而非停留在归纳总结。


## 8. Mechanism Revision Narrative

## 8.1 预注册假设

实验计划预先登记：full-append 无门禁下的毒株传播服从 **Galton-Watson 分支过程**（S-H3）：后代数随亲代种群扩张，$E[Z_{n+1}\mid Z_n]=\hat m Z_n$，超临界（$\hat m>1$）时以正概率永不灭绝（Lean T4），预期观测到谱系倍增型增长。

## 8.2 机制证据与证伪

逐代 offspring 核对（`e_supercritical_sh3.py`）发现与分支过程矛盾的结构性事实：

1. **写入恒定**：每代新写 P1 恒为 1 条（$w_n\equiv1$），与 $Z_n$ 无关；
2. **线性累积**：$Z_{n+1}=Z_n+1$（未饱和段），实测 Z=[1,2,2.917,3.917,3.917,4.917,4.917,4.917]（g0–g7 全代）——无倍增、无超线性；
3. **容量饱和**：触及 $M=16$ 后进入 FIFO 竞争稳态（$5/16$），而非分支过程的随机灭绝路径。

结论：**S-H3 被机制证据证伪**。full-append 的传播是**线性累积-容量竞争**（机制 B），"超临界"保留为工程语义（持续累积不灭绝），精确机制不再是 GW 分支。

## 8.3 修订后的理论

- 机制 A（分支衰减）仍适用于 selective 架构（几何律 $R^2=0.958$ / $0.923$，Lean T1/T2 条件成立）；
- 机制 B（累积-竞争）适用于 full-append：$Z_{n+1}=Z_n+w_n$（$w_n\equiv1$），结局由容量 $M$ 决定（$M_c\in(8,16)$）；
- 隔离不变性（S-H4）与机制无关——C3-full 12/12 在分支前提不成立处仍截断传播，说明隔离承诺比其形式化前提更稳健。

## 8.4 论文处理原则

- **不隐藏**：证伪事实在 Results（§6.1）与本文完整呈现；
- **不混淆**：机制 B 的"持续累积"与 GW 的"超临界"是不同数学对象，全文符号纪律（$w_n$ vs $M$ vs $\hat m$）防止误读；
- **方法论资产**：此案例演示了预注册假说如何被结构证据而非显著性检验证伪——机制识别优先于统计推断。

> 论文定稿时本节可与 §7.2 合并；专著处理见 `docs/preface/03-axioms-and-invariance.md` 公理 IV SUPERCRITICAL 段（完成态：机制区分+术语声明）。


## 9. Scope and Generalizability

## 9.1 适用边界（四重）

1. **任务族**：主实验任务族为测试用例编写（pytest），四变体（正确性/边界/负例/回归）；跨任务族传播强度的不可迁移（$\hat m\in[0.29,1.00]$）是实测结论——本文不声称对任意任务族的数值预测；
2. **通道**：理论实证限定于**纯社会传播通道**（SubstratePass 关闭，无物理执行反馈）；生产现场的工程闭环（模式 23/24）满足五重物理判据，其与理论通道的定量连接（$q$ 回路与 $\hat m$ 耦合）为开放项（§10.4）；
3. **模型**：三模型档（pro/Kimi/Flash），$\hat m$ 模型特定；隔离保证不依赖模型；
4. **架构**：selective / full-append / 容量档 $M\in\{8,16,32\}$；向量库直写以 full-append 为代理，未单列。

## 9.2 保证与数值的分层

- **跨边界保证（理论层）**：隔离（$\sigma=1$）截断传播——跨模型、跨任务族、跨架构实测成立，Lean 机检（T3 条件定理）支撑其结构必然性；
- **边界内数值（经验层）**：$\hat m$、$M_c$、乘性律参数——仅对实测域有效，跨域迁移禁止；
- **工程层**：生产现场五重判据为部署裁决，其与理论参数的耦合列为开放项。

## 9.3 收缩声明

本文对"无门禁智能体记忆系统的投毒传播"给出机制分类（架构决定）与防御分离（隔离>标记），不声称：任意任务族/模型的定量预测、跨通道因果、记忆系统的整体安全性。超出范围的推论视为读者延伸而非本文主张。


## 10. Limitations and Future Work

## 10.1 标记门效应的模型异质性

pro 档标记门方向为负（C1/C0 比值 0.529，$p=0.15$，功效不足 $n=12$），Flash 档零压缩（$p=0.69$，$n=48$ 功效充足）。两档方向不一致的原因未归因：可能是模型对软信号（DRAFT_SUSPECT 标记）的采纳倾向差异，也可能是任务族调节。**future work**：同协议跨模型配对比较标记采纳率。

## 10.2 双毒株事件倍增失败

H1AC 的 P2 毒株几乎不传播（$\mu\approx0.001$）——模型未采纳 P2 的事件通道，"事件密度倍增"设计目标未达成。P1 的 48/64 样本量已远超主实验，但双毒株相互作用的统计设计需重新构造（如提高事件信号强度）。

## 10.3 统计口径教训

H1AC 池化 per-parent 口径在 C2 下因幸存者偏差失效（末代存活仅 6%，池化比值 1.017 无意义）——已改用链均并在计划 §9 记录。启示：传播实验的判读单位必须在预注册阶段固定；B-H1c 的 CI 下界微出（0.017）同样提示边界判据需要更保守的界定或更大样本。

## 10.4 双层连接未定理化

生产现场工程闭环（晋升/拦截/泄漏，五重判据）与理论通道（纯社会传播，$\hat m$）的定量连接（$q$ 回路 ↔ $\hat m$ 耦合）尚未定理化——本文不声称工程闭环是理论通道的实证（专著 §1.4.5 同口径）。**future work 首位**：构造双层通道的耦合模型。

## 10.5 生态效度

主实证集中于测试编写任务族；跨任务族仅隔离保证获得推广证据（48/48 链），乘性律与容量临界的跨族推广未测。向量库直写架构未单列实验（以 full-append 为代理）。

## 10.6 其他

- 模型档时间快照：三模型均为 2025–2026 代际，结论对新模型族的漂移未验证；
- 温度 0.7 固定，未扫描温度对 $w_n$ 的影响；
- 判读脚本依赖确定性重组种子，跨平台浮点差异未测。


## 11. Conclusion

## 11.1 结论（对应摘要三句主张）

1. **机制**：无门禁的累积型（full-append）智能体记忆架构下，注入毒株持续累积不灭绝——机制为**线性累积-容量竞争**（每代恒定写入 $w_n\equiv1$、$Z_{n+1}=Z_n+w_n$），实测 $\hat m=1.166$（boot95 CI $[1.156,1.176]$），容量饱和后 FIFO 竞争稳态 $5/16$；
2. **架构效应**：传播机制由架构决定而非模型——selective 转写=分支衰减（GW，跨模型 $\hat m\in[0.56,0.98]$），full-append=累积-竞争；记忆容量 $M$ 为控制参量，临界 $M_c\in(8,16)$（$M\le M_c$ 灭绝、$M>M_c$ 持续累积）；
3. **隔离不变性**：隔离（$\sigma=1$）跨机制截断传播——Lean 4 机检条件定理（T3）+ 跨模型 24/24、跨任务族 48/48、full-append 12/12 实测；标记门三档零压缩（pro $p=0.15$ / C1-full / H1AC $p=0.69$）——**防御依赖隔离而非标记**。

## 11.2 贡献回顾

1. 机制层：架构决定机制的两分法 + 容量控制参量（§3）；
2. 形式化层：Lean 4 机检定理链，零 `sorry`（§4）；
3. 实证层：预注册、跨模型×跨架构×跨任务族×大样本闭合判据（§5–§6）；
4. 工程含义：隔离优先的防御设计原则（§7.1）+ 诚实机制修正案例（§8）。

## 11.3 学科含义

软件工程的经验定律可以且应当提升为"条件定理 + 实测支撑"的工程公理结构；本工作提供了完整实例（形式化 + 预注册 + 机制修正），并给出可迁移的方法论模板（三层知识地位 + 预注册判据 + 机制识别优先）。


## Appendix

## A. 判读脚本与数据清单

**判读脚本**（全部入 git）：

| 脚本 | 产出 | 用途 |
| :--- | :--- | :--- |
| `e_supercritical_judge.py` / `judge2.py` | `e_supercritical_judgement2.json` | SUPERCRITICAL 档：$\hat m$/CI、Z 轨迹、存活率、容量敏感性 |
| `e_supercritical_sh3.py` | `e_supercritical_sh3.json` | 逐代 offspring 核对（S-H3 证伪机制证据） |
| `e_cross_task_judge.py` | 跨任务族判读 JSON | T-H1/T-H4 |
| `e_h1ac_judge.py` | `e_h1ac_judgement.json` | H1AC：B-H1a/B-H1c/B-H2（bootstrap/符号翻转 10⁴） |
| `e_power_markgate.py` | `e_power_markgate.json` | 功效分析（min_n=48） |

**原始会话**（全部入 git）：`axiom4_results_supercritical*.json`（C0/C1/C3-full、W8/W32、w1–w4 shards）、`axiom4_results_flash_selective_ctrl.json`、`axiom4_results_h1ac_*.json`（C0/C1/C2/smoke）、跨模型/跨任务族会话 JSON。

**预注册计划**：`EXPERIMENT_PLAN_AXIOM4_SUPERCRITICAL.md`、`EXPERIMENT_PLAN_AXIOM4_H1AC_BOOST.md`（§9 判读回填与口径修订记录）。

**执行环境**：DeepSeek-V4.1-Flash-1017（scnet-flash 网关，temperature 0.7）；模型档偏离预注册 v4-pro 档的记录见 SUPERCRITICAL 计划 §9。

## B. 判读 JSON 关键数值表（与正文同源）

| 量 | 值 | 来源 |
| :--- | :--- | :--- |
| C0-full $\hat m$ | 1.166，boot95 [1.156,1.176] | e_supercritical_judgement2 |
| C0-full Z 轨迹 | [1,2,2.917,3.917,3.917,4.917,4.917,4.917] | 同上 |
| C0-full mem 轨迹 | [6,9,12,15,16,16,16,16]（g4 饱和） | 同上 |
| C1-full $\hat m$ | 1.165（[1.163,1.167]） | 同上 |
| C3-full | mem 恒 6、Z 恒 1（12/12） | 同上 |
| W=8 | $\hat m$=0.829（[0.739,0.875]）、g7 存活 0 | 同上 |
| W=32 | $\hat m$=1.25、Z=[1..8]、mem→27 | 同上 |
| S-H3 机制证据 | $w_n\equiv1$、pmf=[0,1]、criterion pass=False | e_supercritical_sh3 |
| B-H1a | $\bar d$=+0.0201、正差 15/48、p=0.6918 | e_h1ac_judgement |
| B-H1c | $\hat r$=0.4661、CI [0.3331,0.6017]、点✅ CI⚠️ | 同上 |
| B-H2 | R²=0.9233、slope −0.086 | 同上 |
| μ 链均 | C0=0.905 / C1=0.885 / C2=0.422 | 同上 |
| 存活率末代 | C0=0.750 / C1=0.729 / C2=0.062 | 同上 |
| 功效 | n=12→0.379、n=48→0.848、min_n=48 | e_power_markgate |
| 主实验效应量 | pair_diff=0.167、sd=0.432、C1/C0=0.529 | 同上 |

## C. 判读单位与口径声明

- 判读单位：**链均**（H1AC）；SUPERCRITICAL 为链均 Z/存活率；
- 池化口径在 C2 下因幸存者偏差失效（末代存活仅 6%，池化比值 1.017 无意义）——已改链均并在计划 §9 记录；
- bootstrap / 符号翻转置换各 10⁴ 次；B-H1a 以 replicate 级链均配对差（§2.3 预注册口径）判读。


## References

1. Amodei, D., Olah, C., Steinhardt, J., Christiano, P., Schulman, J., & Mané, D. (2016). *Concrete Problems in AI Safety*. arXiv:1606.06565.
2. Anthropic Alignment Team (2025). *Natural emergent misalignment from reward hacking in production RL*. arXiv:2511.18397.
3. Brooks, F. P. (1987). *No Silver Bullet: Essence and Accidents of Software Engineering*. IEEE Computer, 20(4), 10–19. DOI: 10.1109/MC.1987.1663532.
4. Chroma Research (2024). *Context Rot: How Increasing Input Tokens Impacts LLM Performance*. Technical Report.
5. Conway, M. E. (1968). *How do committees invent?* Datamation, 14(4), 28–31.
6. Gilbert, S., & Lynch, N. (2002). *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services*. ACM SIGACT News, 33(2), 51–59. DOI: 10.1145/564585.564601.
7. Harris, T. E. (1963). *The Theory of Branching Processes*. Springer.
8. Hsieh, C.-P., et al. (2024). *RULER: What's the Real Context Size of Your Long-Context Language Models?* arXiv:2404.06654.
9. Krakovna, V., et al. (2020). *Specification Gaming: The Flip Side of AI Ingenuity*. DeepMind Blog.
10. Lehman, M. M. (1980). *Programs, Life Cycles, and Laws of Software Evolution*. Proceedings of the IEEE, 68(9), 1060–1076. DOI: 10.1109/PROC.1980.11805.
11. Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. TACL, 12.
12. MemoryGraft (2025). *Persistent Compromise of LLM Agents via Poisoned Experience Retrieval*. arXiv:2512.16962.
13. Moura, L., & Ullrich, S. (2021). *The Lean 4 Theorem Prover and Programming Language*. CADE-28, LNCS 12699, 625–635. DOI: 10.1007/978-3-030-79876-5_40.
14. OEP (2026). *Poisoning Self-Evolving LLM Agents via Locally Correct but Non-Transferable Experiences*. arXiv:2605.18930.
15. Shumailov, I., Shumaylov, Z., Zhao, Y., Papernot, N., Anderson, R., & Gal, Y. (2024). *AI models collapse when trained on recursively generated data*. Nature, 631, 755–759. DOI: 10.1038/s41586-024-07566-y.
16. Turing, A. M. (1936). *On Computable Numbers, with an Application to the Entscheidungsproblem*. Proceedings of the LMS, 42, 230–265.
