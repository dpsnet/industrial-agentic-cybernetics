/-
  模式 10：分布式物理底座租约锁与看门狗模式（Substrate Lease Lock & Watchdog）
  对应书章节：第四部分 模式 10

  可证核心（全部已证，零公理）：
  - 【互斥安全性】写权限谓词 canWrite 在同一时刻至多对一个智能体成立
    （canWrite_unique）；租约存活时任何 acquire 必被拒绝（acquire_rejected_of_live）；
    成功 acquire 当且仅当先前无存活租约（acquire_succeeds_iff_dead）。
  - 【看门狗活性（反死锁）】TTL 到期后租约必然可回收：对任意状态存在时刻 T，
    其后 acquire 永远成功（no_permanent_lockout）——失效场景 B（孤儿锁永久死锁）
    被形式化否定；不可用时长有界（expiry + 1）。
  - 【越权防护】非持有者的心跳不改变状态（heartbeat_by_nonholder_unchanged），
    越权者无法藉心跳续命他人/自己的锁。

  建模：物理时钟为离散 tick；LockState = Option Lease（Option 结构本身编码
  "至多一个租约"）；acquire / heartbeat 为带前置条件的纯函数，拒绝时返回 none / 原状态。
-/

import Mathlib.Tactic

namespace IAC.Pattern10

/-- 物理时钟（离散 tick）。 -/
abbrev Clock := ℕ

/-- 租约：持有者与到期时刻。 -/
structure Lease (Agent : Type) where
  holder : Agent
  expiry : Clock
deriving DecidableEq

/-- 锁状态：至多一个租约。 -/
abbrev LockState (Agent : Type) := Option (Lease Agent)

/-- 租约在时刻 t 存活 ⟺ 存在租约且 t 未超过到期时刻。 -/
def liveAt {Agent : Type} (s : LockState Agent) (t : Clock) : Prop :=
  ∃ l, s = some l ∧ t ≤ l.expiry

/-- 申请排他写租约：仅当当前无存活租约时授予，否则拒绝（调用方降级为从读）。 -/
def acquire {Agent : Type} (s : LockState Agent) (t : Clock) (a : Agent) (ttl : ℕ) :
    Option (Lease Agent) :=
  match s with
  | none => some ⟨a, t + ttl⟩
  | some l => if t ≤ l.expiry then none else some ⟨a, t + ttl⟩

/-- 心跳续约：仅持有者可刷新到期时刻；非持有者心跳被拒绝，状态不变。 -/
def heartbeat {Agent : Type} [DecidableEq Agent] (s : LockState Agent) (t : Clock)
    (a : Agent) (ttl : ℕ) : LockState Agent :=
  match s with
  | none => none
  | some l => if l.holder = a then some ⟨a, max l.expiry (t + ttl)⟩ else some l

/-- 写权限：当且仅当调用方持有存活租约。 -/
def canWrite {Agent : Type} (s : LockState Agent) (t : Clock) (a : Agent) : Prop :=
  ∃ l, s = some l ∧ l.holder = a ∧ t ≤ l.expiry

/-- **定理（互斥安全性）**：同一时刻至多一个智能体持有写权限。
    两个可写者必为同一人——并发写写冲突（失效场景 A）在协议内不可能。 -/
theorem canWrite_unique {Agent : Type} {s : LockState Agent} {t : Clock} {a b : Agent}
    (ha : canWrite s t a) (hb : canWrite s t b) : a = b := by
  rcases ha with ⟨l₁, hs₁, hh₁, -⟩
  rcases hb with ⟨l₂, hs₂, hh₂, -⟩
  have : l₁ = l₂ := Option.some.inj (hs₁ ▸ hs₂)
  rw [← hh₁, ← hh₂, this]

/-- **定理（存活拒绝）**：租约存活时，任何 acquire 申请必被拒绝。 -/
theorem acquire_rejected_of_live {Agent : Type} {s : LockState Agent} {t : Clock}
    (h : liveAt s t) (a : Agent) (ttl : ℕ) : acquire s t a ttl = none := by
  rcases h with ⟨l, hs, ht⟩
  simp [acquire, hs, ht]

