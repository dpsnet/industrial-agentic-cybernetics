/-
  跨公理接口：公理 II（注意力稀释）↔ 公理 IV（记忆投毒分支过程）
  对应书章节：§3.2 公理层间的纵向边；EXPERIMENT_PLAN.md §8 的 T7 与 §9 的 A5/E7

  动机（缺口陈述）：

    分层公理系统要求各层之间有**明确的纵向边**——上层结论可被下层引用，
    但**无反馈回路**。此前公理 II（`Axiom2_AttentionDilution.lean`）与
    公理 IV（`Axiom4_MemoryPoisoning.lean`）**互不 import**：两者各自成立，
    却没有任何定理把"记忆注入速率 μ"接到"上下文无关量 → 违约概率下界"上。
    于是专著在结构上只是若干独立模型的集合，而不是一个分层系统。

  本模块补上这条纵向边，方向单一（**无反馈**）：

      注入速率 μ  ──(单调映射 steps)──▶  几何步数 n
                                             │
                                             ▼  公理 II 的违约下界
      1 - c^n ≤ P_violate(n)，  c = 1/(1+γ)

  内容：

    - `InjectionCoupling`：把公理 II 的 `DilutionDynamics`、公理 IV 的
      `BranchingProcess`、以及"注入速率 → 有效几何步数"的单调映射放在同
      一个对象里（耦合的**载体**）；
    - `violation_lower_bound_at_injection`：纵向边本体——给定注入速率 μ，
      Axiom II 侧的违约概率下界成立（`violation_prob_lower_bound` 的直接实例）；
    - `injection_strengthens_lower_bound`：注入越强（μ↑），下界越严
      （依赖 `steps` 单调 + `1 - c^n` 关于 n 单调）；
    - `violation_under_injection`：上面两条的合成——μ₁ ≤ μ₂ 时，
      μ₁ 处的下界 ≤ μ₂ 处的违约概率；
    - `violation_bound_beyond_plateau`：**适用域校正**（对接 A1 的两相模型）——
      若注入把步数推过饱和点 `ρ*`，则 Axiom II 的无界下界 `1 - c^n` **不再成立**，
      须改用 `PhaseModel` 的**平台相常数下界**。

  认识论与诚实性声明：

    - `steps : ℝ → ℕ` 是"实数无关量 ρ 取整为几何步数"（ρ ↦ ⌈ρ⌉₊）的投影响；
      把 ℝ 值无关量压缩为 ℕ 步数是**建模步骤**，不是新增经验公设；
    - `hmono : Monotone steps` 是本模块**唯一的**结构前提，其经验内容为
      "提高注入速率不会减少无关上下文量"，属公理 II 前提增长律的直接推广；
    - 本模块不引入任何新的经验公设、不引入测度论/鞅模块，只用实数代数与
      整数单调性；`0 sorry`。
-/

import IACFormalization.Axiom2_AttentionDilution
import IACFormalization.Axiom2_PhaseModel
import IACFormalization.Axiom4_MemoryPoisoning

namespace IAC.Bridge

open IAC.Axiom2 IAC.Axiom4

/-- **跨公理耦合（A5 / T7 的载体）**：
    - `dilution`：公理 II 侧的稀释动力学（给出 `snr`、`c` 与违约下界）；
    - `lineage`：公理 IV 侧的分支过程（投毒经验的跨代传播）；
    - `steps`：注入速率 μ ↦ 有效几何步数（ℝ 值无关量取整后的步计数）；
    - `hmono`：`steps` 单调 —— 本模块唯一的结构前提，也是纵向边的方向性载体。 -/
structure InjectionCoupling where
  /-- 公理 II 侧：注意力稀释动力学 -/
  dilution : DilutionDynamics
  /-- 公理 IV 侧：投毒经验的分支过程 -/
  lineage : BranchingProcess
  /-- 注入速率 μ ↦ 有效几何步数（无关量的整数步计数） -/
  steps : ℝ → ℕ
  /-- 步数关于注入速率单调非减 -/
  hmono : Monotone steps

/-! ### 辅助引理 -/

/-- **几何损失的单调性**：当 `0 ≤ c ≤ 1` 时，`n ↦ 1 - c^n` 关于 `n` 单调非减。
    即"步数越多，违约概率下界的数值越高"（注意方向：`c^n` 递减，故 `1 - c^n` 递增）。 -/
