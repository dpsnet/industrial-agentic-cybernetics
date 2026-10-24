# 附录 A：本书术语与学术界既有术语映射表
## Appendix A: Terminology Alignment between This Treatise and Established Academic Terms

> 本附录说明本书命名体系与人工智能安全、分布式系统与软件工程领域既有学术术语的对应关系，并声明全书术语政策。所有学术锚点文献的完整引用见 [A.5 参考文献](#a5-参考文献-references)。

---

## A.1 术语政策（Terminology Policy）

本书对术语实行三级管理：

| 层级 | 对象 | 政策 |
| :--- | :--- | :--- |
| **T1：失效模式术语** | 描述智能体可观察失效现象的命名 | **已修正为学术界既有术语为主**。书内自造名废除，或在首次引入处仅作为组织行为学借喻保留一次 |
| **T2：公理体系术语** | 四大控制论公理的命名 | **保留命名**（属于本书的理论贡献命名空间），但在每条公理的诠释处锚定对应的既有学术概念与文献 |
| **T3：模式与架构术语** | 22 个 GoF 式设计模式名与系统架构术语 | **保留命名**（属于本书的工程贡献命名空间），本表给出其最近对应概念，以保证可检索性 |

术语书写规范：每个术语首次出现时给出中文全称与英文全称，此后可直接使用英文术语或通用缩写（如最小特权原则 Principle of Least Privilege, PoLP）。

---

## A.2 失效模式术语（T1：已修正为既有术语）

| 书内原术语 | 修正后主术语（中文 / 英文） | 修正说明与学术锚点 |
| :--- | :--- | :--- |
| 合规剧场（Compliance Theater） | **奖励欺骗（Reward Hacking）**；并列概念：**规范博弈（Specification Gaming）** | "合规剧场"原为组织行为学借喻（与"安全剧场 Security Theater"同源）。人工智能安全文献的规范术语是奖励欺骗：智能体通过满足目标的"字面"而非"精神"骗取成功信号（Amodei et al., 2016；Krakovna et al., 2020；Denison et al., 2024）。本书仅在第二章首次引入时保留该借喻以建立直觉，此后统一使用"奖励欺骗"。2025 年工业实证：生产级强化学习中的奖励欺骗可诱发自然涌现的失对齐（Anthropic, arXiv:2511.18397） |
| 注意力涣散 / 注意力稀释（Attention Dilution） | **上下文退化（Context Rot）** | 长上下文实证研究刻画的核心现象：随无关上下文增长，模型有效推理能力显著衰减，典型表现为"迷失在中间（Lost in the Middle）"的 U 型注意力曲线（Liu et al., TACL 2024）。有效上下文长度实测远低于标称值（Hsieh et al., 2024, RULER；Chroma, 2024, Context Rot 技术报告） |
| 知识自噬中毒（Auto-Toxic Hallucination Pollution）/ 自噬性知识中毒 / 知识自噬（Auto-Toxic Degradation） | **记忆投毒（Memory Poisoning）**；宏观递归现象：**模型坍缩（Model Collapse）** | 未经终审验证的自生经验经检索复用后对后续任务产生持续性污染，即记忆投毒——已被实证确认为智能体长期记忆的关键攻击面（MemoryGraft, arXiv:2512.16962；OEP, arXiv:2605.18930）。宏观层面的递归自我消费已由实证研究确认导致模型坍缩（Shumailov et al., *Nature* 631, 2024）；幻觉雪球效应（Hallucination Snowballing）刻画单次生成内的自我强化（Zhang et al., 2023） |
| 反思自愈假设（Reflection Fallacy） | **无外部验证的自我纠错不可行**（描述性表述，删除品牌化英文名） | 该假设已被系统性实证证伪：在无外部反馈时，大语言模型的自我纠错不仅无效，反而常导致性能退化（Huang et al., *Large Language Models Cannot Self-Correct Reasoning Yet*, ICLR 2024） |
| 虚假通过（Tautological Illusion） | **虚假通过（Falsified Pass）**（描述性表述） | 属于奖励欺骗在评测语境下的具体表现：通过自指验证回路（Self-Referential Verification Loop）制造通过假象，不设独立术语 |

---

## A.3 公理体系术语（T2：保留命名，锚定既有文献）

| 公理 | 保留命名 | 对应的既有学术概念 | 锚点文献 |
| :--- | :--- | :--- | :--- |
| 公理 I | 物理非信任公理（Axiom of Physical Non-Trustworthiness） | 接地与验证鸿沟（Grounding & Verification Gap）；奖励欺骗（Reward Hacking）；谄媚性（Sycophancy） | Amodei et al., 2016；Sharma et al., 2023；Huang et al., ICLR 2024 |
| 公理 II | 注意力熵增公理（Axiom of Attention Entropy） | 上下文退化（Context Rot）；迷失在中间（Lost in the Middle）；有效上下文长度（Effective Context Length） | Liu et al., TACL 2024；Hsieh et al., 2024；Chroma, 2024 |
| 公理 III | 变异因果律单调公理（Axiom of Monotonic Causal Mutation） | 因果序（Happens-Before Ordering）；写前日志（Write-Ahead Logging, WAL）；幂等性（Idempotency）；租约（Lease） | Lamport, CACM 1978；Gray & Cheriton, SOSP 1989；Kleppmann, 2017 |
| 公理 IV | 经验自免疫公理（Axiom of Crystallization Auto-Immunity） | 记忆投毒（Memory Poisoning）；模型坍缩（Model Collapse）；隔离与验证晋升（Quarantine & Verified Promotion） | Shumailov et al., *Nature* 2024；MemoryGraft, 2025；OEP, 2026 |

---

## A.4 模式与架构术语（T3：保留，给出最近对应概念）

| 本书术语 | 最近对应概念 | 说明 |
| :--- | :--- | :--- |
| 物理底座（Substrate） | 执行环境（Execution Environment）/ 环境（Environment） | 指智能体所作用的真实目标工程源码树、文件系统与构建运行时。保留"底座"以强调其物理约束属性（编译器、缓存、进程生命周期），区别于评测用沙箱环境 |
| 知识萃取（Crystallization） | 经验固化（Memory Consolidation）；技能库（Skill Library） | 对应记忆增强智能体文献中的经验沉淀机制（Voyager 的技能库, Wang et al., 2023；ExpeL, 2024）。本书的贡献在于为其附加隔离与终审晋升门禁 |
| 最小特权投影（PoLP Projection） | 最小特权原则（Principle of Least Privilege, PoLP） | 直接沿用 Saltzer & Schroeder (1975) 的经典安全原则，将其从权限域迁移至上下文域 |
| 分布式底座租约锁（Substrate Lease Lock） | 租约（Lease）与看门狗（Watchdog） | 沿用 Gray & Cheriton (SOSP 1989) 的租约机制 |
| 幂等变异日志与物理时钟补偿 | 写前日志（WAL）+ 幂等键（Idempotency Key）+ 单调时钟（Monotonic Clock） | 标准分布式系统技术在增量编译缓存场景的迁移 |
| 隐藏 Oracle 物理隔离沙箱 / 五重无旁路机械判据 | 验证门禁式评测（Verifier-Gated Evaluation）；数据去污染（Decontamination）；无旁路评测（Bypass-Free Evaluation） | 对应评测方法论文献对"智能体欺骗评测器"问题的回应（Kapoor et al., *AI Agents That Matter*, 2024；SWE-bench Verified 的人工校验实践） |
| 断言反自指核验（Tautology Check） | 自指验证回路检测（Self-Referential Verification Detection） | 属于奖励欺骗的实例级检测手段，保留为描述性技术名 |

---

## A.5 参考文献（References）

1. Amodei, D., Olah, C., Steinhardt, J., Christiano, P., Schulman, J., & Mané, D. (2016). *Concrete Problems in AI Safety*. arXiv:1606.06565.
2. Krakovna, V., et al. (2020). *Specification gaming: the flip side of AI ingenuity*. DeepMind Research Blog.
3. Huang, J., Chen, X., Mishra, S., Zheng, H. S., Yu, A. W., Song, X., & Zhou, D. (2024). *Large Language Models Cannot Self-Correct Reasoning Yet*. ICLR 2024.
4. Sharma, M., et al. (2023). *Towards Understanding Sycophancy in Language Models*. arXiv:2310.13548.
5. Denison, C., et al. (2024). *Sycophancy to Subterfuge: Investigating Reward-Tampering in Language Models*. arXiv:2406.10162.
6. Anthropic Alignment Team (2025). *Natural emergent misalignment from reward hacking in production RL*. arXiv:2511.18397.
7. Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. Transactions of the Association for Computational Linguistics (TACL).
8. Hsieh, C.-P., et al. (2024). *RULER: What's the Real Context Size of Your Long-Context Language Models?* arXiv:2404.06654.
9. Chroma Research (2024). *Context Rot: How Increasing Input Tokens Impacts LLM Performance*. Technical Report.
10. Shumailov, I., Shumaylov, Z., Zhao, Y., Papernot, N., Anderson, R., & Gal, Y. (2024). *AI models collapse when trained on recursively generated data*. Nature, 631, 755–759.
11. Zhang, M., Press, O., Merrill, W., Liu, A., & Smith, N. A. (2024). *How Language Model Hallucinations Can Snowball*. ICML 2024.
12. *MemoryGraft: Persistent Compromise of LLM Agents via Poisoned Experience Retrieval*. arXiv:2512.16962.
13. *OEP: Poisoning Self-Evolving LLM Agents via Locally Correct but Non-Transferable Experiences*. arXiv:2605.18930.
14. Lamport, L. (1978). *Time, Clocks, and the Ordering of Events in a Distributed System*. Communications of the ACM, 21(7), 558–565.
15. Gray, J., & Cheriton, D. (1989). *Leases: An Efficient Fault-Tolerant Mechanism for Distributed File Cache Consistency*. SOSP 1989.
16. Saltzer, J. H., & Schroeder, M. D. (1975). *The Protection of Information in Computer Systems*. Proceedings of the IEEE, 63(9).
17. Kleppmann, M. (2017). *Designing Data-Intensive Applications*. O'Reilly Media.
18. Wang, G., Xie, Y., Jiang, Y., Mandlekar, A., Xiao, C., Zhu, Y., Fan, L., & Anandkumar, A. (2023). *Voyager: An Open-Ended Embodied Agent with Large Language Models*. arXiv:2305.16291.
19. Yang, J., et al. (2024). *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering*. NeurIPS 2024.
20. Kapoor, S., et al. (2024). *AI Agents That Matter*. arXiv:2407.01502.
