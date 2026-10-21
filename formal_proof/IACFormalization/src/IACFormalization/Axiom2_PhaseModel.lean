/-
  Axiom2（续）：两相稀释动力学 —— 饱和点与适用域
  ================================================================

  动机（对应 EXPERIMENT_PLAN.md §8 A1 与 §9 E6）：

    `DilutionDynamics.hgrowth` 对**全部** `ρ ≥ 0` 断言"非目标质量每步几何膨胀"。
    但 E2/E3 实测显示：注意力稀释只在**稀释区**呈几何律，越过饱和点 `ρ*` 后进入
    平台区（膨胀显著放缓）。于是原模型的经验前提在 `ρ > ρ*` 时**失效**，而
    `violation_prob_lower_bound` 仍被继续引用——这是一处适用域缺口。

  本模块把"两相"形式化：

    - 几何膨胀律**只在稀释相** `n < N_star` 被断言（`hgrowth_dilute`）；
    - 饱和相不再假定膨胀，仅沿用 `AttentionMechanism` 的弱结论
      （`ha_nonincr` 与 `hb_nondec`），由此得到饱和度处的**不逆转**上界：
      进入平台后 `snr` 不会回升到超过 `snr(ρ*)`；
    - 工程结论相应弱化但仍有可用保证：
      `P_violate(n) ≥ 1 - snr(ρ*)/snr(0)` 在 `n ≥ ρ*` 上继续成立（下界不再随 n 改善）。

  与单相模型的关系（本模块的两条"接口定理"）：

    - `toDilutionDynamics`：若膨胀律在**全域**成立，两相模型**退化为**
      `DilutionDynamics`，原有全部结论（`snr_decay_iterated`、
      `violation_prob_lower_bound` 等）随之恢复；
    - `plateau_violates_geometric_bound`：存在合法的两相模型，其**全域**几何衰减界
      在饱和区**失效**。故域截断并非记号修饰，而是放宽了一条真实的假定。

  数值纪律：本模块只用实数代数与自然数归纳，不引入新的经验公设；
  `N_star` 是**参数**而非拟合值，其经验取值由 E3 的变点检测给出。
-/

import IACFormalization.Axiom2_AttentionDilution

namespace IAC.Axiom2

/-- **两相稀释动力学**：`AttentionMechanism` + 稀释相几何膨胀律 + 饱和点。
    与原 `DilutionDynamics` 的唯一区别是膨胀律的定义域被截到稀释相 `n < N_star`。 -/
structure PhaseModel extends AttentionMechanism where
  /-- 稀释相单步膨胀因子 `1+γ`（`γ > 0`） -/
  γ : ℝ
  hγ_pos : 0 < γ
  /-- **饱和点**（以 ρ 的整数步计数）：`n < N_star` 为稀释相，`n ≥ N_star` 为饱和相 -/
  N_star : ℕ
  /-- **稀释相膨胀律**：仅对 `n < N_star` 断言，饱和相不假定膨胀 -/
  hgrowth_dilute : ∀ n : ℕ, n < N_star → (1 + γ) * b (n : ℝ) ≤ b ((n : ℝ) + 1)

/-! ### 自然数上的单调性辅助引理 -/

/-- 辅助：`a` 逐点不增 ⟹ 在自然数索引上反单调（`N ≤ n ⟹ a(n) ≤ a(N)`）。 -/
theorem PhaseModel.a_le_of_le (m : PhaseModel) {N n : ℕ} (h : N ≤ n) :
    m.a (n : ℝ) ≤ m.a (N : ℝ) := by
  induction n, h using Nat.le_induction with
  | base => exact le_refl _
  | succ k _ ih =>
    have hstep : m.a ((k : ℝ) + 1) ≤ m.a (k : ℝ) := m.ha_nonincr (k : ℝ) (by positivity)
    have hcast : (((k + 1 : ℕ) : ℝ)) = (k : ℝ) + 1 := by
      rw [Nat.cast_add, Nat.cast_one]
    rw [hcast]
    exact le_trans hstep ih

/-- 辅助：`b` 逐点非减 ⟹ 在自然数索引上单调（`N ≤ n ⟹ b(N) ≤ b(n)`）。 -/
theorem PhaseModel.b_le_of_le (m : PhaseModel) {N n : ℕ} (h : N ≤ n) :
    m.b (N : ℝ) ≤ m.b (n : ℝ) := by
  induction n, h using Nat.le_induction with
  | base => exact le_refl _
  | succ k _ ih =>
    have hstep : m.b (k : ℝ) ≤ m.b ((k : ℝ) + 1) := m.hb_nondec (k : ℝ) (by positivity)
    have hcast : (((k + 1 : ℕ) : ℝ)) = (k : ℝ) + 1 := by
      rw [Nat.cast_add, Nat.cast_one]
    rw [hcast]
    exact le_trans ih hstep

