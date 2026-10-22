# §4 Formalization（论文全文扩写）

> 状态：**扩写 v1**（2026-10-22）；定理源：Lean 4 内核验证（toolchain v4.34.0-rc2 + mathlib4），`formal_proof/IACFormalization/`（`lake build` 通过）；论文口径与专著附录 B.5 一致。
> 位置：公理 IV 论文骨架 §4。

---

## 4.1 模型结构

传播模型为**分支过程**（`BranchingProcess` 结构，每代一个有限支撑 PMF）：未终审经验的跨代传播中，双盲隔离门禁的选择度 $\sigma$ 将名义繁殖均值 $\mu$ 压缩为有效繁殖数

$$m = \mu(1-\sigma) \quad \text{(乘性压缩律)}$$

所有定理以**条件定理**呈现：结构前提（如 $m<1$）为显式假设，"真实系统满足该前提"由 §5–§6 实测支撑，不在形式系统内断言。这一分工即本文采用的三层知识地位结构：**定理层**（Lean 机检的结构蕴含）、**经验层**（$\hat m$、$M_c$、$\sigma$ 等参数的预注册实测）、**工程层**（生产判据的部署裁决）；数值与定理互不冒充。

## 4.2 定理链（Lean 4 机检，零 `sorry`）

**T1 期望几何律**（`expected_population_geometric`，归纳证明）：$E[Z_n]=m^n E[Z_0]$。

**T2 亚临界概率灭绝**（`subcritical_extinction_in_probability`）：由 Markov 不等式与几何衰减，$m<1$ 时存活概率 $P(Z_n\ge1)\to0$。这是隔离晋升门禁有效性的定量核心：门禁把 $m$ 压到 $<1$，谱系以概率 1 消亡。

**T3 隔离压缩后代**（`quarantine_compresses_offspring`）：$\sigma$ 越严格，有效繁殖数越小；完全隔离（$\sigma=1$）使 $m=0$，谱系单代内归零。**应用条件**：分支性 + 乘性压缩——在 selective 架构下实测满足（几何律 $R^2=0.958$）；在 full-append 架构下分支前提不成立，隔离的有效性由实测直接给出（C3-full 12/12，mem 恒 6、$Z$ 恒 1），机制修正如实记录（§8）。

**T4 超临界不灭绝**（`galton_watson_non_extinction` + `supercritical_expectation_diverges`）：$m>1$ 时，灭绝概率为生成函数 $\varphi$ 在 $[0,1]$ 上的**最小不动点** $q=\min\{s\in[0,1]:\varphi(s)=s\}<1$——以正概率永不灭绝；期望 $E(n)\to+\infty$。证明采用初等生成函数不动点分析（单调夹逼 + 多项式截断），避免对 $\varphi$ 连续性的依赖。

## 4.3 定理-应用映射

| 定理 | 断言 | 应用侧 |
| :--- | :--- | :--- |
| T1 | $E[Z_n]=m^nE[Z_0]$ | 几何律判据（S-H2/B-H2 的期望侧） |
| T2 | $m<1 \Rightarrow P(Z_n\ge1)\to0$ | 隔离/随机过滤压灭谱系（C2 存活率 0.062 vs C0 0.750） |
| T3 | $\sigma\!\uparrow \Rightarrow m\downarrow$；$\sigma=1\Rightarrow m=0$ | 隔离不变性（S-H4/T-H1/X-H1） |
| T4 | $m>1 \Rightarrow q<1$，期望发散 | 机制 B"持续累积不灭绝"的期望侧对照（工程语义超临界） |

## 4.4 形式化的边界

$\hat m$、$M_c$、$\sigma$ 的**数值**为经验/工程层参数，不入形式化接口；形式化保证的是**结构蕴含**（若前提成立则结论必真），数值由预注册实测估计。这一分工避免了两类错误：把经验常数当定理、把定理当经验常数。
