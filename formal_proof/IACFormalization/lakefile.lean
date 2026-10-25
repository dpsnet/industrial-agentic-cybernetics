import Lake
open Lake DSL

package «IACFormalization» where
  -- 工业级智能体控制论（Industrial Agentic Cybernetics）形式化证明工程
  -- 公开可复现构建：mathlib4 git 依赖，其 lakefile 传递引入
  -- batteries / aesop / Qq / LeanSearchClient / importGraph / proofwidgets / plausible / Cli

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git"

lean_lib «IACFormalization» where
  srcDir := "src"

@[default_target]
lean_exe «iacformalization» where
  root := `Main
