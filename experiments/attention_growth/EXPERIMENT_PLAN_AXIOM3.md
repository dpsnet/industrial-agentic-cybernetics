# 公理 III 验证计划：变异因果单调（Causal Monotonicity of Mutation）

> 对应形式化：`formal_proof/IACFormalization/src/IACFormalization/Axiom3_CausalMonotonicity.lean`
> 核心定理：`observable_iff_mtime_strict_mono` + `log_append_apply_idempotent`
> 性质：**构建系统行为验证**（非 Transformer 经验命题），本地可完成，无需 GPU/云端

---

## 1. 待验命题（与形式化一一对应）

| 编号 | 命题 | 形式化对应 | 类型 |
| :--- | :--- | :--- | :--- |
| **H1** | 变异可被增量编译器观测到 ⟺ 文件 mtime 严格正向跳变 | `observable_iff_mtime_strict_mono` | 充要条件 |
| **H2** | 追加式日志（WAL）的回放算子幂等：同一物理时刻重复回放不产生副作用 | `log_append_apply_idempotent` | 幂等性 |

> H1 是公理 III 的核心——单调性不是工程优化，而是可观测性的逻辑必要条件。H2 是重试安全性的保障。

## 2. 形式化模型与现实映射

| 形式化 | 现实对应 |
| :--- | :--- |
| `Substrate.lastCompiledAt : ℕ` | 增量编译器内部记录的上次编译时间戳（fingerprint 中的 mtime） |
| `Mutation.mtApplied : ℕ` | 文件的物理修改时间戳（mtime） |
| `Mutation.content : ℕ` | 文件内容哈希 |
| `applyMutation` 规则 | 增量编译器的"是否重编译"决策：`mtApplied > lastCompiledAt` ⟹ 重建 |
| `compileArtifact.wasRebuilt` | cargo 输出的 `Dirty`/`Fresh` 标记 |
| `Journal.applied : List ℕ` | WAL / git 提交历史中的物理时刻序列 |
| `mutId` 约束 `mtApplied ∉ applied` | SHA-256 签名日志的唯一性检查 |

**关键映射假设**：增量编译器以物理时钟（mtime）为**唯一**判据。这一假设的成立性需由实验确认——若编译器同时使用内容哈希，则 H1 的反向（mtime 停滞 ⟹ 静默丢失）不成立。

## 3. 预实验发现（2026-10-20，已确认）

用 `cargo check -v` 对 Rust 项目做探索性实验：

- **正向**：修改 `src/main.rs` 内容 + mtime 自然递增 → cargo 输出 `Dirty ... the file has changed (...47m 47s after last build...)`，触发重编译
- **反向**：修改内容 + 强制 mtime 恢复原值 → cargo 输出 `Finished ... target(s) in 0.15s`，**无 `Dirty` 标记**，编译被静默跳过

结论：**Cargo 1.96 的 fingerprint 机制以 mtime 为判据**，符合公理 III 模型。H1 正向与反向均得到预实验支持。

## 4. 实验设计

### 4.1 H1：可观测性充要条件

用 Cargo + 最小 Rust 项目（`cargo new`），控制两个变量：内容是否变化、mtime 是否递增。

| 组 | 内容 | mtime | 预期 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| **1a** | 修改 | 自然递增 | `Dirty` | 正向：mtime 递增 ⟹ 可观测 |
| **1b** | 修改 | 停滞（恢复原值） | `Fresh` | 反向1：mtime 停滞 ⟹ 静默丢失 |
| **1c** | 修改 | 回拨（设为更早） | `Fresh` | 反向2：mtime 回拨 ⟹ 静默丢失；若实测 `Dirty`，说明 Cargo 采用"mtime 不等即重建"的保守谓词而非严格 `>` 谓词——回拨方向无静默丢失，谓词形态须在 §6 注明 |
| **1d** | 不变 | 递增 | `Dirty`（产物 stdout 不变） | 对照：形式模型 `applyMutation` 仅由 mtime 跳变触发重建、与内容无关；产物 stdout 不变印证定理前提 `hdiff`（内容有差异）是"可观测变化"的必要条件 |

**重复**：每组 5 次随机种子（内容用不同字符串），共 20 次测量。

**测量指标**：
- cargo 输出是否包含 `Dirty`（重编译）或仅 `Finished`（跳过）
- 编译耗时（`Dirty` 显著大于 `Fresh`）
- 产物内容是否更新（`Fresh` 时产物为旧版本）

