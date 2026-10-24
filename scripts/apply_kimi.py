# -*- coding: utf-8 -*-
import os, re

EVT = """#### 3.2.1 四公理证据等级总览

> 口径声明：四公理均为**工程公理**（1.4.1）——占据推理起点地位、内容是经验命题。下表按评审可审计口径给出各公理当前的形式化、实证、模型覆盖与生产验证状态；同一"公理"名号不均分信用，证据分布以本表为准。

| 公理 | 认识论类型 | 形式化层（Lean 4 机检） | 受控实验（规模/模型） | 生产验证 | 显式边界 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| I 物理非信任 | 安全文献共识的工程格言化（渐近命题） | B.2：3 定理（自检后验=先验、闭环风险因子化、后验与机制无关） | 文献锚点（Amodei 2016；Huang ICLR 2024；Anthropic 2511.18397） | 模式 23：F1/F2 检出 1.00（各 n=10）、F4 零误报（60 期） | 形式陈述为极限式 $\\lim P\\le\\epsilon$，有限实验不能确立极限；实证支撑工程推论"自报不可信" |
| II 注意力稀释 | 带边界声明的经验律 | B.3：稀释严格性、三增长分支衰减、违约下界、两相模型、口径定理 + InjectionCoupling 桥接 | E3/E3b+E4（Qwen2.5-1.5B/7B，≤131k）；E8 负结果（三结构量跨模型不稳健） | 无直接生产闭环 | $W^*$ 为经验参数不写入形式化接口；定理 $a/b$ ↔ 实验 needle/填充段口径映射为未证假设（B.11） |
| III 变异因果单调 | 分布式系统经典结论的应用迁移 | B.4：2 定理 + B.8/B.9（租约 5 定理、主写从读单写者因果序） | Cargo 1.96/NTFS 28/28 组受控测量 | 模式 23/24：篡改注入 20 例全拒；708 条误拒装置缺陷自曝（已修复） | 适用域为 mtime 增量编译器（Bazel/Nix 不适用）；Windows PE 使比特层幂等不可能 |
| IV 经验自免疫 | 定理 + 多模型实证 + 生产闭环（最强支柱） | B.5：GW 相变族 + B.7 Foster-Lyapunov 停时界 + B.10 观测-学习回路稳定性 | 288+288+144+160 链（DeepSeek v4-pro / Kimi / Flash-1017，预注册判读） | 模式 24：晋升 14/14、拦截 1.00、泄漏 0 | $q$–$\\hat m$ 耦合未建立（开放项 1）；切换动力学待测 |

> 三条结论：① 证据强度排序为 IV > II > III ≈ I——"公理"名号不承载同等级经验确认；② 形式化层（B.2–B.10）全部为 Lean 4 内核验证（0 sorry），其确证不随本表排序变化；③ 各公理适用域与开放项见 3.4 与附录 B.11。

#### 公理 I：物理非信任公理（Axiom of Physical Non-Trustworthiness）"""

PEER = """| **系统稳态 (Equilibrium)** | 文本回答结束即结束 | 物理三态合一：代码落地、原生验证、终审晋升 |

**同行现状说明**：以物理退出码为闭环反馈的 CI 门控在头部工程团队已是成熟实践（编译失败即阻断合并、测试红灯即拒收）。本书的增量不在"引入闭环"这一概念本身，而在将其**公理化**（四大工程公理）、**形式化**（Lean 4 机检，附录 B）与**系统化**（24 模式 + 生产实证）：范式飞跃的落点是体系的工程纪律与可审计证据结构，而非闭环概念的首创。"""

IND = """### 1.2 工业级软件底座的真实物理特质

> **『工业级』口径声明**：本书所称"工业级"指**经 DevForge-AI 生产环境验证的软件工程智能体场景**（Docker 受控生产拓扑、真实编译/文件系统/审计链路，模式 23/24），并以跨模型（DeepSeek-V4 系 / Kimi / Qwen2.5）、跨任务族受控实验辅助锚定；其对全部工业场景的普遍性由读者依据各章适用域声明自行判断，本书不作全称覆盖宣称。"""

files = [
    r"E:\workspace\industrial-agentic-cybernetics\docs\preface\03-axioms-and-invariance.md",
    r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md",
    r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-merged.md",
]
AX = "#### 公理 I：物理非信任公理（Axiom of Physical Non-Trustworthiness）"
EQ = "| **系统稳态 (Equilibrium)** | 文本回答结束即结束 | 物理三态合一：代码落地、原生验证、终审晋升 |\n\n**闭环口径声明**"
I2 = "### 1.2 工业级软件底座的真实物理特质\n\n与学术 Benchmark"
for f in files:
    t = open(f, encoding="utf-8").read()
    n = 0
    if AX in t:
        t = t.replace(AX, EVT, 1); n += 1
    if EQ in t:
        t = t.replace(EQ, PEER + "\n**闭环口径声明**", 1); n += 1
    if I2 in t:
        t = t.replace(I2, "### 1.2 工业级软件底座的真实物理特质\n\n> **『工业级』口径声明**：本书所称\"工业级\"指**经 DevForge-AI 生产环境验证的软件工程智能体场景**（Docker 受控生产拓扑、真实编译/文件系统/审计链路，模式 23/24），并以跨模型（DeepSeek-V4 系 / Kimi / Qwen2.5）、跨任务族受控实验辅助锚定；其对全部工业场景的普遍性由读者依据各章适用域声明自行判断，本书不作全称覆盖宣称。\n\n与学术 Benchmark", 1); n += 1
    # B 附录目录标题行级替换（仅以 ## 开头的标题）
    t2 = re.sub(r"(^## B\.\d+ [^（\n]*?)（全部已证）", r"\1（形式化层全部已证）", t, flags=re.M)
    if t2 != t:
        n += sum(1 for m in re.finditer(r"(^## B\.\d+ [^（\n]*?)（全部已证）", t, flags=re.M))
        t = t2
    if n:
        open(f, "w", encoding="utf-8", newline="\n").write(t)
        print("OK", os.path.basename(f), "+%d" % n)
# appendix 文件（独立于三源之外的权威附录源）
ap = r"E:\workspace\industrial-agentic-cybernetics\docs\appendix-formal-proofs.md"
t = open(ap, encoding="utf-8").read()
t2 = re.sub(r"(^## B\.\d+ [^（\n]*?)（全部已证）", r"\1（形式化层全部已证）", t, flags=re.M)
print("OK appendix-formal-proofs.md +%d" % (sum(1 for m in re.finditer(r"(^## B\.\d+ [^（\n]*?)（全部已证）", t, flags=re.M))))
open(ap, "w", encoding="utf-8", newline="\n").write(t2)
print("done")
