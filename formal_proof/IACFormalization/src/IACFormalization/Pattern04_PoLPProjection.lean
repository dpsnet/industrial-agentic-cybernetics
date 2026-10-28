/-
  模式 04：任务级最小特权上下文投影模式（Task-Level PoLP Projection Pattern）
  对应书章节：第二部分 模式 04；§3.2 公理 II（注意力稀释与特权发散公理）

  可证核心（全部已证，零公理，零 sorry）：
  - 【最小特权投影保真定理】裁剪无关上下文（b_ext > 0）必然使得任务目标 token
    检索信噪比严格提升：snr(b_T) > snr(b_T + b_ext)（polp_preserves_snr_strictly）；
  - 【越界违约概率压降定理】最小特权投影严格压降模型的注意力退化与越界代码篡改风险：
    P_violate(b_T) < P_violate(b_T + b_ext)（polp_strictly_reduces_violation_risk）；
  - 【特权嵌套单调性定理】投影切片越紧凑（b₁ ≤ b₂），其违约风险上界单调更低
    （polp_monotone_nesting）。

  建模：上下文质量划分为目标质量 a > 0、任务必要噪声质量 b_T > 0，
  以及全局注入的无关外部质量 b_ext ≥ 0；投影算子将 b_ext 截断置零。
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic
import IACFormalization.Axiom2_AttentionDilution

namespace IAC.Pattern04

/-- 任务上下文环境：目标有效质量 a，任务内必要背景质量 b_T，外部多余上下文质量 b_ext。 -/
structure TaskContext where
  a : ℝ
  b_T : ℝ
  b_ext : ℝ
  ha : 0 < a
  hb_T : 0 < b_T
  hb_ext : 0 ≤ b_ext

/-- 投影前全局无关总质量：必要质量 + 外部冗余质量。 -/
def globalNoise (ctx : TaskContext) : ℝ :=
  ctx.b_T + ctx.b_ext

/-- 最小特权投影算子（PoLP Projection）：将外部冗余质量截断剥离，仅保留任务必要切片。 -/
def projectPoLP (ctx : TaskContext) : TaskContext :=
  { ctx with b_ext := 0, hb_ext := le_refl 0 }

/-- 检索信噪比：目标质量与无关质量之比。 -/
noncomputable def snr (a : ℝ) (b : ℝ) : ℝ :=
  a / b

/-- 越界违约概率：由注意力份额稀释所诱发的特权违约与代码幻觉风险。 -/
noncomputable def violationProb (a : ℝ) (b : ℝ) : ℝ :=
  1 - a / (a + b)

/-- **定理（最小特权投影保真定理）**：
    若存在非零外部冗余上下文（b_ext > 0），
    执行最小特权投影后，任务检索信噪比严格大于全量未投影信噪比。 -/
theorem polp_preserves_snr_strictly (ctx : TaskContext) (hext : 0 < ctx.b_ext) :
    snr ctx.a (globalNoise (projectPoLP ctx)) > snr ctx.a (globalNoise ctx) := by
  unfold snr globalNoise projectPoLP
  dsimp
  have h_bT_pos : 0 < ctx.b_T := ctx.hb_T
  have h_denom : ctx.b_T < ctx.b_T + ctx.b_ext := by linarith
  have h_add_pos : 0 < ctx.b_T + ctx.b_ext := by linarith
  have ha_pos : 0 < ctx.a := ctx.ha
  rw [add_zero]
  exact div_lt_div_of_pos_left ha_pos h_bT_pos h_denom

/-- **定理（越界违约风险严格压降）**：
    若存在非零外部冗余上下文（b_ext > 0），
    最小特权投影后的越界代码篡改与契约违规概率严格小于未投影全量上下文。 -/
theorem polp_strictly_reduces_violation_risk (ctx : TaskContext) (hext : 0 < ctx.b_ext) :
    violationProb ctx.a (globalNoise (projectPoLP ctx)) < violationProb ctx.a (globalNoise ctx) := by
  unfold violationProb globalNoise projectPoLP
  dsimp
  rw [add_zero]
  have ha_pos : 0 < ctx.a := ctx.ha
  have hbT_pos : 0 < ctx.b_T := ctx.hb_T
  have h_less : ctx.b_T < ctx.b_T + ctx.b_ext := by linarith
  have h_dilution := Axiom2.attention_dilution_strict ha_pos hbT_pos h_less
  linarith

/-- **定理（特权嵌套单调性定理）**：
    在任意两个投影切片中，若切片 1 的无关噪声不大于切片 2（b₁ ≤ b₂），
    则切片 1 的违约风险上界必然不高于切片 2。
    此定理在数学上确立了：任务切片越精细最小化，智能体越轨风险单调更低。 -/
theorem polp_monotone_nesting {a b₁ b₂ : ℝ} (ha : 0 < a) (hb₁ : 0 < b₁) (hle : b₁ ≤ b₂) :
    violationProb a b₁ ≤ violationProb a b₂ := by
  unfold violationProb
  have h_add₁ : 0 < a + b₁ := add_pos ha hb₁
  have h_denom_le : a + b₁ ≤ a + b₂ := by linarith
  have h_div_le : a / (a + b₂) ≤ a / (a + b₁) := div_le_div_of_nonneg_left (le_of_lt ha) h_add₁ h_denom_le
  linarith

end IAC.Pattern04
