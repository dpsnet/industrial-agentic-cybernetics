# 公理 IV 聚焦论文——骨架（Skeleton）

> 状态：**骨架 v1**（2026-10-22，实证全部闭合后动笔）
> 目标出口：ICSE/FSE/ASE 实证轨道 或 arXiv cs.SE → ACM TOSEM
> 事实层引用（单源）：`experiments/attention_growth/` 判读产物；叙述层按论文体例独立写作，不复制专著段落（见 `PROJECT_RULES.md` §2–3）

---

## 候选标题

**Memory Poisoning in Ungated Agentic Memory Architectures: Phase Transitions, Architecture Effects, and Quarantine Invariance**

备选副题路径：… / With Lean-4-Verified Quarantine Invariance / … under Full-Append vs Selective-Replay Memory

---

## 摘要（Abstract，主张三句，骨架句）

1. 无门禁的累积型（full-append）智能体记忆架构下，注入毒株持续累积不灭绝——机制为**线性累积-容量竞争**（每代恒定写入 $W\equiv1$、$Z_{n+1}=Z_n+W$），实证 $\hat m=1.166$（boot95 CI $[1.156,1.176]$）；
2. 传播机制由**架构**决定而非模型：选择性转写=分支衰减（GW，$\hat m$ 区间 $[0.56,0.98]$ 跨模型），全量追加=累积-竞争；容量 $W$ 为控制参量，临界 $W_c\in(8,16)$；
3. 隔离（门禁 $\sigma=1$）跨机制截断传播（Lean 4 机检定理 + 跨模型 24/24、跨任务族 48/48、全量架构 12/12 实测）；标记门零压缩（三档实验三重确认）——**防御依赖隔离而非标记**。

---

## 1. Introduction

> **已扩写全文**：`sections/01-introduction.md`（v1，2026-10-22）

- **问题**：LLM 智能体的长期记忆会被注入内容持久污染；现有防御（软标记、审查门）在真实记忆架构下缺乏机制层面的保证。
- **文献缺口**：
  - Model collapse（Shumailov et al., *Nature* 631, 2024）——递归自生成数据的循环退化，但未覆盖"记忆架构差异"这一维度；
  - Memory poisoning（arXiv:2512.16962；arXiv:2605.18930）——攻击可跨会话持久，防御讨论停留在启发式；
  - Reward hacking（Amodei et al., 2016；arXiv:2511.18397）——外部锚定缺失的退化，与公理 I 同族但无记忆传播机制；
  - Context rot（Liu et al., TACL 2024；RULER）——上下文退化，不涉及代际传播；
  - **SE 定律谱系**（定位句）：Brooks 1986 本质复杂性、Lehman's Laws（递增复杂性=软件熵增）、Conway's Law、CAP、停机问题——SE 的"近公理"规律历来是经验观察，本工作首次将其中一支（经验自免疫）提升为**可机检 + 预注册实测**的公理体系。
- **本工作主张**（对应摘要三句）。
- **贡献清单**：
  1. 机制层：识别"架构决定传播机制"——selective（分支衰减）vs full-append（累积-竞争），$W$ 为控制参量（S1）；
  2. 形式化层：Lean 4 机检条件定理链（隔离⟹灭绝、GW 灭绝概率=最小不动点、几何律、超临界发散），零 sorry（S2）；
  3. 实证层：预注册、跨模型（Pro/Kimi/Flash）×跨架构（selective/full-append/W 档）×跨任务族（144 链）×大样本配对（160 链）闭合判据（S3）；
  4. 工程含义：防御依赖隔离而非标记，三重独立确认（S4）。

---

## 2. Background & Related Work

> **已扩写全文**：`sections/02-related-work.md`（v1，2026-10-22）

