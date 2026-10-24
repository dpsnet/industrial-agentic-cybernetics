# -*- coding: utf-8 -*-
"""Section 11.4 deployment overhead assessment (zh+en)."""
import io

S = r"E:\workspace\industrial-agentic-cybernetics\paper\sections\11-limitations.md"
E = r"E:\workspace\industrial-agentic-cybernetics\paper\sections_en\11-limitations.md"

zh_anchor = "控制律升级路线（future work）：当前探针测量的是**外生扰动**（模型毒株转写状态，不受窗口 $W$ 影响），控制结构更接近前馈补偿；教科书意义的**输出反馈**应改为直接测量受控对象自身输出（实验链记忆内的毒丸存量或存留率）再调 $W$。"

zh_add = zh_anchor + (
    "**部署附加投入评估**（基于上述实测读数；Flash 计价 1 token=0.19 credits、单链约 14,000 tokens 折 2,660 credits）："
    "12 链受控批下，静态高态 $W{=}8$ 批成本 31,920 credits（毒丸存活期望 10.0 链、效用保留 0.541）；"
    "门控方案（+1 探针）34,580 credits（存活 4.0 链、效用 0.328），增量 2,660 credits、即每消灭一条毒丸链 443 credits；"
    "随动 1:3（+4 探针，02:38 实测配置）42,560 credits（增量 1,773 credits/毒丸链）；"
    "随动 1:2 加门控 50,540 credits（增量 3,103 credits/毒丸链）。"
    "安全与效用在三档防御配置下完全相同（0.333/0.328，高态分支读数）——"
    "**探针开销增量全部购买的是“批内漂移可行使性”（切换动力学，上文列为待测），而非直接的安全收益**；"
    "权衡点实为效用侧：$W{=}4$ 较静态 $W{=}8$ 牺牲 21.3 个百分点良性记忆（0.541→0.328）。"
    "对照而言，隔离在纯 credits–安全–效用表上绝对占优（零增量、毒丸 0 存活、效用保留 0.88）；"
    "动态容量控制的部署合理性因此依赖**隔离的可用性代价**（记忆冻结期间功能不可用）这一运营前提——"
    "该代价未计入 credits、不可量化，部署决策需按可用性需求取舍。"
    "成本结论对 token 量纲不变：生产环境单价不同时按 token 数等比换算。"
)

en_anchor = "The control-law upgrade route (future work): the probe currently measures an **exogenous disturbance** (the model's strain-transcription state, unaffected by the window $W$), so the control structure is closer to feedforward compensation; textbook **output feedback** would instead measure the controlled object's own output (poison load or retention within the experimental chains' memory) to adjust $W$."

en_add = en_anchor + (
    " **Deployment overhead assessment** (based on the measured readings above; Flash pricing 1 token=0.19 credits, one chain \u224814,000 tokens \u22482,660 credits): "
    "for a 12-chain controlled batch, static high-state $W{=}8$ costs 31,920 credits (expected poison survival 10.0 chains, utility retention 0.541); "
    "the gated scheme (+1 probe) costs 34,580 credits (survival 4.0 chains, utility 0.328)\u2014an increment of 2,660 credits, i.e. 443 credits per poison chain eliminated; "
    "companion probing at 1:3 (+4 probes, the 02:38 measured configuration) costs 42,560 credits (1,773 credits per poison chain); "
    "companion 1:2 plus gating costs 50,540 credits (3,103 credits per poison chain). "
    "Safety and utility are identical across the three defense configurations (0.333/0.328, high-state-branch readings)\u2014"
    "**the incremental probe cost buys only \u201cwithin-batch drift exercisability\u201d (the switching dynamics listed as untested above), not direct safety gains**; "
    "the actual tradeoff is on the utility side: $W{=}4$ sacrifices 21.3 percentage points of benign-memory retention relative to static $W{=}8$ (0.541\u21920.328). "
    "For comparison, quarantine is strictly dominant on the pure credits\u2013safety\u2013utility table (zero increment, zero poison survival, utility retention 0.88); "
    "the deployment rationale for dynamic capacity control therefore rests on the **availability cost of quarantine** (memory frozen and unusable during quarantine)\u2014"
    "a cost not counted in credits and not quantifiable, to be weighed against availability requirements. "
    "The cost conclusions are invariant to token scale: different production pricing rescales linearly by token count."
)

for path, old, new in ((S, zh_anchor, zh_add), (E, en_anchor, en_add)):
    c = io.open(path, encoding="utf-8").read()
    n = c.count(old)
    assert n == 1, (path, n)
    io.open(path, "w", encoding="utf-8", newline="\n").write(c.replace(old, new))
print("applied both")