/-! ### 稀释相：受限的几何衰减界 -/

/-- **稀释相单步衰减**（`snr_geometric_decay` 的定义域受限版）：
    仅需 `n < N_star` 这一步的膨胀律，即可得 `snr(n+1) ≤ c·snr(n)`，`c = 1/(1+γ)`。
    证明与 `snr_geometric_decay` 相同，差别只在前提按步供给。 -/
theorem PhaseModel.hdilute_step (m : PhaseModel) {n : ℕ} (hn : n < m.N_star) :
    snr m.toAttentionMechanism ((n : ℝ) + 1)
      ≤ (1 / (1 + m.γ)) * snr m.toAttentionMechanism (n : ℝ) := by
  have hn0 : 0 ≤ (n : ℝ) := by positivity
  have ha : m.a ((n : ℝ) + 1) ≤ m.a (n : ℝ) := m.ha_nonincr (n : ℝ) hn0
  have hg : (1 + m.γ) * m.b (n : ℝ) ≤ m.b ((n : ℝ) + 1) := m.hgrowth_dilute n hn
  have hb_pos : 0 < m.b (n : ℝ) := m.hb_pos (n : ℝ) hn0
  have hb1_pos : 0 < m.b ((n : ℝ) + 1) := m.hb_pos ((n : ℝ) + 1) (by linarith)
  have ha_pos : 0 < m.a (n : ℝ) := m.ha_pos (n : ℝ) hn0
  have h1γ : 0 < 1 + m.γ := by linarith [m.hγ_pos]
  have h2 : m.a ((n : ℝ) + 1) / m.b ((n : ℝ) + 1) ≤ m.a (n : ℝ) / m.b ((n : ℝ) + 1) :=
    div_le_div_of_nonneg_right ha (le_of_lt hb1_pos)
  have h3 : m.a (n : ℝ) / m.b ((n : ℝ) + 1)
      ≤ m.a (n : ℝ) / ((1 + m.γ) * m.b (n : ℝ)) :=
    div_le_div_of_nonneg_left (le_of_lt ha_pos) (mul_pos h1γ hb_pos) hg
  have h4 : m.a (n : ℝ) / ((1 + m.γ) * m.b (n : ℝ))
      = (1 / (1 + m.γ)) * (m.a (n : ℝ) / m.b (n : ℝ)) := by
    field_simp [h1γ.ne', hb_pos.ne']
  have h5 : m.a ((n : ℝ) + 1) / m.b ((n : ℝ) + 1)
      ≤ (1 / (1 + m.γ)) * (m.a (n : ℝ) / m.b (n : ℝ)) := by
    rw [h4] at h3
    exact le_trans h2 h3
  simpa [snr] using h5

/-- **定理（稀释相迭代衰减界）**：`n ≤ N_star` 时 `snr(n) ≤ c^n · snr(0)`，`c = 1/(1+γ)`。
    这是原 `snr_decay_iterated` 的**适用域受限版**：只在稀释相内成立。 -/
theorem PhaseModel.snr_dilute_decay (m : PhaseModel) :
    ∀ n : ℕ, n ≤ m.N_star →
      snr m.toAttentionMechanism (n : ℝ) ≤ (1 / (1 + m.γ)) ^ n * snr m.toAttentionMechanism 0 := by
  intro n
  induction n with
  | zero => intro _; simp
  | succ k ih =>
    intro hk
    have hkn : k < m.N_star := Nat.lt_of_succ_le hk
    have hstep := m.hdilute_step hkn
    have hik := ih (Nat.le_of_lt hkn)
    have hc_nn : 0 ≤ 1 / (1 + m.γ) :=
      le_of_lt (one_div_pos.mpr (by linarith [m.hγ_pos]))
    have hcast : snr m.toAttentionMechanism (((k + 1 : ℕ) : ℝ))
        = snr m.toAttentionMechanism ((k : ℝ) + 1) := by
      congr 1
      push_cast
      ring
    rw [hcast]
    calc
      snr m.toAttentionMechanism ((k : ℝ) + 1)
          ≤ (1 / (1 + m.γ)) * snr m.toAttentionMechanism (k : ℝ) := hstep
      _ ≤ (1 / (1 + m.γ)) * ((1 / (1 + m.γ)) ^ k * snr m.toAttentionMechanism 0) :=
            mul_le_mul_of_nonneg_left hik hc_nn
      _ = (1 / (1 + m.γ)) ^ (k + 1) * snr m.toAttentionMechanism 0 := by ring

