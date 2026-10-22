# 第三章 工业智能体四大公理与因果不变性形式化定义
## Chapter 3: Four Cybernetic Axioms and Causal Invariance Formulation

> “没有形式化公理的体系，充其量只是经验的碎片；唯有将系统约束沉淀为数理不变性，自主软件工程才能从玄学演进为精密科学。”

---

### 3.1 导论：软件智能体状态空间的不变性

在经典软件工程中，系统演化是由人类工程师单步介入的确定性状态机。但在自主智能体（Autonomous Agents）接管代码变异、构建和重试后，系统进入了一个高维非线性的**随机动力学系统（Stochastic Dynamical System）**。

为了确保智能体在该随机动力学空间中不会漂移向发散态（Divergent State），整个控制论系统必须建立在不可动摇的**底层公理与因果不变性（Causal Invariance）**之上。

---

### 3.2 工业级智能体四大基础公理（The Four Foundational Axioms）

```mermaid
flowchart TD
    subgraph AxiomSystem["智能体控制论公理体系"]
        A1["公理 I：物理非信任公理<br/>(Axiom of Physical Non-Trustworthiness)"]
        A2["公理 II：注意力熵增公理<br/>(Axiom of Attention Entropy)"]
        A3["公理 III：变异因果律单调公理<br/>(Axiom of Monotonic Causal Mutation)"]
        A4["公理 IV：经验自免疫公理<br/>(Axiom of Crystallization Auto-Immunity)"]
    end
    
    A1 -->|"导出控制约束"| C1["物理 Exit 0 穿透 & 反自指审计"]
    A2 -->|"导出控制约束"| C2["任务级最小特权投影 (PoLP Context)"]
    A3 -->|"导出控制约束"| C3["幂等变异 Journal & Mtime +1s 补偿"]
    A4 -->|"导出控制约束"| C4["草稿隔离区 (DRAFT_SUSPECT) & 终审晋升"]
```

#### 公理 I：物理非信任公理（Axiom of Physical Non-Trustworthiness）
* **数学表达**：设智能体内部认知状态输出为 $\hat{Y}_{agent}$，外部客观物理世界状态为 $Y_{phys} \in \{0, 1\}$（0 代表失败，1 代表物理通过）。
  $$ \lim_{k \to \infty} P\left( Y_{phys} = 1 \mid \hat{Y}_{agent} = \text{"SUCCESS"}, \text{Sensor}_{ext} = \emptyset \right) \le \epsilon \ll 1 $$
* **公理诠释**：在没有任何外部物理传感器（独立外部执行器、真实编译退出码、无桩 HTTP 探针）强介入的封闭推理链中，智能体声称“任务成功”的物理真实率趋近于零。一切未锚定于物理底座真实返回的完成声称，在控制论上均必须判定为非法伪信号。
* **适用边界扩展（隔离环境场景，2026-10-21）**：当压力测试等验证环境与开发环境完全隔离时，智能体无法直接穿透至该物理底座。此时公理 I 的要求转化为：**隔离环境的结果必须经独立审计通道（模式 02 探针 4）验证真实性、完整性与同质性后方可采信**——智能体自报或转述的隔离环境结果仍属非法伪信号。
* **学术锚点**：该公理形式化了人工智能安全文献的核心实证结论——无外部接地（Grounding）的模型自我报告不可信；且在可被欺骗的评价信号下，智能体必然涌现奖励欺骗（Reward Hacking）行为（Amodei et al., 2016；Huang et al., ICLR 2024；Anthropic, arXiv:2511.18397）。

#### 公理 II：注意力熵增与特权发散公理（Axiom of Attention Entropy）
* **数学表达**：设智能体注意力视野中包含的上下文集合为 $\mathcal{C}$，当前子任务的充要上下文集合为 $\mathcal{C}^*$。定义上下文特权冗余比 $\rho = |\mathcal{C} \setminus \mathcal{C}^*| / |\mathcal{C}^*|$。智能体产生越界破坏性变更的概率 $P_{violate}$ 满足：
  $$ P_{violate}(\rho) \ge 1 - e^{-\alpha \rho}, \quad (\alpha > 0) $$
