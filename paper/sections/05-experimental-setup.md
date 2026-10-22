# §5 Experimental Setup（论文全文扩写）

> 状态：**扩写 v1**（2026-10-22）；判读产物事实层单源：`experiments/attention_growth/*_judgement*.json`、`EXPERIMENT_PLAN_AXIOM4_*.md`。
> 位置：公理 IV 论文骨架 §5。

---

## 5.1 预注册原则

全部判据先于实验固定（假说清单见 §3.5）：显著性门槛（$p<0.05$ 置换/单侧）、判读单位（链均 vs 池化，见 5.5）、方向性命题一律预先声明。实验计划文档随判读产物存档（`EXPERIMENT_PLAN_AXIOM4_SUPERCRITICAL.md`、`EXPERIMENT_PLAN_AXIOM4_H1AC_BOOST.md`），任何口径修订在 §9 如实记录（如 H1AC 池化口径失效）。

## 5.2 模型档

| 档 | 模型 | 用途 |
| :--- | :--- | :--- |
| 主实验 | **DeepSeek-V4-Pro-0813**（简称 Pro；采样温度 temperature 0.7） | selective 协议，4 条件 × 12 会话 × 6 代 = 288 会话 |
| 跨模型 | Kimi `kimi-for-coding` + 同 Pro 协议 | X-H1/X-H4，288 会话 |
| SUPERCRITICAL | **DeepSeek-V4.1-Flash-1017**（简称 Flash） | full-append/容量档/selective 对照（与预注册模型档的偏离已在计划 §9 记录） |
| H1AC | 同 Flash | 160 链双毒株大样本 |

## 5.3 传播协议

- **毒株规范注入**：第 0 代注入 1 条携带谱系标记（P1/P2）的种子经验；逐代转写（selective：仅被判定相关者转写；full-append：全量追加）；
- **谱系追踪**：每条记忆条目携带 lineage 标记，$Z_n$=第 $n$ 代毒株谱系条目数（判读单位）；
- **双盲过滤（DRAFT_SUSPECT）**：标记门条件（C1）对疑似条目打标但不阻断；隔离门禁（C3/C2）物理阻断未终审条目（即未通过五重物理判据与独立审查终审的条目，定义见 §2.3）。

## 5.4 条件矩阵

- **selective**：C0（无门禁）/ C1（标记门）/ C2（随机过滤 $\sigma=0.5$）/ C3（隔离 $\sigma=1$）；
- **full-append**：C0-full / C1-full / C3-full（各 12 会话 × 8 代）；容量档 $M=8$ / $M=32$（各 6 会话 × 8 代）；selective 对照（2 会话 × 6 代）；
- **H1AC（Flash 双毒株）**：C0（48）/ C1（48）/ C2（64），6 代。

会话-代单元合计 **1,264**（= 主实验 288 + 跨模型 288 + 跨任务族 144 + SUPERCRITICAL 384 + H1AC 160）；其中 SUPERCRITICAL 384 = 3 条件 × 12 replicate × 8 代（C0/C1/C3-full）+ 敏感性 2 档 × 6 × 8（W=8/32），selective 对照 2 链 × 6 代另计。

## 5.5 判读口径

- bootstrap CI（$10^4$ 重采样）估计 $\hat m$ 及比值 CI；符号翻转配对置换（$10^4$）检验标记门配对差；
- **链均 vs 池化**：传播实验的判读单位取链均（per-parent 池化在 C2 下因幸存者偏差失效——末代存活率仅 6%，池化比值 1.017 无意义；已在计划 §9 记录并改用链均）；
- 几何律复验：log-linear 拟合 $R^2$；
- **功效**（Pro 档标记门）：配对差 $d=0.167$、$sd=0.432$、C1/C0 比值 0.529 → 当前 $n=12$ 功效仅 0.38，达 0.8 需 $n\approx48$（`e_power_markgate.py/.json`）——H1AC 档以 48 配对补齐该缺口。

## 5.6 可复现性

- 判读脚本：`e_supercritical_judge.py`/`judge2.py`/`sh3.py`、`e_cross_task_judge.py`、`e_h1ac_judge.py`（全部入 git）；
- 原始会话：`axiom4_results_*.json`（SUPERCRITICAL/H1AC/跨模型/跨任务族全套入 git）；
- 环境：模型档固定、采样温度 0.7、采样参数随会话归档。