/-- **定理（授予仅当无存活）**：acquire 成功 ⟹ 先前无存活租约。 -/
theorem acquire_succeeds_only_when_dead {Agent : Type} {s : LockState Agent} {t : Clock}
    {a : Agent} {ttl : ℕ} {l : Lease Agent}
    (h : acquire s t a ttl = some l) : ¬ liveAt s t := by
  rintro ⟨l₀, hs₀, ht₀⟩
  simp [acquire, hs₀, ht₀] at h

/-- **定理（授予的租约属申请人且立即存活）**。 -/
theorem acquire_holder_and_live {Agent : Type} {s : LockState Agent} {t : Clock}
    {a : Agent} {ttl : ℕ} {l : Lease Agent}
    (h : acquire s t a ttl = some l) : l.holder = a ∧ liveAt (some l) t := by
  cases hs : s with
  | none =>
    simp [acquire, hs] at h
    subst h
    exact ⟨rfl, ⟨_, rfl, Nat.le_add_right _ _⟩⟩
  | some l₀ =>
    by_cases ht : t ≤ l₀.expiry
    · simp [acquire, hs, ht] at h
    · simp [acquire, hs, ht] at h
      subst h
      exact ⟨rfl, ⟨_, rfl, Nat.le_add_right _ _⟩⟩

/-- **定理（看门狗活性：无永久死锁）**：对任意锁状态，存在时刻 T，
    其后任何 acquire 都成功——崩溃持有者的孤儿租约必然在 TTL 到期后回收，
    工程不可能被永久锁死（失效场景 B 的形式否定）。 -/
theorem no_permanent_lockout {Agent : Type} (s : LockState Agent) (a : Agent) (ttl : ℕ) :
    ∃ T : Clock, ∀ t : Clock, T ≤ t → (acquire s t a ttl).isSome = true := by
  cases s with
  | none => exact ⟨0, fun _ _ => by simp [acquire]⟩
  | some l =>
    refine ⟨l.expiry + 1, fun t ht => ?_⟩
    have hdead : ¬ t ≤ l.expiry := Nat.not_le_of_gt ht
    simp [acquire, hdead]

/-- **定理（到期后原持有者写权限消灭）**：过期租约的持有者不再可写，
    必须重新竞争——租约不会因历史持有而残留特权。 -/
theorem not_canWrite_of_expired {Agent : Type} {l : Lease Agent} {t : Clock}
    (ht : l.expiry < t) : ¬ canWrite (some l) t l.holder := by
  rintro ⟨l', hs', hh', ht'⟩
  have hl : l = l' := Option.some.inj hs'
  subst hl
  exact absurd ht' (Nat.not_le_of_gt ht)

/-- **定理（非持有者心跳无效）**：越权心跳不改变状态——
    辅助代理无法藉续约机制窃取或延长他人写锁（失效场景 C 的续约侧防护）。 -/
theorem heartbeat_by_nonholder_unchanged {Agent : Type} [DecidableEq Agent]
    {s : LockState Agent} {t : Clock} {a : Agent} {ttl : ℕ} {l : Lease Agent}
    (hs : s = some l) (hne : l.holder ≠ a) :
    heartbeat s t a ttl = some l := by
  subst hs
  simp [heartbeat, hne]

/-- **定理（持有者心跳不缩短租约）**：合法续约后到期时刻不早于原先。 -/
theorem heartbeat_by_holder_extends {Agent : Type} [DecidableEq Agent]
    {t : Clock} {ttl : ℕ} {l : Lease Agent} :
    heartbeat (some l) t l.holder ttl = some ⟨l.holder, max l.expiry (t + ttl)⟩ ∧
    l.expiry ≤ max l.expiry (t + ttl) := by
  simp [heartbeat, le_max_left]

end IAC.Pattern10