theorem one_sub_pow_mono {c : ℝ} (hc0 : 0 ≤ c) (hc1 : c ≤ 1) {k n : ℕ} (h : k ≤ n) :
    1 - c ^ k ≤ 1 - c ^ n := by
  have hpow : c ^ n ≤ c ^ k := pow_le_pow_of_le_one hc0 hc1 h
  linarith

/-! ### 纵向边：公理 IV 的注入速率 → 公理 II 的违约下界 -/

/-- **定理（纵向边本体）**：给定耦合对象与注入速率 μ，公理 II 的违约概率下界
    在由 μ 诱导的几何步数 `steps μ` 处成立。

    这就是 §8「层间无反馈的那条纵向边」：把公理 IV 的外生参数 μ 接到
    公理 II 的定量结论上，由 `violation_prob_lower_bound`（已证定理）直接实例化。 -/
theorem violation_lower_bound_at_injection (ic : InjectionCoupling) (μ : ℝ) :
    1 - ic.dilution.c ^ ic.steps μ
      ≤ violation_prob ic.dilution (ic.steps μ : ℝ) :=
  violation_prob_lower_bound ic.dilution (ic.steps μ)

/-- **定理（注入强度的单调效应）**：注入越强（μ₁ ≤ μ₂），
    适用域内的违约概率下界越严（数值越大）。
    依赖 `steps` 单调与 `one_sub_pow_mono`；`c ∈ (0,1)` 由 `DilutionDynamics` 给出。 -/
theorem injection_strengthens_lower_bound (ic : InjectionCoupling) {μ₁ μ₂ : ℝ}
    (h : μ₁ ≤ μ₂) :
    1 - ic.dilution.c ^ ic.steps μ₁ ≤ 1 - ic.dilution.c ^ ic.steps μ₂ :=
  one_sub_pow_mono (le_of_lt ic.dilution.hc_pos) (le_of_lt ic.dilution.hc_lt_one) (ic.hmono h)

/-- **定理（合成：注入速率放大违约下界）**：若 μ₁ ≤ μ₂，则
    在 μ₁ 处成立的下界**也**在 μ₂ 处的违约概率上成立——
    即"以弱注入为基准的下界，被强注入进一步抬高"。
    这是本模块对外的**单一纵向陈述**：μ 上升 → 违约概率下界上升。 -/
theorem violation_under_injection (ic : InjectionCoupling) {μ₁ μ₂ : ℝ} (h : μ₁ ≤ μ₂) :
    1 - ic.dilution.c ^ ic.steps μ₁ ≤ violation_prob ic.dilution (ic.steps μ₂ : ℝ) :=
  le_trans (injection_strengthens_lower_bound ic h)
    (violation_lower_bound_at_injection ic μ₂)

/-! ### 适用域校正：越过饱和点后改用两相模型的平台下界

公理 II 的单相下界 `1 - c^n ≤ P_violate(n)` 依赖"几何膨胀律在全域成立"。
A1（`Axiom2_PhaseModel.lean`）已把该律截到稀释相 `n < N_star`：越过饱和点后
膨胀显著放缓，`1 - c^n` **可能失效**（见 `plateau_violates_geometric_bound`）。
故纵向边在饱和区必须切换到平台相的**常数**下界——这是本模块对"纵向边"的
适用域校正，也是 A5 依赖 A1 的原因。 -/

/-- **定理（饱和区纵向边）**：若注入把步数推过饱和点（`N_star ≤ steps μ`），
    则纵向边成立的是 `PhaseModel` 的平台相常数下界：
      `1 - snr(ρ*)/snr(0) ≤ P_violate(steps μ)`
    —— 收益不再随注入增强，但也**不逆转**。 -/
theorem violation_bound_beyond_plateau (m : PhaseModel) (steps : ℝ → ℕ) (μ : ℝ)
    (h : m.N_star ≤ steps μ) :
    1 - snr m.toAttentionMechanism (m.N_star : ℝ) / snr m.toAttentionMechanism 0
      ≤ m.violation_prob (steps μ) :=
  m.violation_prob_plateau_lower_bound h

end IAC.Bridge
