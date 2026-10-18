import Lake
open Lake DSL

package «IACFormalization» where
  -- 工业级智能体控制论（Industrial Agentic Cybernetics）形式化证明工程

-- 依赖：本机共享的 mathlib4 预编译包（离线路径引用，不污染其他项目）
require mathlib from "D:/tools/lean/.lake/packages/mathlib"
require batteries from "D:/tools/lean/.lake/packages/batteries"
require Qq from "D:/tools/lean/.lake/packages/Qq"
require aesop from "D:/tools/lean/.lake/packages/aesop"
require proofwidgets from "D:/tools/lean/.lake/packages/proofwidgets"
require importGraph from "D:/tools/lean/.lake/packages/importGraph"
require LeanSearchClient from "D:/tools/lean/.lake/packages/LeanSearchClient"
require plausible from "D:/tools/lean/.lake/packages/plausible"
require Cli from "D:/tools/lean/.lake/packages/Cli"

lean_lib «IACFormalization» where
  srcDir := "src"

@[default_target]
lean_exe «iacformalization» where
  root := `Main