* **公理诠释**：给智能体注入的无关工程文件、非目标接口契约越多（$\rho$ 越大），目标信号的注意力份额被稀释得越低，其无意识修改不相关源码、破坏全局单测的概率下界随无关质量增长律发散——几何膨胀下指数级、幂律膨胀下幂律级（形式化对应见附录 B.3）。必须对上下文施加**最小特权原则（Principle of Least Privilege, PoLP）**投影。
* **经验支撑与适用边界（形式化 + 实测，2026-10）**：稀释的单调性核心（无关质量增加 ⟹ 目标份额严格下降）为 Lean 4 机检定理；衰减率的**形态**取决于无关质量的增长律，属经验命题。在 Qwen2.5-1.5B/7B、上下文至 131k 的受控检索实验（E3/E3b）中：无关质量幂律增长占优（AIC 33/36 cell，几何 0 票），故指数下界 $1-e^{-\alpha\rho}$ 应读作最强情形参考，幂律分支给出与实测一致的主刻画；目标质量非增（弱前提）方向性成立而"目标质量恒定"被证伪——衰减由分子收缩与分母膨胀共同贡献；残差（sink）通道为动态通道，总非目标质量全程非减，填充口径的 SNR 系统性高估 35.8%–36.7%。**衰减参数并非常数**：近义对抗填充使 SNR 基线降至中性填充的 $1/2.25$（衰减指数不变），即理论承诺的是"给定增长参数的衰减"，参数本身由填充类型等外部条件标定。**口径映射声明**：定理中的 $a$ 是单目标 token 的注意力质量，实验中的 $a$ 是 needle 整段总质量；定理中的 $b$ 是全部非目标质量，实验中的 $b$ 是填充段总质量——这两条模型–现实映射是**未经证明的假设**，其成立性由残差通道漂移检验背书（附录 B.11）。**违约概率的传导边界（E4，2026-10-20）**：定理中的 $P_{\text{violate}}(\rho) = 1 - \operatorname{snr}(\rho)/\operatorname{snr}(0)$ 是**信噪比相对损失**，不是任务失败概率。E4 端到端实验（Qwen2.5-1.5B/7B needle 检索正确率与 E3 SNR 对齐）表明两者之间存在**补偿阈值 $W^*$**：$\rho < W^*$ 时模型的补偿机制（注意力 sink、KV cache 策略、长上下文训练对齐）抵消 SNR 衰减，任务正确率 ≈ 100%；$\rho > W^*$ 时补偿失效，正确率陡降。实测 $W^*_{1.5\text{B}} \approx 32\text{k–64k} < W^*_{7\text{B}} > 131\text{k} < W^*_{\text{Kimi}} \ge 1\text{M}$，与模型能力正相关。**违约下界 $P_{\text{violate}} \ge 1 - c^n$ 只在 $\rho > W^*$ 时传导为可观测的任务失败**；$\rho < W^*$ 时 SNR 虽已衰减（7B 在 131k 处 SNR 损失 44%），但任务正确率不受影响。$W^*$ 是经验参数，不写入形式化接口。实验设计与判读详见 `experiments/attention_growth/EXPERIMENT_PLAN.md`，认识论边界见附录 B.11。
* **学术锚点**：该公理对应长上下文实证研究所刻画的**上下文退化（Context Rot）**现象：模型有效推理能力随无关上下文增长而显著衰减，呈“迷失在中间（Lost in the Middle）”的 U 型注意力分布（Liu et al., TACL 2024）；实测有效上下文长度远低于标称值（Hsieh et al., 2024, RULER；Chroma, 2024, Context Rot）。

