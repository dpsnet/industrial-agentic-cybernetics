# EN_TERMS.md — 英译术语表（Industrial Agentic Cybernetics English Translation Glossary）

> **用途**：本表是《工业级智能体控制论》全书英译的唯一术语权威。所有分片/章节翻译必须严格引用本表；同一概念全书用词一致，禁止同义词漂移或随意意译。不确定的术语先查原文合稿 `monograph/manuscript-latex.md` 与 `docs/terminology-mapping.md`（附录 A）再定。
>
> **证据来源**：`docs/terminology-mapping.md`（附录 A 术语映射表）、各章 H1 官方英文名、`docs/index.md` 英文副题/分部名、`monograph/manuscript-latex.md`（完整合稿）。
>
> **书写规范**（沿用中文版附录 A 术语政策）：每个术语首次出现时中英全称并列（英文版以英文为主，必要时括注中文原名一次），此后统一使用英文术语，禁止再混用其他译法。

---

## 1. 书名、作者、版本与元数据（固定不变，全站一致）

| 中文 | 英文（固定） |
| :--- | :--- |
| 《工业级智能体控制论：自主软件工程的设计模式与形式化架构》 | Industrial Agentic Cybernetics: Design Patterns and Formal Architecture for Autonomous Software Engineering |
| 副题（大纲版）：从离散提示词到闭环控制论——大型语言模型智能体的物理锚定、因果不变性与自免疫收敛 | From Discrete Prompting to Closed-Loop Cybernetics: Physical Anchoring, Causal Invariance, and Auto-Immunity Convergence for Large Language Model Agents |
| 作者 王斌（Bin Wang） | Bin Wang |
| 机构 北京开路者科技有限公司 | 无官方英文名——英文页保留中文原名「北京开路者科技有限公司」，待作者裁决后统一替换 |
| 版本 | v1.1.2 |
| 概念 DOI | https://doi.org/10.5281/zenodo.23636677（始终指向最新版，正文引用不得另造 DOI） |
| 许可证 | Code MIT · Text CC BY 4.0 |

---

## 2. 四大公理（T2：保留命名，锚定既有文献）

| 中文（保留命名） | 英文（保留命名） | 既有学术锚点（英文不变） |
| :--- | :--- | :--- |
| 公理 I 物理非信任公理 | Axiom of Physical Non-Trustworthiness | Grounding & Verification Gap; Reward Hacking; Sycophancy |
| 公理 II 注意力稀释（与特权发散）公理 | Axiom of Attention Dilution | Context Rot; Lost in the Middle; Effective Context Length |
| 公理 III 变异因果律单调公理 | Axiom of Monotonic Causal Mutation | Happens-Before Ordering; Write-Ahead Logging (WAL); Idempotency; Lease |
| 公理 IV 经验自免疫公理 | Axiom of Crystallization Auto-Immunity | Memory Poisoning; Model Collapse; Quarantine & Verified Promotion |

> 公理罗马数字写法固定为 Axiom I / II / III / IV（或 Axiom 1–4，但同章内不得混用）。

---

## 3. 九大模式族（分部名，英文固定）

| 中文分部 | 英文分部 |
| :--- | :--- |
| 序言与公理 | Preface & Axioms |
| 第一部分 物理底座与现实锚定 | Part I: Substrate Anchoring |
| 第二部分 注意力约束与最小特权投影 | Part II: Cognitive Attention & PoLP |
| 第三部分 执行韧性与微循环自愈 | Part III: Execution Resilience & Self-Healing |
| 第四部分 并发争用与分布式状态协调 | Part IV: Concurrency & Coordination |
| 第五部分 知识萃取与自免疫演进 | Part V: Knowledge Crystallization & Auto-Immunity |
| 第六部分 人机共生与非对称认知交互 | Part VI: Human-Agent Symbiosis |
| 第七部分 客观度量与基准测评 | Part VII: Objective Evaluation & Benchmarks |
| 第八部分 智能体能效与收敛工程学 | Part VIII: Convergence Economics & Tokenomics |
| 第九部分 生产韧性与反馈闭环 | Part IX: Production Resilience & Feedback Loop |
| 结语与附录 | Epilogue & Appendix |
| 模式族（9 大模式族） | pattern family（9 pattern families） |

---

## 4. 24 个模式（T3：保留命名；英文名取各章 H1 括号内官方英文名，一字不改）