/-! ### 饱和相：不逆转上界与工程保证 -/

/-- **定理（饱和相不逆转）**：进入饱和相后，`snr` 不会回升到超过 `snr(ρ*)`。
    只用到 `AttentionMechanism` 的弱结论（`ha_nonincr` 与 `hb_nondec`），
    **不使用**任何膨胀律假定——这正是两相模型在 `ρ > ρ*` 处仍留有余地的原因。 -/
theorem PhaseModel.snr_plateau_le (m : PhaseModel) {n : ℕ} (h : m.N_star ≤ n) :
    snr m.toAttentionMechanism (n : ℝ) ≤ snr m.toAttentionMechanism ((m.N_star : ℕ) : ℝ) := by
  have ha : m.a (n : ℝ) ≤ m.a ((m.N_star : ℕ) : ℝ) := m.a_le_of_le h
  have hb : m.b ((m.N_star : ℕ) : ℝ) ≤ m.b (n : ℝ) := m.b_le_of_le h
  have hbn : 0 < m.b (n : ℝ) := m.hb_pos (n : ℝ) (by positivity)
  have hbN : 0 < m.b ((m.N_star : ℕ) : ℝ) := m.hb_pos _ (by positivity)
  have haN : 0 ≤ m.a ((m.N_star : ℕ) : ℝ) :=
    le_of_lt (m.ha_pos _ (by positivity))
  have h1 : m.a (n : ℝ) / m.b (n : ℝ)
      ≤ m.a ((m.N_star : ℕ) : ℝ) / m.b (n : ℝ) :=
    div_le_div_of_nonneg_right ha (le_of_lt hbn)
  have h2 : m.a ((m.N_star : ℕ) : ℝ) / m.b (n : ℝ)
      ≤ m.a ((m.N_star : ℕ) : ℝ) / m.b ((m.N_star : ℕ) : ℝ) :=
    div_le_div_of_nonneg_left haN hbN hb
  simpa [snr] using le_trans h1 h2

/-- 两相模型的违约概率（与 `violation_prob` 同口径：相对首步信噪比的损失份额）。 -/
noncomputable def PhaseModel.violation_prob (m : PhaseModel) (n : ℕ) : ℝ :=
  1 - snr m.toAttentionMechanism (n : ℝ) / snr m.toAttentionMechanism 0

/-- **定理（饱和相工程保证，弱化但可用）**：在 `n ≥ ρ*` 上，
    `P_violate(n) ≥ 1 - snr(ρ*)/snr(0)`。
    即：稀释收益不再继续增长，但**已获得的收益不会逆转**——故工程结论在饱和区
    仍有一条可用的（常数）下界，而不是"前提失效即无结论"。 -/
theorem PhaseModel.violation_prob_plateau_lower_bound (m : PhaseModel) {n : ℕ}
    (h : m.N_star ≤ n) :
    1 - snr m.toAttentionMechanism ((m.N_star : ℕ) : ℝ) / snr m.toAttentionMechanism 0
      ≤ m.violation_prob n := by
  have hsnr0 : 0 < snr m.toAttentionMechanism 0 := by
    have ha : 0 < m.a 0 := m.ha_pos 0 (by norm_num)
    have hb : 0 < m.b 0 := m.hb_pos 0 (by norm_num)
    simpa [snr] using div_pos ha hb
  have hle := m.snr_plateau_le h
  have h2 : snr m.toAttentionMechanism (n : ℝ) / snr m.toAttentionMechanism 0
      ≤ snr m.toAttentionMechanism ((m.N_star : ℕ) : ℝ) / snr m.toAttentionMechanism 0 :=
    div_le_div_of_nonneg_right hle (le_of_lt hsnr0)
  simp only [PhaseModel.violation_prob]
  linarith

/-! ### 与单相模型（原 `DilutionDynamics`）的关系 -/

/-- **接口（退化）**：若膨胀律在**全域**成立，则两相模型给出一个 `DilutionDynamics`，
    原模型的全部结论（`snr_decay_iterated`、`violation_prob_lower_bound` 等）随之可用。
    故 `PhaseModel` 是原模型的**严格弱化**。 -/