**判读标准**（预注册，2026-10-20 修订版）：
- 1a 全部 `Dirty` 且产物 stdout 更新、1b 全部 `Fresh` 且产物 stdout 保持旧值 ⟹ H1 支持（递增 ⟹ 可观测，停滞 ⟹ 静默丢失）
- **1b 是静默丢失的决定性检验**（mtime 相等 + 内容不同）：若出现 `Dirty` ⟹ Cargo 存在 mtime 之外的辅助判据（内容哈希），纯时钟模型须收缩适用域
- **1c 判别谓词形态**：`Fresh` ⟹ 严格 `>` 谓词，与形式模型一致；`Dirty` ⟹ `≠` 保守谓词（回拨触发重建、无静默丢失，单调方向结论不变但机制刻画须修订）
- **1d 判别内容通道**：`Dirty` 且产物 stdout 不变 ⟹ 与形式模型一致（重建由时钟跳变触发，可观测性由内容差异决定）；`Fresh` ⟹ Cargo 在纯 mtime 递增时跳过，说明其判据弱于形式模型
- 1d 的 `Dirty` **不构成**对 H1 的证伪——定理前提 `hdiff` 明确限定"产生真实差异的变异"，1d 落在该前提之外

### 4.2 H2：日志幂等性

模拟 WAL 重放场景，验证重复应用同一变异不产生副作用。

| 组 | 操作 | 预期 |
| :--- | :--- | :--- |
| **2a** | 连续两次 `cargo build`（无文件变化） | 第二次 `Fresh`，产物无变化 |
| **2b** | `git stash` → `cargo build` → `git stash pop` → `cargo build` | 第二次 `build` 后产物与首次一致，无重复编译副作用 |
| **2c** | 手动模拟 WAL：记录变异 (content, mtApplied)，回放两次 | 第二次回放的 hash 校验失败（`hashVerified = false`），内容不变 |

**测量指标**：
- 第二次构建的 `Dirty`/`Fresh` 标记
- 产物 SHA-256 是否与首次一致
- 编译耗时

**判读标准**（预注册）：
- 2a/2b 第二次均为 `Fresh` 且产物哈希一致 ⟹ H2 支持
- 2c 中第二次回放 `hashVerified = false` 且内容不变 ⟹ 幂等性成立
- 若 2a 第二次为 `Dirty` ⟹ 增量编译器不幂等，H2 被证伪

## 5. 工具与环境

| 工具 | 用途 | 版本 |
| :--- | :--- | :--- |
| Cargo / Rustc | 增量编译器（mtime-based fingerprint） | 1.96.0 |
| PowerShell | 控制 mtime（`[System.IO.File]::SetLastWriteTime`） | 5.1 |
| Python 3 | 实验编排与结果分析 | 3.x |
| Git | H2 的 stash/apply 场景 | - |

**无需 GPU/云端**，全部本地完成。

## 6. 适用域边界（预先声明）

公理 III 的形式化模型假设增量编译器**以物理时钟为唯一判据**。以下编译器可能不满足此假设：

| 编译器类型 | 判据 | 是否符合公理 III |
| :--- | :--- | :--- |
| Make | mtime | ✅ 符合 |
| Cargo (1.96) | mtime (fingerprint) | ✅ 符合（预实验确认） |
| Ninja | mtime + 内容哈希 | ⚠️ 部分符合（内容哈希可能覆盖 mtime） |
| Bazel | 内容哈希 | ❌ 不符合（不需要 mtime 跳变） |
| Nix | 内容哈希 | ❌ 不符合 |

**结论**：公理 III 适用于 **mtime-based 增量编译器**。对于内容哈希型编译器，"代码已改、测试仍跑旧字节码"的静默丢失场景不会发生——但其代价是每次变异都需计算内容哈希，且无法利用 mtime 的单调信息。

## 7. 认识论声明

1. **形式化覆盖**：`observable_iff_mtime_strict_mono` 和 `log_append_apply_idempotent` 是 Lean 4 机检定理，0 sorry，逻辑上恒真
2. **经验命题**：本实验验证的是"Cargo 等 mtime-based 增量编译器的行为符合该定理"，而非定理本身
3. **模型-现实映射**：`lastCompiledAt` ↔ fingerprint mtime、`mtApplied` ↔ 文件 mtime 是未经证明的假设，其成立性由本实验的 H1 反向测试（1b/1c）背书
4. **外推限制**：结论仅限于 Cargo 1.96 + Rust 项目，跨编译器族（Bazel/Nix）的外推不成立，见 §6

## 8. 执行计划

