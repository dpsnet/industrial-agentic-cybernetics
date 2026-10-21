/-
  IACFormalization 根模块
  《工业级智能体控制论》形式化证明卷

  模块拓扑（无循环依赖，与书中章节对应）：
    Axiom3（§3.2 公理 III；模式 09）—— 因果单调性，最先证明，不依赖 mathlib
    Axiom1（§3.2 公理 I；第二章）—— 接地不可替代性
    Axiom2（§3.2 公理 II；模式 04）—— 注意力稀释单调性
    Axiom2_PhaseModel（§3.2 公理 II 适用域）—— 两相稀释：饱和点与平台相
    Axiom4（§3.2 公理 IV；模式 14/15）—— 记忆投毒相变
    Axiom2_Axiom4_Bridge（§3.2 层间纵向边）—— 注入速率 → 违约下界（公理 II ↔ IV）
    Theorem31（§3.3）—— 收敛因果不变性，汇合模块
-/
import IACFormalization.Axiom3_CausalMonotonicity
import IACFormalization.Axiom1_Grounding
import IACFormalization.Axiom2_AttentionDilution
import IACFormalization.Axiom2_PhaseModel
import IACFormalization.Axiom4_MemoryPoisoning
import IACFormalization.Axiom2_Axiom4_Bridge
import IACFormalization.Theorem3_1_CausalInvariance
import IACFormalization.GaltonWatson
import IACFormalization.StochasticFosterLyapunov
import IACFormalization.Pattern10_LeaseLock
