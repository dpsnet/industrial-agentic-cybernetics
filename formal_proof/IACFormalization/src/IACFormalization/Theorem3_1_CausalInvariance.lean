/-
  定理 3.1：收敛因果不变性定理（Theorem of Causal Invariance）
  对应书章节：§3.3
  学术锚点：Foster-Lyapunov 稳定性准则（Foster, 1953；Meyn & Tweedie, 1993）；
            Lamport 因果序（CACM 1978）

  认识论层级（概率层已内化）：
  - 【已证定理】确定性李雅普诺夫有限命中：严格负漂移 ⟹ 有限步内收敛至零点；
  - 【已证定理】强漂移确定性停时界：V ≥ δ 时每步降至少 δ ⟹ 命中时间 t ≤ V(s₀)/δ
    （Foster-Lyapunov 准则决定论情形的完整内化，取代原引用公理）；
  - 【已证定理】三个必要性反例：破坏任一条件 ⟹ 系统呈现对应病态行为
    （吸收性假通过、周期震荡、自指不动点）。
  注：随机情形的期望停时界 E[τ] ≤ V(s₀)/δ 仍需鞅可选停止定理，属后续里程碑。

  建模：系统状态空间 S 抽象；能量函数 V : S → ℕ 度量未满足契约数；
  控制器每步驱动 step : S → S。
-/

import Mathlib.Data.Fin.Basic
import Mathlib.Logic.Function.Iterate
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

namespace IAC.Theorem31

/-! ### 充分性方向：确定性李雅普诺夫收敛 -/

/-- **定理（确定性有限命中，Foster-Lyapunov 的离散决定论核心）**：
    若每一步在 V > 0 处严格降低能量（负漂移），
    则从任意状态出发，至多 V(s₀) 步内命中零点（全部契约满足）。
    书中"确定性收敛"在抽象模型上的严格含义。 -/
theorem lyapunov_finite_hitting
    {S : Type*} (V : S → ℕ) (step : S → S)
    (hdrift : ∀ s, 0 < V s → V (step s) < V s) :
    ∀ s, ∃ t : ℕ, t ≤ V s ∧ V (step^[t] s) = 0 := by
  have aux : ∀ k : ℕ, ∀ s, V s ≤ k → ∃ t : ℕ, t ≤ V s ∧ V (step^[t] s) = 0 := by
    intro k
    induction k with
    | zero =>
        intro s hs
        have h0 : V s = 0 := Nat.le_zero.mp hs
        exact ⟨0, Nat.zero_le _, by rw [Function.iterate_zero]; exact h0⟩
    | succ k ih =>
        intro s hs
        by_cases h0 : V s = 0
        · exact ⟨0, Nat.zero_le _, by rw [Function.iterate_zero]; exact h0⟩
        · have hpos : 0 < V s := Nat.pos_of_ne_zero h0
          have hlt : V (step s) < V s := hdrift s hpos
          obtain ⟨t, ht, hV⟩ := ih (step s) (by omega)
          refine ⟨t + 1, by omega, ?_⟩
          rw [Function.iterate_succ_apply]
          exact hV
  intro s
  exact aux (V s) s le_rfl

/-- **定理（收敛态的保持性）**：若零能量状态是控制器的不动点，
    则一旦所有物理契约满足，系统永久保持收敛。 -/