| 章 | 中文模式名 | 官方英文名（H1） |
| :--- | :--- | :--- |
| Ch.4 / P01 | 物理底座穿透核验 | Substrate Penetration Pattern |
| Ch.5 / P02 | 审查者现实审计一票否决 | Reality Audit VETO Pattern |
| Ch.6 / P03 | 脚手架与解题域双阶段隔离 | Two-Phase Mandate Pattern |
| Ch.7 / P04 | 任务级最小特权投影 | Task-Level PoLP Context Slicing Pattern |
| Ch.8 / P05 | 两阶段宏微观渐进设计展开 | Macro-Micro Elaboration Pattern |
| Ch.9 / P06 | 流式拓扑分解与选择性断点续跑 | Streaming Decomposition & Selective Resume Pattern |
| Ch.10 / P07 | 沙箱驱动-导航结对微循环 | Driver-Navigator Pairing Pattern |
| Ch.11 / P08 | 白盒隐式分支嗅探与内部锚定 | Implicit Branch Sniffing & Internal Invariants Pattern |
| Ch.12 / P09 | 幂等变异日志与物理时钟补偿 | Idempotent Journaling & Mtime Touch Pattern |
| Ch.13 / P10 | 分布式物理底座租约锁 | Substrate Lease Lock & Watchdog Pattern |
| Ch.14 / P11 | 主写从读降级互斥 | Primary-Writer Replica-Reader Pattern |
| Ch.15 / P12 | 异构对等智能体抽象协议桥接 | Peer-Agent Protocol Bridge Pattern |
| Ch.16 / P13 | 单源事实-模式双模萃取 | Dual-Mode Technical Crystallization Pattern |
| Ch.17 / P14 | 隔离草稿与终审晋升门禁 | Quarantined Promotion Gate Pattern |
| Ch.18 / P15 | 污点污染防御与防伪退化 | Tainted Pattern Rejection & Anti-Degradation Pattern |
| Ch.19 / P16 | 手风琴式认知多分辨率投影 | Accordion Multiresolution Projection Pattern |
| Ch.20 / P17 | 飞行指挥官异步中断与航向锁定 | Asynchronous Flight-Director Interrupt Pattern |
| Ch.21 / P18 | 隐藏 Oracle 物理隔离沙箱测评 | Hidden Oracle Sandbox Pattern |
| Ch.22 / P19 | 五重无旁路机械判据 | Five-Fold Bypass-Free Evaluator Pattern |
| Ch.23 / P20 | 工业基准 A/B 物理对照评测 | Industrial Substrate A/B Benchmark Pattern |
| Ch.24 / P21 | Token 吞吐断崖式压缩架构 | Tokenomics Convergence Architecture Pattern |
| Ch.25 / P22 | 纯模型原生 Provider 解耦桥接 | Pure Native Provider Bridge Pattern |
| Ch.26 / P23 | 生产环境运行时监控与异常嗅探 | Production Runtime Anomaly Sniffing Pattern |
| Ch.27 / P24 | 生产缺陷萃取与热修复闭环 | Production Defect Crystallization & Hotfix Loop Pattern |

**章节标题 H1 规则**：英文版 H1 = `Chapter N: …`（N 与「第X章」对应）。序言三章与结语、附录 B 直接用作者官方英文 H2 原文作 H1（见 §6）；模式章 H1 = `Chapter N: Pattern NN — <官方英文名>`。

---

## 5. 失效模式与既有学术术语（T1：已修正为既有术语，禁用旧自造名）

| 中文 | 英文（既有术语，唯一） | 禁用（旧自造名） |
| :--- | :--- | :--- |
| 奖励欺骗 | reward hacking | 合规剧场（仅第二章首次引入作借喻保留一次） |
| 规范博弈 | specification gaming | — |
| 上下文退化 | context rot | 注意力涣散 / 注意力稀释（作为失效现象名） |
| 记忆投毒 | memory poisoning | 知识自噬中毒 / 自噬性知识中毒 / 知识自噬 |
| 模型坍缩 | model collapse | — |
| 级联错误传播 | cascade error propagation | — |
| 虚假通过 | falsified pass | 虚假通过（Tautological Illusion） |
| 迷失在中间 | lost in the middle | — |
| 有效上下文长度 | effective context length | — |
| 幻觉雪球效应 | hallucination snowballing | — |
| 反思自愈假设 | reflection-based self-healing assumption（描述性表述，无品牌化英文名） | Reflection Fallacy |
| 无外部验证的自我纠错不可行 | self-correction without external verification is infeasible | — |
| 自指验证回路 | self-referential verification loop | — |
| 谄媚性 | sycophancy | — |
| 接地与验证鸿沟 | grounding & verification gap | — |

---

## 6. 各章标题官方英文（作者自定，英文版 H1 原样采用）

