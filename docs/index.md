---
title: 工业级智能体控制论
---

# 《工业级智能体控制论：自主软件工程的设计模式与形式化架构》

**Industrial Agentic Cybernetics: Design Patterns and Formal Architecture for Autonomous Software Engineering**

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.23636677-1769AA.svg)](https://doi.org/10.5281/zenodo.23636677)
[![License: MIT (Code)](https://img.shields.io/badge/Code-MIT-blue.svg)](https://github.com/dpsnet/industrial-agentic-cybernetics/blob/master/LICENSE)
[![License: CC BY 4.0 (Text)](https://img.shields.io/badge/Text-CC--BY--4.0-green.svg)](https://github.com/dpsnet/industrial-agentic-cybernetics/blob/master/LICENSE-CC-BY-4.0.txt)
[![Standard: GoF-Style Patterns](https://img.shields.io/badge/Pattern-GoF--Style-success.svg)](https://github.com/dpsnet/industrial-agentic-cybernetics)
[![Field: Agentic Cybernetics](https://img.shields.io/badge/Domain-Software%20Engineering-orange.svg)](https://github.com/dpsnet/industrial-agentic-cybernetics)

本书将经典系统控制论（Cybernetics）、分布式系统因果一致性理论、编译原理与认知注意力约束系统性引入智能体系统架构，提炼出 **9 大模式族、24 个工业级设计模式** 与 **四大底层控制论公理**；全部核心定理经 Lean 4 内核验证（118 条：117 定理 + 1 辅助引理，0 公理 0 sorry）。

- **完整排版 PDF**：[📄 Industrial-Agentic-Cybernetics.pdf（LaTeX 编译版，约 180 页）](Industrial-Agentic-Cybernetics.pdf)
- **Zenodo DOI（概念，指向最新版）**：`https://doi.org/10.5281/zenodo.23636677`
- **许可证**：代码 MIT · 文本 CC BY 4.0（署名 王斌 / 北京开路者科技有限公司）

---

## 序言与公理 (Preface & Axioms)

- [01. 范式转移：从离散提示词工程到闭环控制论](preface/01-paradigm-shift.html)
- [02. 奖励欺骗（Reward Hacking）的形式化分析与物理破局](preface/02-compliance-theater.html)
- [03. 工业级智能体四大公理与因果不变性形式化定义](preface/03-axioms-and-invariance.html)

## 第一部分：物理底座与现实锚定 (Substrate Anchoring)

- [模式 01：物理底座穿透核验模式](part1-substrate-anchoring/pattern-01-substrate-penetration.html)
- [模式 02：审查者现实审计一票否决模式](part1-substrate-anchoring/pattern-02-reality-audit-veto.html)
- [模式 03：脚手架与解题域双阶段隔离模式](part1-substrate-anchoring/pattern-03-two-phase-mandate.html)

## 第二部分：注意力约束与最小特权投影 (Cognitive Attention & PoLP)

- [模式 04：任务级最小特权投影模式](part2-cognitive-attention/pattern-04-task-level-polp.html)
- [模式 05：两阶段宏微观渐进设计展开模式](part2-cognitive-attention/pattern-05-macro-micro-elaboration.html)
- [模式 06：流式拓扑分解与选择性断点续跑模式](part2-cognitive-attention/pattern-06-streaming-decomposition.html)

## 第三部分：执行韧性与微循环自愈 (Execution Resilience & Self-Healing)

- [模式 07：沙箱驱动-导航结对微循环模式](part3-execution-resilience/pattern-07-driver-navigator-pairing.html)
- [模式 08：白盒隐式分支嗅探与内部锚定模式](part3-execution-resilience/pattern-08-implicit-branch-sniffing.html)
- [模式 09：幂等变异日志与物理时钟补偿模式](part3-execution-resilience/pattern-09-idempotent-journal-mtime.html)

## 第四部分：并发争用与分布式状态协调 (Concurrency & Coordination)

- [模式 10：分布式物理底座租约锁模式](part4-concurrency-coordination/pattern-10-substrate-lease-lock.html)
- [模式 11：主写从读降级互斥模式](part4-concurrency-coordination/pattern-11-primary-writer-replica-reader.html)
- [模式 12：异构对等智能体抽象协议桥接模式](part4-concurrency-coordination/pattern-12-peer-agent-protocol-bridge.html)

## 第五部分：知识萃取与自免疫演进 (Knowledge Crystallization & Auto-Immunity)

- [模式 13：单源事实-模式双模萃取模式](part5-crystallization-immunity/pattern-13-dual-mode-crystallization.html)
- [模式 14：隔离草稿与终审晋升门禁模式](part5-crystallization-immunity/pattern-14-quarantine-promotion-gate.html)
- [模式 15：污点污染防御与防伪退化模式](part5-crystallization-immunity/pattern-15-tainted-pattern-rejection.html)

## 第六部分：人机共生与非对称认知交互 (Human-Agent Symbiosis)

- [模式 16：手风琴式认知多分辨率投影模式](part6-human-agent-symbiosis/pattern-16-accordion-projection.html)
- [模式 17：飞行指挥官异步中断与航向锁定模式](part6-human-agent-symbiosis/pattern-17-flight-director-interrupt.html)

## 第七部分：客观度量与基准测评 (Objective Evaluation & Benchmarks)

- [模式 18：隐藏 Oracle 物理隔离沙箱测评模式](part7-objective-evaluation/pattern-18-hidden-oracle-sandbox.html)
- [模式 19：五重无旁路机械判据模式](part7-objective-evaluation/pattern-19-five-fold-mechanical-evaluator.html)
- [模式 20：工业基准 A/B 物理对照评测模式](part7-objective-evaluation/pattern-20-substrate-ab-benchmark.html)

## 第八部分：智能体能效与收敛工程学 (Convergence Economics & Tokenomics)

- [模式 21：Token 吞吐断崖式压缩架构](part8-convergence-economics/pattern-21-token-compression-architecture.html)
- [模式 22：纯模型原生 Provider 解耦桥接模式](part8-convergence-economics/pattern-22-native-provider-bridge.html)

## 第九部分：生产韧性与反馈闭环 (Production Resilience & Feedback Loop)

- [模式 23：生产环境运行时监控与异常嗅探模式](part9-production-resilience/pattern-23-production-runtime-anomaly-sniffing.html)
- [模式 24：生产缺陷萃取与热修复闭环模式](part9-production-resilience/pattern-24-production-defect-crystallization-hotfix-loop.html)

## 结语与附录 (Epilogue & Appendix)

- [结语：通向自给自足的自主软件工程](epilogue/towards-autonomous-cybernetics.html)
- [附录 B：形式化收敛性与稳定性证明（Lean 4 机检）](appendix-formal-proofs.html)

---

## 参与讨论：批评、建议与想法

本书诚挚欢迎批评、反例与反驳，同样欢迎建议与想法：**章节化阅读的另一重意义是——每条批评都可以直接锚定到具体章节与定理编号**。

- 前往 [GitHub Discussions](https://github.com/dpsnet/industrial-agentic-cybernetics/discussions)（分类：建议与想法 / 批评与反例 / 数学与形式化 / 实证与实验 / 开放问题）
- 或使用 [结构化批评 Issue 模板](https://github.com/dpsnet/industrial-agentic-cybernetics/issues/new/choose)
- 作者承诺 7 日内回应；不采纳意见以 `wontfix-declined` 标签记录可追溯理由

> 引用请注明版本（tag，当前 v1.1.2）与 Zenodo 概念 DOI `https://doi.org/10.5281/zenodo.23636677`（始终指向最新版归档）。
