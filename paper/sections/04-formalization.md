# §4 Formalization（论文全文扩写）

> 状态：**扩写 v1**（2026-10-22）；定理源：Lean 4 内核验证（toolchain v4.34.0-rc2 + mathlib4），`formal_proof/IACFormalization/`（`lake build` 通过）；论文口径与专著附录 B.5 一致。
> 位置：公理 IV 论文骨架 §4。

---

## 4.1 模型结构

传播模型为**分支过程**（`BranchingProcess` 结构，每代一个有限支撑 PMF）：未终审经验的跨代传播中，双盲隔离门禁的选择度 $\sigma$ 将名义繁殖均值 $\mu$ 压缩为有效繁殖数

$$m = \mu(1-\sigma) \quad \text{(乘性压缩律)}$$

所有定理以**条件定理**呈现：结构前提（如 $m<1$）为显式假设，"真实系统满足该前提"由 §5–§6 实测支撑，不在形式系统内断言。这一分工即本文采用的三层知识地位结构：**定理层**（Lean 机检的结构蕴含）、**经验层**（$\hat m$、$M_c$、$\sigma$ 等参数的预注册实测）、**工程层**（生产判据的部署裁决）；数值与定理互不冒充。$\sigma$ 的口径与 §3.1 一致（拦截率，写出通过率 $=1-\sigma$）；EXP-A 的随机过滤档以放行率 $r=1-\sigma$ 实现（表 5 标注，§6.5）。

## 4.2 定理链（Lean 4 机检，零 `sorry`）

形式化源码：`formal_proof/IACFormalization`（本仓库 commit `4825137`；Lean 4，mathlib 版本见 `lakefile.lean`）。

**T1 期望几何律**（`expected_population_geometric`，归纳证明）：$E[Z_n]=m^n E[Z_0]$。

**T2 亚临界概率灭绝**（`subcritical_extinction_in_probability`）：由 Markov 不等式与几何衰减，$m<1$ 时存活概率 $P(Z_n\ge1)\to0$。这是隔离晋升门禁有效性的定量核心：门禁把 $m$ 压到 $<1$，长期存活概率 $P(Z_n\ge1)\to0$（依概率收敛）——应用侧措辞严格为“存活概率趋向 0”，而非“以概率 1 消亡”。

**T3 隔离压缩后代**（`quarantine_compresses_offspring`）：$\sigma$ 越严格，有效繁殖数越小；完全隔离（$\sigma=1$）使 $m=0$，谱系单代内归零。**应用条件**：分支性 + 乘性压缩——在 selective 架构下实测满足（几何律 $R^2=0.958$）；在 full-append 架构下分支前提不成立，隔离的有效性由实测直接给出（C3-full 12/12，mem 恒 6、$Z$ 恒 1），机制修正如实记录（§8）。

**T4 超临界不灭绝**（`galton_watson_non_extinction` + `supercritical_expectation_diverges`）：$m>1$ 时，灭绝概率为生成函数 $\varphi$ 在 $[0,1]$ 上的**最小不动点** $q=\min\{s\in[0,1]:\varphi(s)=s\}<1$——以正概率永不灭绝；期望 $E[Z_n]\to+\infty$。证明采用初等生成函数不动点分析（单调夹逼 + 多项式截断），避免对 $\varphi$ 连续性的依赖。

## 4.3 定理-应用映射

| 定理 | 断言 | 应用侧 |
| :--- | :--- | :--- |
| T1 | $E[Z_n]=m^nE[Z_0]$ | 几何律判据（S-H2/B-H2 的期望侧） |
| T2 | $m<1 \Rightarrow P(Z_n\ge1)\to0$ | 隔离/随机过滤压灭谱系（C2 存活率 0.062 vs C0 0.750） |
| T3 | $\sigma\!\uparrow \Rightarrow m\downarrow$；$\sigma=1\Rightarrow m=0$ | 隔离不变性（S-H4/T-H1/X-H1） |
| T4 | $m>1 \Rightarrow q<1$，$E[Z_n]\to+\infty$ | 机制 A 超临界侧对照；机制 B 的持续累积由实测占据率给出（工程语义） |

## 4.5 机制 B 稳态占据率（普通数学命题，非 Lean 机检）

**命题（机制 B 稳态占据率）**：full-append 架构、FIFO 容量 $M$、每代良性写入 $b$ 条、毒株写入链均 $\bar w$（$0<\bar w\le1$）时，在"毒株条目在容量内均匀混合"的近似下，稳态毒株占据为

$$Z^\* = \frac{M\,\bar w}{b+\bar w}$$

**证明**：每代写入总量期望 $b+\bar w$ 条（毒株 $\bar w$ 条）；FIFO 每代挤出等量最旧条目。若毒株均匀分布于 $M$ 槽位，则每代被挤出的毒株数期望为 $(b+\bar w)\cdot Z/M$。稳态要求流入等于流出：$(b+\bar w)\cdot Z^\*/M = \bar w$，即 $Z^\*=M\bar w/(b+\bar w)$。$\blacksquare$

**实测验证**：C0-full（$b=2$、$\bar w=0.917$、$M=16$）预测 $Z^\*=16\times0.917/2.917=5.03$，实测稳态 4.917（g5–g7 稳定），相对偏差 2.3%。

**限定**：均匀混合为近似——FIFO 下毒株条目位置分布非均匀且存在代际相关性，精确解依赖具体写入序列；本文以该闭式作为机制 B 的**内生稳态描述量**（取代 GW 参数的机制内生化，§8）。

## 4.6 形式化的边界

机制 A 的 $\hat m$、$M_c$、$\sigma$ 的**数值**为经验/工程层参数，不入形式化接口（机制 B 无 GW 语义的 $\hat m$，其传播比估计见 §6.1 表注）；形式化保证的是**结构蕴含**（若前提成立则结论必真），数值由预注册实测估计。这一分工避免了两类错误：把经验常数当定理、把定理当经验常数。
