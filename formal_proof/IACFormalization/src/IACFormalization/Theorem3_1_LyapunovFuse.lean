/-
  定理 3.1 补充：极限环震荡与李雅普诺夫契约残差停时熔断定理
  对应书章节：§3.3 定理 3.1（收敛因果不变性）；附录 B.7 停时界

  可证核心（全部已证，零公理，零 sorry）：
  - 【连续停滞累积引理】若轨迹在连续 k 步内残差非负漂移（ΔV ≥ 0），
    则第 k 步的能量不低于初始能量：V(t+k) ≥ V(t)（consecutive_stalls_accumulate）；
  - 【周期极限环排斥李雅普诺夫存在性】对任意非平凡周期极限环（s_{t+k} = s_t 且 k ≥ 1），
    不存在任何处处严格递减的李雅普诺夫超鞅能量证书（cycle_defeats_strict_lyapunov）；
  - 【停时熔断资源有界定理】李雅普诺夫契约残差熔断器将连续无效震荡的步数严格截断在上界 k 之内，
    杜绝无限死循环与 Token 黑洞（fuse_halts_divergence_at_k）。

  建模：离散时间轨迹 V : ℕ → ℝ，单步漂移 ΔV(t) = V(t+1) - V(t)；
  停滞判据为 ΔV ≥ 0；熔断器在连续 k 步停滞时触发。
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

namespace IAC.Theorem31.Fuse

/-- 能量残差轨迹：离散时间点到非负实数能量的映射。 -/
structure EnergyTrajectory where
  V : ℕ → ℝ
  h_nonneg : ∀ t, 0 ≤ V t

/-- 单步残差漂移：下一步能量减去当前步能量。 -/
def drift (tr : EnergyTrajectory) (t : ℕ) : ℝ :=
  tr.V (t + 1) - tr.V t

/-- 停滞/发散判据：单步能量非严格递减（ΔV ≥ 0）。 -/
def isStalled (tr : EnergyTrajectory) (t : ℕ) : Prop :=
  0 ≤ drift tr t

/-- **定理（连续停滞能量累积引理）**：
    若从时刻 t 开始，连续 k 步的漂移均为非负（系统未发生负漂移收敛），
    则时刻 t + k 的能量不小于时刻 t 的能量：V(t+k) ≥ V(t)。 -/
theorem consecutive_stalls_accumulate (tr : EnergyTrajectory) (t : ℕ) :
    ∀ k : ℕ, (∀ i : ℕ, i < k → isStalled tr (t + i)) → tr.V t ≤ tr.V (t + k) := by
  intro k
  induction k with
  | zero =>
      intro _
      simp
  | succ n ih =>
      intro h_stalls
      have h_stalls_n : ∀ i : ℕ, i < n → isStalled tr (t + i) := by
        intro i hi
        exact h_stalls i (Nat.lt_trans hi (Nat.lt_succ_self n))
      have ih_le := ih h_stalls_n
      have h_last := h_stalls n (Nat.lt_succ_self n)
      unfold isStalled drift at h_last
      have h_step : tr.V (t + n) ≤ tr.V (t + n + 1) := by linarith
      have h_add : t + (n + 1) = t + n + 1 := by omega
      rw [h_add]
      exact le_trans ih_le h_step

/-- 状态空间上的离散转移系统。 -/
structure DiscreteSystem (S : Type) where
  step : S → S
  V : S → ℝ
  h_nonneg : ∀ s, 0 ≤ V s

/-- 周期为 k 的极限环状态：经过 k 步迭代回到自身。 -/
def isCycleState {S : Type} (sys : DiscreteSystem S) (s₀ : S) (k : ℕ) : Prop :=
  0 < k ∧ (sys.step^[k] s₀ = s₀)

/-- **定理（极限环排斥李雅普诺夫严格负漂移）**：
    若系统存在非平凡周期极限环（k ≥ 1），
    则该轨迹上不可能处处满足严格负漂移条件（即不可能处处 V(step s) < V(s)）。
    此定理在数学上证明了：自愈重试若陷入震荡环，继续重试绝不可能单调收敛，
    必须依赖硬熔断机制强制跳出。 -/
theorem cycle_defeats_strict_lyapunov {S : Type} (sys : DiscreteSystem S) (s₀ : S) (k : ℕ)
    (hcycle : isCycleState sys s₀ k) :
    ¬ (∀ i : ℕ, i < k → sys.V (sys.step^[i + 1] s₀) < sys.V (sys.step^[i] s₀)) := by
  intro h_strictly_decreasing
  have h_iter_lt : ∀ i ≤ k, 0 < i → sys.V (sys.step^[i] s₀) < sys.V s₀ := by
    intro i hi hi_pos
    induction i with
    | zero => exact False.elim (lt_irrefl 0 hi_pos)
    | succ j ih =>
        by_cases hj : j = 0
        · subst hj
          have h0 : 0 < k := hi
          have h_step := h_strictly_decreasing 0 h0
          exact h_step
        · have hj_pos : 0 < j := Nat.pos_of_ne_zero hj
          have hj_lt : j < k := Nat.lt_of_succ_le hi
          have ih_val := ih (le_of_lt hj_lt) hj_pos
          have h_step := h_strictly_decreasing j hj_lt
          exact lt_trans h_step ih_val
  have h_strict_drop := h_iter_lt k le_rfl hcycle.1
  rcases hcycle with ⟨_, h_eq⟩
  rw [h_eq] at h_strict_drop
  exact lt_irrefl (sys.V s₀) h_strict_drop

/-- 李雅普诺夫停时熔断器触发谓词：在时刻 t，连续 k 轮能量未严格递减。 -/
def fuseTripped (tr : EnergyTrajectory) (k : ℕ) (t : ℕ) : Prop :=
  k ≤ t ∧ (∀ i : ℕ, i < k → isStalled tr (t - k + i))

/-- **定理（熔断停时截断资源消耗定理）**：
    若熔断阈值设为 k，当系统从时刻 t₀ 陷入连续停滞震荡，
    熔断器必然在时刻 t₀ + k 触发，保证无效试错轮数精确截断在 k 步之内。 -/
theorem fuse_halts_divergence_at_k (tr : EnergyTrajectory) (t₀ : ℕ) (k : ℕ)
    (h_stalls : ∀ i : ℕ, i < k → isStalled tr (t₀ + i)) :
    fuseTripped tr k (t₀ + k) := by
  unfold fuseTripped
  constructor
  · omega
  · intro i hi
    have h_idx : t₀ + k - k + i = t₀ + i := by omega
    rw [h_idx]
    exact h_stalls i hi

end IAC.Theorem31.Fuse
