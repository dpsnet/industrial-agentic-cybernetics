/-
  公理 II：注意力熵增与特权发散公理（Axiom of Attention Entropy）
  对应书章节：§3.2 公理 II；模式 04（任务级最小特权投影）
  学术锚点：上下文退化 Context Rot（Liu et al., TACL 2024）；Lost in the Middle

  认识论层级（经验公设已内化）：
  - 【已证定理】softmax 注意力稀释的严格单调性（纯实分析，mathlib 内完成）：
    无关上下文质量增加 ⟹ 目标 token 注意力权重严格下降。
  - 【已证定理】原经验公设 attention_snr_decay（SNR 几何衰减）已内化为定理：
    定义 AttentionMechanism（目标质量 a、无关质量 b），SNR := a/b；
    由"目标信号不增" + "无关质量几何膨胀"证明 snr(ρ+1) ≤ c·snr(ρ)。
    唯一剩余的经验命题是"真实 Transformer 的无关质量满足该增长律"，
    由 Context Rot / Lost in the Middle 实测支撑，不作为形式系统内的断言。

  建模：目标 token 的注意力权重为 softmax 份额 a / (a + b)，
  其中 a = exp(l*) > 0 为目标 logit 质量，b > 0 为全部无关 token 的总质量。

  口径对齐（本轮修订，对应 EXPERIMENT_PLAN.md §8.1 的 A2/A3）：
  - `b` 是**总非目标质量**（含 BOS/attention sink 与指令 token），故几何增长前提
    `hgrowth` 承载在**总量**上，而**不是**实测中只统计的"填充子通道"；
  - 实测只统计填充段 ⇒ 由残差子通道 `r` 分离出 `filler := b - r`。定理 `snr_le_proxy`
    给出实测代理与理论 SNR 的精确关系：只统计填充段会**系统性高估** SNR
    （即低估稀释严重程度），偏差因子为 `b / filler`；
  - `DilutionDynamics.c` 是**定义**而非定理（`snr_geometric_decay` 的结论以字面量
    `1/(1+γ)` 写出），故"衰减率互反关系"在形式系统内不作为断言；
  - `ha_nonincr`（`a` 非增）是**最弱充分前提**——全部证明只用到 `≤`；实测若落在
    更强的"A 为常数"上，是对该前提的**加强支持**，而非定理所需。
  - 幂律增长分支（A4）：除几何（`snr_geometric_decay`）/线性（`snr_polynomial_decay`）
    外，补精确幂比前提 `((ρ+1)/ρ)^β` 下的 `snr_power_decay`——E3 判读（计划书 §5.1 H3）
    幂律在 33/36 cell 占优、几何 0 票，故该分支由可选升为必要。
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Analysis.Convex.SpecificFunctions.Basic

namespace IAC.Axiom2