- **2.1 智能体记忆与投毒**：记忆库架构谱系（选择性转写 / 全量追加 / 向量库直写）；投毒注入面。
- **2.2 Model Collapse 与递归退化**：Shumailov Nature 2024；与 GW 分支过程的既有联系（Bishop 2006 / Galton-Watson 谱系）。
- **2.3 记忆投毒防御**：arXiv:2512.16962 的启发式防御；标记门（DRAFT_SUSPECT）、隔离门禁（五重判据）。
- **2.4 智能体退化的一般机制**：reward hacking（Amodei 2016）、context rot（Liu/RULER）、评估解耦（定理 3.1 同族，跨论文引用）。
- **2.5 SE 定律谱系（定位）**：Lehman 递增复杂性 ↔ 公理 II 注意力熵增（专著）；Brooks/Conway 作为"经验近公理"先例——本工作是"形式化-实测化推进"。
- **2.6 相关证明工具**：Lean 4 / mathlib；软件工程中的形式化验证先例。

---

## 3. Model（机制）

> **已扩写全文**：`sections/03-model.md`（v1，2026-10-22；符号纪律：$M$=记忆容量 vs $w_n$=每代写入）

- **3.1 两机制并存（核心主张 1）**：
  - 分支衰减（selective）：GW 分支过程 $E(n)=m^nE(0)$、几何律、灭绝概率=最小不动点（Lean B.2/B.4）；
  - 累积-竞争（full-append）：每代恒定写入 $W$，$Z_{n+1}=Z_n+W$，容量饱和后 FIFO 竞争稳态——**与 GW 非同一机制**（逐代 offspring 核对：$W\equiv1$，无倍增）。
- **3.2 容量控制参量**：$W$ 为传播强度控制参量，临界 $W_c\in(8,16)$（S-H1 + W 档）。
- **3.3 架构决定机制（核心主张 2）**：selective=分支衰减（$\hat m$ 由模型转写倾向决定 $[0.56,0.98]$）、full-append=累积-竞争——变量是架构不是模型。
- **3.4 预注册假说清单**（§5 实验）：
  - S-H1 超临界（full-append $\hat m>1$ 且 CI 下限 $>1$）；S-H2 存活率 1.0；S-H3 GW 匹配（**被机制证据否定**）；S-H4 隔离不变性；
  - B-H1a 标记门压缩（**不成立**）；B-H1c 乘性压缩律 $m=\mu(1-\sigma)$；B-H2 几何律复验；
  - X-H1/X-H4 跨模型；T-H1/T-H4 跨任务族。

---

## 4. Formalization（Lean 4）

> **已扩写全文**：`sections/04-formalization.md`（v1，2026-10-22；定理源：Lean B.5 机检，零 sorry）

- **4.1 定理链**（`formal_proof/` + `docs/appendix-formal-proofs.md` B.2–B.5，零 sorry）：
  - T1 GW 灭绝概率 $=\min\{s:\varphi(s)=s\}$；
  - T2 几何律（亚临界指数衰减）；
  - T3 **隔离⟹灭绝**（条件定理：分支性 + 乘性压缩 ⇒ 门禁 $\sigma=1$ 下谱系以概率 1 灭绝）；
  - T4 超临界发散（期望发散判据）。
- **4.2 定理-应用映射**：T3 的应用条件（分支性、乘性压缩）在 selective 架构实测满足（$R^2=0.958$）；在 full-append 架构 T3 前提不成立——隔离实证由 C3-full 12/12 直接给出（mem 恒 6、Z 恒 1），机制修正如实记录（§8）。
- **4.3 形式化的边界**：$\hat m$、$W^*$ 为经验/工程层参数，不入形式化接口（三层地位，专著 §1.4.2 同口径）。

---

## 5. Experimental Setup

> **已扩写全文**：`sections/05-experimental-setup.md`（v1，2026-10-22）

