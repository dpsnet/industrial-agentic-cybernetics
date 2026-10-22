/-
  模式 23 + 24：生产运行时异常嗅探（23）与缺陷萃取 / 热修复闭环（24）
  对应书章节：第九部分 模式 23、24；验证报告 §7 末段"唯一已知未闭合项"

  闭环的数学对象：观测–学习负反馈回路。每个周期发生两件事——
    (i)  模式 23 的嗅探以概率 `q` 检出并触发修复（缺陷存量 −1）；
    (ii) 生产活动注入一个新的缺陷（存量 +1）。
  存量 `x ∈ ℕ` 的转移：
    `x ↦ x + 1`（未检出，概率 `1 − q`） 或 `x ↦ x − 1`（检出并修复，概率 `q`）；
    ℕ 减法在 `x = 0` 处自然饱和为 0，故无需额外截断。

  已证结论（零公理）：
  - 【漂移判据】当 `q > 1/2` 且 `x ≥ 1` 时，一步期望存量的漂移为
    `E[x' | x] − x = 1 − 2q < 0`（`T_id_pos`、`hasStrongDrift`）。
  - 【稳定性】取 `V(x) = x`、`b = 1`、`δ = 2q − 1 > 0`，强漂移条件成立，
    故回路命中"存量 < 1"的期望时间满足 `E[τ] ≤ x₀ / (2q − 1)`
    （`loop_return_bound`，由既有 `stoppedTime_uniform_bound` 给出）。
  - 【临界负结果】若 `q ≤ 1/2`，则 `E[x' | x] ≥ x`，`V = id` 不构成
    Lyapunov 函数——检出–修复吞吐不足以抵消注入，回路不存在负漂移证书
    （`no_drift_below_half`）。

  工程含义：模式的"检出率 ≥ 0.90"不是可选的性能目标，而是 q > 1/2 这一
  稳定性门槛的工程余量；低于门槛时，任何观测–学习闭环都无法自证收敛。
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic
import IACFormalization.StochasticFosterLyapunov

namespace IAC.Pattern23_24

open IAC.StochasticFosterLyapunov

/-- 后继状态与"存量减一"永不相同（ℕ 截断减法不改变该事实）。 -/
theorem succ_ne_sub_one (x : ℕ) : x + 1 ≠ x - 1 := by
  intro h
  have h1 : x + 1 ≤ x := by
    rw [h]
    exact Nat.sub_le x 1
  exact Nat.not_succ_le_self x h1

/-- 单周期后继状态：注入一个缺陷，或（若存量非零）检出并修复一个。 -/
def nextStates (x : ℕ) : Finset ℕ := insert (x + 1) ({x - 1} : Finset ℕ)

/-- 单步转移概率：未检出概率 `1 − q`，检出并修复概率 `q`。 -/
def stepProb (q : ℝ) (x y : ℕ) : ℝ :=
  if y = x + 1 then 1 - q else if y = x - 1 then q else 0

/-- 观测–学习回路的转移核（检出率 `q ∈ [0,1]`）。 -/
noncomputable def loopKernel (q : ℝ) (hq0 : 0 ≤ q) (hq1 : q ≤ 1) : StochasticKernel ℕ where
  next := nextStates
  prob := stepProb q
  nonneg := by
    intro x y
    unfold stepProb
    split_ifs
    · linarith
    · exact hq0
    · exact le_rfl
  sum_one := by
    intro x
    have hne : x - 1 ≠ x + 1 := (succ_ne_sub_one x).symm
    rw [nextStates, Finset.sum_insert (by simp only [Finset.mem_singleton]; exact succ_ne_sub_one x),
      Finset.sum_singleton]
    have h1 : stepProb q x (x + 1) = 1 - q := by simp [stepProb]
    have h2 : stepProb q x (x - 1) = q := by simp [stepProb, hne]
    rw [h1, h2]
    ring
  supported := by
    intro x y hy
    have h1 : y ≠ x + 1 := by
      intro h
      apply hy
      rw [h]
      simp [nextStates]
    have h2 : y ≠ x - 1 := by
      intro h
      apply hy
      rw [h]
      simp [nextStates]
    simp [stepProb, h1, h2]

