import Mathlib.Data.Real.Basic
import Mathlib.Data.Finset.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Tactic

/-!
# 随机 Foster-Lyapunov 期望停时界（初等证明，零测度论依赖）

避开鞅与可选停止定理的完整测度论基础设施，直接在**有限支撑转移核**上
递归定义停时期望，用归纳法 + 单调有界收敛证明停时界。

定理：若 Markov 链满足强漂移条件 `E[V(X_{t+1}) - V(X_t) | X_t = x] ≤ -δ`
（当 `V(x) ≥ b`），则命中集合 `{V < b}` 的期望时间 `E[τ] ≤ V(x₀)/δ`。
-/

namespace IAC.StochasticFosterLyapunov

open Finset

/-- 有限支撑随机转移核：每个状态 x 的下一步分布支撑在有限集 `next x` 上。 -/
structure StochasticKernel (S : Type*) where
  next : S → Finset S
  prob : S → S → ℝ
  nonneg : ∀ x y, 0 ≤ prob x y
  sum_one : ∀ x, ∑ y ∈ next x, prob x y = 1
  supported : ∀ x y, y ∉ next x → prob x y = 0

/-- 一步期望算子：`(T f)(x) = E[f(X_1) | X_0 = x]`。 -/
def T {S : Type*} (k : StochasticKernel S) (f : S → ℝ) (x : S) : ℝ :=
  ∑ y ∈ k.next x, k.prob x y * f y

/-- 强漂移条件：当 `V(x) ≥ b` 时，`E[V(X_1) - V(x) | X_0 = x] ≤ -δ`。 -/
def HasStrongDrift {S : Type*} (k : StochasticKernel S)
    (V : S → ℝ) (b δ : ℝ) : Prop :=
  ∀ x, b ≤ V x → T k V x ≤ V x - δ

/-- 截断停时的值函数：`W(n, x) = E[V(X_{τ_n}) + δ·τ_n | X_0 = x]`，
    其中 `τ_n = min(τ, n)` 是命中 `{V < b}` 的截断停时。
    递归：若已命中（V x < b），则 W = V x；否则走一步并累积 δ。 -/
noncomputable def stoppedValue {S : Type*} (k : StochasticKernel S)
    (V : S → ℝ) (b δ : ℝ) : ℕ → S → ℝ
  | 0, x => V x
  | n + 1, x =>
    if V x < b then V x
    else (∑ y ∈ k.next x, k.prob x y * stoppedValue k V b δ n y) + δ

/-- 截断停时的期望：`T_hat(n, x) = E[τ_n | X_0 = x]`。 -/
noncomputable def stoppedTime {S : Type*} (k : StochasticKernel S)
    (V : S → ℝ) (b : ℝ) : ℕ → S → ℝ
  | 0, x => 0
  | n + 1, x =>
    if V x < b then 0
    else ∑ y ∈ k.next x, k.prob x y * (stoppedTime k V b n y + 1)

/-- **定理（截断值函数的李雅普诺夫界）**：
    `W(n, x) ≤ V(x)` 对所有 n, x 成立。
    证明要点：归纳；命中态直接成立；未命中态用漂移条件
    `T V x ≤ V x - δ` 与归纳假设 `W(n, y) ≤ V(y)` 夹逼。 -/
theorem stoppedValue_le_V {S : Type*} (k : StochasticKernel S)
    (V : S → ℝ) (b δ : ℝ) (hδ : 0 < δ)
    (hnn : ∀ x, 0 ≤ V x) (hdrift : HasStrongDrift k V b δ) :
    ∀ (n : ℕ) (x : S), stoppedValue k V b δ n x ≤ V x := by
  intro n
  induction n with
  | zero =>
    intro x
    simp [stoppedValue]
  | succ n ih =>
    intro x
    by_cases hb : V x < b
    · simp [stoppedValue, hb]
    · have hge : b ≤ V x := by linarith
      have hstep : T k V x ≤ V x - δ := hdrift x hge
      have hsum : (∑ y ∈ k.next x, k.prob x y * stoppedValue k V b δ n y)
          ≤ T k V x := by
        apply sum_le_sum
        intro y _
        have h2 : stoppedValue k V b δ n y ≤ V y := ih y
        have hp : 0 ≤ k.prob x y := k.nonneg x y
        nlinarith
      simp [stoppedValue, hb, not_lt.mpr hge]
      linarith

/-- **定理（截断停时界）**：`δ · E[τ_n] ≤ W(n, x)`，
    因为 `V(X_{τ_n}) ≥ 0` 故 `W = E[V(X_{τ_n}) + δτ_n] ≥ δ·E[τ_n]`。 -/
