# 公理 I–IV 验证总结报告

> 工业智能体控制论（IAC）四条元公理的形式化与实证验证总账
> 日期：2026-10-21　状态：**四条公理全部闭环（形式化 + 实证 + 文档回写）**
> 形式化工程：`formal_proof/IACFormalization`（Lean 4 + mathlib4，**0 sorry**，全部定理经内核验证）
> 正文：`docs/preface/03-axioms-and-invariance.md`；形式化附录：`docs/appendix-formal-proofs.md`

---

## 0. 总览

| 公理 | 核心主张 | Lean 4 形式化 | 实证验证 | 判定 |
| :--- | :--- | :--- | :--- | :--- |
| **I 物理非信任** | 无外部接地的自检声称成功不可信 | B.2：3 定理已证 | 文献锚点支撑（奖励欺骗实证） | ✅ 闭环 |
| **II 注意力熵增** | 违约概率下界随无关上下文膨胀发散 | B.3：稀释定理链 + 三增长分支 + 两相模型已证 | E3/E3b（注意力通道）+ E4（W\* 阈值）+ E8（负结果） | ✅ 闭环 |
| **III 变异因果单调** | 可观测 ⟺ 物理时钟严格单调跳变；幂等可溯 | B.4：2 定理已证 | Cargo 28/28 组受控测量 | ✅ 闭环 |
| **IV 经验自免疫** | 双盲门禁压缩有效繁殖数，隔离 ⟹ 谱系灭绝 | B.5：分支过程 + GW 相变定理链已证 | DeepSeek 288 会话多代传播 + GW 仿真 | ✅ 闭环 |
| **定理 3.1 因果不变性** | 可观测 ∧ 局部 ∧ 解耦 ⟺ 确定性收敛 | B.6：充分性 + 三反例已证 | E-B6：12 组 Lyapunov 界 + 3×10⁴ 反例复现 | ✅ 闭环 |
| **随机 Foster-Lyapunov** | $\mathbb{E}[\tau] \le V(x_0)/\delta$ | B.7：截断停时 + 主定理已证 | E-B7：27 组蒙特卡洛 + 截断一致界 | ✅ 闭环 |
| **租约锁（模式 10）** | 互斥 ∧ 看门狗活性 ∧ 心跳防护 | B.8：5 定理已证 | E-B8：5×10⁴ 离散时钟仿真 | ✅ 闭环 |

验证方法论统一遵循：**预注册判读标准先于实验执行；结论一律条件定理化；与理论不符的观测如实记录为适用域边界，不修补理论**。

---

## 1. 公理 I：物理非信任公理（Axiom of Physical Non-Trustworthiness）

**主张**：封闭推理链中（无外部物理传感器），智能体声称"任务成功"的物理真实率趋近于零。

**形式化（B.2，全部已证）**：
- `self_verdict_zero_information`：条件独立封闭闭环中，自检通过的后验真值率等于先验——自检证据的贝叶斯似然比恒为 1；
- `closed_loop_risk_factorizes`：闭环风险被先验乘积结构锁定，纯反思策略无法改变；
- `posterior_independent_of_mechanism`：后验真值率与自检机制复杂度无关——排除"更强模型靠自省突破"的幻想。

**实证支撑**：该公理是工程立场的形式化，其经验内容来自文献锚点——无接地模型自我报告不可信、可欺骗评价信号下必然涌现奖励欺骗（Amodei et al. 2016；Huang et al., ICLR 2024；Anthropic arXiv:2511.18397）。物理 Exit 0 穿透（模式 01）是"获得任何证据的唯一通道"。

---

## 2. 公理 II：注意力熵增与特权发散公理（Axiom of Attention Entropy）

**主张**：$P_{\text{violate}}(\rho) \ge 1 - e^{-\alpha\rho}$——无关上下文注入使违约概率下界发散，必须施加最小特权（PoLP）投影。