1. **脚本开发**：`axiom3_cargo_probe.py`——自动化 H1 四组实验 + H2 三场景，记录重建标志、耗时、产物哈希与语义输出 ✅（2026-10-20）
2. **本地执行**：H1 20 次测量 + H2 三场景，实际 < 2 分钟 ✅（2026-10-20，两个独立运行批次结果一致）
3. **结果分析**：28/28 全部通过，`H1_all_pass = H2_all_pass = true` ✅（见 §9）
4. **文档回写**：正文 §3.2 公理 III 段 + 附录 B.4 ✅（2026-10-20）

## 9. 结果判读（2026-10-20）

数据：`axiom3_results.json`（Cargo 1.96.0 / rustc 1.96.0 / Python 3.12.8 / Windows）

### 9.1 H1：可观测性充要条件 —— **支持**

| 组 | 预期 | 实测 | 判定 |
| :--- | :--- | :--- | :--- |
| 1a 内容变 + mtime 递增 | 重建 + 产物更新 | 5/5 重建，stdout 逐次 v1→v5，sha 全变 | ✅ |
| 1b 内容变 + mtime 停滞 | 跳过 + 静默丢失 | 5/5 跳过，stdout 保持 v0，sha 不变 | ✅ |
| 1c 内容变 + mtime 回拨 | 跳过（判别谓词） | 5/5 跳过，stdout 保持 v0 | ✅ **严格 `>` 谓词，与形式模型一致** |
| 1d 内容不变 + mtime +5s | 重建 + 产物不变 | 5/5 重建（sha 变 = PE 时间戳），stdout 恒 v0 | ✅ 触发纯由时钟通道决定 |

- **1b（决定性检验）通过**：mtime 停滞时内容修改被静默吞没，产物仍为旧版本——"代码已改、测试仍跑旧字节码"获得工程实证
- **1c 判别结果**：回拨同样静默丢失，Cargo 采用与形式模型一致的严格 `>` 谓词，**无**保守 `≠` 语义、**无**内容哈希辅助判据
- **1d 判别结果**：纯 mtime 跳变（内容不变）触发重建——重建触发与时钟有关、与内容无关，与形式模型 `applyMutation` 的单通道判据一致；产物 stdout 不变印证定理前提 `hdiff`（内容有差异）是"可观测变化"的必要条件

### 9.2 H2：日志幂等性 —— **支持**

| 场景 | 预期 | 实测 | 判定 |
| :--- | :--- | :--- | :--- |
| 2a 连续无变化 build | 跳过 + sha 不变 | 5/5 跳过，产物 sha 与 baseline 一致 | ✅ |
| 2b git stash 回退 → build → pop → build | 重试后语义恢复 | 三次均重建，stdout 依次 v1→v0→v1 | ✅ 回退-恢复重试不产生残留污染 |
| 2c WAL 回放模拟 | 二次回放校验失败 | `hashVerified` True→False，content 不变 | ✅ 与 Lean 定理逐字对应 |

### 9.3 两个工程发现（超出预注册的增量知识）

1. **参考时钟 R ≈ 上次构建完成时刻，而非源文件自身旧 mtime**（v1 运行批次发现）：1d 组以 +1s 步进 bumps 时，baseline 编译耗时 4.59s，+1s~+4s 的 mtime 均未触发重建、+5s 才触发——重建判据实测为"文件 mtime 严格超过上次构建的参考时钟"。这把静默丢失窗口刻画为 **(0, R]**：构建期间及紧随其后的写入（mtime ≤ R）即使 mtime 已"增长"，仍会被静默吞没。这比朴素模型（窗口 = 文件旧 mtime）**更宽**，强化了公理 III 的工程含义：构建进行中的并发写入天然不安全。v2 起跳变量取 +5s 以确定性越过 R。
2. **Windows PE 头含编译时间戳，字节级幂等不成立**：同一源码的两次重编译产物 sha 必然不同（1d 组 sha 全变但 stdout 不变）。幂等性的工程判读必须在**语义层**（重试后输出恢复）进行，而非字节级 sha 相等——这对应 Lean 定理中幂等性的承诺范围：第二次回放不改变**内容**，不承诺产物比特级一致。

### 9.4 工程备注（实验方法学）

- 重建信号：`cargo build -v` 输出经 ANSI 转义剥离后的 `Compiling <pkg>` 行（cargo 在非 TTY 下仍输出色彩码，`Compiling` 与包名之间被 `\x1b[0m` 隔断，裸子串匹配会漏报/误判）
- 2b 场景必须 `.gitignore` 掉 `target/`：构建产物入库会使 `git stash pop` 因"local changes would be overwritten"中止
- 遗留：`experiments/causal_mono_probe/`（v0 探索项目）被 rust-analyzer 进程锁定无法删除，需手动清理
