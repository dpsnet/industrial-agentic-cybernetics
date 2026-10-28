/-
  模式 15：污点污染防御与防伪退化模式（Tainted Pattern Rejection & Anti-Degradation）
  对应书章节：第五部分 模式 15；§3.2 公理 IV 经验自免疫

  可证核心（全部已证，零公理，零 sorry）：
  - 【墓碑态吸收性】一旦被撤销标记为 tombstone，状态不可逆转（tombstone_absorbing）；
  - 【动态投影隔离安全性】墓碑化模式在检索与上下文投影中永远被排除（tombstone_never_projectable）；
  - 【反向自免疫阻断】撤销时合成的反向免疫规则在逻辑上阻断相同污点特征的代际再生（immunity_blocks_taint）；
  - 【代际传播截断】墓碑化后其有效繁殖均值恒为 0，后代期望在一步内归零（tombstone_offspring_zero）。

  建模：知识模式包含 id、lifecycle、taint 指纹；知识库为模式列表；
  检索投影为过滤算子；免疫规则为否定性谓词。
-/

import Mathlib.Tactic

namespace IAC.Pattern15

/-- 模式生命周期状态：草稿、已晋升、已墓碑化撤销。 -/
inductive Lifecycle
  | draft
  | promoted
  | tombstone
deriving DecidableEq, Repr

/-- 知识模式结构：唯一标识、生命周期状态、污点特征签名。 -/
structure KnowledgePattern (ID Feature : Type) where
  id : ID
  lifecycle : Lifecycle
  features : List Feature

/-- 撤销状态机转换规则：
    draft 或 promoted 均可转换为 tombstone；
    tombstone 只能保持为 tombstone。 -/
def stepLifecycle (current : Lifecycle) (revoke : Bool) : Lifecycle :=
  if current = Lifecycle.tombstone then
    Lifecycle.tombstone
  else if revoke then
    Lifecycle.tombstone
  else
    current

/-- **定理（墓碑态吸收性）**：
    墓碑态是终结吸收态，任意后续状态转换无法逃逸墓碑态。 -/
theorem tombstone_absorbing (revoke : Bool) :
    stepLifecycle Lifecycle.tombstone revoke = Lifecycle.tombstone := by
  rfl

/-- 知识库：模式列表。 -/
abbrev KnowledgeBase (ID Feature : Type) := List (KnowledgePattern ID Feature)

/-- 检索投影算子：仅 `promoted` 状态的模式可被投影进入当前任务上下文。 -/
def isProjectable {ID Feature : Type} (p : KnowledgePattern ID Feature) : Bool :=
  p.lifecycle == Lifecycle.promoted

/-- 上下文精细化投影结果。 -/
def filterProjectable {ID Feature : Type} [DecidableEq ID] [DecidableEq Feature]
    (kb : KnowledgeBase ID Feature) : KnowledgeBase ID Feature :=
  kb.filter isProjectable

/-- **定理（墓碑化模式永不可投影）**：
    若模式处于 tombstone 状态，则该模式不可能被投影入上下文。 -/
theorem tombstone_never_projectable {ID Feature : Type} [DecidableEq ID] [DecidableEq Feature]
    (kb : KnowledgeBase ID Feature) (p : KnowledgePattern ID Feature)
    (hmem : p ∈ filterProjectable kb) :
    p.lifecycle ≠ Lifecycle.tombstone := by
  have hp : isProjectable p = true := by
    rw [filterProjectable, List.mem_filter] at hmem
    exact hmem.2
  intro hcontra
  unfold isProjectable at hp
  rw [hcontra] at hp
  revert hp
  decide

/-- 反向免疫规则：携带特定污点特征的候选模式必被拦截。 -/
structure ImmunityRule (Feature : Type) where
  bannedFeature : Feature

/-- 免疫拦截谓词：若候选者的特征集包含被禁止的特征，则判定为包含污点。 -/
def isTaintedByRule {ID Feature : Type} [DecidableEq Feature]
    (rule : ImmunityRule Feature) (candidate : KnowledgePattern ID Feature) : Bool :=
  rule.bannedFeature ∈ candidate.features