**形式化（B.3，全部已证）**：稀释严格性（`attention_dilution_strict`）、三增长分支衰减律（几何 `snr_geometric_decay` / 多项式 `snr_polynomial_decay` / 幂律 `snr_power_decay`）、迭代几何界 `snr_decay_iterated`、违约下界 `violation_prob_lower_bound`、两相模型（稀释相 + 平台相不逆转）、口径定理（`snr_le_proxy`：填充口径系统性高估、`filler_growth_not_sufficient` 反例）。

**实证验证**：
- **E3/E3b（注意力通道，Qwen2.5-1.5B/7B，≤131k，scnet DCU）**：幂律分支占优（AIC 33/36 cell，几何 0 票）；弱前提"$a$ 非增"方向性成立，强假设"$a$ 恒定"被证伪——衰减由分子收缩与分母膨胀共同贡献；残差（sink）通道为动态通道，总非目标质量全程非减，填充口径 SNR 系统性高估 35.8%–36.7%；近义对抗填充使 SNR 基线降至中性填充的 1/2.25（衰减参数由填充类型标定，并非常数）。
- **E4（W\* 补偿阈值，2026-10-20/21）**：SNR 衰减与任务正确率衰减之间存在补偿阈值 $W^*$——$\rho < W^*$ 时正确率 ≈100%，$\rho > W^*$ 时陡降。实测 $W^*_{1.5\text{B}} \approx 32\text{k–64k} < W^*_{7\text{B}} > 131\text{k} < W^*_{\text{Kimi}} \ge 1\text{M}$（辅线难任务独立支撑：5-needle + 语义干扰下 512k 档 9/9 全对，prompt 725k tokens）。**违约下界只在 $\rho > W^*$ 时传导为可观测任务失败**；$W^*$ 为经验参数，不写入形式化接口。
- **E8（负结果，关闭）**：注意力熵、top-1% 集中度、key 有效秩三候选结构量跨 3 模型无一稳健复现——$\gamma/\beta$ 保持自由参数；方向一致性（三模型同号）记录为弱信号。

---

## 3. 公理 III：变异因果律单调公理（Axiom of Monotonic Causal Mutation）

**主张**：物理生效 ⟺ mtime 严格正向跳变，且变异动作具备幂等可溯的规范化签名。

**形式化（B.4，全部已证）**：`observability_iff_mtime_strict_mono`（可观测 ⟺ 物理时钟严格单调跳变；回拨/停滞 ⟹ 静默吞没）与 WAL 幂等回放定理。

**实证验证（Cargo 1.96 / Windows NTFS，28/28 组全部支持预注册假设）**：
- mtime 停滞/回拨 ⟹ 静默丢失（各 5/5，产物保持旧版本）；
- mtime 严格跳变 ⟹ 重建（5/5，纯时钟跳变即使内容不变也触发——重建触发纯由时钟通道决定，可观测性由内容差异决定，与定理前提划分一致）；
- 幂等性在无变化重构建（5/5 跳过、sha 不变）与 git 回退-重试（语义输出恢复）中成立。

**两个超出预注册的工程边界（如实回写）**：① 参考时钟实测为"上次构建完成时刻" $R$，静默丢失窗口 $(0,R]$ 宽于朴素模型——构建进行中并发写入天然不安全；② Windows PE 头含编译时间戳，同源码重编译字节级必异，幂等承诺在内容/语义层而非比特层。适用域：mtime-based 增量编译器（Cargo、Make）；内容哈希型构建系统（Bazel、Nix）不适用。

---

## 4. 公理 IV：经验自免疫公理（Axiom of Crystallization Auto-Immunity）

**主张**：未终审经验视为 `DRAFT_SUSPECT`，严禁横向传播；双盲过滤（$\text{Verdict}_{audit} \wedge \text{SubstratePass}$）后才准入全局知识库。

**形式化（B.5，全部已证）**：`expected_population_geometric`（$E(n)=m^n E(0)$）、`subcritical_extinction_in_probability`（亚临界按概率灭绝）、`quarantine_compresses_offspring`（$m=\mu(1-\sigma)$）、`supercritical_expectation_diverges`、`galton_watson_non_extinction` + `galton_watson_extinctProb_exact`（超临界以正概率永续，$q=\min\{s:\varphi(s)=s\}$）。