| 章 | 中文 H1 | 官方英文（原 H2 / H1 括号） |
| :--- | :--- | :--- |
| 第一章 | 范式转移：从离散提示词工程到闭环控制论 | Chapter 1: The Paradigm Shift — From Discrete Prompting to Closed-Loop Cybernetics |
| 第二章 | 奖励欺骗（Reward Hacking）的形式化分析与物理破局 | Chapter 2: A Formal Analysis of Reward Hacking and Substrate Breakthrough |
| 第三章 | 工业级智能体四大公理与因果不变性形式化定义 | Chapter 3: Four Cybernetic Axioms and Causal Invariance Formulation |
| 第二十八章 | 结语：通向自给自足的自主软件工程 | Epilogue: Towards Autonomous and Resilient Cybernetics |
| 附录 B | 附录 B：形式化收敛性与稳定性证明（Lean 4 机检） | Appendix B: Formal Proofs of Convergence and Stability (Lean 4 Mechanized) |

---

## 7. 核心机制与架构术语（全书统一，禁止漂移）

| 中文 | 英文 |
| :--- | :--- |
| 控制论（工程闭环反馈借喻，非 Wiener 学科继承） | cybernetics（engineering closed-loop feedback metaphor, not a disciplinary inheritance） |
| 闭环控制 / 闭环 | closed-loop control / closed loop |
| 负反馈回路 | negative feedback loop |
| 一阶开环生成 | first-order open-loop generation |
| 二阶闭环物理控制论 | second-order closed-loop physical cybernetics |
| 物理底座 | substrate |
| 物理现实性 | physical reality |
| 物理穿透核验 | substrate penetration verification / reality audit（物理真伪一票否决门禁 = Reality Veto Gate） |
| 现实审计 | reality audit |
| 一票否决权 | veto power（模式 02 官名为 VETO，保持大写） |
| 最小特权原则 | Principle of Least Privilege (PoLP) |
| 最小特权投影 | PoLP projection / least-privilege projection |
| 权限域 → 上下文域迁移 | migrated from the permission domain to the context domain |
| 世界线 | **worldline（保留映射）**：当前全书正文未出现该词，禁止在现有译文中添加；仅在作者后续新增内容中使用 |
| 可追溯矩阵（24 模式可追溯矩阵） | traceability matrix（24-pattern traceability matrix） |
| 经验资产 | empirical asset（全书统一指称智能体萃取的可复用经验条目） |
| 知识萃取 | crystallization（对应 memory consolidation / skill library，见术语映射 A.4） |
| 免疫 / 自免疫 | immunity / auto-immunity（经验繁殖阈值 q>1/2 下的谱系抑制，非生物学免疫） |
| 经验繁殖阈值 | experience reproduction threshold |
| 谱系抑制 | lineage suppression |
| 隔离草稿 | quarantined draft |
| 终审晋升门禁 | promotion gate（终审 = final review，晋升 = promotion） |
| 隔离与验证晋升 | quarantine & verified promotion |
| 污点标记 / 逆向传播撤回 | taint tracking / taint quarantine propagation |
| 降级标记 | `DEPRECATED_QUARANTINED`（保持原标识符） |
| 幂等变异日志 | idempotent journaling |
| 物理时钟补偿 / mtime 补偿 | mtime touch / physical clock compensation |
| 分布式底座租约锁 | substrate lease lock |
| 看门狗 | watchdog |
| 主写从读降级互斥 | primary-writer replica-reader（degraded mutual exclusion） |
| 白盒隐式分支嗅探 | implicit branch sniffing |
| 内部锚定（不变式） | internal invariants |
| 断点续跑 | selective resume |
| 脚手架与解题域 | scaffolding & solution domain |
| 双阶段隔离 | two-phase mandate（isolation） |
| 宏微观渐进设计展开 | macro-micro elaboration |
| 流式拓扑分解 | streaming decomposition |
| 驱动-导航结对微循环 | driver-navigator pairing micro-loop |
| 微循环自愈 | micro-loop self-healing |
| 隐藏 Oracle | hidden oracle |
| 五重无旁路机械判据 | five-fold bypass-free mechanical criteria |
| 断言反自指核验 | tautology check（assertion anti-self-referential verification） |
| 航向锁定器 | course-lock enforcer |
| 硬不变式 | hard invariant |
| 手风琴式认知多分辨率投影 | accordion multiresolution projection |
| 飞行指挥官异步中断 | asynchronous flight-director interrupt |
| 智能体能效 | agent efficiency（tokenomics） |
| Token 吞吐断崖式压缩 | token-throughput cliff compression |
| 纯模型原生 Provider 桥接 | pure native provider bridge |
| 生产环境运行时监控 | production runtime monitoring |
| 异常嗅探 | anomaly sniffing |
| 热修复闭环 | hotfix loop |
| 状态转移图 | state transition graph |
| 收敛状态机 | convergent state machine |
| 因果倒退 | causal backtracking |
| 白名单契约 | whitelist contract |
| 玩具级假设 / 提示词迷思 | toy-level assumptions / prompt fallacy |
| 马尔可夫无后效性假设 | Markovian memorylessness assumption |
| 反思自愈假设 | reflection-based self-healing assumption |
| 黑盒沙箱等价假设 | black-box sandbox equivalence assumption |
| 思维链 | chain-of-thought (CoT) |
| Mock 桩 | mock stubs |
| 增量编译缓存 | incremental compilation cache |
| 系统修改时间 | modification time (mtime) |
| 隐式传递耦合 | implicit transitive coupling |
| 环境污染不可逆性 | substrate mutation irreversibility |
| 状态残留效应 | state residue effects |
| 级联半径 | cascade radius |
| 受控对象 / 执行机构 / 反馈传感器 / 偏差调节器 / 系统稳态 | plant / actuator / sensor / controller / equilibrium |
| 物理三态合一 | physical triad（code landed · natively verified · promotion-gate approved） |
| 工程公理 | engineering axiom（占据推理起点、内容为经验命题） |
| 适用域 | applicability domain |
| 证伪判据 | falsifiability criteria |
| 边界声明 | boundary declaration |
| 定理层 / 经验层 / 工程层 | theorem layer / empirical layer / engineering layer |
| 证据账本 / 证据分布总账 | evidence ledger / evidence-distribution ledger |
| 正文锚点 / Lean 模块 / 实证证据 / 文中指标 | in-text anchors / Lean module / empirical evidence / in-text metrics |
| 可定理化（核心已证） | theoremizable (core proven) |
| 工程约定 | engineering convention |
| 实测型（未执行） | empirically measured (not yet executed) |
| 实测型（相对量） | empirically measured (relative quantities) |
| 预注册 | preregistration / preregistered |
| 内核验证 | kernel-verified |
| 机检 | mechanized |
| 回写（实证结果回写文档） | written back |
| 显式开放项 | explicitly open item |
| 工程基质层（通道） | engineering substrate layer (channel) |
| 纯社会传播通道 | purely social transmission channel |
| 文本转写传播 | text-transcription transmission |
| 观测-学习回路 | observation-learning loop |
| 检出率 / 误报率 / 晋升比例 / 泄漏计数 / 拦截率 | detection rate / false-positive rate / promotion ratio / leak count / interception rate |
| 篡改自测 | tamper self-test |
| 首字时延 | time-to-first-token (TTFT) |
| 近临界 / 超临界 / 相变 | near-critical / supercritical / phase transition（Galton-Watson 分支过程术语，非热力学） |
| 分支过程 | branching process |
| 繁殖核 | reproduction kernel（$\hat m$） |
| 存活率 | survival rate |
| 线性累积-容量竞争 | linear accumulation–capacity competition |
| Lyapunov 强漂移 | Lyapunov strong drift |
| 双峰（漂移状态双峰） | bimodal (bimodal drift states) |
| 内核验证的数学事实 | mathematically verified facts checked by the kernel |