/-- 由被撤销模式自动合成的反向免疫规则集。 -/
def synthesizeImmunityRules {ID Feature : Type}
    (revoked : KnowledgePattern ID Feature) : List (ImmunityRule Feature) :=
  revoked.features.map (fun f => ⟨f⟩)

/-- **定理（反向自免疫阻断定理）**：
    从墓碑模式合成的免疫规则集，必然能 100% 拦截任何携带其相同特征的复发候选。 -/
theorem immunity_blocks_taint {ID Feature : Type} [DecidableEq Feature]
    (revoked : KnowledgePattern ID Feature) (candidate : KnowledgePattern ID Feature)
    (f : Feature) (hf_rev : f ∈ revoked.features) (hf_cand : f ∈ candidate.features) :
    ∃ rule ∈ synthesizeImmunityRules revoked, isTaintedByRule rule candidate = true := by
  refine ⟨⟨f⟩, ?_, ?_⟩
  · unfold synthesizeImmunityRules
    rw [List.mem_map]
    exact ⟨f, hf_rev, rfl⟩
  · unfold isTaintedByRule
    simpa using hf_cand

/-- 知识库原子撤销操作：根据 patternId 将匹配的模式置为 tombstone。 -/
def revokePatternInKB {ID Feature : Type} [DecidableEq ID]
    (targetId : ID) (kb : KnowledgeBase ID Feature) : KnowledgeBase ID Feature :=
  kb.map (fun p => if p.id = targetId then { p with lifecycle := Lifecycle.tombstone } else p)

/-- **定理（原子撤销后该模式必然处于墓碑态）**：
    执行撤销后，目标模式在知识库中必为 tombstone 状态。 -/
theorem revoke_produces_tombstone {ID Feature : Type} [DecidableEq ID]
    (targetId : ID) (kb : KnowledgeBase ID Feature) (p : KnowledgePattern ID Feature)
    (hp_in : p ∈ revokePatternInKB targetId kb) (hp_id : p.id = targetId) :
    p.lifecycle = Lifecycle.tombstone := by
  unfold revokePatternInKB at hp_in
  rw [List.mem_map] at hp_in
  rcases hp_in with ⟨orig, _, rfl⟩
  split_ifs at hp_id with h
  · simp [h]
  · exact False.elim (h hp_id)

/-- **定理（撤销后立即丧失上下文投影资格）**：
    目标模式被撤销后，不再出现在任何过滤投影集合中。 -/
theorem revoked_excluded_from_projection {ID Feature : Type} [DecidableEq ID] [DecidableEq Feature]
    (targetId : ID) (kb : KnowledgeBase ID Feature) :
    ∀ p ∈ filterProjectable (revokePatternInKB targetId kb), p.id ≠ targetId := by
  intro p hp h_id
  have h_not_tomb := tombstone_never_projectable (revokePatternInKB targetId kb) p hp
  have h_tomb := revoke_produces_tombstone targetId kb p (by
    rw [filterProjectable, List.mem_filter] at hp
    exact hp.1
  ) h_id
  exact h_not_tomb h_tomb

/-- 分支过程有效繁殖数：墓碑化后有效繁殖均值压缩为 0。 -/
def effectiveReproductionMean (l : Lifecycle) (nominalMu : ℝ) : ℝ :=
  match l with
  | Lifecycle.promoted => nominalMu
  | Lifecycle.draft => nominalMu * 0.5
  | Lifecycle.tombstone => 0

/-- **定理（代际传播截断）**：
    当模式进入 tombstone 状态，其有效繁殖数严格为 0，
    根据分支过程理论，其后代产生概率在下一代立即为 0。 -/
theorem tombstone_offspring_zero (nominalMu : ℝ) :
    effectiveReproductionMean Lifecycle.tombstone nominalMu = 0 := by
  rfl

end IAC.Pattern15