**实证验证（DeepSeek v4-pro，4 条件 × 12 replicate × 6 代 = 288 会话，预注册判读先于实验）**：

| 判据 | 结果 | 判定 |
| :--- | :--- | :--- |
| H1b 完全隔离（σ=1） | 全部 replicate $Z_1=0$，无 de novo 再发现 | ✅ 通过 |
| H2 几何律 | 池化 $R^2=0.958\ge0.8$，逐代比无趋势 | ✅ 通过 |
| H3-数值 | 三亚临界变体 $q_{sim}=1.0000=q^*$ 无自由参数吻合，Markov 界成立 | ✅ 通过 |
| H1a 标记门压缩 | 方向符合（−38%）但 $p=0.15$ 未达显著性 | ⚠️ 未通过（功效不足） |
| H1c 乘性压缩律 | 过滤层有效样本 $n=1$，写出层涨落主导 | ⚠️ 字面未通过（不可判定） |

**总判定**：工程核心承诺"**隔离 ⟹ 灭绝**"获最强形式验证；种群几何律成立；标记门显著性与乘性律 LLM 层直接检验受样本规模限制，记录为适用域边界（直接检验需 $\ge 10^2$ 量级 replicate），防御实现应依赖隔离而非仅依赖标记。

**意外发现（适用域边界）**：无门禁下 $\hat m=0.56<1$——选择性逐代转写协议本身将传播压入亚临界；超临界坍缩动力学对应**无转写衰减的记忆架构**（全量追加式记忆库、向量库直写），本协议未覆盖。

**跨模型复核（M2：Kimi `kimi-for-coding`，288 会话，2026-10-21）**：

| 判据 | 结果 | 判定 |
| :--- | :--- | :--- |
| X-H1 隔离不变性 | 两模型合计 24/24 链 $Z_1=0$ | ✅ 通过 |
| X-H4 跨模型幅度差异 | $\hat m_{C0}$：DeepSeek $0.560$ CI $[0.294,0.735]$ vs Kimi $0.983$ CI $[0.944,1.000]$，差 CI 不含 0 | ✅ 显著成立 |
| X-H3 标记门方向 | 两模型同号（Kimi $0.957<0.986$，$p=0.323$） | ⚠️ 方向成立/不显著 |
| X-H2 几何律（M2） | 池化 $R^2=0.744<0.8$，近临界区无动态范围 | ⚠️ 预注册未通过（判据无功效） |
| H3-数值（M2） | $q_{sim}$ 与 $\varphi^{30}(0)$ 差 0.001，但与 $q^*$ 差 0.65 | ⚠️ 字面未通过（时域截断） |

**结论修订**：$\hat m$ 是**模型特定参数**而非普适常数，实测跨模型区间 $[0.56,0.98]$ 且可含近临界核。Kimi 的繁殖核退化为 Bernoulli($p\approx0.98$)，6 代存活率仍达 0.917，灭绝需 $\sim50$–$100$ 代——**工程上等于不退场**。因此公理 IV 的适用域表述收紧为："无门禁下的 $\hat m$ 由模型转写倾向决定；隔离（$\sigma=1$）的灭绝保证与 $\hat m$ 取值无关。"防御效果不得依赖模型自身的转写衰减，须依赖完全隔离。详见 `EXPERIMENT_PLAN_AXIOM4_CROSS_MODEL.md` §8。

---

## 5. 跨公理接口与体系完整性

`Axiom2_Axiom4_Bridge`（B.3 末尾）给出分层公理系统的纵向边：`InjectionCoupling` 将公理 IV 的记忆注入速率 $\mu$ 经无关量映射 $\rho(\mu)$ 接入公理 II 的稀释动力学——注入越快违约下界越紧（`injection_strengthens_lower_bound`）。四条公理由此不是独立模型的集合，而是带严格无反馈规则的层间耦合体系：公理 I 划定证据合法性边界，公理 II 刻画上下文膨胀的必然代价，公理 III 保证状态变异的可观测与可溯，公理 IV 封顶经验传播的种群动力学。

