/-
  公理 IV：经验自免疫公理（Axiom of Crystallization Auto-Immunity）
  对应书章节：§3.2 公理 IV；模式 14（隔离晋升门禁）、模式 15（污点拦截）
  学术锚点：模型坍缩 Model Collapse（Shumailov et al., Nature 2024）；
            记忆投毒 Memory Poisoning（arXiv:2512.16962）；
            分支过程灭绝理论（Athreya & Ney, 1972）

  认识论层级（已全面内化概率层）：
  - 【已证定理】亚临界几何衰减：期望种群按有效繁殖数 m 的幂次几何衰减；
  - 【已证定理】当 m < 1 时期望种群趋零（压缩映射极限）；
  - 【已证定理】Markov 不等式 P(Z_n ≥ 1) ≤ E[Z_n]
    （在有限支撑 PMF 上初等证明，见 Probability_Markov.lean）；
  - 【已证定理】亚临界灭绝（概率意义）：m < 1 时存活概率 → 0；
  - 【已证定理】超临界期望发散：m > 1 且 E(0) > 0 时 E(n) → +∞
    （这是 Galton-Watson 超临界爆炸的期望层弱化版本，已内化为已证定理；
     强结论"以正概率永不灭绝"涉及生成函数不动点分析，仍为文献事实，
     但不再作为 Lean axiom 声明）。

  建模：未终审经验进入知识库的跨代传播为分支过程，
  双盲隔离门禁的选择度 σ ∈ [0,1] 将名义繁殖均值 μ 压缩为有效繁殖数 m = μ(1-σ)。
-/

import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Tactic
import IACFormalization.Probability_Markov

namespace IAC.Axiom4

open Filter Topology IACFormalization.Probability

/-- **分支过程结构**：每一代 n 对应一个有限支撑 PMF，
    其期望满足分支递归 E(n+1) = m · E(n)。 -/
structure BranchingProcess where
  pmf : ℕ → PMF
  m : ℝ
  hrec : ∀ n, expectation (pmf (n + 1)) = m * expectation (pmf n)

/-- **定理（亚临界几何衰减）**：
    分支过程的期望满足 E(n) = m^n · E(0)。 -/
theorem expected_population_geometric (bp : BranchingProcess) :
    ∀ n, expectation (bp.pmf n) = bp.m ^ n * expectation (bp.pmf 0) := by
  intro n
  induction n with
  | zero => simp
  | succ k ih =>
      rw [bp.hrec k, ih, pow_succ]
      ring

/-- **定理（亚临界收敛）**：当有效繁殖数 0 ≤ m < 1 时，期望种群趋于 0。
    工程含义：只要双盲门禁使 μ(1-σ) < 1，投毒经验在期望意义下必然消亡 —
    这是模式 14 隔离晋升门禁有效性的定量核心。 -/
theorem subcritical_expectation_vanishes (bp : BranchingProcess)
    (hm0 : 0 ≤ bp.m) (hm1 : bp.m < 1) :
    Tendsto (fun n => expectation (bp.pmf n)) atTop (nhds 0) := by
  have hgeo : ∀ n, expectation (bp.pmf n) = bp.m ^ n * expectation (bp.pmf 0) :=
    expected_population_geometric bp
  have hzero : Tendsto (fun n => bp.m ^ n * expectation (bp.pmf 0)) atTop
      (nhds (0 * expectation (bp.pmf 0))) :=
    Tendsto.mul_const (expectation (bp.pmf 0))
      (tendsto_pow_atTop_nhds_zero_of_lt_one hm0 hm1)
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

/-- **定理（亚临界灭绝，概率意义）**：
    由 Markov 不等式（已证）与几何衰减，m < 1 时存活概率 P(Z_n ≥ 1) → 0。
    即灭绝概率 → 1：隔离晋升门禁足以在概率意义下清除投毒经验。 -/
theorem subcritical_extinction_in_probability (bp : BranchingProcess)
    (hm0 : 0 ≤ bp.m) (hm1 : bp.m < 1) :
    Tendsto (fun n => survivalProb (bp.pmf n)) atTop (nhds 0) := by
  let E := fun n => expectation (bp.pmf n)
  let P := fun n => survivalProb (bp.pmf n)
  have hE := subcritical_expectation_vanishes bp hm0 hm1
  have hnn : ∀ n, 0 ≤ P n := by
    intro n
    apply Finset.sum_nonneg
    intro i _
    exact (bp.pmf n).nonneg i
  have hle : ∀ n, P n ≤ E n := by
    intro n
    exact markov_inequality (bp.pmf n)
  exact tendsto_of_tendsto_of_tendsto_of_le_of_le tendsto_const_nhds hE hnn hle

/-- **定理（超临界期望发散）**：
    当有效繁殖数 m > 1 且初始期望 E(0) > 0 时，期望种群 E(n) → +∞。

    这是 Galton-Watson 超临界爆炸定理的**期望层弱化版本**（已内化为已证定理）。
    它严格弱于经典结论"以正概率永不灭绝"（后者需生成函数不动点分析），
    但足以在工程意义上表明：无隔离门禁（σ = 0）且 μ > 1 时，
    投毒经验的期望载荷无界增长 —— 模型坍缩的期望动力学对应。 -/
theorem supercritical_expectation_diverges (bp : BranchingProcess)
    (hm1 : 1 < bp.m) (hE0 : 0 < expectation (bp.pmf 0)) :
    Tendsto (fun n => expectation (bp.pmf n)) atTop atTop := by
  have hgeo : ∀ n, expectation (bp.pmf n) = bp.m ^ n * expectation (bp.pmf 0) :=
    expected_population_geometric bp
  have hpow : Tendsto (fun n : ℕ => bp.m ^ n) atTop atTop :=
    tendsto_pow_atTop_atTop_of_one_lt hm1
  have h := hpow.const_mul_atTop hE0
  exact Tendsto.congr (fun n => by rw [hgeo n, mul_comm]) h

end IAC.Axiom4
