# monograph/ — 专著出版级组装区

面向出版审阅者/读者的**完成态**产物。专著正文是 `docs/`（preface、part1–9、epilogue、附录 A/B），本目录**不复制正文**（防双源漂移），只存放出版级组装物与发布说明。`docs/` 内的 file:/// 相对引用保持不动。

## 专著构成（正文在主目录 docs/）

- 前篇：`docs/preface/01-paradigm-shift.md`（范式转移+方法论 1.4.1–1.4.5）、`02-compliance-theater.md`、`03-axioms-and-invariance.md`（四大公理+定理 3.1）
- 九部 24 模式：`docs/part1-…/part9-…`
- 结语：`docs/epilogue/`
- 附录：`docs/appendix-formal-proofs.md`（Lean 4 机检 B.2–B.5）、`docs/terminology-mapping.md`、`docs/axioms-validation-report.md`（验证总报告）
- 大纲：`docs/book-outline.md`；`SUMMARY.md`（目录）

## 本目录职责（占位清单）

- [x] 送审目录/章节清单：`submission-toc.md`（2026-10-24，完成态化预处理后生成）
- [x] 合并版正文：`manuscript-merged.md`（2026-10-24，完成态化预处理后机械合并；改动仍回写 docs/ 后重跑生成）
- [ ] 版式与封面素材（未做，依赖出版社格式要求）
- [x] 发布说明：`release-notes.md`（版本、修订记录、数据来源声明）

## 完成态化预处理（2026-10-24）

合并版生成前对 `docs/` 执行的处理（正文因此回改，属实证事实/文体更新）：删除 `03-axioms-and-invariance.md` 7 处过程性溯源指针（实证数值与边界声明保留，来源声明移入发布说明）；`axioms-validation-report.md` 头部加"验证证据附录"元声明（定位为证据账本，非范式正文）；修正 3 处过时声明（appendix B.10 $q$ 实测、pattern-23 $q$ 待测、pattern-24 实证依赖）；压缩 pattern-23/24 实测块的"完整判读见"文件指针。

## 当前状态（2026-10-22）

- 方法学加固全部落地：§1.4.1 工程公理声明 / §1.4.2 三层知识地位 / §1.4.3 术语声明 / §1.4.4 实证范围收缩 / §1.4.5 双层连接声明 + 1.3 闭环口径统一
- 公理 IV 实证闭合：SUPERCRITICAL（S-H1/H2/H4 ✅，机制修正已入库）、跨模型、跨任务族、生产现场
- H1AC_BOOST 判读已闭合（2026-10-22）：B-H1a ❌ 标记门零压缩（三重独立确认）、B-H1c 🟡 乘性律点估计支持（64 链 0.466≈0.5，CI 下界微出）、B-H2 ✅ 几何律大样本复验——公理 IV 标记门压缩实证标注回填完成（validation-report §4 H1a/H1c 行 + 公理 IV 段）
- 公理 IV 实证事实更新（2026-10-24，论文闭环回写）：漂移状态双峰 + 探针校准协议、$M_c$ 状态条件量（低转写态标注修正）、容量调控控制律高态分支三窗口实证（$p{=}0.0040$）、部署成本-收益边界声明——已回写 `03-axioms-and-invariance.md` 公理 IV 段与 `axioms-validation-report.md` §4

## 专著 vs 论文

专著=完成态（研究过程压缩为边界声明）；论文=辩护态（见 `paper/README.md`）。专著正文本轮不因论文写作而回改，除非实证事实更新。