## 6. 认识论声明

1. 全部形式化定理（B.2–B.5）为 Lean 4 内核验证的数学事实，不需要经验"证真"；实验检验的是**模型–现实映射**的适用性。
2. 所有实测结论以条件定理形式呈现，适用域逐条声明（模型族、任务族、协议、平台）；
3. 与预注册判据不符的观测（H1a 功效不足、H1c 不可判定、E8 跨族崩溃、$\rho=0$ 异常）一律如实记录为边界，理论未作任何事后修补。

**数据与复现**：`experiments/attention_growth/`（EXPERIMENT_PLAN.md、EXPERIMENT_PLAN_AXIOM3.md、EXPERIMENT_PLAN_AXIOM4.md 及各结果 JSON）；形式化复现见附录 B.10。

---

## 7. 局限与后续验证计划

四条公理的验证均条件化于实测的模型、任务族与协议。下表为针对每项边界的补足路径；其中**跨模型已执行完毕**，其余四份为预注册计划（未执行）。

| 局限 | 计划 | 性质 | 预注册核心判据 |
| :--- | :--- | :--- | :--- |
| 单一模型（仅 DeepSeek v4-pro） | [EXPERIMENT_PLAN_AXIOM4_CROSS_MODEL.md](file:///e:/workspace/industrial-agentic-cybernetics/experiments/attention_growth/EXPERIMENT_PLAN_AXIOM4_CROSS_MODEL.md) | **✅ 已执行**：Kimi 平行实验 288 会话 | X-H1 通过（24/24）、X-H4 显著；X-H2/H3-数值 受近临界区功效限制未通过 |
| 单一任务族（pytest 编写） | [EXPERIMENT_PLAN_AXIOM4_CROSS_TASK.md](file:///e:/workspace/industrial-agentic-cybernetics/experiments/attention_growth/EXPERIMENT_PLAN_AXIOM4_CROSS_TASK.md) | 四任务族 × 三条件（864 会话） | $\hat\mu$ 随毒株–任务邻接度单调；族内毒株对照 |
| 超临界未出现（$\hat m=0.56<1$） | [EXPERIMENT_PLAN_AXIOM4_SUPERCRITICAL.md](file:///e:/workspace/industrial-agentic-cybernetics/experiments/attention_growth/EXPERIMENT_PLAN_AXIOM4_SUPERCRITICAL.md) | 全量追加 + FIFO 容量架构（384 会话） | $\hat m>1$ 且 CI 下限 $>1$；$q_{sim}$ 与 $q^*$ 偏差 $<0.02$ |
| H1a 功效不足（$p=0.15$）/ H1c 不可判定（$n=1$） | [EXPERIMENT_PLAN_AXIOM4_H1AC_BOOST.md](file:///e:/workspace/industrial-agentic-cybernetics/experiments/attention_growth/EXPERIMENT_PLAN_AXIOM4_H1AC_BOOST.md) | 配对设计 + 双毒株（960 会话） | 配对置换 $p<0.05$；比值 CI 完全落入 $[0.35,0.65]$ |
| 模式 23/24 无形式化与实证 | [EXPERIMENT_PLAN_PRODUCTION_FIELD_TEST.md](file:///e:/workspace/industrial-agentic-cybernetics/experiments/attention_growth/EXPERIMENT_PLAN_PRODUCTION_FIELD_TEST.md) | Docker Compose 受控生产环境（40 次运行） | 检出率 $\ge0.90$、篡改否决率 $=1.00$、错误修复拦截率 $=1.00$ |

**尚未形式化的结构性缺口**：模式 23→24→23 构成的"观测–学习"负反馈回路，其长期稳定性尚未构造 Lyapunov 函数并纳入 Lean 工程（B.7 框架可套用，但漂移条件 $\delta$ 与 $V$ 未给出）。这是当前理论体系中唯一已知的未闭合项，不以推论代替证明。
