# paper/ — 论文产出区

面向审稿人/期刊会议的**主张辩护态**产物。原始研究资料一律留在主目录（`docs/`、`experiments/`、`formal_proof/`），本目录只放论文本体及其派生素材；正文引用主目录原始文档，**不复制**（防双源漂移，docs 内的 file:/// 相对引用不断）。

## 当前唯一候选：公理 IV 聚焦论文

**主题**：无门禁智能体记忆架构下的毒株传播——相变、架构效应与隔离不变性。

**核心主张（三句）**：
1. 无门禁的累积型记忆架构下，毒株池持续累积不可自愈（工程语义的超临界，机制为线性累积-容量竞争；C0-full 12/12，m̂=1.166，CI [1.156,1.176]）；
2. 传播机制由**架构**决定而非模型：选择性转写=分支衰减（GW，m̂ 区间 [0.56,0.98]），全量追加=累积-竞争（W≡1 线性写入，容量 W 为控制参量，临界 W_c∈(8,16)）；
3. 隔离跨机制截断累积（C3-full 12/12、跨模型 24/24、跨任务族 48/48）；标记门零压缩（Flash 档 C1-full 12/12；pro 档功效分析待 H1AC 判读）——**防御依赖隔离而非标记**。

**目标出口**：ICSE/FSE/ASE 实证轨道，或 arXiv cs.SE → ACM TOSEM。

**结构映射（论文章节 ← 原始文档素材）**：

| 论文部分 | 素材来源 |
| :--- | :--- |
| Introduction（问题→缺口→主张） | `docs/preface/03` 公理 IV + `docs/axioms-validation-report.md` |
| 机制模型（GW 分支 vs 累积-竞争） | `experiments/attention_growth/EXPERIMENT_PLAN_AXIOM4_SUPERCRITICAL.md` §8.4 |
| 形式化（Lean 条件定理） | `docs/appendix-formal-proofs.md` B.5 |
| 实验（跨模型×跨架构×容量×隔离/标记门） | SUPERCRITICAL 384 会话 + 跨模型 288 + 跨任务族 144 + H1AC 960（待判读） |
| 功效分析 | `experiments/attention_growth/e_power_markgate.py/.json` |
| 方法论（工程公理、三层知识地位） | `docs/preface/01` §1.4.1–1.4.2 |
| Scope & Generalizability | `docs/preface/01` §1.4.4–1.4.5 |
| Limitations / 双层连接 | `docs/preface/01` §1.4.5 |

**写作口径（专著 vs 论文差异）**：
- 专著=完成态（演化压缩为边界）；论文=辩护态（S-H3 被机制证据否定 → 理论修订为累积-竞争，写成叙事亮点）
- 论文 Introduction 用"问题→文献缺口→本工作主张"，不从公理体系讲起
- 论文 Methods 从"方法论选择"角度写 1.4 声明段，而非"术语纪律"角度

## 状态

- [ ] H1AC_BOOST 判读（Trae 执行中，产物：`experiments/attention_growth/axiom4_results_h1ac_*.json`）
- [ ] 论文骨架（动笔条件：H1AC 判读完成）
- [ ] Related Work 紧对标（Shumailov Nature 2024 / arXiv:2512.16962 / arXiv:2511.18397 / Liu TACL 2024 / RULER）
- [ ] 正文初稿
- [ ] 目标 venue 提交
