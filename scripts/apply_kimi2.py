# -*- coding: utf-8 -*-
PEER = """| **系统稳态 (Equilibrium)** | 文本回答结束即结束 | 物理三态合一：代码落地、原生验证、终审晋升 |

**同行现状说明**：以物理退出码为闭环反馈的 CI 门控在头部工程团队已是成熟实践（编译失败即阻断合并、测试红灯即拒收）。本书的增量不在"引入闭环"这一概念本身，而在将其**公理化**（四大工程公理）、**形式化**（Lean 4 机检，附录 B）与**系统化**（24 模式 + 生产实证）：范式飞跃的落点是体系的工程纪律与可审计证据结构，而非闭环概念的首创。"""
f = r"E:\workspace\industrial-agentic-cybernetics\docs\preface\01-paradigm-shift.md"
t = open(f, encoding="utf-8").read()
n = 0
EQ = "| **系统稳态 (Equilibrium)** | 文本回答结束即结束 | 物理三态合一：代码落地、原生验证、终审晋升 |\n\n**闭环口径声明**"
if EQ in t:
    t = t.replace(EQ, PEER + "\n**闭环口径声明**", 1); n += 1
I2 = "### 1.2 工业级软件底座的真实物理特质\n\n与学术 Benchmark"
IND = "### 1.2 工业级软件底座的真实物理特质\n\n> **『工业级』口径声明**：本书所称\"工业级\"指**经 DevForge-AI 生产环境验证的软件工程智能体场景**（Docker 受控生产拓扑、真实编译/文件系统/审计链路，模式 23/24），并以跨模型（DeepSeek-V4 系 / Kimi / Qwen2.5）、跨任务族受控实验辅助锚定；其对全部工业场景的普遍性由读者依据各章适用域声明自行判断，本书不作全称覆盖宣称。\n\n与学术 Benchmark"
if I2 in t:
    t = t.replace(I2, IND, 1); n += 1
open(f, "w", encoding="utf-8", newline="\n").write(t)
print("OK 01-paradigm-shift.md +%d" % n)
