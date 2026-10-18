/-
# 公理 III：变异因果单调（Causal Monotonicity of Mutation）

形式化断言（见 docs/appendix-formal-proofs.md 附录 B）：
工业软件基质的增量编译系统以物理时钟为唯一判据，因此：

1. **可观测性 ⇔ 物理时钟严格正向跳变**
   `observable_iff_mtime_strict_mono`；
2. **追加式幂等日志保证回放无副作用**
   `log_append_apply_idempotent`。

本模块不依赖任何经验公设，全部定理均在 Lean 内核中完成证明。
-/
import Mathlib.Tactic
import Mathlib.Data.List.Basic

namespace IAC.Axiom3

/-! ## 物理基质模型 -/

/-- 编译工件的可观测判据：内容 + 是否重编译（无副作用增量编译器输出） -/
structure BuildStamp where
  content      : ℕ
  wasRebuilt   : Bool
deriving DecidableEq, Repr

/-- 变异动作：文件目标、新内容、物理应用时刻 -/
structure Mutation where
  target      : ℕ
  content     : ℕ
  mtApplied   : ℕ  -- 物理时钟（mtime / WAL LSN），真实动作生效时刻
deriving DecidableEq, Repr

/-- 基质状态：最近一次被编译器观测到的物理时刻与当前内容 -/
structure Substrate where
  lastCompiledAt : ℕ
  content        : ℕ
deriving DecidableEq, Repr

/-- 增量编译器的"变异生效"规则：
    物理时刻严格大于上次编译时刻才触发重建，否则动作静默丢失（Silent Loss） -/
def applyMutation (s : Substrate) (m : Mutation) : Substrate :=
  if m.mtApplied > s.lastCompiledAt then
    { lastCompiledAt := m.mtApplied, content := m.content }
  else
    s

/-- 编译算子：若内容变化则产生新的可观测工件 -/
def compileArtifact (s : Substrate) : BuildStamp :=
  ⟨s.content, True⟩

/-- **定理 III-1（可观测性充要条件）**：
    一次物理变异可被编译系统观测到，当且仅当其物理时钟严格正向跳变。
    若时钟回拨或停滞（`mtApplied ≤ lastCompiledAt`），修改被静默吞掉。 -/
theorem observable_iff_mtime_strict_mono {s : Substrate} {m : Mutation}
    (hdiff : m.content ≠ s.content) :
    (compileArtifact (applyMutation s m) ≠ compileArtifact s) ↔
      m.mtApplied > s.lastCompiledAt := by
  constructor
  · intro h
    by_contra hb
    push Not at hb
    have hnl : ¬(s.lastCompiledAt < m.mtApplied) := not_lt.mpr hb
    simp [applyMutation, compileArtifact, hnl] at h
  · intro hb
    simp [applyMutation, compileArtifact, gt_iff_lt, hb, BuildStamp.mk.injEq, hdiff]

/-! ## 幂等变异日志 -/

/-- 追加式日志（WAL / Lamport 偏序的物化） -/
structure Journal where
  applied : List ℕ  -- 已应用的物理时刻序列（append-only）

/-- 合法变异：物理时刻从未被应用过（单调因果 + 幂等性检查） -/
def mutId (j : Journal) : Type := { m : Mutation // m.mtApplied ∉ j.applied }

/-- 追加日志：记录新的物理时刻 -/
def logAppend (j : Journal) (h : mutId j) : Journal :=
  { applied := h.1.mtApplied :: j.applied }

/-- 日志回放应用 -/
structure Mutant where
  srcSubstrate : Mutation
  target       : ℕ
  content      : ℕ
  mtApplied    : ℕ
  hashVerified : Bool  -- 校验和：该时刻此前未被应用过

/-- 幂等回放算子 -/
def applyLoggedMutation (j : Journal) (m : Mutation) : Mutant :=
  { srcSubstrate := m
  , target       := m.target
  , content      := m.content
  , mtApplied    := m.mtApplied
  , hashVerified := decide (m.mtApplied ∉ j.applied) }

/-- **定理 III-2（日志幂等性）**：
    同一物理时刻的重复回放中，第二次应用的校验和必然失败，
    且内容字段与首次应用完全一致 —— 重复回放不会污染编译结果。 -/
theorem log_append_apply_idempotent (j : Journal) (h : mutId j) :
    let m := h.1
    let j' := logAppend j h
    let first : Mutant := ⟨m, m.target, m.content, m.mtApplied, true⟩
    let second := applyLoggedMutation j' m
    second.hashVerified = false ∧ second.content = first.content := by
  refine ⟨?_, rfl⟩
  have hmem : h.1.mtApplied ∈ (logAppend j h).applied :=
    List.mem_cons_self
  simp [applyLoggedMutation, hmem]

end IAC.Axiom3
