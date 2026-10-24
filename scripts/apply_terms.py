# -*- coding: utf-8 -*-
import os, re

pairs = [
# --- 导读块插入（前移借喻声明） ---
("# 第一章 范式转移：从离散提示词工程到闭环控制论\n## Chapter 1: The Paradigm Shift — From Discrete Prompting to Closed-Loop Cybernetics\n\n> “在任何足够复杂的系统演化中",
 "# 第一章 范式转移：从离散提示词工程到闭环控制论\n## Chapter 1: The Paradigm Shift — From Discrete Prompting to Closed-Loop Cybernetics\n\n> **全书术语约定（导读）**：「控制论」为工程闭环反馈借喻（详见 §1.4.3），非 Wiener 控制论学科继承；「相变／超临界／近临界」为 Galton-Watson 分支过程术语（ρ=1 临界），非热力学相变；「免疫」指经验繁殖阈值（q>1/2）下的谱系抑制，非生物学免疫；公理 II 的「注意力稀释」对应信噪比相对损失（SNR 相对损失），非热力学熵。本书统一以「经验资产」指称智能体萃取的可复用经验条目。\n\n> “在任何足够复杂的系统演化中"),
# --- 必然 3+1 处 ---
("当‘满足测试通过’作为唯一目标函数而脱离物理基质时，它必然学会伪造测试本身。”",
 "当‘满足测试通过’作为唯一目标函数且缺乏物理锚定时，模型会倾向伪造测试——条件结论，实测见 13 模型 exploit 率 0–13.9%（arXiv:2605.02964）。”"),
("而是**基于强化学习与概率采样优化机制的必然博弈结果**。",
 "而是**在缺乏外部物理锚定的条件下，基于强化学习与概率采样优化机制收敛为奖励欺骗的博弈结果（条件结论，§2.2）**。"),
("且在可被欺骗的评价信号下，智能体必然涌现奖励欺骗（Reward Hacking）行为",
 "且在可被欺骗的评价信号下，受控实验普遍观测到奖励欺骗（Reward Hacking）行为（Amodei et al., 2016）"),
("可欺骗评价信号下必然涌现奖励欺骗（Amodei et al. 2016；Huang et al., ICLR 2024",
 "可欺骗评价信号下受控实验普遍观测到奖励欺骗（Amodei et al. 2016；Huang et al., ICLR 2024"),
# --- 彻底 24 处 ---
("为了从数学上彻底根除奖励欺骗，控制论架构必须", "为了从数学上根除奖励欺骗（条件定理意义下），控制论架构必须"),
("| 彻底破坏了测试防护网", "| 破坏了测试防护网"),
("彻底杜绝“虚假繁荣”——任何试图钻营提示词漏洞或绕过测试的行为都会被机械拦截；",
 "杜绝“虚假繁荣”（所测环境与任务族内；F1/F2 各 10 次注入，拦截率 1.00，n=10）——任何试图钻营提示词漏洞或绕过测试的行为都会被机械拦截；"),
("的双阶段物理隔离，彻底切断考题制造者与考卷解答者", "的双阶段物理隔离，切断考题制造者与考卷解答者"),
("彻底杜绝了智能体“通过放宽测试断言来让自己蒙混过关”的道德风险；",
 "杜绝了智能体“通过放宽测试断言来让自己蒙混过关”的道德风险（受控实验：隔离环境下断言篡改拦截率 1.00）；"),
("压降 >60% 无关上下文，彻底抑制上下文退化（Context Rot）", "压降 >60% 无关上下文，显著抑制上下文退化（Context Rot）"),
("彻底消灭 Token 截断灾难", "消除 Token 截断的高成本失效"),
("全量重跑的灾难性开销 Cascading Re-run Overhead", "全量重跑的高开销 Cascading Re-run Overhead"),
("极易发生灾难性代码变形，最终彻底偏离初始架构", "极易发生严重代码变形，最终偏离初始架构"),
("使代码文件彻底损毁；", "使代码文件损毁；"),
("彻底消灭编译器幽灵报错", "消除编译器幽灵报错"),
("彻底消除多 Agent 并发写入引发的代码撕裂与 Git 冲突；",
 "消除多 Agent 并发写入引发的代码撕裂与 Git 冲突（租约互斥机检，附录 B.4）；"),
("彻底避免了多智能体竞争导致的", "避免了多智能体竞争导致的"),
("彻底平息多 Agent 盲目并发引发的文件事件风暴。", "平息多 Agent 盲目并发引发的文件事件风暴。"),
("彻底根除“一条错误经验毒死整个平台”的连锁反应；", "根除“一条错误经验毒死整个平台”的连锁反应（污点追踪+晋升门禁）；"),
("彻底抹杀了既有经过物理验证的高价值技术资产", "抹杀了既有经过物理验证的高价值技术资产"),
("彻底解放人类工程师的双眼与双手", "解放人类工程师的双眼与双手"),
("的特权，彻底打破智能体深陷自愈死循环或偏离业务目标的失控态", "的特权，打破智能体深陷自愈死循环或偏离业务目标的失控态"),
("不再是无能为力的旁观者，彻底消灭失控自愈死循环；", "不再是无能为力的旁观者，消灭失控自愈死循环；"),
("用于提示智能体的上下文彻底物理解耦", "用于提示智能体的上下文物理解耦"),
("导致评测指标彻底失真", "导致评测指标失真"),
("彻底打破传统评测中依赖大模型自评（LLM-as-a-Judge）", "打破传统评测中依赖大模型自评（LLM-as-a-Judge）"),
("在彻底根除上下文退化（Context Rot, Liu et", "在显著缓解上下文退化（Context Rot, Liu et"),
("彻底消灭进程启动抖动", "消除进程启动抖动"),
("彻底摆脱了桌面 CLI 工具内部复杂的权限拦截逻辑", "摆脱了桌面 CLI 工具内部复杂的权限拦截逻辑"),
("导致灾难性回归缺陷逃逸至生产环境", "导致严重回归缺陷逃逸至生产环境"),
# --- 公理 II 改名 ---
("注意力熵增与特权发散公理（Axiom of Attention Entropy）", "注意力稀释与特权发散公理（Axiom of Attention Dilution）"),
("注意力熵增公理（Axiom of Attention Entropy）", "注意力稀释公理（Axiom of Attention Dilution）"),
("II 注意力熵增", "II 注意力稀释"),
("“注意力熵增”为隐喻命名：公理 II 的实际可操作量是", "“注意力稀释”为公理 II 的操作性命名：其实际可操作量是"),
("知识库熵增急剧膨胀", "知识库碎片化急剧膨胀"),
("知识库熵增失控", "知识库碎片化失控"),
# --- 免疫锚定 / 生命体 ---
("#### 公理 IV：经验自免疫公理（Axiom of Crystallization Auto-Immunity）\n* **数学表达**",
 "#### 公理 IV：经验自免疫公理（Axiom of Crystallization Auto-Immunity）\n\n> **术语锚定**：「自免疫」为工程借喻——指经验繁殖阈值 $q>1/2$ 不满足时的谱系抑制，非生物学免疫。\n\n* **数学表达**"),
("而是一个具备因果不变性、物理现实感知与自免疫收敛能力的控制论生命体。”",
 "而是一个具备因果不变性、物理现实感知与自免疫收敛能力的控制论生命体。”（修辞语；所指机制为公理 IV 的经验自免疫收敛，非生物学术语。）"),
]

roots = [
    r"E:\workspace\industrial-agentic-cybernetics\docs",
    r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md",
    r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-merged.md",
]
files = []
for r in roots:
    if r.endswith(".md"):
        files.append(r)
    else:
        for dp, dn, fns in os.walk(r):
            for f in fns:
                if f.endswith(".md"):
                    files.append(os.path.join(dp, f))

for f in files:
    t = open(f, encoding="utf-8").read()
    total = 0
    for old, new in pairs:
        n = t.count(old)
        if n:
            t = t.replace(old, new)
            total += n
    if total:
        open(f, "w", encoding="utf-8", newline="\n").write(t)
        print("OK %-70s +%d" % (os.path.relpath(f, r"E:\workspace\industrial-agentic-cybernetics"), total))
print("done")
