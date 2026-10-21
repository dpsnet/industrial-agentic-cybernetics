/- Galton-Watson 超临界分支过程：正概率永不灭绝。

用生成函数与多项式截断 + 中值定理的初等方法证明，
不依赖测度论鞅框架。核心结论：后代均值 m > 1 时，
灭绝概率 q < 1，即以正概率永不灭绝。 -/

import Mathlib.Topology.Algebra.InfiniteSum.Basic
import Mathlib.Topology.Algebra.InfiniteSum.Order
import Mathlib.Topology.Algebra.InfiniteSum.Real
import Mathlib.Topology.Basic
import Mathlib.Topology.Order.MonotoneConvergence
import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Analysis.Calculus.Deriv.Basic
import Mathlib.Analysis.Calculus.Deriv.Pow
import Mathlib.Analysis.Calculus.Deriv.MeanValue
import Mathlib.Data.Finset.Basic
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Data.Real.Basic

namespace IACFormalization.GaltonWatson

/-- 后代分布：非负、归一化、具有有限均值 m > 1（超临界）。 -/
structure OffspringDistribution where
  p : ℕ → ℝ
  nonneg : ∀ k, 0 ≤ p k
  hsum : Summable p ∧ tsum p = 1
  hmean : Summable (fun (k : ℕ) => (k : ℝ) * p k) ∧ 1 < tsum (fun (k : ℕ) => (k : ℝ) * p k)

/-- 后代均值 m = ∑ k·p_k。 -/
noncomputable def mean (od : OffspringDistribution) : ℝ := tsum (fun (k : ℕ) => (k : ℝ) * od.p k)

/-- 概率生成函数 φ(s) = ∑ p_k · s^k, s ∈ [0,1]。 -/
noncomputable def genFun (od : OffspringDistribution) (s : ℝ) : ℝ :=
  tsum (fun k => od.p k * s ^ k)

/-- 生成函数的 N 阶部分和（多项式）。 -/
def genFun_N (od : OffspringDistribution) (N : ℕ) (s : ℝ) : ℝ :=
  ∑ k ∈ Finset.range (N + 1), od.p k * s ^ k

/-- genFun_N 的导数（多项式形式导数）。 -/
def genFun_N' (od : OffspringDistribution) (N : ℕ) (s : ℝ) : ℝ :=
  ∑ k ∈ Finset.range (N + 1), (k : ℝ) * od.p k * s ^ (k - 1)

/- 生成函数项的可求和性。 -/
lemma genFun_summable (od : OffspringDistribution) {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) :
    Summable (fun k : ℕ => od.p k * s ^ k) := by
  apply Summable.of_nonneg_of_le (f := od.p) (g := fun k : ℕ => od.p k * s ^ k)
  · intro k
    have hpk : 0 ≤ od.p k := od.nonneg k
    have hsk : 0 ≤ s ^ k := by positivity
    exact mul_nonneg hpk hsk
  · intro k
    have hpk : 0 ≤ od.p k := od.nonneg k
    have hsk : s ^ k ≤ 1 := pow_le_one₀ hs0 hs1
    nlinarith
  · exact od.hsum.1

/- genFun(s) ≤ 1 对 s ∈ [0,1]。 -/
theorem genFun_le_one (od : OffspringDistribution) {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) :
    genFun od s ≤ 1 := by
  have hsum1 := od.hsum.1
  have hleq : ∀ k, od.p k * s ^ k ≤ od.p k := by
    intro k
    have h1 : 0 ≤ od.p k := od.nonneg k
    have h2 : s ^ k ≤ 1 := pow_le_one₀ hs0 hs1
    nlinarith
  have hsm : Summable (fun k : ℕ => od.p k * s ^ k) := genFun_summable od hs0 hs1
  have hts : tsum (fun k : ℕ => od.p k * s ^ k) ≤ tsum od.p :=
    hsm.tsum_le_tsum hleq hsum1
  rw [od.hsum.2] at hts
  exact hts

