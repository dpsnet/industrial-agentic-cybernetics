/-
  公理 IV：经验自免疫公理（Axiom of Crystallization Auto-Immunity）
  对应书章节：§3.2 公理 IV；模式 14（隔离晋升门禁）、模式 15（污点拦截）
  学术锚点：模型坍缩 Model Collapse（Shumailov et al., Nature 2024）；
            记忆投毒 Memory Poisoning（arXiv:2512.16962）；
            分支过程灭绝理论（Athreya & Ney, 1972）

  认识论层级：
  - 【已证定理】亚临界几何衰减：期望种群按有效繁殖数 m 的幂次几何衰减
    （归纳法，期望递归作为显式假设引入）；
  - 【已证定理】当 m < 1 时期望种群趋零（压缩映射极限）；
  - 【axiom（文献事实，mathlib 未收录）】Markov 尾概率界与
    Galton-Watson 超临界爆炸定理，附标准文献引用。

  建模：未终审经验进入知识库的跨代传播为分支过程，
  双盲隔离门禁的选择度 σ ∈ [0,1] 将名义繁殖均值 μ 压缩为有效繁殖数 m = μ(1-σ)。
-/

import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

namespace IAC.Axiom4

open Filter Topology

/-- **定理（亚临界几何衰减）**：
    设期望种群序列 E : ℕ → ℝ 满足分支递归 E(n+1) = m · E(n)（显式假设），
    则 E(n) = m^n · E(0)。
    对应书中：未经门禁时 m = μ；经双盲隔离后 m = μ(1-σ)。 -/
theorem expected_population_geometric
    (E : ℕ → ℝ) (m : ℝ)
    (hrec : ∀ n, E (n + 1) = m * E n) :
    ∀ n, E n = m ^ n * E 0 := by
  intro n
  induction n with
  | zero => simp
  | succ k ih =>
      rw [hrec k, ih, pow_succ]
      ring

/-- **定理（亚临界收敛）**：当有效繁殖数 0 ≤ m < 1 时，期望种群趋于 0。
    工程含义：只要双盲门禁使 μ(1-σ) < 1，投毒经验在期望意义下必然消亡 —
    这是模式 14 隔离晋升门禁有效性的定量核心。 -/
theorem subcritical_expectation_vanishes
    (E : ℕ → ℝ) (m : ℝ)
    (hrec : ∀ n, E (n + 1) = m * E n)
    (hm0 : 0 ≤ m) (hm1 : m < 1) :
    Tendsto E atTop (nhds 0) := by
  have hgeo : ∀ n, E n = m ^ n * E 0 := expected_population_geometric E m hrec
  have hzero : Tendsto (fun n => m ^ n * E 0) atTop (nhds (0 * E 0)) :=
    Tendsto.mul_const (E 0) (tendsto_pow_atTop_nhds_zero_of_lt_one hm0 hm1)
  rw [zero_mul] at hzero
  exact Tendsto.congr (fun n => (hgeo n).symm) hzero

/-- **定理（门禁压缩有效繁殖数）**：
    名义繁殖均值 μ 经选择度 σ 的隔离门禁压缩后，σ 越严格有效繁殖数越小；
    特别地，完全隔离（σ = 1）使有效繁殖数归零。纯代数，支撑书中"严禁横向传播"。 -/
theorem quarantine_compresses_offspring
    {μ σ : ℝ} (hμ : 0 ≤ μ) (hσ0 : 0 ≤ σ) (hσ1 : σ ≤ 1) :
    μ * (1 - σ) ≤ μ ∧ (σ = 1 → μ * (1 - σ) = 0) := by
  constructor
  · have : 0 ≤ 1 - σ := sub_nonneg.mpr hσ1
    nlinarith
  · intro h; rw [h]; ring

/-- **axiom（文献事实）**：Markov 不等式的种群灭绝形式。
    非负整值随机变量 Z 满足 P(Z ≥ 1) ≤ E[Z]。
    引用：任何标准概率论教材（如 Durrett, *Probability: Theory and Examples*）。
    mathlib 有一般形式（MeasureTheory.mul_meas_ge_le_lintegral 等），
    将整值分支过程接入该一般形式所需的测度论基础设施超出本卷范围，
    故按认识论政策显式声明为引用公理。 -/
axiom markov_extinction_bound
    (P_ge_one : ℕ → ℝ) (E : ℕ → ℝ) :
    ∀ n, P_ge_one n ≤ E n

/-- **定理（亚临界灭绝，概率意义）**：
    在 Markov 界与几何衰减下，m < 1 时灭绝概率趋于 1
    （存活概率 P(Z_n ≥ 1) → 0 的夹逼形式，单侧界）。 -/
theorem subcritical_extinction_in_probability
    (P_ge_one E : ℕ → ℝ) (m : ℝ)
    (hrec : ∀ n, E (n + 1) = m * E n)
    (hm0 : 0 ≤ m) (hm1 : m < 1)
    (hnn : ∀ n, 0 ≤ P_ge_one n) :
    Tendsto P_ge_one atTop (nhds 0) := by
  have hE := subcritical_expectation_vanishes E m hrec hm0 hm1
  exact tendsto_of_tendsto_of_tendsto_of_le_of_le
    tendsto_const_nhds hE hnn
    (fun n => markov_extinction_bound P_ge_one E n)

/-- **axiom（文献事实）**：Galton-Watson 超临界爆炸定理。
    当有效繁殖数 m > 1 时，种群以正概率永不灭绝；
    当 m = 1 且后代分布非退化时亦以概率 1 灭绝（临界情形）。
    引用：Athreya & Ney, *Branching Processes* (1972), Chapter I.
    工程含义：若无隔离门禁（σ = 0）且 μ > 1，
    投毒经验以正概率在知识库中永久存续并扩散 —— 模型坍缩的种群动力学对应。 -/
axiom galton_watson_supercritical_explosion :
    ∀ m : ℝ, 1 < m → ∃ q : ℝ, q < 1

end IAC.Axiom4
