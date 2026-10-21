import Mathlib.Data.Real.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Finset.Basic

/-!
# 初等有限概率：Markov 不等式

避开测度论的完整基础设施，直接在「有限支撑概率质量函数」上证明
Markov 不等式 `P(X ≥ 1) ≤ E[X]`。

这是把公理 IV 中引用公理 `markov_extinction_bound` 内化为已证定理的核心工具。
-/

namespace IACFormalization.Probability

/-- 有限支撑概率质量函数：取值在 ℕ 上、支撑有限、归一化。 -/
structure PMF where
  support : Finset ℕ
  prob : ℕ → ℝ
  nonneg : ∀ i, 0 ≤ prob i
  sum_one : ∑ i ∈ support, prob i = 1
  supported : ∀ i ∉ support, prob i = 0

/-- 期望：E[X] = Σᵢ i · p(i) -/
def expectation (p : PMF) : ℝ := ∑ i ∈ p.support, (i : ℝ) * p.prob i

/-- 存活概率：P(X ≥ 1) = Σ_{i≥1} p(i) -/
def survivalProb (p : PMF) : ℝ :=
  ∑ i ∈ p.support.filter (fun i => 1 ≤ i), p.prob i

/-- **Markov 不等式**（初等有限形式，已证）：
对任意非负整值随机变量，`P(X ≥ 1) ≤ E[X]`。

证明要点：在 `i ≥ 1` 区域内 `1 ≤ i`，故 `p(i) ≤ i·p(i)`；求和后
存活概率不超过该区域内的期望贡献，而后者不超过全域期望（其余项非负）。 -/
theorem markov_inequality (p : PMF) : survivalProb p ≤ expectation p := by
  let S := p.support.filter (fun i => 1 ≤ i)
  have hsub : S ⊆ p.support := Finset.filter_subset _ _
  have h1 : survivalProb p ≤ ∑ i ∈ S, (i : ℝ) * p.prob i := by
    simp only [survivalProb]
    apply Finset.sum_le_sum
    intro i hi
    have h_i1 : 1 ≤ i := (Finset.mem_filter.mp hi).2
    have hp : 0 ≤ p.prob i := p.nonneg i
    have h_ir : (1 : ℝ) ≤ (i : ℝ) := by exact_mod_cast h_i1
    have h : (1 : ℝ) * p.prob i ≤ (i : ℝ) * p.prob i :=
      mul_le_mul_of_nonneg_right h_ir hp
    simpa [one_mul] using h
  have h2 : (∑ i ∈ S, (i : ℝ) * p.prob i) ≤ expectation p := by
    simp only [expectation]
    apply Finset.sum_le_sum_of_subset_of_nonneg hsub
    intro i _ _
    have hp : 0 ≤ p.prob i := p.nonneg i
    have h_ir : 0 ≤ (i : ℝ) := Nat.cast_nonneg i
    exact mul_nonneg h_ir hp
  exact le_trans h1 h2

end IACFormalization.Probability