/- genFun 在 [0,1] 上单调递增。 -/
theorem genFun_mono (od : OffspringDistribution) {s t : ℝ}
    (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (ht0 : 0 ≤ t) (ht1 : t ≤ 1) (hst : s ≤ t) :
    genFun od s ≤ genFun od t := by
  have hleq : ∀ k, od.p k * s ^ k ≤ od.p k * t ^ k := by
    intro k
    have hpk : 0 ≤ od.p k := od.nonneg k
    have hpk2 : s ^ k ≤ t ^ k := by gcongr
    nlinarith
  have hsm1 : Summable (fun k : ℕ => od.p k * s ^ k) := genFun_summable od hs0 hs1
  have hsm2 : Summable (fun k : ℕ => od.p k * t ^ k) := genFun_summable od ht0 ht1
  exact hsm1.tsum_le_tsum hleq hsm2

/- genFun_N 在每一点可导，导数为 genFun_N'。 -/
theorem hasDerivAt_genFun_N (od : OffspringDistribution) (N : ℕ) (s : ℝ) :
    HasDerivAt (genFun_N od N) (genFun_N' od N s) s := by
  have h : ∀ k ∈ Finset.range (N + 1),
      HasDerivAt (fun x : ℝ => od.p k * x ^ k) ((k : ℝ) * od.p k * s ^ (k - 1)) s := by
    intro k _
    have hpow : HasDerivAt (fun x : ℝ => x ^ k) ((k : ℝ) * s ^ (k - 1)) s :=
      hasDerivAt_pow k s
    have hmul : HasDerivAt (fun x : ℝ => od.p k * x ^ k) (od.p k * ((k : ℝ) * s ^ (k - 1))) s :=
      hpow.const_mul (od.p k)
    convert hmul using 1
    ring
  have hsum : HasDerivAt (∑ i ∈ Finset.range (N + 1), (fun x : ℝ => od.p i * x ^ i))
      (genFun_N' od N s) s := by
    simpa [genFun_N'] using HasDerivAt.sum h
  convert hsum using 1
  funext x
  simp [genFun_N, Finset.sum_apply]

/- genFun_N 在任意区间上连续。 -/
theorem continuous_genFun_N (od : OffspringDistribution) (N : ℕ) :
    Continuous (genFun_N od N) := by
  have h : ∀ k ∈ Finset.range (N + 1), Continuous (fun x : ℝ => od.p k * x ^ k) := by
    intro k _; exact (continuous_pow k).const_mul (od.p k)
  have hcont : Continuous (fun x : ℝ => ∑ i ∈ Finset.range (N + 1), od.p i * x ^ i) :=
    _root_.continuous_finsetSum (s := Finset.range (N + 1)) (f := fun k => fun x : ℝ => od.p k * x ^ k) h
  convert hcont using 1
  funext x
  simp [genFun_N]

/- genFun_N' 在 [0,1] 上单调递增（因二阶导 ≥ 0）。 -/
theorem genFun_N'_mono (od : OffspringDistribution) (N : ℕ) {s t : ℝ}
    (hs0 : 0 ≤ s) (ht0 : 0 ≤ t) (hst : s ≤ t) :
    genFun_N' od N s ≤ genFun_N' od N t := by
  simp only [genFun_N']
  apply Finset.sum_le_sum
  intro k _
  have hpk : 0 ≤ od.p k := od.nonneg k
  have hcoef : 0 ≤ (k : ℝ) * od.p k := by positivity
  by_cases hk : k = 0
  · simp [hk]
  · have hk1 : 1 ≤ k := Nat.pos_of_ne_zero hk
    have hpow : s ^ (k - 1) ≤ t ^ (k - 1) := by
      gcongr
    nlinarith

/- genFun_N' 连续（多项式）。 -/
theorem continuous_genFun_N' (od : OffspringDistribution) (N : ℕ) :
    Continuous (genFun_N' od N) := by
  have h : ∀ k ∈ Finset.range (N + 1), Continuous (fun x : ℝ => (k : ℝ) * od.p k * x ^ (k - 1)) := by
    intro k _; exact (continuous_pow (k - 1)).const_mul ((k : ℝ) * od.p k)
  have hcont : Continuous (fun x : ℝ => ∑ i ∈ Finset.range (N + 1), (i : ℝ) * od.p i * x ^ (i - 1)) :=
    _root_.continuous_finsetSum (s := Finset.range (N + 1)) (f := fun (k : ℕ) => fun x : ℝ => (k : ℝ) * od.p k * x ^ (k - 1)) h
  convert hcont using 1
  funext x
  simp [genFun_N']

/-- **核心引理**：存在 `s₀ < 1` 使得 `φ(s₀) < s₀`。
    证明：取 N 使部分均值 > 1；由 `genFun_N'` 连续性，存在 `s₀` 接近 1 使
    `genFun_N'(s₀) > 1`；用 MVT 得 `genFun_N(s₀) < 1 - r_N - (1-s₀)`；
    尾部 `≤ r_N`，故 `φ(s₀) < s₀`。 -/
theorem exists_lt_sub_id (od : OffspringDistribution) :
    ∃ (s₀ : ℝ), 0 ≤ s₀ ∧ s₀ < 1 ∧ genFun od s₀ < s₀ := by
  set m := mean od with hm
  have hgt1 : 1 < m := od.hmean.2
  have hsm : Summable (fun (k : ℕ) => (k : ℝ) * od.p k) := od.hmean.1
  have hsum : HasSum (fun (k : ℕ) => (k : ℝ) * od.p k) m := hsm.hasSum
  have hpt : Filter.Tendsto (fun n : ℕ => ∑ k ∈ Finset.range n, (k : ℝ) * od.p k) Filter.atTop (nhds m) :=
    hsum.tendsto_sum_nat
  have hSNt : Filter.Tendsto (fun N : ℕ => genFun_N' od N 1) Filter.atTop (nhds m) := by
    have hSN : ∀ N : ℕ, genFun_N' od N 1 = ∑ k ∈ Finset.range (N + 1), (k : ℝ) * od.p k := by
      intro N; simp [genFun_N']
    have hcomp : Filter.Tendsto (fun N : ℕ => ∑ k ∈ Finset.range (N + 1), (k : ℝ) * od.p k) Filter.atTop (nhds m) :=
      hpt.comp (Filter.tendsto_add_atTop_nat 1)
    convert hcomp using 1
    funext N; rw [hSN N]
  have hev : ∀ᶠ N in Filter.atTop, 1 < genFun_N' od N 1 :=
    hSNt (isOpen_Ioi.mem_nhds hgt1)
  have hexN : ∃ N : ℕ, 1 < genFun_N' od N 1 := by
    rcases Filter.eventually_atTop.mp hev with ⟨N, hN⟩
    exact ⟨N, hN N (le_refl N)⟩
  rcases hexN with ⟨N, hN1⟩
  have hcontN' : Continuous (genFun_N' od N) := continuous_genFun_N' od N
  have hcontε : Continuous (fun ε : ℝ => genFun_N' od N (1 - ε)) :=
    hcontN'.comp (continuous_const.sub continuous_id)
  have hex_ε : ∃ ε : ℝ, 0 < ε ∧ ε < 1 ∧ 1 < genFun_N' od N (1 - ε) := by
    have hca : ContinuousAt (fun ε : ℝ => genFun_N' od N (1 - ε)) (0 : ℝ) := hcontε.continuousAt
    have hca2 : Filter.Tendsto (fun ε : ℝ => genFun_N' od N (1 - ε)) (nhds (0 : ℝ))
        (nhds ((fun ε : ℝ => genFun_N' od N (1 - ε)) 0)) := hca
    have hf0 : (fun ε : ℝ => genFun_N' od N (1 - ε)) 0 = genFun_N' od N 1 := by norm_num
    rw [hf0] at hca2
    have ht : Filter.Tendsto (fun ε : ℝ => genFun_N' od N (1 - ε)) (nhds (0 : ℝ)) (nhds (genFun_N' od N 1)) := hca2
    have hev2 : ∀ᶠ ε in nhds (0 : ℝ), 1 < genFun_N' od N (1 - ε) :=
      ht (isOpen_Ioi.mem_nhds hN1)
    rcases Metric.mem_nhds_iff.mp hev2 with ⟨δ, hδ, hball⟩
    let ε := min (δ / 2) (1 / 2 : ℝ)
    have hε0 : 0 < ε := by positivity
    have hεδ : ε < δ := by linarith [min_le_left (δ / 2) (1 / 2 : ℝ)]
    have hε1 : ε < 1 := by linarith [min_le_right (δ / 2) (1 / 2 : ℝ)]
    have hmem : ε ∈ Metric.ball (0 : ℝ) δ := by
      simp [Metric.mem_ball, hεδ, abs_of_pos hε0]
    have hgt : 1 < genFun_N' od N (1 - ε) := hball hmem
    exact ⟨ε, hε0, hε1, hgt⟩
  rcases hex_ε with ⟨ε, hε0, hε1, hN'⟩
  set a := 1 - ε with ha
  have ha0 : 0 < a := by linarith
  have ha1 : a < 1 := by linarith
  have ha1' : 0 ≤ a := by linarith
  have hN'2 : 1 < genFun_N' od N a := by simpa [ha] using hN'
  -- MVT on [a, 1]
  have hcontN : Continuous (genFun_N od N) := continuous_genFun_N od N
  have hderiv : ∀ x ∈ Set.Ioo a 1, HasDerivAt (genFun_N od N) (genFun_N' od N x) x :=
    fun x _ => hasDerivAt_genFun_N od N x
  have hmvt : ∃ c ∈ Set.Ioo a 1,
      genFun_N' od N c = (genFun_N od N 1 - genFun_N od N a) / (1 - a) :=
    exists_hasDerivAt_eq_slope (f := genFun_N od N) (f' := genFun_N' od N)
      ha1 hcontN.continuousOn hderiv
  rcases hmvt with ⟨c, hc, hslope⟩
  have hc1 : a < c := hc.1
  have hle : genFun_N' od N a ≤ genFun_N' od N c :=
    genFun_N'_mono od N ha1' (by linarith) (by linarith)
  have hpos : 0 < 1 - a := by linarith
  have hsub : genFun_N od N a ≤ genFun_N od N 1 - genFun_N' od N a * (1 - a) := by
    have h9 : genFun_N' od N c * (1 - a) = genFun_N od N 1 - genFun_N od N a := by
      rw [hslope]; field_simp [show (1 - a : ℝ) ≠ 0 by linarith]
    have h10 : genFun_N' od N a * (1 - a) ≤ genFun_N' od N c * (1 - a) := by
      gcongr
    linarith
  have hstrict : genFun_N od N a < genFun_N od N 1 - (1 - a) := by
    have h11 : (1 - a : ℝ) < genFun_N' od N a * (1 - a) := by
      have h12 : (1 : ℝ) < genFun_N' od N a := hN'2
      nlinarith
    linarith
  -- 尾部估计
  set r := tsum (fun i : ℕ => od.p (i + N + 1)) with hr
  have hpsum : Summable (fun i : ℕ => od.p (i + N + 1)) :=
    (summable_nat_add_iff (k := N + 1)).mpr od.hsum.1
  have hdecomp : genFun_N od N 1 + r = 1 := by
    have h := od.hsum.1.sum_add_tsum_nat_add (N + 1)
    rw [od.hsum.2] at h
    simpa [hr, genFun_N, add_assoc] using h
  have hgN1 : genFun_N od N 1 = 1 - r := by linarith
  have hgsm : Summable (fun i : ℕ => od.p (i + N + 1) * a ^ (i + N + 1)) := by
    apply Summable.of_nonneg_of_le (f := fun i : ℕ => od.p (i + N + 1)) (g := fun i : ℕ => od.p (i + N + 1) * a ^ (i + N + 1))
    · intro i; exact mul_nonneg (od.nonneg (i + N + 1)) (pow_nonneg ha1' _)
    · intro i
      have hpk : 0 ≤ od.p (i + N + 1) := od.nonneg (i + N + 1)
      have hpow : a ^ (i + N + 1) ≤ 1 := pow_le_one₀ ha1' (by linarith)
      nlinarith
    · exact hpsum
  have hdecomp2 : genFun od a = genFun_N od N a + tsum (fun i : ℕ => od.p (i + N + 1) * a ^ (i + N + 1)) := by
    have h := (genFun_summable od ha1' (by linarith)).sum_add_tsum_nat_add (N + 1)
    simpa [genFun, genFun_N, add_assoc] using h.symm
  have htail : tsum (fun i : ℕ => od.p (i + N + 1) * a ^ (i + N + 1)) ≤ r := by
    have hleq : ∀ i, od.p (i + N + 1) * a ^ (i + N + 1) ≤ od.p (i + N + 1) := by
      intro i
      have hpk : 0 ≤ od.p (i + N + 1) := od.nonneg (i + N + 1)
      have hpow : a ^ (i + N + 1) ≤ 1 := pow_le_one₀ ha1' (by linarith)
      nlinarith
    exact hgsm.tsum_le_tsum hleq hpsum
  have hmain : genFun od a < a := by
    linarith [hgN1, hdecomp2, htail, hstrict]
  exact ⟨a, by linarith, ha1, hmain⟩

/- genFun(s) ≥ 0 对 s ∈ [0,1]。 -/
theorem genFun_nonneg (od : OffspringDistribution) {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) :
    0 ≤ genFun od s := by
  have hsm : Summable (fun k : ℕ => od.p k * s ^ k) := genFun_summable od hs0 hs1
  have hn : ∀ k, 0 ≤ od.p k * s ^ k := by
    intro k; exact mul_nonneg (od.nonneg k) (pow_nonneg hs0 k)
  exact tsum_nonneg hn

/- 灭绝概率迭代：q_n = φ^n(0)。 -/
noncomputable def extinctIter (od : OffspringDistribution) : ℕ → ℝ
  | 0 => 0
  | n + 1 => genFun od (extinctIter od n)

/- q_n ∈ [0,1]。 -/
theorem extinctIter_bounds (od : OffspringDistribution) :
    ∀ n, 0 ≤ extinctIter od n ∧ extinctIter od n ≤ 1 := by
  intro n
  induction n with
  | zero =>
    simp only [extinctIter]
    exact ⟨by norm_num, by norm_num⟩
  | succ n ih =>
    have h0 : 0 ≤ extinctIter od n := ih.1
    have h1 : extinctIter od n ≤ 1 := ih.2
    exact ⟨genFun_nonneg od h0 h1, genFun_le_one od h0 h1⟩

/- q_n 单调递增。 -/
theorem extinctIter_mono (od : OffspringDistribution) :
    ∀ n, extinctIter od n ≤ extinctIter od (n + 1) := by
  intro n
  induction n with
  | zero =>
    simp only [extinctIter]
    exact genFun_nonneg od (by norm_num) (by norm_num)
  | succ n ih =>
    have hbn := extinctIter_bounds od n
    have hbn1 := extinctIter_bounds od (n + 1)
    have hle : extinctIter od n ≤ extinctIter od (n + 1) := ih
    exact genFun_mono od hbn.1 hbn.2 hbn1.1 hbn1.2 hle

/- 灭绝概率 q = sup_n q_n。 -/
noncomputable def extinctProb (od : OffspringDistribution) : ℝ :=
  sSup (Set.range (extinctIter od))

/- q_n ≤ s₀ 对所有 n（其中 genFun(s₀) < s₀, s₀ < 1）。 -/
theorem extinctIter_le_s0 (od : OffspringDistribution) {s₀ : ℝ}
    (hs00 : 0 ≤ s₀) (hs01 : s₀ ≤ 1) (hfix : genFun od s₀ < s₀) :
    ∀ n, extinctIter od n ≤ s₀ := by
  intro n
  induction n with
  | zero =>
    simp only [extinctIter]
    linarith
  | succ n ih =>
    have hbn := extinctIter_bounds od n
    have hle1 : extinctIter od n ≤ s₀ := ih
    have hmono : genFun od (extinctIter od n) ≤ genFun od s₀ :=
      genFun_mono od hbn.1 hbn.2 hs00 hs01 hle1
    simp only [extinctIter]
    linarith [hmono, hfix]

/-- **主定理（Galton-Watson 超临界正概率永不灭绝）**：
    后代均值 m > 1 时，灭绝概率 q < 1，即以正概率永不灭绝。 -/
theorem galton_watson_non_extinction (od : OffspringDistribution) :
    extinctProb od < 1 := by
  rcases exists_lt_sub_id od with ⟨s₀, hs00, hs01, hfix⟩
  have hle : ∀ n, extinctIter od n ≤ s₀ := extinctIter_le_s0 od hs00 (le_of_lt hs01) hfix
  have hbdd : ∀ y ∈ Set.range (extinctIter od), y ≤ s₀ := by
    intro y hy
    rcases hy with ⟨n, rfl⟩
    exact hle n
  have hnonempty : Set.Nonempty (Set.range (extinctIter od)) :=
    ⟨extinctIter od 0, ⟨0, rfl⟩⟩
  have hsup : sSup (Set.range (extinctIter od)) ≤ s₀ := csSup_le hnonempty hbdd
  have hq : extinctProb od = sSup (Set.range (extinctIter od)) := rfl
  rw [hq]
  exact lt_of_le_of_lt hsup hs01

/-! ### 精确刻画：q 是 φ 在 [0,1] 上的最小不动点 -/

/- q_n → q（单调有界序列收敛于上确界）。 -/
theorem extinctIter_tendsto (od : OffspringDistribution) :
    Filter.Tendsto (extinctIter od) Filter.atTop (nhds (extinctProb od)) := by
  have hbdd : BddAbove (Set.range (extinctIter od)) := by
    refine ⟨1, ?_⟩; rintro _ ⟨n, rfl⟩; exact (extinctIter_bounds od n).2
  have hne : Set.Nonempty (Set.range (extinctIter od)) := ⟨_, ⟨0, rfl⟩⟩
  have hmono : Monotone (extinctIter od) := monotone_nat_of_le_succ (extinctIter_mono od)
  exact tendsto_atTop_isLUB hmono (isLUB_csSup hne hbdd)

/- q ∈ [0,1]。 -/
theorem extinctProb_bounds (od : OffspringDistribution) :
    0 ≤ extinctProb od ∧ extinctProb od ≤ 1 := by
  have hbdd : BddAbove (Set.range (extinctIter od)) := by
    refine ⟨1, ?_⟩; rintro _ ⟨n, rfl⟩; exact (extinctIter_bounds od n).2
  have hne : Set.Nonempty (Set.range (extinctIter od)) := ⟨_, ⟨0, rfl⟩⟩
  have hlub := isLUB_csSup hne hbdd
  refine ⟨?_, csSup_le hne (by rintro _ ⟨n, rfl⟩; exact (extinctIter_bounds od n).2)⟩
  have h0 : extinctIter od 0 ≤ extinctProb od := hlub.1 ⟨0, rfl⟩
  simpa [extinctIter] using h0

/- 部分和不超过整级数：genFun_N(s) ≤ genFun(s) 对 s ∈ [0,1]。 -/
theorem genFun_N_le (od : OffspringDistribution) {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (N : ℕ) :
    genFun_N od N s ≤ genFun od s := by
  have hsm := genFun_summable od hs0 hs1
  have hnn : ∀ k, 0 ≤ od.p k * s ^ k := fun k => mul_nonneg (od.nonneg k) (pow_nonneg hs0 k)
  simpa [genFun_N, genFun] using hsm.sum_le_tsum (Finset.range (N + 1)) (fun k _ => hnn k)

/- 定点处级数收敛：genFun_N(s) → genFun(s)。 -/
theorem genFun_N_tendsto (od : OffspringDistribution) {s : ℝ} (hs0 : 0 ≤ s) (hs1 : s ≤ 1) :
    Filter.Tendsto (fun N => genFun_N od N s) Filter.atTop (nhds (genFun od s)) := by
  have hs : HasSum (fun k => od.p k * s ^ k) (genFun od s) := (genFun_summable od hs0 hs1).hasSum
  have h := hs.tendsto_sum_nat.comp (Filter.tendsto_add_atTop_nat 1)
  simpa [genFun_N, Function.comp_def] using h

/- **不动点定理**：q = φ(q)。
    上界 q ≤ φ(q)：由 q_{n+1} = φ(q_n) ≤ φ(q)（单调性）取极限。
    下界 φ(q) ≤ q：先用多项式截断 φ_N 的连续性取 n → ∞ 得 φ_N(q) ≤ q，再取 N → ∞。
    全程仅用单调性与多项式连续性，无需证明 φ 自身的连续性。 -/
theorem genFun_extinctProb_fixed (od : OffspringDistribution) :
    genFun od (extinctProb od) = extinctProb od := by
  have hb := extinctProb_bounds od
  have hq0 : 0 ≤ extinctProb od := hb.1
  have hq1 : extinctProb od ≤ 1 := hb.2
  have hlim := extinctIter_tendsto od
  have hbdd : BddAbove (Set.range (extinctIter od)) := by
    refine ⟨1, ?_⟩; rintro _ ⟨n, rfl⟩; exact (extinctIter_bounds od n).2
  have hne : Set.Nonempty (Set.range (extinctIter od)) := ⟨_, ⟨0, rfl⟩⟩
  have hqn_le : ∀ n, extinctIter od n ≤ extinctProb od := fun n => (isLUB_csSup hne hbdd).1 ⟨n, rfl⟩
  have hle1 : extinctProb od ≤ genFun od (extinctProb od) := by
    have hlim1 : Filter.Tendsto (fun n => extinctIter od (n + 1)) Filter.atTop
        (nhds (extinctProb od)) := hlim.comp (Filter.tendsto_add_atTop_nat 1)
    have hstep : ∀ n, extinctIter od (n + 1) ≤ genFun od (extinctProb od) := by
      intro n
      have hbn := extinctIter_bounds od n
      have hmono : genFun od (extinctIter od n) ≤ genFun od (extinctProb od) :=
        genFun_mono od hbn.1 hbn.2 hq0 hq1 (hqn_le n)
      exact hmono
    exact le_of_tendsto_of_tendsto hlim1 tendsto_const_nhds (Filter.Eventually.of_forall hstep)
  have hle2 : genFun od (extinctProb od) ≤ extinctProb od := by
    have hN : ∀ N, genFun_N od N (extinctProb od) ≤ extinctProb od := by
      intro N
      have hcont : Filter.Tendsto (fun n => genFun_N od N (extinctIter od n)) Filter.atTop
          (nhds (genFun_N od N (extinctProb od))) :=
        (continuous_genFun_N od N).continuousAt.tendsto.comp hlim
      have hbound : ∀ n, genFun_N od N (extinctIter od n) ≤ extinctProb od := by
        intro n
        have hbn := extinctIter_bounds od n
        exact le_trans (genFun_N_le od hbn.1 hbn.2 N) (hqn_le (n + 1))
      exact le_of_tendsto_of_tendsto hcont tendsto_const_nhds (Filter.Eventually.of_forall hbound)
    have hlimN := genFun_N_tendsto od hq0 hq1
    exact le_of_tendsto_of_tendsto hlimN tendsto_const_nhds (Filter.Eventually.of_forall hN)
  exact le_antisymm hle2 hle1

/- **最小性**：任何 [0,1] 中的不动点 s 都满足 q ≤ s。 -/
theorem extinctProb_le_of_fixed (od : OffspringDistribution) {s : ℝ}
    (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (hfix : genFun od s = s) :
    extinctProb od ≤ s := by
  have hle : ∀ n, extinctIter od n ≤ s := by
    intro n
    induction n with
    | zero => simp [extinctIter, hs0]
    | succ n ih =>
      have hbn := extinctIter_bounds od n
      calc extinctIter od (n + 1) = genFun od (extinctIter od n) := rfl
        _ ≤ genFun od s := genFun_mono od hbn.1 hbn.2 hs0 hs1 ih
        _ = s := hfix
  have hne : Set.Nonempty (Set.range (extinctIter od)) := ⟨_, ⟨0, rfl⟩⟩
  exact csSup_le hne (by rintro _ ⟨n, rfl⟩; exact hle n)

/-- **精确刻画（Galton-Watson 灭绝概率）**：后代均值 m > 1 时，
    灭绝概率 q 是生成函数 φ 在 [0,1] 上的**最小不动点**，且 q < 1。 -/
theorem galton_watson_extinctProb_exact (od : OffspringDistribution) :
    genFun od (extinctProb od) = extinctProb od ∧ extinctProb od < 1 ∧
    ∀ s : ℝ, 0 ≤ s → s ≤ 1 → genFun od s = s → extinctProb od ≤ s :=
  ⟨genFun_extinctProb_fixed od, galton_watson_non_extinction od,
   fun s hs0 hs1 hfix => extinctProb_le_of_fixed od hs0 hs1 hfix⟩

end IACFormalization.GaltonWatson