#### 公理 III：变异因果律单调公理（Axiom of Monotonic Causal Mutation）
* **数学表达**：设文件系统物理状态在时间 $t$ 的状态为 $\Phi(t)$，物理修改时间戳集合为 $\mathcal{M}(t) = \{ \text{mtime}(f) \mid f \in \text{Files} \}$。对于智能体连续执行的变异动作序列 $a_1, a_2$，其物理生效充要条件为：
  $$ \forall f \in \text{Modified}(a_k), \quad \text{mtime}_{new}(f) > \text{mtime}_{old}(f) \quad \text{且} \quad \text{Hash}(a_k) \text{ 具备幂等可溯性} $$
* **公理诠释**：智能体执行的代码写回，若物理时间戳未发生单调正向跳变，构建工具的增量解析器将直接跳过变异。同时，所有的变异动作必须拥有唯一规范化 SHA-256 签名日志，防止重试过程中的状态二次错位叠加。
* **经验支撑与适用边界（实测，2026-10-20）**：在 Cargo 1.96（Windows NTFS）上对增量编译判据做了 28 项受控测量：变异可观测当且仅当文件 mtime 严格超过上次构建的参考时钟——mtime 停滞或回拨时内容修改被**静默吞没**（产物仍为旧版本，各 5/5 复现）；纯 mtime 跳变即使内容不变也触发重建（触发通道与时钟有关、与内容无关），而"可观测变化"以内容差异为必要条件，与形式化定理的前提划分一致。实测发现参考时钟 $R \approx$ 上次构建完成时刻而非源文件旧 mtime，静默丢失窗口为 $(0, R]$——构建进行中的并发写入天然不安全，比朴素模型更严格。日志幂等性在无变化重构建与 git 回退-重试场景中均成立（重试后语义输出恢复；Windows PE 时间戳使字节级一致不可能，幂等承诺在内容/语义层）。适用域：**mtime-based 增量编译器**（Cargo、Make）；内容哈希型构建系统（Bazel、Nix）不依赖 mtime 跳变，静默丢失场景在其上不成立。实验设计与判读详见 `experiments/attention_growth/EXPERIMENT_PLAN_AXIOM3.md`。
* **学术锚点**：该公理是分布式系统经典结论在智能体—文件系统交互上的直接迁移：事件排序遵循**因果序（Happens-Before Ordering）**（Lamport, CACM 1978），状态变更的可重放性依赖**写前日志（Write-Ahead Logging, WAL）**与**幂等性（Idempotency）**保障（Kleppmann, 2017），并发协作依赖**租约（Lease）**机制（Gray & Cheriton, SOSP 1989）。

#### 公理 IV：经验自免疫公理（Axiom of Crystallization Auto-Immunity）
* **数学表达**：设智能体在单次生命周期内自发萃取的知识资产集合为 $\mathcal{K}_{raw}$。全局知识库状态更新算子必须满足双盲过滤：
  $$ \mathcal{K}_{global}(t+1) = \mathcal{K}_{global}(t) \cup \left\{ k \in \mathcal{K}_{raw} \mid \text{Verdict}_{audit}(k) = \text{PROMOTE} \wedge \text{SubstratePass}(k) = \text{TRUE} \right\} $$