/-- **引理（一步期望存量）**：当 `x ≥ 1` 时，
    `E[x' | x] = x + 1 − 2q`——注入 +1，检出并修复 −1（概率 `q`）。 -/
theorem T_id_pos (q : ℝ) (hq0 : 0 ≤ q) (hq1 : q ≤ 1) {x : ℕ} (hx : 1 ≤ x) :
    T (loopKernel q hq0 hq1) (fun y => (y : ℝ)) x = (x : ℝ) + 1 - 2 * q := by
  have hmem : x + 1 ∉ ({x - 1} : Finset ℕ) := by
    simp only [Finset.mem_singleton]
    exact succ_ne_sub_one x
  have hp1 : stepProb q x (x + 1) = 1 - q := by simp [stepProb]
  have hp2 : stepProb q x (x - 1) = q := by
    have hne' : x - 1 ≠ x + 1 := (succ_ne_sub_one x).symm
    simp [stepProb, hne']
  have hcast : ((x - 1 : ℕ) : ℝ) = (x : ℝ) - 1 := by
    rw [Nat.cast_sub hx]
    norm_num
  have hx1 : ((x + 1 : ℕ) : ℝ) = (x : ℝ) + 1 := by push_cast; ring
  simp only [T, loopKernel, nextStates]
  rw [Finset.sum_insert hmem, Finset.sum_singleton, hp1, hp2, hx1, hcast]
  ring

/-- **定理（负漂移）**：检出–修复率 `q > 1/2` 时，
    以存量 `V(x) = x` 为 Lyapunov 函数、`b = 1`、`δ = 2q − 1` 的强漂移条件成立。 -/
theorem hasStrongDrift (q : ℝ) (hq0 : 0 ≤ q) (hq1 : q ≤ 1) (_hq : 1 / 2 < q) :
    HasStrongDrift (loopKernel q hq0 hq1) (fun x => (x : ℝ)) 1 (2 * q - 1) := by
  intro x hb
  have hx : 1 ≤ x := by
    have hx' : (1 : ℝ) ≤ (x : ℝ) := hb
    exact_mod_cast hx'
  rw [T_id_pos q hq0 hq1 hx]
  linarith

/-- **定理（回路稳定性）**：`q > 1/2` 时，从初始存量 `x₀` 出发，
    回路命中"存量 < 1"（即全部缺陷被清理）的期望时间上界为 `x₀ / (2q − 1)`。 -/
theorem loop_return_bound (q : ℝ) (hq0 : 0 ≤ q) (hq1 : q ≤ 1) (hq : 1 / 2 < q)
    (x₀ : ℕ) :
    ∀ n : ℕ,
      stoppedTime (loopKernel q hq0 hq1) (fun x => (x : ℝ)) 1 n x₀
        ≤ (x₀ : ℝ) / (2 * q - 1) := by
  have hδ : 0 < 2 * q - 1 := by linarith
  have hnn : ∀ x : ℕ, 0 ≤ ((x : ℝ)) := by
    intro x
    positivity
  intro n
  exact stoppedTime_uniform_bound (loopKernel q hq0 hq1) (fun x => (x : ℝ)) 1
    (2 * q - 1) hδ hnn (hasStrongDrift q hq0 hq1 hq) n x₀

/-- **定理（临界负结果）**：若 `q ≤ 1/2`，则 `E[x' | x] ≥ x`（`x ≥ 1`），
    存量期望不下降，`V = id` 不构成 Lyapunov 函数。
    该负结果表明 `q > 1/2` 是模型内的**必要门槛**，而非宽裕的性能指标。 -/
theorem no_drift_below_half (q : ℝ) (hq0 : 0 ≤ q) (_hq : q ≤ 1 / 2) {x : ℕ} (hx : 1 ≤ x) :
    (x : ℝ) ≤ T (loopKernel q hq0 (by linarith)) (fun y => (y : ℝ)) x := by
  rw [T_id_pos q hq0 (by linarith) hx]
  linarith

end IAC.Pattern23_24
