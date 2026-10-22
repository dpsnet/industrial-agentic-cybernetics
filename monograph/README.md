# monograph/ — 专著出版级组装区

面向出版审阅者/读者的**完成态**产物。专著正文是 `docs/`（preface、part1–9、epilogue、附录 A/B），本目录**不复制正文**（防双源漂移），只存放出版级组装物与发布说明。`docs/` 内的 file:/// 相对引用保持不动。

## 专著构成（正文在主目录 docs/）

- 前篇：`docs/preface/01-paradigm-shift.md`（范式转移+方法论 1.4.1–1.4.5）、`02-compliance-theater.md`、`03-axioms-and-invariance.md`（四大公理+定理 3.1）
- 九部 24 模式：`docs/part1-…/part9-…`
- 结语：`docs/epilogue/`
- 附录：`docs/appendix-formal-proofs.md`（Lean 4 机检 B.2–B.5）、`docs/terminology-mapping.md`、`docs/axioms-validation-report.md`（验证总报告）
- 大纲：`docs/book-outline.md`；`SUMMARY.md`（目录）

## 本目录职责（占位清单）

- [ ] 送审目录/章节清单（出版审阅用）
- [ ] 合并版正文（机械合并，供送审/排版；改动仍回写 docs/）
- [ ] 版式与封面素材
- [ ] 发布说明（版本、修订记录、数据来源声明）

## 当前状态（2026-10-22）

- 方法学加固全部落地：§1.4.1 工程公理声明 / §1.4.2 三层知识地位 / §1.4.3 术语声明 / §1.4.4 实证范围收缩 / §1.4.5 双层连接声明 + 1.3 闭环口径统一
- 公理 IV 实证闭合：SUPERCRITICAL（S-H1/H2/H4 ✅，机制修正已入库）、跨模型、跨任务族、生产现场
- 剩余：H1AC_BOOST 判读（Trae 执行中）→ 回填公理 IV 标记门压缩实证标注

## 专著 vs 论文

专著=完成态（研究过程压缩为边界声明）；论文=辩护态（见 `paper/README.md`）。专著正文本轮不因论文写作而回改，除非实证事实更新。
