# -*- coding: utf-8 -*-
"""Normalize work-flow wording to academic expressions (zh/en)."""
import io

ZH = r"E:\workspace\industrial-agentic-cybernetics\paper\sections\07-capacity-regulation.md"
ZR = r"E:\workspace\industrial-agentic-cybernetics\paper\sections\06-results.md"
ZF = r"E:\workspace\industrial-agentic-cybernetics\paper\sections\04-formalization.md"
ZE = r"E:\workspace\industrial-agentic-cybernetics\paper\sections\05-experimental-setup.md"
ZL = r"E:\workspace\industrial-agentic-cybernetics\paper\sections\11-limitations.md"
EN = r"E:\workspace\industrial-agentic-cybernetics\paper\sections_en\07-capacity-regulation.md"

jobs = [
    (ZH, "## 7.3 三方案权衡面（推导 + 基线锚定，实验前）", "## 7.3 三方案权衡面（推导与基线锚定）", 1),
    (ZH, "## 7.4 实验方案与预期效果（实验前注册）", "## 7.4 实验方案与预期效果（预先注册）", 1),
    (ZH, "2026-10-23 23:23 门控窗口 12 链，实验前已测", "2026-10-23 23:23 探针门控窗口 12 链，于实验前测得", 1),
    (ZH, "此处锚定的均为**实验前已测基线**", "此处锚定数据均为**实验前测得**", 1),
    (ZH, "本节把 §7.1–§7.3 的三个可证伪预言固化为控制实验方案。**前置基线已测（2026-10-23 23:23 门控窗口", "本节将 §7.1–§7.3 的三个可证伪预言固定为受控实验方案。**基线于实验前测得（2026-10-23 23:23 探针门控窗口", 1),
    (ZH, "C2 基线落地为 0.305", "C2 基线确定为 0.305", 1),
    (ZH, "- **协议（写死）**", "- **协议（预先固定）**", 1),
    (ZH, "- **判据（写死）**", "- **判据（预先固定）**", 1),
    (ZH, "- **预期效果（推导）**：C1 命中 ⟹ \"动态容量是状态反馈的有效软调节，安全-效用 Pareto 优于静态高态 $W{=}8$\"，本章从理论衍生升级为控制实验实证；C1 失败（动态未显著优于静态）⟹ 控制律表述按 §11 惯例留痕修正（可能退化为\"状态感知的静态配置\"）。",
     "- **预期效果**：C1 满足 ⟹ \"动态容量是状态反馈的有效软调节，安全-效用 Pareto 优于静态高态 $W{=}8$\"，本章主张由理论推导转为受控实验实证；C1 未满足（动态未显著优于静态）⟹ 控制律表述按 §11 惯例修正并记录在案（可能退化为\"状态感知的静态配置\"）。", 1),
    (ZH, "**控制实验已执行（2026-10-24 02:38 凌晨窗口，探针 4/4", "**受控实验于 2026-10-24 02:38 凌晨窗口执行（探针 4/4", 1),
    (ZH, "判据核验：", "判据检验：", 1),
    (ZH, "（敏感性 0.5→0.8 重判同向 PASS）", "（按 §11.3 敏感性惯例以 0.8 阈值复核，方向结论一致，通过）", 1),
    (ZH, "分层与整批判读方向一致 PASS", "分层与整批判读方向一致，通过", 1),
    (ZH, "任一判据失败均如实记录。", "未达判据的结果均按预注册要求如实报告。", 1),
    (ZH, "三判据全数命中——**本章升级为控制实验实证：", "三项判据均满足——**本章主张由此得到受控实验实证：", 1),
    (ZH, "\n**定位**：期刊版增量（漂移表征路线），不阻塞当前投稿。", "", 1),
    (ZR, "（计划 §1.2e，写死：高转写态下 $W{=}8$ 存活率 $\\ge0.5$ ⟹", "（计划 §1.2e 预先固定：高转写态下 $W{=}8$ 存活率 $\\ge0.5$ ⟹", 1),
    (ZR, "第二事件通道未被模型采纳，如实记录（§11）", "第二事件通道未被模型采纳（记录在案，§11）", 1),
    (ZR, "非单调异常如实记录：$b=2, W=4$ 存活率 1.00", "非单调异常记录在案：$b=2, W=4$ 存活率 1.00", 1),
    (ZR, "（非单调异常，如实记录）", "（非单调异常，记录在案）", 1),
    (ZR, "处分裂如实记录；", "处分裂记录在案；", 1),
    (ZR, "**判据命中**：", "**判据满足**：", 1),
    (ZF, "机制修正如实记录（§9）", "机制修正记录在案（§9）", 1),
    (ZE, "任何口径修订在 §11 如实记录（如 H1AC 池化口径失效）", "任何口径修订在 §11 记录在案（如 H1AC 池化口径失效）", 1),
    (ZL, "均已如实记录于计划 §9", "均已记录于计划文档 §9", 1),
    (ZL, "修正须留痕，不得静默移动球门", "修正须记录在案，不得在结果已知后更改判据", 1),
    (ZL, "按现有数据重判，$W_c(b)$ 为", "按现有数据复核，$W_c(b)$ 为", 1),
    (EN, "## 7.3 Three-scheme trade-off (derivation + baseline anchoring, pre-experiment)", "## 7.3 Three-scheme trade-off (derivation and baseline anchoring)", 1),
    (EN, "## 7.4 Experimental protocol and expected effects (pre-registered, pre-experiment)", "## 7.4 Experimental protocol and expected effects (pre-registered)", 1),
    (EN, "The prerequisite baseline is measured (gated window 2026-10-23 23:23", "The baseline was measured before the experiment (gated window 2026-10-23 23:23", 1),
    (EN, "amended with the §11 trail (possibly degrading to", "amended and recorded per the §11 convention (possibly degrading to", 1),
    (EN, "The control experiment is executed (gated window 2026-10-24 02:38", "The control experiment was executed at 02:38 on 2026-10-24 in a gated window (probes 4/4", 1),
    (EN, "Criterion check: C1 survival 0.333 $\\le0.5$ and vs static 0.833 Fisher one-sided $p{=}0.018<0.05$ (sensitivity re-judgment 0.5→0.8 also PASS); C2 utility 0.328 $\\ge0.275$ PASS; C3 all probe segments share one window, layered and pooled readings agree in direction PASS.",
     "Criterion check: C1 survival 0.333 $\\le0.5$ and vs static 0.833 Fisher one-sided $p{=}0.018<0.05$ (sensitivity re-check at the 0.8 threshold also met); C2 utility 0.328 $\\ge0.275$ met; C3 all probe segments share one window, layered and pooled readings agree in direction, met.", 1),
    (EN, "Any unmet criterion is recorded truthfully.", "Any unmet criterion is reported as per the pre-registration.", 1),
    (EN, "All three criteria are met—this chapter is upgraded to control-experiment validation:", "All three criteria are met—the chapter's claim is thereby supported by control-experiment validation:", 1),
    (EN, "\n- **Positioning**: journal-version increment (drift-characterization route); does not block the current submission.", "", 1),
]

for path, old, new, expect in jobs:
    s = io.open(path, encoding="utf-8").read()
    n = s.count(old)
    if n != expect:
        print("WARN %s: expected %d got %d -> %s" % (path.split("\\")[-1], expect, n, old[:60]))
        continue
    io.open(path, "w", encoding="utf-8", newline="\n").write(s.replace(old, new))
    print("OK  %s: %s" % (path.split("\\")[-1], old[:60]))