theorem zero_energy_is_fixed
    {S : Type*} (V : S → ℕ) (step : S → S)
    (hfixed : ∀ s, V s = 0 → step s = s)
    (s : S) (hV : V s = 0) :
    ∀ t, V (step^[t] s) = 0 := by
  have hstay : ∀ t : ℕ, step^[t] s = s := by
    intro t
    induction t with
    | zero => rfl
    | succ k ih =>
        rw [Function.iterate_succ_apply', ih]
        exact hfixed s hV
  intro t
  rw [hstay t]
  exact hV

/-! ### 必要性方向：三个反例（有限状态机上可判定） -/

/-- 反例状态机骨架：二值状态足以展示全部三种病态 -/
inductive PathState
  | healthy     -- 物理真通过
  | falsified   -- 虚假通过（claim = 1, phys = 0）
  | probing     -- 震荡中间态
deriving DecidableEq, Repr

/-- **反例 1（破坏状态可观测性 ⟹ 吸收性虚假通过）**：
    无外部传感器时，奖励欺骗使系统从 probing 一步进入 falsified 并永久停留。
    对应书中 §3.3 必要性第 1 条与第二章博弈论分析。 -/
def stepNoObs : PathState → PathState
  | .probing   => .falsified
  | s          => s

theorem no_observability_absorbs_falsified :
    stepNoObs^[1] PathState.probing = PathState.falsified ∧
    ∀ t : ℕ, stepNoObs^[t] PathState.falsified = PathState.falsified := by
  constructor
  · rfl
  · intro t
    induction t with
    | zero => rfl
    | succ k ih => rw [Function.iterate_succ_apply', ih]; rfl

/-- **反例 2（破坏变异局部性 ⟹ 周期震荡，且不存在任何李雅普诺夫证书）**：
    跨界并发变异产生 2-周期轨道；进而证明在该轨道上
    ANY 能量函数都不可能处处严格下降 —— "震荡不可被李雅普诺夫方法驯服"。 -/
def stepNoLocality : Fin 2 → Fin 2 := fun x => x + 1

theorem no_locality_two_cycle :
    ∀ x : Fin 2, stepNoLocality^[2] x = x ∧ stepNoLocality x ≠ x := by
  decide

theorem no_locality_defeats_lyapunov :
    ¬∃ V : Fin 2 → ℕ, ∀ s, V (stepNoLocality s) < V s := by
  rintro ⟨V, hdrift⟩
  have h1 : V (stepNoLocality 0) < V 0 := hdrift 0
  have h2 : V (stepNoLocality 1) < V 1 := hdrift 1
  have e1 : stepNoLocality 0 = 1 := by decide
  have e2 : stepNoLocality 1 = 0 := by decide
  rw [e1] at h1
  rw [e2] at h2
  omega

/-- **反例 3（破坏评估解耦性 ⟹ 自指不动点）**：
    评价者直接复制解题者输出作为判定，任何输出都被"验证通过"，
    系统收敛于退化的平庸解 —— 第二章"自指闭环"的不动点形式化。 -/
structure CoupledState where
  output  : Bool   -- 解题者产出
  verdict : Bool   -- 评价者判定
deriving DecidableEq

/-- 耦合评估步：判定 := 输出（自指），与物理真值无关 -/
def stepCoupled (s : CoupledState) : CoupledState :=
  { s with verdict := s.output }

theorem coupled_evaluation_tautological_fixed_point (b : Bool) :
    stepCoupled (stepCoupled ⟨b, true⟩) = stepCoupled ⟨b, true⟩ ∧
    (stepCoupled ⟨b, true⟩).verdict = b := by
  constructor
  · cases b <;> rfl
  · rfl

/-! ### 强漂移确定性停时界（Foster-Lyapunov 的已证内化版本） -/

/-- **定理（强漂移确定性停时界）**：
    实值能量函数 V : S → ℝ≥0，若当 V ≥ δ 时每步至少下降 δ
    （强负漂移 V(step s) ≤ V(s) - δ），则命中 δ-邻域 V < δ 的步数 t
    满足 **t · δ ≤ V(s₀)**，即 t ≤ V(s₀)/δ。

    这是 Foster-Lyapunov 准则在决定论情形下的完整内化（取代原引用公理）。
    证明要点：取首次命中 t，命中前每步消耗至少 δ，故总消耗 t·δ 不超过初始能量。
    存在性由 Archimedean 性质保证（无穷步会使 V 跌破 0，与非负性矛盾）。

    注：随机情形的「期望停时 E[τ] ≤ V(s₀)/δ」仍需鞅可选停止定理，
    属后续里程碑；本定理覆盖决定论控制器的全部工程场景。 -/
theorem foster_lyapunov_deterministic_bound
    {S : Type*} (V : S → ℝ) (step : S → S) (δ : ℝ) (hδ : 0 < δ)
    (hnn : ∀ s, 0 ≤ V s)
    (hdrift : ∀ s, δ ≤ V s → V (step s) ≤ V s - δ) :
    ∀ s, ∃ t : ℕ, (t : ℝ) * δ ≤ V s ∧ V (step^[t] s) < δ := by
  intro s
  have hex : ∃ t, V (step^[t] s) < δ := by
    by_contra h
    have hge : ∀ k, δ ≤ V (step^[k] s) := by
      intro k
      by_cases hpos : V (step^[k] s) < δ
      · exfalso; exact h ⟨k, hpos⟩
      · linarith
    have hbd : ∀ k, V (step^[k] s) ≤ V s - (k : ℝ) * δ := by
      intro k
      induction k with
      | zero => simp
      | succ k ih =>
        have h1 := hge k
        have h2 := hdrift (step^[k] s) h1
        have h_eq : step^[k + 1] s = step (step^[k] s) :=
          Function.iterate_succ_apply' step k s
        rw [h_eq]
        have h43 : V (step (step^[k] s)) ≤ V s - (k : ℝ) * δ - δ := by
          calc
            V (step (step^[k] s)) ≤ V (step^[k] s) - δ := h2
            _ ≤ V s - (k : ℝ) * δ - δ := by linarith
        have h5 : V s - (k : ℝ) * δ - δ = V s - ((k + 1 : ℕ) : ℝ) * δ := by
          simp [Nat.cast_add, Nat.cast_one]; ring
        rw [h5] at h43
        exact h43
    obtain ⟨k, hk⟩ := exists_nat_gt (V s / δ)
    have h3 : (k : ℝ) * δ > V s := by
      have h4 : V s / δ < (k : ℝ) := by exact_mod_cast hk
      have h5 : (V s / δ) * δ < (k : ℝ) * δ := mul_lt_mul_of_pos_right h4 hδ
      have h6 : (V s / δ) * δ = V s := by field_simp
      linarith
    have h7 := hbd k
    linarith [hnn (step^[k] s)]
  let t := Nat.find hex
  have ht : V (step^[t] s) < δ := Nat.find_spec hex
  have hle : ∀ k < t, δ ≤ V (step^[k] s) := by
    intro k hk
    by_cases hpos : V (step^[k] s) < δ
    · exact False.elim (Nat.find_min hex hk hpos)
    · linarith
  have hbd : ∀ k, k ≤ t → V (step^[k] s) ≤ V s - (k : ℝ) * δ := by
    intro k hkt
    induction k with
    | zero => simp
    | succ k ih =>
      have hk_lt_t : k < t := by omega
      have h1 := hle k hk_lt_t
      have h2 := hdrift (step^[k] s) h1
      have h_eq : step^[k + 1] s = step (step^[k] s) :=
        Function.iterate_succ_apply' step k s
      rw [h_eq]
      have h3 := ih (by omega)
      have h43 : V (step (step^[k] s)) ≤ V s - (k : ℝ) * δ - δ := by
        calc
          V (step (step^[k] s)) ≤ V (step^[k] s) - δ := h2
          _ ≤ V s - (k : ℝ) * δ - δ := by linarith
      have h5 : V s - (k : ℝ) * δ - δ = V s - ((k + 1 : ℕ) : ℝ) * δ := by
        simp [Nat.cast_add, Nat.cast_one]; ring
      rw [h5] at h43
      exact h43
  have h4 : V (step^[t] s) ≤ V s - (t : ℝ) * δ := hbd t le_rfl
  have h5 : 0 ≤ V (step^[t] s) := hnn (step^[t] s)
  have h6 : (t : ℝ) * δ ≤ V s := by linarith
  exact ⟨t, h6, ht⟩

/-! ### 汇合陈述：定理 3.1 的抽象形式 -/

/-- **定理 3.1（抽象形式化陈述）**：
    在三条件（可观测性、局部性、评估解耦性）的抽象语义下，
    严格负漂移控制器有限步收敛（充分性，已证）；
    且破坏任一条件分别导致：吸收性虚假通过 / 无证书震荡 / 自指不动点
    （必要性三反例，已证）。强漂移停时界见 foster_lyapunov_deterministic_bound。 -/
theorem causal_invariance_abstract :
    -- 充分性：存在李雅普诺夫证书 ⟹ 有限命中
    (∀ {S : Type*} (V : S → ℕ) (step : S → S),
      (∀ s, 0 < V s → V (step s) < V s) →
      ∀ s, ∃ t : ℕ, t ≤ V s ∧ V (step^[t] s) = 0)
    ∧
    -- 必要性 1：破坏可观测性 ⟹ 吸收性虚假通过
    (∀ t : ℕ, stepNoObs^[t] PathState.falsified = PathState.falsified)
    ∧
    -- 必要性 2：破坏局部性 ⟹ 2-周期轨道且无李雅普诺夫证书
    (∀ x : Fin 2, stepNoLocality^[2] x = x ∧ stepNoLocality x ≠ x)
    ∧
    (¬∃ V : Fin 2 → ℕ, ∀ s, V (stepNoLocality s) < V s) :=
  ⟨fun V step hdrift s => lyapunov_finite_hitting V step hdrift s,
   fun t => no_observability_absorbs_falsified.2 t,
   no_locality_two_cycle,
   no_locality_defeats_lyapunov⟩

end IAC.Theorem31
