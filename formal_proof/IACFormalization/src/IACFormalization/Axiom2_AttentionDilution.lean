/-
  公理 II：注意力熵增与特权发散公理（Axiom of Attention Entropy）
  对应书章节：§3.2 公理 II；模式 04（任务级最小特权投影）
  学术锚点：上下文退化 Context Rot（Liu et al., TACL 2024）；Lost in the Middle

  认识论层级：
  - 【已证定理】softmax 注意力稀释的严格单调性（纯实分析，mathlib 内完成）：
    无关上下文质量增加 ⟹ 目标 token 注意力权重严格下降。
  - 【Postulate（经验公设）】attention_snr_decay：
    无关 token logit 的信噪比衰减速率 α 的存在性，属于对 Transformer
    实际行为的经验刻画，不能从抽象模型推出，显式声明并标注文献。

  建模：目标 token 的注意力权重为 softmax 份额 a / (a + b)，
  其中 a = exp(l*) > 0 为目标 logit 质量，b > 0 为全部无关 token 的总质量。
-/

import Mathlib.Data.Real.Basic
import Mathlib.Tactic

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

/-- 未解释函数：目标检索信噪比作为冗余比 ρ 的函数。
    其具体形态依赖 Transformer 内部注意力动力学，无法在抽象模型中定义，
    故以常量引入 —— 公设只约束其衰减速率，不伪装其闭式表达。 -/
opaque snr : ℝ → ℝ

/-- **Postulate（经验公设，不可从抽象模型推出）**：
    存在衰减因子 c ∈ (0, 1)，使每增加一单位冗余上下文，
    目标检索信噪比至少按比例 c 衰减（几何/指数衰减的离散形式）：
      snr(ρ + 1) ≤ c · snr(ρ)。
    归纳即得 snr(ρ + n) ≤ cⁿ · snr(ρ)，与书中 §3.2 公理 II 的
    P_violate(ρ) ≥ 1 - e^{-αρ} 在 ρ ∈ ℕ 上等价（c = e^{-α}）。
    该因子的存在性属于对 Transformer 实际行为的经验刻画；
    实证支撑：Liu et al. (TACL 2024) 的 U 型注意力曲线、
    Hsieh et al. (2024, RULER) 的有效上下文长度测量。 -/
axiom attention_snr_decay :
    ∃ c : ℝ, 0 < c ∧ c < 1 ∧ ∀ ρ : ℝ, 0 ≤ ρ →
      snr (ρ + 1) ≤ c * snr ρ

end IAC.Axiom2
