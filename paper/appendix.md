# 附录（论文可选）

> 状态：**定稿 v1**（2026-10-22）；事实层单源：`experiments/attention_growth/` 判读产物。

---

## A. 判读脚本与数据清单

**判读脚本**（全部入 git）：

| 脚本 | 产出 | 用途 |
| :--- | :--- | :--- |
| `e_supercritical_judge.py` / `judge2.py` | `e_supercritical_judgement2.json` | SUPERCRITICAL 档：$\hat m$/CI、Z 轨迹、存活率、容量敏感性 |
| `e_supercritical_sh3.py` | `e_supercritical_sh3.json` | 逐代 offspring 核对（S-H3 证伪机制证据） |
| `e_cross_task_judge.py` | 跨任务族判读 JSON | T-H1/T-H4 |
| `e_h1ac_judge.py` | `e_h1ac_judgement.json` | H1AC：B-H1a/B-H1c/B-H2（bootstrap/符号翻转 10⁴） |
| `e_power_markgate.py` | `e_power_markgate.json` | 功效分析（min_n=48） |

**原始会话**（全部入 git）：`axiom4_results_supercritical*.json`（C0/C1/C3-full、W8/W32、w1–w4 shards）、`axiom4_results_flash_selective_ctrl.json`、`axiom4_results_h1ac_*.json`（C0/C1/C2/smoke）、跨模型/跨任务族会话 JSON。

**预注册计划**：`EXPERIMENT_PLAN_AXIOM4_SUPERCRITICAL.md`、`EXPERIMENT_PLAN_AXIOM4_H1AC_BOOST.md`（§9 判读回填与口径修订记录）。

**执行环境**：DeepSeek-V4.1-Flash-1017（简称 Flash；scnet-flash 网关，采样温度 0.7）；模型档偏离预注册 DeepSeek-V4-Pro-0813（Pro）档的记录见 SUPERCRITICAL 计划 §9。

## B. 判读 JSON 关键数值表（与正文同源）

| 量 | 值 | 来源 |
| :--- | :--- | :--- |
| C0-full $\hat m$ | 1.166，boot95 [1.156,1.176] | e_supercritical_judgement2 |
| C0-full Z 轨迹 | [1,2,2.917,3.917,3.917,4.917,4.917,4.917] | 同上 |
| C0-full mem 轨迹 | [6,9,12,15,16,16,16,16]（g4 饱和） | 同上 |
| C1-full $\hat m$ | 1.165（[1.163,1.167]） | 同上 |
| C3-full | mem 恒 6、Z 恒 1（12/12） | 同上 |
| W=8 | $\hat m$=0.829（[0.739,0.875]）、g7 存活 0 | 同上 |
| W=32 | $\hat m$=1.25、Z=[1..8]、mem→27 | 同上 |
| S-H3 机制证据 | $w_n\equiv1$、pmf=[0,1]、criterion pass=False | e_supercritical_sh3 |
| B-H1a | $\bar d$=+0.0201、正差 15/48、p=0.6918 | e_h1ac_judgement |
| B-H1c | $\hat r$=0.4661、CI [0.3331,0.6017]、点✅ CI⚠️ | 同上 |
| B-H2 | R²=0.9233、slope −0.086 | 同上 |
| μ 链均 | C0=0.905 / C1=0.885 / C2=0.422 | 同上 |
| 存活率末代 | C0=0.750 / C1=0.729 / C2=0.062 | 同上 |
| 功效 | n=12→0.379、n=48→0.848、min_n=48 | e_power_markgate |
| 主实验效应量 | pair_diff=0.167、sd=0.432、C1/C0=0.529 | 同上 |

## C. 判读单位与口径声明

- 判读单位：**链均**（H1AC）；SUPERCRITICAL 为链均 Z/存活率；
- 池化口径在 C2 下因幸存者偏差失效（末代存活仅 6%，池化比值 1.017 无意义）——已改链均并在计划 §9 记录；
- bootstrap / 符号翻转置换各 10⁴ 次；B-H1a 以 replicate 级链均配对差（§2.3 预注册口径）判读。