/-- **定理（注意力稀释单调性）**：
    固定目标质量 a > 0，无关上下文总质量从 b 增至 b'（b < b'），
    则目标 token 的注意力份额严格下降：
      a / (a + b') < a / (a + b)。
    这是最小特权投影（PoLP，模式 04）必须压缩无关上下文的代数核心：
    稀释不是"可能影响"，而是严格不等式意义上的必然。 -/
theorem attention_dilution_strict
    {a b b' : ℝ} (ha : 0 < a) (hb : 0 < b) (hbb' : b < b') :
    a / (a + b') < a / (a + b) := by
  have h1 : 0 < a + b := add_pos ha hb
  have h2 : 0 < a + b' := add_pos ha (lt_trans hb hbb')
  rw [div_lt_div_iff₀ h2 h1]
  have h3 : a + b < a + b' := by linarith
  nlinarith [mul_lt_mul_of_pos_left h3 ha]

/-- **推论（softmax 实例的抽象形式）**：任意正权重函数 w（如 w = exp ∘ logit）
    下，无关质量增加使目标份额严格下降 —— 覆盖 softmax 参数化，
    而不依赖具体的指数函数定义。 -/
theorem softmax_share_strictly_decreases
    {ι : Type*} (w : ι → ℝ) (x : ι) (hw : 0 < w x) {b b' : ℝ}
    (hb : 0 < b) (hbb' : b < b') :
    w x / (w x + b') < w x / (w x + b) :=
  attention_dilution_strict hw hb hbb'

/-! ### 经验公设的内化：从注意力机制推导 SNR 衰减

原 `attention_snr_decay` 把"信噪比几何衰减"作为 `DilutionDynamics` 的
裸前提（`hdecay` 字段）。本轮将其**内化为定理**：

  1. 定义 `AttentionMechanism`：目标注意力质量 `a(ρ)`、无关上下文总质量 `b(ρ)`；
  2. SNR 不再是"无闭式的经验量"，而被精确定义为 `snr(ρ) := a(ρ)/b(ρ)`
     （目标与无关注意力质量之比），注意力份额 `a(ρ)/(a(ρ)+b(ρ))`；
  3. 唯一的结构性前提是**上下文质量增长律**（关于物理因——注意力分母如何膨胀），
     而非直接假设 SNR 衰减（关于果）；
  4. 由"目标信号不随冗余增强"(`a` 不增) + "无关质量几何增长"，
     **证明** `snr(ρ+1) ≤ c·snr(ρ)`，其中 `c = 1/(1+γ) < 1`。
     原经验公设 `hdecay` 降级为定理；其一切后承（迭代衰减、违约概率下界）
     均由该定理导出。

同时给出加性增长律下的多项式衰减界，表明书中几何界承诺的是"无关质量几何膨胀"。 -/

/-- **注意力机制结构**：把 softmax 注意力的目标/非目标质量显式化。
    - `a(ρ)`：目标 token 的注意力质量（如 `exp(q·k*/√d)`）；
    - `b(ρ)`：**全部非目标 token 的注意力总质量** —— 这是定理前提的承载对象，
      包含残差通道 `r`（BOS/attention sink、指令 token）在内的**总量**；
    - `r(ρ)`：残差子通道（不随冗余增长的"固定占用"），满足 `0 ≤ r < b`；
    - `ha_nonincr`：增加冗余不会增强目标信号（自然前提，亦为**最弱充分前提**）；
    - `hb_nondec`：非目标总质量随冗余非减 —— 命题 H2 的形式对应物。

    注意力份额为 `a/(a+b)`，SNR 为 `a/b`；实测口径（只统计填充段）对应 `filler := b - r`。 -/
structure AttentionMechanism where
  a : ℝ → ℝ
  b : ℝ → ℝ
  r : ℝ → ℝ
  ha_pos : ∀ ρ, 0 ≤ ρ → 0 < a ρ
  hb_pos : ∀ ρ, 0 ≤ ρ → 0 < b ρ
  hr_nonneg : ∀ ρ, 0 ≤ ρ → 0 ≤ r ρ
  hr_lt_b : ∀ ρ, 0 ≤ ρ → r ρ < b ρ
  ha_nonincr : ∀ ρ, 0 ≤ ρ → a (ρ + 1) ≤ a ρ
  hb_nondec : ∀ ρ, 0 ≤ ρ → b ρ ≤ b (ρ + 1)

/-- 填充子通道 `filler(ρ) := b(ρ) - r(ρ)`：**实测口径**下真正被统计的"填充段总质量"。
    形式侧的 `b` 是含残差的总量，故 `filler ≤ b`，二者之差即被实验遗漏的残差质量。 -/
noncomputable def filler (m : AttentionMechanism) (ρ : ℝ) : ℝ := m.b ρ - m.r ρ

/-- 注意力份额 `s(ρ) = a(ρ)/(a(ρ)+b(ρ))`。 -/
noncomputable def attention_share (m : AttentionMechanism) (ρ : ℝ) : ℝ :=
  m.a ρ / (m.a ρ + m.b ρ)

/-- 检索信噪比 `snr(ρ) = a(ρ)/b(ρ)`：目标质量与无关质量之比。 -/
noncomputable def snr (m : AttentionMechanism) (ρ : ℝ) : ℝ :=
  m.a ρ / m.b ρ

/-- **定理（份额定性稀释）**：无关质量严格增大时，目标注意力份额严格下降。
    这是 `attention_dilution_strict` 在 `AttentionMechanism` 下的直接实例——
    定性稀释是注意力公式的代数必然，不依赖任何增长律假设。 -/
theorem attention_share_dilution (m : AttentionMechanism) (ρ : ℝ) (hρ : 0 ≤ ρ)
    (hgrow : m.b ρ < m.b (ρ + 1)) :
    attention_share m (ρ + 1) < attention_share m ρ := by
  have ha_pos : 0 < m.a ρ := m.ha_pos ρ hρ
  have ha1_pos : 0 < m.a (ρ + 1) := m.ha_pos (ρ + 1) (by linarith)
  have hb_pos : 0 < m.b ρ := m.hb_pos ρ hρ
  have hb1_pos : 0 < m.b (ρ + 1) := m.hb_pos (ρ + 1) (by linarith)
  have ha_nonincr : m.a (ρ + 1) ≤ m.a ρ := m.ha_nonincr ρ hρ
  have hdenom1 : 0 < m.a (ρ + 1) + m.b (ρ + 1) := by linarith
  have hdenom : 0 < m.a ρ + m.b ρ := by linarith
  have hcross : m.a (ρ + 1) * (m.a ρ + m.b ρ) < m.a ρ * (m.a (ρ + 1) + m.b (ρ + 1)) := by
    nlinarith
  have hmain : m.a (ρ + 1) / (m.a (ρ + 1) + m.b (ρ + 1)) < m.a ρ / (m.a ρ + m.b ρ) := by
    rw [div_lt_div_iff₀ hdenom1 hdenom]; exact hcross
  simpa [attention_share] using hmain

/-- **核心内化定理（几何上下文增长 ⟹ SNR 几何衰减）**：
    若无关注意力质量每步至少按因子 `(1+γ)` 膨胀（`γ>0`），
    且目标信号不增，则 `snr(ρ+1) ≤ c·snr(ρ)`，其中 `c = 1/(1+γ) < 1`。

    这就是原经验公设 `attention_snr_decay`，现为**定理**：
    前提是关于"注意力分母如何膨胀"的结构性假设（因），
    结论是关于"信噪比如何衰减"的定量界（果）。 -/
theorem snr_geometric_decay (m : AttentionMechanism) (γ : ℝ) (hγ : 0 < γ)
    (hgrowth : ∀ ρ, 0 ≤ ρ → m.b (ρ + 1) ≥ (1 + γ) * m.b ρ) :
    ∀ ρ, 0 ≤ ρ → snr m (ρ + 1) ≤ (1 / (1 + γ)) * snr m ρ := by
  intro ρ hρ
  have ha_nonincr : m.a (ρ + 1) ≤ m.a ρ := m.ha_nonincr ρ hρ
  have hgrow : (1 + γ) * m.b ρ ≤ m.b (ρ + 1) := hgrowth ρ hρ
  have hb_pos : 0 < m.b ρ := m.hb_pos ρ hρ
  have hb1_pos : 0 < m.b (ρ + 1) := m.hb_pos (ρ + 1) (by linarith)
  have ha_pos : 0 < m.a ρ := m.ha_pos ρ hρ
  have h1γ : 0 < 1 + γ := by linarith
  have h2 : m.a (ρ + 1) / m.b (ρ + 1) ≤ m.a ρ / m.b (ρ + 1) :=
    div_le_div_of_nonneg_right ha_nonincr (le_of_lt hb1_pos)
  have h3 : m.a ρ / m.b (ρ + 1) ≤ m.a ρ / ((1 + γ) * m.b ρ) :=
    div_le_div_of_nonneg_left (le_of_lt ha_pos) (by positivity) hgrow
  have h4 : m.a ρ / ((1 + γ) * m.b ρ) = (1 / (1 + γ)) * (m.a ρ / m.b ρ) := by
    field_simp [h1γ.ne', hb_pos.ne'] <;> ring
  have h5 : m.a (ρ + 1) / m.b (ρ + 1) ≤ (1 / (1 + γ)) * (m.a ρ / m.b ρ) := by
    rw [h4] at h3; exact le_trans h2 h3
  simpa [snr] using h5

/-- 辅助：`a` 不增 ⟹ `a(n) ≤ a(0)` 对所有 `n : ℕ`。 -/
theorem a_iter_nonincr (m : AttentionMechanism) : ∀ n : ℕ, m.a (n : ℝ) ≤ m.a 0 := by
  intro n
  induction n with
  | zero => simp
  | succ k ih =>
    have hstep : m.a ((k : ℝ) + 1) ≤ m.a (k : ℝ) := m.ha_nonincr (k : ℝ) (by positivity)
    simpa [Nat.cast_add, Nat.cast_one] using le_trans hstep ih

/-- 辅助（`a_iter_nonincr` 的一般形式）：`a` 不增 ⟹ `N ≤ n` 时 `a(n) ≤ a(N)`。 -/
theorem a_le_of_le (m : AttentionMechanism) {N n : ℕ} (h : N ≤ n) :
    m.a (n : ℝ) ≤ m.a (N : ℝ) := by
  induction n, h using Nat.le_induction with
  | base => exact le_refl _
  | succ k _ ih =>
    have hstep : m.a ((k : ℝ) + 1) ≤ m.a (k : ℝ) := m.ha_nonincr (k : ℝ) (by positivity)
    simpa [Nat.cast_add, Nat.cast_one] using le_trans hstep ih

/-- 辅助：无关质量每步至少加 `δ` ⟹ `b(n) ≥ b(0) + n·δ`。 -/
theorem b_linear_growth (m : AttentionMechanism) (δ : ℝ) (hδ : 0 < δ)
    (hgrowth : ∀ ρ, 0 ≤ ρ → m.b (ρ + 1) ≥ m.b ρ + δ) :
    ∀ n : ℕ, m.b (n : ℝ) ≥ m.b 0 + (n : ℝ) * δ := by
  intro n
  induction n with
  | zero => simp
  | succ k ih =>
    have hstep : m.b ((k : ℝ) + 1) ≥ m.b (k : ℝ) + δ := hgrowth (k : ℝ) (by positivity)
    have h : m.b (k : ℝ) + δ ≥ m.b 0 + ((k : ℝ) + 1) * δ := by linarith
    have hle1 : m.b (k : ℝ) + δ ≤ m.b ((k : ℝ) + 1) := hstep
    have hle2 : m.b 0 + ((k : ℝ) + 1) * δ ≤ m.b (k : ℝ) + δ := h
    have hgoal : m.b 0 + ((k : ℝ) + 1) * δ ≤ m.b ((k : ℝ) + 1) := le_trans hle2 hle1
    simpa [Nat.cast_add, Nat.cast_one] using hgoal

/-- **核心内化定理（线性上下文增长 ⟹ SNR 多项式衰减）**：
    若无关注意力质量每步至少增加 `δ>0`，且目标信号不增，
    则 `snr(n) ≤ a(0)/(b(0) + n·δ)`，即 SNR 按 `O(1/n)` 多项式衰减。

    这表明：书中的几何界（`e^{-αρ}`）承诺的是"无关质量几何膨胀"；
    若实际仅为线性膨胀，则衰减为多项式级。两条定理共同刻画了
    "增长律 → 衰减率"的精确对应。 -/
theorem snr_polynomial_decay (m : AttentionMechanism) (δ : ℝ) (hδ : 0 < δ)
    (hgrowth : ∀ ρ, 0 ≤ ρ → m.b (ρ + 1) ≥ m.b ρ + δ) :
    ∀ n : ℕ, snr m n ≤ m.a 0 / (m.b 0 + (n : ℝ) * δ) := by
  intro n
  have hb_lin : m.b n ≥ m.b 0 + (n : ℝ) * δ := b_linear_growth m δ hδ hgrowth n
  have ha_le : m.a n ≤ m.a 0 := a_iter_nonincr m n
  have hb_pos : 0 < m.b n := m.hb_pos n (by positivity)
  have hb0_pos : 0 < m.b 0 := m.hb_pos 0 (by norm_num)
  have hmul : 0 ≤ (n : ℝ) * δ := by positivity
  have hdenom_pos : 0 < m.b 0 + (n : ℝ) * δ := add_pos_of_pos_of_nonneg hb0_pos hmul
  have h2 : m.a n / m.b n ≤ m.a 0 / m.b n :=
    div_le_div_of_nonneg_right ha_le (le_of_lt hb_pos)
  have h3 : m.a 0 / m.b n ≤ m.a 0 / (m.b 0 + (n : ℝ) * δ) :=
    div_le_div_of_nonneg_left (le_of_lt (m.ha_pos 0 (by norm_num))) hdenom_pos hb_lin
  simpa [snr] using le_trans h2 h3

/-! ### 幂律增长分支（A4，对应 EXPERIMENT_PLAN.md §8.1）

E3 判读（计划书 §5.1 H3）：AIC 计票幂律 33/36 cell 占优、几何 0 票，故幂律分支
由"可选"升为**必要**——`snr_geometric_decay` 的几何膨胀前提在 L2 档实测不成立，
形式系统须覆盖实测占优的增长形态。

前提写法的口径说明（为何用精确幂比而非计划书字面的 `1+β/ρ`）：
- 两种写法在 `ρ = 0` 均奇异，故迭代链锚定在 `ρ = 1`（结论中的 `a₀/b₀` 相应为
  `a(1)/b(1)`）；
- 对 `β ≥ 1`，由 `1+β/ρ` 出发的连乘积为 `Γ(n+β)/(Γ(1+β)Γ(n)) ≍ n^β/Γ(1+β)`，
  推不出无常数损失的 `n^β` 界；
- 精确幂比 `((ρ+1)/ρ)^β` 的连乘积严格伸缩（telescoping），给出 `b(n) ≥ b(1)·n^β`；
- 对 `0 < β ≤ 1`（E3 实测档 β̂ ≈ 0.008–0.011 所在区间），Bernoulli 不等式给出
  `((ρ+1)/ρ)^β ≤ 1 + β/ρ`，计划书前提**强于**精确幂比前提，由
  `snr_power_decay_of_one_add` 覆盖。 -/

/-- 辅助：精确幂比增长 ⟹ `b(n) ≥ b(1)·n^β`（连乘积严格伸缩，无常数损失）。 -/
theorem b_power_growth (m : AttentionMechanism) (β : ℝ) (_hβ : 0 < β)
    (hgrowth : ∀ ρ, 1 ≤ ρ → m.b (ρ + 1) ≥ ((ρ + 1) / ρ) ^ β * m.b ρ) :
    ∀ n : ℕ, 1 ≤ n → m.b (n : ℝ) ≥ m.b 1 * (n : ℝ) ^ β := by
  intro n hn
  induction n, hn using Nat.le_induction with
  | base => simp [Real.one_rpow]
  | succ k hk ih =>
    have hk1 : (1 : ℝ) ≤ (k : ℝ) := by exact_mod_cast hk
    have hk0 : (0 : ℝ) < (k : ℝ) := lt_of_lt_of_le (by norm_num) hk1
    have hstep : m.b ((k : ℝ) + 1) ≥ (((k : ℝ) + 1) / (k : ℝ)) ^ β * m.b (k : ℝ) :=
      hgrowth (k : ℝ) hk1
    have htele : (((k : ℝ) + 1) / (k : ℝ)) ^ β * (k : ℝ) ^ β = ((k : ℝ) + 1) ^ β := by
      have hne : (k : ℝ) ^ β ≠ 0 := (Real.rpow_pos_of_pos hk0 β).ne'
      rw [Real.div_rpow (le_of_lt (by linarith : (0 : ℝ) < (k : ℝ) + 1)) (le_of_lt hk0)]
      field_simp
    have hfac_nn : (0 : ℝ) ≤ (((k : ℝ) + 1) / (k : ℝ)) ^ β :=
      le_of_lt (Real.rpow_pos_of_pos (div_pos (by linarith) hk0) β)
    have hchain : m.b 1 * ((k : ℝ) + 1) ^ β ≤ m.b ((k : ℝ) + 1) := by
      calc m.b 1 * ((k : ℝ) + 1) ^ β
          = (((k : ℝ) + 1) / (k : ℝ)) ^ β * (m.b 1 * (k : ℝ) ^ β) := by rw [← htele]; ring
        _ ≤ (((k : ℝ) + 1) / (k : ℝ)) ^ β * m.b (k : ℝ) :=
            mul_le_mul_of_nonneg_left ih hfac_nn
        _ ≤ m.b ((k : ℝ) + 1) := hstep
    simpa [Nat.cast_add, Nat.cast_one] using hchain

/-- **核心定理（幂律增长 ⟹ SNR 幂律衰减，A4）**：
    若总非目标质量每步至少按精确幂比 `((ρ+1)/ρ)^β` 膨胀（`β > 0`，`ρ ≥ 1`），
    且目标信号不增，则 `snr(n) ≤ a(1)/(b(1)·n^β)`（`1 ≤ n`）。
    与 `snr_geometric_decay`（几何分支）、`snr_polynomial_decay`（线性分支）并列，
    覆盖 H3 的 AIC 判别中实测占优的幂律形态。锚定在 `ρ = 1`：幂律步进在 `ρ = 0`
    奇异（无论 `((ρ+1)/ρ)^β` 还是 `(1+β/ρ)` 写法），结论中的 `a₀/b₀` 相应为 `a(1)/b(1)`。 -/
theorem snr_power_decay (m : AttentionMechanism) (β : ℝ) (hβ : 0 < β)
    (hgrowth : ∀ ρ, 1 ≤ ρ → m.b (ρ + 1) ≥ ((ρ + 1) / ρ) ^ β * m.b ρ)
    {n : ℕ} (hn : 1 ≤ n) :
    snr m n ≤ m.a 1 / (m.b 1 * (n : ℝ) ^ β) := by
  have hb_pow : m.b (n : ℝ) ≥ m.b 1 * (n : ℝ) ^ β := b_power_growth m β hβ hgrowth n hn
  have ha_le : m.a (n : ℝ) ≤ m.a 1 := by simpa using a_le_of_le m hn
  have hn_pos : (0 : ℝ) < (n : ℝ) := by
    exact_mod_cast Nat.lt_of_lt_of_le Nat.zero_lt_one hn
  have hnβ_pos : (0 : ℝ) < (n : ℝ) ^ β := Real.rpow_pos_of_pos hn_pos β
  have hb_pos : 0 < m.b (n : ℝ) := m.hb_pos n (by positivity)
  have hb1_pos : 0 < m.b 1 := m.hb_pos 1 (by norm_num)
  have hdenom_pos : 0 < m.b 1 * (n : ℝ) ^ β := mul_pos hb1_pos hnβ_pos
  have h2 : m.a (n : ℝ) / m.b (n : ℝ) ≤ m.a 1 / m.b (n : ℝ) :=
    div_le_div_of_nonneg_right ha_le (le_of_lt hb_pos)
  have h3 : m.a 1 / m.b (n : ℝ) ≤ m.a 1 / (m.b 1 * (n : ℝ) ^ β) :=
    div_le_div_of_nonneg_left (le_of_lt (m.ha_pos 1 (by norm_num))) hdenom_pos hb_pow
  simpa [snr] using le_trans h2 h3

/-- **幂律衰减的相对形式**：`snr(n) ≤ snr(1)/n^β` —— 衰减仅由幂指数 `β` 决定，
    便于与 `DilutionDynamics` 的 `c^n` 相对界对照。 -/
theorem snr_power_decay_relative (m : AttentionMechanism) (β : ℝ) (hβ : 0 < β)
    (hgrowth : ∀ ρ, 1 ≤ ρ → m.b (ρ + 1) ≥ ((ρ + 1) / ρ) ^ β * m.b ρ)
    {n : ℕ} (hn : 1 ≤ n) :
    snr m n ≤ snr m 1 / (n : ℝ) ^ β := by
  have h := snr_power_decay m β hβ hgrowth hn
  have hn_pos : (0 : ℝ) < (n : ℝ) := by
    exact_mod_cast Nat.lt_of_lt_of_le Nat.zero_lt_one hn
  have hnβ_ne : (n : ℝ) ^ β ≠ 0 := (Real.rpow_pos_of_pos hn_pos β).ne'
  have hb1_ne : m.b 1 ≠ 0 := (m.hb_pos 1 (by norm_num)).ne'
  have heq : m.a 1 / (m.b 1 * (n : ℝ) ^ β) = snr m 1 / (n : ℝ) ^ β := by
    simp only [snr]
    field_simp
  rwa [heq] at h

/-- **前提桥（小指数档，覆盖计划书字面写法 `1+β/ρ`）**：对 `0 < β ≤ 1`，
    Bernoulli 不等式 `(1+s)^β ≤ 1 + β·s`（mathlib `rpow_one_add_le_one_add_mul_self`）
    给出 `((ρ+1)/ρ)^β ≤ 1 + β/ρ`，即该档下计划书前提**强于**精确幂比前提，
    幂律衰减界同样成立。E3 实测 β̂ ∈ [0.008, 0.011]，正在本桥覆盖区间内。 -/
theorem snr_power_decay_of_one_add (m : AttentionMechanism) (β : ℝ) (hβ : 0 < β)
    (hβ1 : β ≤ 1) (hgrowth : ∀ ρ, 1 ≤ ρ → m.b (ρ + 1) ≥ (1 + β / ρ) * m.b ρ)
    {n : ℕ} (hn : 1 ≤ n) :
    snr m n ≤ m.a 1 / (m.b 1 * (n : ℝ) ^ β) := by
  refine snr_power_decay m β hβ ?_ hn
  intro ρ hρ
  have hρ0 : (0 : ℝ) < ρ := lt_of_lt_of_le (by norm_num) hρ
  have hbern : ((ρ + 1) / ρ) ^ β ≤ 1 + β / ρ := by
    have hs : (-1 : ℝ) ≤ 1 / ρ := by
      have h : (0 : ℝ) ≤ 1 / ρ := by positivity
      linarith
    have h := rpow_one_add_le_one_add_mul_self hs (le_of_lt hβ) hβ1
    have e1 : ((ρ + 1) / ρ) = 1 + 1 / ρ := by field_simp [hρ0.ne']
    rw [e1]
    simpa [div_eq_mul_inv] using h
  have hb_nn : (0 : ℝ) ≤ m.b ρ := le_of_lt (m.hb_pos ρ (le_of_lt hρ0))
  exact le_trans (mul_le_mul_of_nonneg_right hbern hb_nn) (hgrowth ρ hρ)

/-! ### 口径对齐：残差通道与前提的承载对象

实测口径只统计**填充段**，而形式侧的前提承载在**总非目标质量** `b` 上。以下三条把
这一差异固化：（1）H2 的迭代形式；（2）实测代理与理论 SNR 的精确关系；
（3）**非蕴含反例**——只对填充子通道假设几何膨胀，不足以推出总量的几何膨胀。 -/

/-- **H2 的形式对应物（迭代形式）**：非目标总质量随冗余非减，故 `b(n) ≥ b(0)`。 -/
theorem b_iter_nondec (m : AttentionMechanism) : ∀ n : ℕ, m.b 0 ≤ m.b n := by
  intro n
  induction n with
  | zero => simp
  | succ k ih =>
    have hstep : m.b (k : ℝ) ≤ m.b ((k : ℝ) + 1) := m.hb_nondec (k : ℝ) (by positivity)
    simpa [Nat.cast_add, Nat.cast_one] using le_trans ih hstep

/-- **定理（实测代理与理论 SNR 的精确关系）**：只统计填充段会**系统性高估** SNR。
    形式侧 `snr = a/b`，实测代理为 `a/filler`，且 `filler ≤ b`，故
      `snr ≤ a/filler`，
    偏差因子为 `b/filler ≥ 1`。这解释了为何"填充口径"的实测 SNR 总是偏乐观，
    并给出**可校正**的关系：`a/filler = snr · (b/filler)`。 -/
theorem snr_le_proxy (m : AttentionMechanism) (ρ : ℝ) (hρ : 0 ≤ ρ) :
    snr m ρ ≤ m.a ρ / filler m ρ := by
  have ha : 0 < m.a ρ := m.ha_pos ρ hρ
  have hr_nn : 0 ≤ m.r ρ := m.hr_nonneg ρ hρ
  have hr_lt : m.r ρ < m.b ρ := m.hr_lt_b ρ hρ
  have hf_pos : 0 < filler m ρ := by simp only [filler]; linarith
  have hf_le : filler m ρ ≤ m.b ρ := by simp only [filler]; linarith
  simpa [snr] using div_le_div_of_nonneg_left (le_of_lt ha) hf_pos hf_le

/-- **非蕴含反例（前提对象必须落在总量上）**：若只对**填充子通道**假设几何膨胀
    （且该步膨胀恰为 `(1+γ)` 倍），而残差通道 `r > 0` 又不随 ρ 变化，
    则**总非目标质量**的膨胀严格小于 `(1+γ)` —— 即定理所需的前提并不成立。
    这正是 `hgrowth` 必须承载在 `b`（总量）而非实测填充段上的理由。 -/
theorem filler_growth_not_sufficient (m : AttentionMechanism) (γ : ℝ) (hγ : 0 < γ)
    (ρ : ℝ) (hr_pos : 0 < m.r ρ)
    (hfix : m.r (ρ + 1) = m.r ρ)
    (hfill : filler m (ρ + 1) = (1 + γ) * filler m ρ) :
    m.b (ρ + 1) < (1 + γ) * m.b ρ := by
  have hb_eq : ∀ x : ℝ, m.b x = filler m x + m.r x := by
    intro x
    simp only [filler]
    ring
  have h1 : m.b (ρ + 1) = (1 + γ) * filler m ρ + m.r ρ := by
    rw [hb_eq (ρ + 1), hfill, hfix]
  have h2 : (1 + γ) * m.b ρ = (1 + γ) * (filler m ρ + m.r ρ) := by
    rw [hb_eq ρ]
  rw [h1, h2]
  nlinarith [mul_pos hγ hr_pos]

/-! #### 稀释动力学：几何增长律下的完整推论链

`DilutionDynamics` 现在 = `AttentionMechanism` + 几何增长因子 `γ`。
`snr`、`c` 是定义；`hdecay`（原经验公设）是定理。

**前提的承载对象**：`hgrowth` 施加在**总非目标质量** `b` 上（含残差通道 `r`），
而非实测只统计的填充段 `filler`（理由见 `filler_growth_not_sufficient`）。 -/

/-- **稀释动力学结构**：注意力机制 + 无关质量几何增长律。
    `snr`、`c` 不再是字段而是导出定义；`hdecay` 不再是前提而是定理。 -/
structure DilutionDynamics extends AttentionMechanism where
  γ : ℝ
  hγ_pos : 0 < γ
  hgrowth : ∀ ρ, 0 ≤ ρ → b (ρ + 1) ≥ (1 + γ) * b ρ

/-- 信噪比定义：`snr(ρ) = a(ρ)/b(ρ)`。 -/
noncomputable def DilutionDynamics.snr (d : DilutionDynamics) (ρ : ℝ) : ℝ :=
  d.a ρ / d.b ρ

/-- 单步衰减因子 `c = 1/(1+γ)`。 -/
noncomputable def DilutionDynamics.c (d : DilutionDynamics) : ℝ :=
  1 / (1 + d.γ)

theorem DilutionDynamics.hc_pos (d : DilutionDynamics) : 0 < d.c := by
  have hγ : 0 < d.γ := d.hγ_pos
  have h1γ : 0 < 1 + d.γ := by linarith
  simpa [DilutionDynamics.c] using one_div_pos.mpr h1γ

theorem DilutionDynamics.hc_lt_one (d : DilutionDynamics) : d.c < 1 := by
  have hγ : 0 < d.γ := d.hγ_pos
  have h1γ : 0 < 1 + d.γ := by linarith
  have h1 : 1 < 1 + d.γ := by linarith
  simpa [DilutionDynamics.c] using (div_lt_one h1γ).mpr h1

theorem DilutionDynamics.hsnr_nonneg (d : DilutionDynamics) :
    ∀ ρ, 0 ≤ ρ → 0 ≤ d.snr ρ := by
  intro ρ hρ
  have ha : 0 ≤ d.a ρ := le_of_lt (d.ha_pos ρ hρ)
  have hb : 0 < d.b ρ := d.hb_pos ρ hρ
  simpa [DilutionDynamics.snr] using div_nonneg ha (le_of_lt hb)

theorem DilutionDynamics.hsnr0_pos (d : DilutionDynamics) : 0 < d.snr 0 := by
  have ha : 0 < d.a 0 := d.ha_pos 0 (by norm_num)
  have hb : 0 < d.b 0 := d.hb_pos 0 (by norm_num)
  simpa [DilutionDynamics.snr] using div_pos ha hb

/-- **原经验公设 `hdecay`，现为定理**：
    `snr(ρ+1) ≤ c·snr(ρ)` 由几何增长律 + 目标不增导出。 -/
theorem DilutionDynamics.hdecay (d : DilutionDynamics) :
    ∀ ρ, 0 ≤ ρ → d.snr (ρ + 1) ≤ d.c * d.snr ρ := by
  intro ρ hρ
  exact snr_geometric_decay d.toAttentionMechanism d.γ d.hγ_pos d.hgrowth ρ hρ

/-- **定理（迭代衰减界）**：由单步几何衰减（定理，非公设），归纳推出
    `snr(ρ + n) ≤ c^n · snr(ρ)`。 -/
theorem snr_decay_iterated (d : DilutionDynamics) :
    ∀ (n : ℕ) (ρ : ℝ), 0 ≤ ρ → d.snr (ρ + n) ≤ d.c ^ n * d.snr ρ := by
  intro n ρ hρ
  induction n with
  | zero => simp
  | succ k ih =>
    have hρk : 0 ≤ ρ + (k : ℝ) := by linarith
    have hstep : d.snr (ρ + (k : ℝ) + 1) ≤ d.c * d.snr (ρ + (k : ℝ)) :=
      d.hdecay (ρ + (k : ℝ)) hρk
    have hcast : d.snr (ρ + ((k + 1 : ℕ) : ℝ)) = d.snr (ρ + (k : ℝ) + 1) := by
      congr 1
      simp [Nat.cast_add, add_assoc]
    have hstep' : d.snr (ρ + ((k + 1 : ℕ) : ℝ)) ≤ d.c * d.snr (ρ + (k : ℝ)) := by
      rw [hcast]; exact hstep
    have hbind : d.c * d.snr (ρ + (k : ℝ)) ≤ d.c * (d.c ^ k * d.snr ρ) :=
      mul_le_mul_of_nonneg_left ih (le_of_lt d.hc_pos)
    have hpow : d.c * (d.c ^ k * d.snr ρ) = d.c ^ (k + 1) * d.snr ρ := by ring
    rw [hpow] at hbind
    exact le_trans hstep' hbind

/-- **定理（几何衰减蕴含严格单调下降）**：当信噪比为正时，
    几何衰减（`c < 1`）意味着每步严格下降。
    这把定量衰减定理与定性稀释定理 `attention_dilution_strict` 衔接——
    衰减定理是定性稀释的定量加强。 -/
theorem geometric_decay_strictly_decreases (d : DilutionDynamics)
    (ρ : ℝ) (hρ : 0 ≤ ρ) (hpos : 0 < d.snr ρ) :
    d.snr (ρ + 1) < d.snr ρ := by
  have h1 : d.snr (ρ + 1) ≤ d.c * d.snr ρ := d.hdecay ρ hρ
  have h2 : d.c * d.snr ρ < d.snr ρ := by
    have h3 : d.c < 1 := d.hc_lt_one
    nlinarith
  exact lt_of_le_of_lt h1 h2

/-- **违约概率**：相对信噪比损失 `P_violate(ρ) = 1 - snr(ρ)/snr(0)`。 -/
noncomputable def violation_prob (d : DilutionDynamics) (ρ : ℝ) : ℝ :=
  1 - d.snr ρ / d.snr 0

/-- **定理（违约概率下界）**：在几何增长律下，
    `P_violate(n) ≥ 1 - c^n`，与书中 §3.2 公理 II 的
    `P_violate(ρ) ≥ 1 - e^{-αρ}` 在 `ρ ∈ ℕ` 上等价（`c = e^{-α}`）。

    这是原经验公设的核心工程推论，现作为**内化定理的后承**导出。
    形式系统断言：对任何满足"无关质量几何膨胀"的注意力系统，
    违约概率至少按此速率增长。"真实 Transformer 满足该增长律"是经验命题，
    由 Context Rot / Lost in the Middle 实测支撑，不在形式系统内断言。 -/
theorem violation_prob_lower_bound (d : DilutionDynamics) (n : ℕ) :
    1 - d.c ^ n ≤ violation_prob d n := by
  have h1 : d.snr n ≤ d.c ^ n * d.snr 0 := by
    simpa using snr_decay_iterated d n 0 (by norm_num)
  have hsnr0 : 0 < d.snr 0 := d.hsnr0_pos
  have h2 : d.snr n / d.snr 0 ≤ d.c ^ n := by
    calc
      d.snr n / d.snr 0 ≤ (d.c ^ n * d.snr 0) / d.snr 0 := by gcongr
      _ = d.c ^ n := by field_simp [hsnr0.ne']
  have h3 : 1 - d.c ^ n ≤ 1 - (d.snr n / d.snr 0) := by linarith
  simpa [violation_prob] using h3

end IAC.Axiom2