---

## 8. 保留原文不变的要素（翻译时禁止改动）

1. **全部 MathJax 公式**（`$…$`、`$$…$$`、`\(…\)`、`\[…\]`）——公式本身不翻译；
2. **Mermaid 代码块**——`flowchart` 类型与节点 ID 不变，仅翻译 `["…"]` 与 `--"…"-->` 内的中文标签；
3. **Lean 模块名 / 定理名 / 标识符**（如 `Pattern02_RealityAudit`、`veto_overrides_high_score`、`Axiom1_Grounding`、`DEPRECATED_QUARANTINED`、`isVetoed`、`DRAFT_SUSPECT`）——原样保留；
4. **实验编号与指标**（E3/E3b、E-B6、E-B8、H1–H5、F1–F4、X-H1…、S-H1…、T-H1…、B-H1a…、Cargo 28/28、288 会话、TTL 30s、心跳 10s、5×10⁴ 仿真等）——原样保留；
5. **文献引用**（arXiv 编号、作者名、论文英文标题、期刊/会议名）——原样保留，仅翻译周围叙述文字；
6. **代码块与命令行**——内容原样保留，仅注释若为中文可译；
7. **文件路径**（`docs/…`、`formal_proof/IACFormalization/…`、`monograph/…`）——原样保留（相对仓库路径，与站点深度无关）；
8. **章节编号**（1.1、1.4.6、B.2–B.5 等）——原样保留。

---

## 9. 术语一致性校对要求（每批译文完成后必做）

- 用 grep 抽查每章关键英文术语（reward hacking、context rot、memory poisoning、substrate、crystallization、auto-immunity、PoLP、veto、traceability matrix、closed-loop、pattern family、各公理名、各模式官方名）的出现形式；
- 同一概念发现两种以上译法即视为违规，回到本表统一；
- 校对记录写入译文交付说明。