- **5.1 预注册**：全部判据先于实验（S-* / B-* / X-* / T-*），判读单位与显著性门槛预先固定。
- **5.2 模型档**：DeepSeek-V4-Pro-0813（简称 Pro；主实验）、Kimi `kimi-for-coding`（跨模型）、DeepSeek-V4.1-Flash-1017（简称 Flash；SUPERCRITICAL 档 + H1AC 档 + selective 对照）；temperature 0.7。
- **5.3 协议**：毒株规范注入 + 逐代转写；DRAFT_SUSPECT 双盲过滤；P1/P2 双毒株（H1AC）；lineage 谱系追踪。
- **5.4 条件矩阵**：
  - selective：C0/C1/C2/C3（Pro，4×12×6 = 288 会话）+ 跨模型（288）+ 跨任务族（144）；
  - full-append：C0-full/C1-full/C3-full（各 12×8）+ W=8/W=32（各 6×8）+ selective 对照（2×6）；
  - H1AC：C0/C1 各 48 + C2 64，6 代（160 链）。
- **5.5 判读口径**：bootstrap CI（$10^4$）、符号翻转置换（$10^4$）、log-linear $R^2$；功效分析（Pro 档配对差 $d=0.167$，$n\approx48$ 达功效 0.8）。
- **5.6 执行与可复现**：脚本 `e_supercritical_judge.py`/`judge2.py`/`sh3.py`/`e_h1ac_judge.py`/`e_cross_task_judge.py` + 判读 JSON；预注册计划文档。

---

## 6. Results

> **已扩写全文**：`sections/06-results.md`（v1，2026-10-22；数据单源判读 JSON）

- **6.1 超临界与机制（S-H1/S-H2/S-H3/S-H4）**：
  - C0-full：$\hat m=1.166$（CI $[1.156,1.176]$）、Z=[1,2,2.92,3.92,3.92,4.92,4.92,4.92]、mem 6→16、存活率 1.0 → S-H1 ✅、S-H2 ✅；
  - C1-full：$\hat m=1.165$（[1.163,1.167]）标记门零压缩；
  - C3-full：12/12 mem 恒 6、Z 恒 1 → S-H4 ✅（跨机制截断）；
  - W 档：W=8 $\hat m=0.829$（[0.739,0.875]）灭绝（g7 存活率 0）、W=32 $\hat m=1.25$ 线性 $[1,\dots,8]$ → $W_c\in(8,16)$；
  - **S-H3 判定**：机制证据（$W\equiv1$ 线性累积）否定 GW 匹配——预注册假说被证伪 → 理论修订为累积-竞争（§8，叙事亮点）。
- **6.2 标记门与乘性律（B-H1a/B-H1c/B-H2，160 链 Flash）**：
  - B-H1a：$\bar d=0.020$（$p=0.69$、正差 15/48）→ 零压缩（三重确认：Pro $p=0.15$ / C1-full / H1AC）；
  - B-H1c：链均写入率比 $\hat r=0.466\in[0.35,0.65]$（乘性预测 0.5，吻合）；bootstrap CI $[0.333,0.602]$ 下界微出（0.017）→ 点估计支持、CI 边界；池化口径因幸存者偏差失效（如实记录）；
  - B-H2：$R^2=0.923$、$m\approx0.92$ → ✅。
- **6.3 跨模型（X-*）**：Pro $\hat m=0.560$（[0.294,0.735]）、Kimi $\hat m=0.983$（[0.944,1.000]）、Flash selective $=1.0$（临界）；隔离 24/24 链 $Z_1=0$；防御不依赖模型转写衰减。
- **6.4 跨任务族（T-*）**：144 链；隔离 48/48；T-H4 $p=0.026$；$\hat m$ 为任务族×适用位点联合参数 $[0.29,1.00]$ 跨族不可迁移。
- **6.5 工程侧（生产现场，关联实证）**：18 报告晋升 14、拦截 4、晋升 1.00、错误拦截 1.00、泄漏 0——工程闭环与理论通道的连接为开放项（§10）。

---

## 7. Discussion

> **已扩写全文**：`sections/07-discussion.md`（v1，2026-10-22）