theorem stoppedTime_le_value {S : Type*} (k : StochasticKernel S)
    (V : S → ℝ) (b δ : ℝ) (hδ : 0 < δ)
    (hnn : ∀ x, 0 ≤ V x) :
    ∀ (n : ℕ) (x : S),
      δ * stoppedTime k V b n x ≤ stoppedValue k V b δ n x := by
  intro n
  induction n with
  | zero =>
    intro x
    simp [stoppedTime, stoppedValue]
    exact hnn x
  | succ n ih =>
    intro x
    by_cases hb : V x < b
    · simp [stoppedTime, stoppedValue, hb]
      exact hnn x
    · have hge : V x ≥ b := by linarith
      simp [stoppedTime, stoppedValue, hb]
      have h1 : ∀ y ∈ k.next x,
          δ * (stoppedTime k V b n y + 1)
          ≤ stoppedValue k V b δ n y + δ := by
        intro y _
        have h2 := ih y
        linarith
      calc
        δ * (∑ y ∈ k.next x, k.prob x y * (stoppedTime k V b n y + 1))
          = ∑ y ∈ k.next x, k.prob x y * (δ * (stoppedTime k V b n y + 1)) := by
            rw [mul_sum]
            congr with y _
            ring
        _ ≤ ∑ y ∈ k.next x, k.prob x y * (stoppedValue k V b δ n y + δ) := by
            apply sum_le_sum
            intro y hy
            have hp : 0 ≤ k.prob x y := k.nonneg x y
            nlinarith [h1 y hy]
        _ = (∑ y ∈ k.next x, k.prob x y * stoppedValue k V b δ n y) + δ := by
            have hterm : ∀ y ∈ k.next x,
                k.prob x y * (stoppedValue k V b δ n y + δ)
                = k.prob x y * stoppedValue k V b δ n y + k.prob x y * δ := by
              intro y _; ring
            have hsum : (∑ y ∈ k.next x, k.prob x y * (stoppedValue k V b δ n y + δ)) =
                (∑ y ∈ k.next x, (k.prob x y * stoppedValue k V b δ n y
                  + k.prob x y * δ)) := by
              apply sum_congr rfl; intro y _; exact hterm y ‹_›
            rw [hsum, sum_add_distrib]
            have hδsum : (∑ y ∈ k.next x, k.prob x y * δ) = δ := by
              rw [← sum_mul, k.sum_one x]; ring
            rw [hδsum]

/-- **定理（截断停时的一致上界）**：
    `E[τ_n] ≤ V(x)/δ` 对所有 n 成立。
    结合 `stoppedValue_le_V` 与 `stoppedTime_le_value`。 -/
theorem stoppedTime_uniform_bound {S : Type*} (k : StochasticKernel S)
    (V : S → ℝ) (b δ : ℝ) (hδ : 0 < δ)
    (hnn : ∀ x, 0 ≤ V x) (hdrift : HasStrongDrift k V b δ) :
    ∀ (n : ℕ) (x : S), stoppedTime k V b n x ≤ V x / δ := by
  intro n x
  have h1 : δ * stoppedTime k V b n x ≤ stoppedValue k V b δ n x :=
    stoppedTime_le_value k V b δ hδ hnn n x
  have h2 : stoppedValue k V b δ n x ≤ V x :=
    stoppedValue_le_V k V b δ hδ hnn hdrift n x
  have h3 : δ * stoppedTime k V b n x ≤ V x := le_trans h1 h2
  have h4 : stoppedTime k V b n x ≤ V x / δ := by
    have h5 : δ * stoppedTime k V b n x ≤ V x := h3
    have h6 : stoppedTime k V b n x ≤ V x / δ := by
      calc
        stoppedTime k V b n x
          = (δ * stoppedTime k V b n x) / δ := by field_simp [hδ.ne']
        _ ≤ V x / δ := by
          apply div_le_div_of_nonneg_right h5 (le_of_lt hδ)
    exact h6
  exact h4

/-- **期望停时**：截断停时期望的上确界（单调有界序列的极限）。
    `E[τ] = sup_n E[τ_n]`。 -/
noncomputable def expectedHittingTime {S : Type*} (k : StochasticKernel S)
    (V : S → ℝ) (b : ℝ) (x : S) : ℝ :=
  sSup {t | ∃ n : ℕ, t = stoppedTime k V b n x}

/-- **主定理（随机 Foster-Lyapunov 期望停时界）**：
    在强漂移条件下，命中 `{V < b}` 的期望停时满足
    `E[τ] ≤ V(x₀) / δ`。

    这是 Foster (1953) / Meyn-Tweedie (1993) 准则的已证内化版本，
    在有限支撑转移核上用初等方法完成，零测度论依赖。 -/
theorem foster_lyapunov_expected_hitting {S : Type*} (k : StochasticKernel S)
    (V : S → ℝ) (b δ : ℝ) (hδ : 0 < δ)
    (hnn : ∀ x, 0 ≤ V x) (hdrift : HasStrongDrift k V b δ) (x : S) :
    expectedHittingTime k V b x ≤ V x / δ := by
  have hbdd : ∀ (n : ℕ), stoppedTime k V b n x ≤ V x / δ :=
    fun n => stoppedTime_uniform_bound k V b δ hδ hnn hdrift n x
  apply csSup_le
  · refine ⟨0, 0, rfl⟩
  · rintro t ⟨n, rfl⟩
    exact hbdd n

end IAC.StochasticFosterLyapunov
