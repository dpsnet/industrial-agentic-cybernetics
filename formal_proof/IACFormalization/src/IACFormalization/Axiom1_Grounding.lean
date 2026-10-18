/-
  公理 I：物理非信任公理（Axiom of Physical Non-Trustworthiness）
  对应书章节：§3.2 公理 I；第二章（奖励欺骗的博弈论分析）
  学术锚点：Grounding & Verification Gap（Amodei et al., 2016；Huang et al., ICLR 2024）

  认识论层级：
  - 【已证定理】自检零信息定理：在条件独立的封闭认知闭环中，
    自检判定关于物理真值的后验等于先验（互信息为零的布尔特例）。
  - 【建模假设】 independence：以显式假设引入，不伪装成关于世界的断言。

  建模说明（对书中概率极限式的修正）：
  书中公理 I 的极限式表达的是"开环自检无证据力"这一工程立场。
  其可严格证明的核心是下面的零信息定理：若自检输出 V_s 与物理真值 V_t
  在给定认知状态下条件独立，则自检结果不改变关于真值的任何后验估计。
  因此外部物理传感器不是"提高置信度"，而是"获得任何证据的唯一通道"。
-/

import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Data.Real.Basic
import Mathlib.Tactic

namespace IAC.Axiom1

/-- 封闭认知闭环的联合分布：V_s（自检判定）× V_t（物理真值）→ ℝ。
    p i j 表示 P(V_s = i, V_t = j)。-/
structure ClosedLoopJoint where
  p : Fin 2 → Fin 2 → ℝ
  nonneg : ∀ i j, 0 ≤ p i j
  sum_one : ∑ i, ∑ j, p i j = 1

/-- 边缘分布：自检判定 -/
def margS (J : ClosedLoopJoint) (i : Fin 2) : ℝ := J.p i 0 + J.p i 1

/-- 边缘分布：物理真值 -/
def margT (J : ClosedLoopJoint) (j : Fin 2) : ℝ := J.p 0 j + J.p 1 j

/-- **建模假设**（作为定理条件而非公理）：闭环内自检与真值独立。
    对应"无任何外部物理传感器介入"（Sensor_ext = ∅）的语义。 -/
def Independent (J : ClosedLoopJoint) : Prop :=
  ∀ i j, J.p i j = margS J i * margT J j

/-- **定理（自检零信息定理）**：
    在条件独立的封闭闭环中，自检通过的后验真值率等于先验真值率：
      P(V_t = 1 | V_s = 1) = P(V_t = 1)。
    即自检证据的贝叶斯似然比恒为 1 —— 它不能为"任务成功"提供任何证据增量。
    这是"物理 Exit 0 穿透"（模式 01）作为必要架构条件的抽象证明核心。 -/
theorem self_verdict_zero_information
    (J : ClosedLoopJoint) (hind : Independent J)
    (hden : 0 < margS J 1) :
    J.p 1 1 / margS J 1 = margT J 1 := by
  have h0 : margS J 1 ≠ 0 := ne_of_gt hden
  rw [hind 1 1]
  field_simp

/-- **定理（自检不可降低误判风险）**：
    闭环内"自检声称成功且物理亦真"的联合概率被先验完全决定：
      P(V_s = 1 ∧ V_t = 1) = P(V_s = 1) · P(V_t = 1)。
    任何不引入外部观测的纯反思重试策略，无法改变该乘积结构。 -/
theorem closed_loop_risk_factorizes
    (J : ClosedLoopJoint) (hind : Independent J) :
    J.p 1 1 = margS J 1 * margT J 1 := hind 1 1

/-- **定理（联合分布非负性的直接推论）**：后验真值率被 margT 唯一决定，
    与自检机制的复杂程度无关 —— 形式化排除了"更强的模型可以靠自省突破"的幻想。 -/
theorem posterior_independent_of_mechanism
    (J J' : ClosedLoopJoint) (hind : Independent J) (hind' : Independent J')
    (hden : 0 < margS J 1) (hden' : 0 < margS J' 1)
    (hsame : margT J 1 = margT J' 1) :
    J.p 1 1 / margS J 1 = J'.p 1 1 / margS J' 1 := by
  rw [self_verdict_zero_information J hind hden,
      self_verdict_zero_information J' hind' hden', hsame]

end IAC.Axiom1