- **7.1 防御依赖隔离而非标记（核心工程结论）**：三档实验、两架构收敛；机制解释——标记是软信号可被模型忽略，隔离是结构阻断。
- **7.2 架构决定机制（理论结论）**：转发协议（选择性 vs 全量追加）改变传播的数学结构；对记忆系统设计的一般含义——记忆架构是安全属性而非性能属性。
- **7.3 模型异质性**：$\hat m$ 是模型-任务-位点联合参数，跨族/跨模型不可迁移是结论非缺陷；隔离保证与之无关。
- **7.4 乘性律的边界**：点估计支持、CI 下界微出；池化口径失效的统计教训（幸存者偏差）——大样本传播实验的判读口径选择。

---

## 8. 机制修正的学术叙事（区别于专著的关键章节）

> **已扩写全文**：`sections/08-mechanism-revision.md`（v1，2026-10-22）

- 预注册 S-H3（GW 分支匹配）→ 逐代 offspring 核对发现 full_append 每代新写 $W\equiv1$（$Z_{n+1}=Z_n+W$）→ 假说被机制证据**证伪** → 理论修订：full_append 为线性累积-容量竞争，"超临界"为工程语义（持续累积不灭绝）而非分支倍增。
- 论文处理：作为"预注册假说被证伪 → 机制重新识别"的正面案例（诚实修订是审稿人加分项）；专著处理为完成态（机制区分+术语声明，`docs/preface/03` 公理 IV SUPERCRITICAL 段）。

---

## 9. Scope & Generalizability

> **已扩写全文**：`sections/09-scope.md`（v1，2026-10-22）

（从专著 §1.4.4 收缩声明改写，不复制段落）
- 任务族：pytest 测试编写四变体；跨族不可迁移为实测结论。
- 通道：理论实证=纯社会传播（SubstratePass 关闭）；工程基质=生产现场（五重判据）；连接=开放项。
- 模型档：三模型，$\hat m$ 模型特定。
- 架构：selective / full-append / W 档；未覆盖向量库直写（W 档为其代理）。

---

## 10. Limitations & Future Work

> **已扩写全文**：`sections/10-limitations.md`（v1，2026-10-22）

- 标记门效应异质性：Pro 档方向（-38%, $p=0.15$）vs Flash 零压缩——需归因（模型对软信号采纳差异）。
- P2 双毒株事件倍增未达成（$\mu\approx0.001$）——事件密度设计教训。
- 双层连接（$q$ ↔ $\hat m$ 耦合）未定理化——future work 首位。
- 统计：B-H1c CI 下界微出需更大样本；池化口径失效需稳健判读设计。
- 生态效度：单任务族为主，跨任务族仅隔离保证推广。

---

## 11. Conclusion

> **已扩写全文**：`sections/11-conclusion.md`（v1，2026-10-22）

- 三句主张复述 + 贡献四项 + 一句工程含义（防御依赖隔离而非标记）。

---

## 附录（论文可选）

- A. 判读脚本与数据清单（事实层路径）。
- B. 判读 JSON 关键数值表（与正文同源）。
- C. 功效分析（`e_power_markgate.py/.json`）。

---

## 待补（骨架动笔清单，状态更新）

1. ✅ Related Work 全文（`sections/02-related-work.md`，16 引文含 DOI/arXiv）
2. ✅ §3 机制模型图示（`figures/fig-mechanism.png/svg`，`make_figs.py` 可重生成）
3. ✅ §6 Results 表（§6.6 正式判读表 5 张，数据直出判读 JSON）
4. ✅ §4 定理陈述改写（`sections/04-formalization.md`，Lean B.5 同源）
5. ✅ Abstract 定稿（`abstract.md`，226 词）+ 标题定稿
6. ✅ 附录（`appendix.md`：脚本/数据/判读数值表/口径声明）
7. ✅ 全稿组装（`manuscript.md`，约 3,400 词 + 图 2 张 + 参考文献 16 条；`assemble_manuscript.py` 可重生成）
8. ⏳ 投稿体例转换（LaTeX/Word 双栏，目标 ICSE/arXiv）——待定
9. ⏳ 字数预算：目标 8–12 页双栏（约 6,000–8,000 词）——正文扩写至目标字数或按会议格式裁剪，待定