def PhaseModel.toDilutionDynamics (m : PhaseModel)
    (hgrowth : ∀ ρ, 0 ≤ ρ → (1 + m.γ) * m.b ρ ≤ m.b (ρ + 1)) : DilutionDynamics where
  a := m.a
  b := m.b
  r := m.r
  ha_pos := m.ha_pos
  hb_pos := m.hb_pos
  hr_nonneg := m.hr_nonneg
  hr_lt_b := m.hr_lt_b
  ha_nonincr := m.ha_nonincr
  hb_nondec := m.hb_nondec
  γ := m.γ
  hγ_pos := m.hγ_pos
  hgrowth := hgrowth

/-- **定理（全域假设下恢复原衰减界）**：把膨胀律补到全域后，
    原 `snr_decay_iterated` 的结论（无 `N_star` 限制）即告恢复。 -/
theorem PhaseModel.global_growth_recovers_decay (m : PhaseModel)
    (hgrowth : ∀ ρ, 0 ≤ ρ → (1 + m.γ) * m.b ρ ≤ m.b (ρ + 1)) :
    ∀ n : ℕ, snr m.toAttentionMechanism (n : ℝ)
      ≤ (1 / (1 + m.γ)) ^ n * snr m.toAttentionMechanism 0 := by
  intro n
  have hc_nn : 0 ≤ 1 / (1 + m.γ) :=
    le_of_lt (one_div_pos.mpr (by linarith [m.hγ_pos]))
  induction n with
  | zero => simp
  | succ k ih =>
    have hstep : snr m.toAttentionMechanism ((k : ℝ) + 1)
        ≤ (1 / (1 + m.γ)) * snr m.toAttentionMechanism (k : ℝ) :=
      snr_geometric_decay m.toAttentionMechanism m.γ m.hγ_pos hgrowth (k : ℝ) (by positivity)
    have hcast : snr m.toAttentionMechanism (((k + 1 : ℕ) : ℝ))
        = snr m.toAttentionMechanism ((k : ℝ) + 1) := by
      congr 1
      push_cast
      ring
    rw [hcast]
    calc
      snr m.toAttentionMechanism ((k : ℝ) + 1)
          ≤ (1 / (1 + m.γ)) * snr m.toAttentionMechanism (k : ℝ) := hstep
      _ ≤ (1 / (1 + m.γ)) * ((1 / (1 + m.γ)) ^ k * snr m.toAttentionMechanism 0) :=
            mul_le_mul_of_nonneg_left ih hc_nn
      _ = (1 / (1 + m.γ)) ^ (k + 1) * snr m.toAttentionMechanism 0 := by ring

/-! ### 非蕴含反例：饱和区可观测到全域衰减界失效 -/

/-- **反例实例**：`γ = 1`、饱和点 `N_star = 1`；非目标质量在 `ρ < 1` 时为 `1`，
    之后恒为 `2`（膨胀只发生一步），目标质量为常数 `1`，残差通道为 `1/2`。
    该实例满足 `AttentionMechanism` 的全部字段与稀释相膨胀律。 -/
noncomputable def plateauCounterexample : PhaseModel where
  a := fun _ => 1
  b := fun ρ => if ρ < 1 then 1 else 2
  r := fun _ => 1 / 2
  ha_pos := by intro ρ _; norm_num
  hb_pos := by intro ρ _; split <;> norm_num
  hr_nonneg := by intro ρ _; norm_num
  hr_lt_b := by intro ρ _; split <;> norm_num
  ha_nonincr := by intro ρ _; norm_num
  hb_nondec := by
    intro ρ hρ
    by_cases h : ρ < 1
    · have h1 : ¬ (ρ + 1 < 1) := by linarith
      simp [h, h1]
    · have h1 : ¬ (ρ + 1 < 1) := by linarith
      simp [h, h1]
  γ := 1
  hγ_pos := by norm_num
  N_star := 1
  hgrowth_dilute := by
    intro n hn
    have hn0 : n = 0 := Nat.lt_one_iff.mp hn
    subst hn0
    norm_num

/-- **定理（非蕴含反例）**：上例中稀释相（`n < 1`）的膨胀律成立，
    但**全域**几何衰减界 `snr(n) ≤ c^n·snr(0)` 在 `n = 2` 处失效
    （实测：`snr(2) = 1/2` 而 `c²·snr(0) = 1/4`）。
    故把定义域截到稀释相**不是**记号修饰，而是放宽了一条真实的假定。 -/
theorem PhaseModel.plateau_violates_geometric_bound :
    ∃ n : ℕ, ¬ (snr plateauCounterexample.toAttentionMechanism (n : ℝ)
      ≤ (1 / (1 + plateauCounterexample.γ)) ^ n
          * snr plateauCounterexample.toAttentionMechanism 0) := by
  refine ⟨2, ?_⟩
  norm_num [plateauCounterexample, snr]

end IAC.Axiom2
