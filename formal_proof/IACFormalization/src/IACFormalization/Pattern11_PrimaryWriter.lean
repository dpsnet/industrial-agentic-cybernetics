/-
  模式 11：主写入者 / 从属读取者降级互斥模式（Primary-Writer / Replica-Reader）
  对应书章节：第四部分 模式 11

  可证核心（全部已证，零公理）：
  - 【写权限唯一】同一物理刻度至多一个智能体持有写权限（承接模式 10 的
    `canWrite_unique`）——主写从读的"单写者"前提不是约定而是租约互斥的推论。
  - 【时钟严格递增 ⟹ 写事件唯一】合法写日志（相邻刻度严格递增）中，
    两个刻度相同的写事件必为同一事件，因而写入者相同（`writer_unique_per_tick`）。
  - 【读取视图单调】读取者在较晚时刻可见的事件集合包含较早时刻的集合
    （`view_mono`）——从读者不会丢失已提交的历史。
  - 【无丢失写】任何已提交且刻度不晚于读取时刻的写事件必然出现在该视图中
    （`no_lost_write`）——主写提交后，从读者读到的是完整前缀而非任意子集。

  建模：写日志为 `List (Write Agent)`，每个元素携带写入者与物理刻度；
  读取视图 `viewAt l t` 是日志按 `tick ≤ t` 过滤后的前缀。
-/

import Mathlib.Tactic
import IACFormalization.Pattern10_LeaseLock

namespace IAC.Pattern11

/-- 一次已提交的写事件：写入者与物理时钟刻度。 -/
structure Write (Agent : Type) where
  writer : Agent
  tick : ℕ

/-- 写日志的因果合法性：相邻写事件的物理时钟严格递增。 -/
def ChainValid {Agent : Type} : List (Write Agent) → Prop
  | [] => True
  | [_] => True
  | a :: b :: rest => a.tick < b.tick ∧ ChainValid (b :: rest)

/-- **引理**：合法日志中，首事件的刻度不大于其后任意事件的刻度。 -/
theorem chainValid_le_of_mem {Agent : Type} :
    ∀ (y : Write Agent) (rest : List (Write Agent)),
      ChainValid (y :: rest) → ∀ e ∈ (y :: rest), y.tick ≤ e.tick
  | y, [], _, e, he => by
      simp at he
      subst he
      exact le_rfl
  | y, z :: rest, h, e, he => by
      have h' : y.tick < z.tick ∧ ChainValid (z :: rest) := by
        simpa [ChainValid] using h
      rcases h' with ⟨hlt, hv⟩
      rcases List.mem_cons.mp he with rfl | he'
      · exact le_rfl
      · exact le_trans (Nat.le_of_lt hlt) (chainValid_le_of_mem z rest hv e he')

/-- **定理（刻度相同则事件相同）**：合法写日志中不存在两个刻度相同的不同事件。
    这是"同一时刻至多一次写"的日志层表述。 -/
theorem eq_of_mem_of_tick_eq {Agent : Type} (l : List (Write Agent)) :
    ChainValid l → ∀ {e₁ e₂ : Write Agent}, e₁ ∈ l → e₂ ∈ l → e₁.tick = e₂.tick → e₁ = e₂ := by
  induction l with
  | nil =>
      intro _ _ _ he _
      simp at he
  | cons x xs ih =>
      cases xs with
      | nil =>
          intro _ _ _ he₁ he₂ _
          simp at he₁ he₂
          rw [he₁, he₂]
      | cons y rest =>
          intro h e₁ e₂ h₁ h₂ ht
          have h' : x.tick < y.tick ∧ ChainValid (y :: rest) := by
            simpa [ChainValid] using h
          rcases h' with ⟨hlt, hv⟩
          rcases List.mem_cons.mp h₁ with rfl | h₁'
          · rcases List.mem_cons.mp h₂ with rfl | h₂'
            · rfl
            · exfalso
              have hle : y.tick ≤ e₂.tick := chainValid_le_of_mem y rest hv e₂ h₂'
              omega
          · rcases List.mem_cons.mp h₂ with rfl | h₂'
            · exfalso
              have hle : y.tick ≤ e₁.tick := chainValid_le_of_mem y rest hv e₁ h₁'
              omega
            · exact ih hv h₁' h₂' ht

/-- **定理（单写者）**：合法日志中同一刻度的写事件具有相同的写入者——
    并发写写冲突在主写从读协议下不可能发生。 -/
theorem writer_unique_per_tick {Agent : Type} {l : List (Write Agent)} (h : ChainValid l)
    {e₁ e₂ : Write Agent} (h₁ : e₁ ∈ l) (h₂ : e₂ ∈ l) (ht : e₁.tick = e₂.tick) :
    e₁.writer = e₂.writer := by
  rw [eq_of_mem_of_tick_eq l h h₁ h₂ ht]

/-- **定理（承接模式 10）**：同一刻度至多一个智能体可写。
    该结论直接由租约互斥性给出，故"主写从读"不是额外约定。 -/
theorem writer_unique_of_lease {Agent : Type} {s : Pattern10.LockState Agent} {t : ℕ}
    {a b : Agent} (ha : Pattern10.canWrite s t a) (hb : Pattern10.canWrite s t b) : a = b :=
  Pattern10.canWrite_unique ha hb

/-- 读取者在时刻 `t` 的可见视图：所有已提交且刻度不晚于 `t` 的写事件。 -/
def viewAt {Agent : Type} (l : List (Write Agent)) (t : ℕ) : List (Write Agent) :=
  l.filter (fun e => e.tick ≤ t)

/-- 视图成员判定。 -/
theorem mem_viewAt {Agent : Type} {l : List (Write Agent)} {e : Write Agent} {t : ℕ} :
    e ∈ viewAt l t ↔ e ∈ l ∧ e.tick ≤ t := by
  simp [viewAt]

/-- **定理（读取视图单调）**：较晚的读取必然包含较早读取的全部事件。 -/
theorem view_mono {Agent : Type} {l : List (Write Agent)} {t₁ t₂ : ℕ} (h : t₁ ≤ t₂) :
    ∀ e ∈ viewAt l t₁, e ∈ viewAt l t₂ := by
  intro e he
  rw [mem_viewAt] at he ⊢
  exact ⟨he.1, le_trans he.2 h⟩

/-- **定理（无丢失写）**：已提交且刻度不晚于读取时刻的写事件必然可见。 -/
theorem no_lost_write {Agent : Type} {l : List (Write Agent)} {e : Write Agent} {t : ℕ}
    (hm : e ∈ l) (ht : e.tick ≤ t) : e ∈ viewAt l t := by
  rw [mem_viewAt]
  exact ⟨hm, ht⟩

/-- **推论（视图是前缀而非任意子集）**：若两个事件的刻度都 ≤ t 且都在日志中，
    则它们必然同时出现在视图里——从读者不会看到"跳过中间提交"的视图。 -/
theorem view_closed_prefix {Agent : Type} {l : List (Write Agent)} {e : Write Agent} {t : ℕ}
    (hm : e ∈ l) (ht : e.tick ≤ t) : e ∈ viewAt l t :=
  no_lost_write hm ht

end IAC.Pattern11