* **公理诠释**：智能体在开发链路中总结的“模式/规则”，在未经过完整的端到端五重物理判据与独立审查者终审前，一律视为高风险疑似污染源（`DRAFT_SUSPECT`），严禁横向传播。
* **经验支撑与适用边界（形式化 + LLM 多代传播实测，2026-10-21）**：跨代传播的分支过程刻画、几何衰减律 $E(n)=m^n E(0)$、亚临界灭绝与超临界相变为 Lean 4 机检定理（附录 B.5）。在 DeepSeek v4-pro 上以"毒株规范注入 + 逐代转写"协议做了 4 条件 × 12 replicate × 6 代共 288 会话的受控传播实验（预注册判读标准先于实验）：**完全隔离门禁（$\sigma=1$）使谱系跨代传播严格为零**（全部 replicate $Z_1=0$，且毒株无独立再发现）——"严禁横向传播"的工程承诺获最强形式验证；未隔离条件（C0/C1）的池化种群序列与几何律 $E(n)=m^n E(0)$ 精确吻合（log-linear $R^2=0.958$，逐代比无趋势），分支性假设在小种群区成立；实测繁殖核参数化的 Galton-Watson 仿真（$10^5$ replicates）与已证定理链无自由参数吻合（三亚临界变体灭绝频率 $q_{sim}=1.0000$，Markov 界全程成立）。两点适用边界如实声明：① **DRAFT_SUSPECT 标记门的压缩效应方向符合预期（$-38\%$）但统计不显著**（置换检验 $p=0.15$，未达预注册 $p<0.05$ 门槛）——防御实现应依赖隔离而非仅依赖标记；② **乘性压缩律 $m=\mu(1-\sigma)$ 的 LLM 层直接检验受样本规模限制不可判定**（过滤层有效样本 $n=1$，写出层涨落主导），仅获分布层间接支撑；直接检验需 $\ge 10^2$ 量级 replicate。意外发现：无门禁条件下 $\hat m=0.56<1$——选择性转写协议本身将传播压入亚临界，超临界模型坍缩动力学对应的现实场景是**无转写衰减的记忆架构**（全量追加式记忆库、向量库直写），本实验协议下未出现。结论以条件定理形式呈现："对满足分支性与乘性压缩的传播系统，隔离门禁使投毒谱系以概率 1 灭绝"。**跨模型复核（Kimi `kimi-for-coding`，288 会话，2026-10-21）**：完全隔离的灭绝保证在第二模型族上同样成立（两模型合计 24/24 链 $Z_1=0$）；但无门禁下的有效繁殖数是**模型特定参数**——Kimi 实测 $\hat m_{C0}=0.983$（bootstrap 95% CI $[0.944,1.000]$，近临界），与 DeepSeek 的 $0.560$（CI $[0.294,0.735]$）差异显著（差 CI $[-0.689,-0.243]$），其繁殖核退化为 Bernoulli($p\approx0.98$)，6 代存活率仍达 $0.917$、灭绝需 $\sim50$–$100$ 代，工程上等于不退场。故本公理的适用域收紧为：**无门禁下的 $\hat m$ 由模型转写倾向决定（实测区间 $[0.56,0.98]$，可含近临界核），隔离（$\sigma=1$）的灭绝保证与 $\hat m$ 取值无关；防御效果不得依赖模型自身的转写衰减**。实验设计与完整判读详见 `experiments/attention_growth/EXPERIMENT_PLAN_AXIOM4.md` 与 `EXPERIMENT_PLAN_AXIOM4_CROSS_MODEL.md` §8，认识论边界见附录 B.11。
* **学术锚点**：该公理对应 2024 年以来的两项核心实证发现：其一，对递归自生成数据的循环训练导致**模型坍缩（Model Collapse）**（Shumailov et al., *Nature* 631, 2024）；其二，智能体长期记忆的**记忆投毒（Memory Poisoning）**攻击可跨会话持久生效，且极低污染率即可造成高攻击成功率（arXiv:2512.16962；arXiv:2605.18930）。

---

### 3.3 因果不变性定理（Theorem of Causal Invariance）

在分布式系统与并发控制理论中，因果不变性保证了多副本状态演化的一致性。将此引入智能体控制论体系，可得出**软件智能体收敛因果不变性定理**：

> **定理 3.1（收敛因果不变性）**：一个自主软件智能体系统在大型代码基质上是**确定性收敛（Deterministically Convergent）**的，当且仅当满足下列三位一体的约束条件：
> 1. **状态可观测性（Observability）**：智能体每一步的动作反馈完全穿透至物理底座，不存在任何由代理层截断伪造的虚拟 Exit 0；
> 2. **变异局部性（Locality）**：每次状态变异严格受限于最小特权投影（PoLP Slice），变异集合与非目标域正交；
> 3. **评估解耦性（Decoupled Evaluation）**：评价者、考题制定者、解题执行者三者在物理环境、上下文内存与进程生命周期上完全物理隔离。

只要破坏上述三项中的任意一项，智能体系统在经过有限轮次演化后，必然陷入震荡（Oscillation）、死锁（Deadlock）或虚假通过（Falsified Pass）。
