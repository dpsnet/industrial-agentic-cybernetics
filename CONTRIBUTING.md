# 参与贡献指南（Contributing）

本仓库是一本开源的学术专著（*Industrial Agentic Cybernetics: Design Patterns and Formal Architecture for Autonomous Software Engineering*），作者**尤其欢迎批评、反例与反驳**——这是理论唯一可信的检验方式；同样欢迎**建议与想法**——新的设计模式、改进方向与路线图讨论。

## 一、如何参与讨论（批评、建议与想法，无需 PR）

讨论、批评与建议不必以 Pull Request 形式提交，直接使用下列通道之一即可：

1. **Discussions**（推荐，用于开放式讨论）——分类见仓库首页：
   - **建议与想法（Ideas）**：对新模式、改进方向与路线图的想法；
   - **批评与反例**：理论/定理的质疑、逻辑漏洞；
   - **数学与形式化**：Lean 4 证明复核、公式推导检查；
   - **实证与实验**：实验设计、统计口径、可复现性；
   - **开放问题**：专著 §3.4 未决项（q–m̂ 双层耦合、a/b 口径映射、W* 阈值等）。
2. **Issue**（适合结构化、可追踪的单一批评）——请使用 [批评模板](.github/ISSUE_TEMPLATE/criticism.md)。

### 推荐批评格式

1. **定位**：注明章节/定理/模式编号（如 §3.3 Theorem 3.1、附录 B.12、模式 02）；
2. **分类**：概念 / 数学 / 形式化 / 实证 / 叙事；
3. **论证**：给出反例、推导或证据（数学类请附定理名与 Lean 文件路径）；
4. **引用**：注明仓库 tag 与 Zenodo DOI `https://doi.org/10.5281/zenodo.23722977`，确保可追溯。

## 二、回应承诺与评审流程

- 作者承诺 **7 日内回应**每条实质批评；
- 每帖/每 Issue 至少得到"已记录，将核验"的回复；
- **不采纳的意见**将以 `wontfix-declined` 标签记录，并在回复中给出可追溯理由——拒绝意见同样留痕，避免重复讨论；
- 涉及 Lean 形式化层的主张，以 `formal_proof/` 的实际代码与 `lake build` 结果为准，不接受口头声称。

## 三、提交代码 / 形式化修补（PR）

若您愿意直接修补 Lean 证明、脚本或文档：

1. Fork 本仓库，从 `master` 新建分支；
2. 修改 Lean 模块请保证 `lake build` 通过（0 公理、0 `sorry`），并在 PR 描述中列出新增/修改的定理名；
3. 修改文档请遵循 [PROJECT_RULES.md](PROJECT_RULES.md)：事实层单源共用、叙述层独立双写；
4. PR 标题建议前缀 `[formalization]` / `[empirical]` / `[docs]` 以利分流。

## 四、行为准则

参见 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)：批评对事不对人，禁止人身攻击；学术争论欢迎，攻讦零容忍。

## 五、版本与引用

- 每次 Release 均与 Zenodo 归档（DOI `https://doi.org/10.5281/zenodo.23722977`）同步，批评请注明版本；
- 引用本书请注明：王斌（Bin Wang）. 《工业级智能体控制论》（CC BY 4.0，见 [README](README.md)）。
