# experiments/attention_growth

本目录（历史目录名 `attention_growth`，与早期公理 II 实验共用）按全书专著 B.12 复现指引与论文附录 A 口径，集中承载以下工件：

- **公理 II（注意力增长律）实验**：E3 / E3b / E4 / t8 探针（`analyze_e3b.py`、`analyze_e4.py`、`analyze_t8.py`）；
- **公理 III（变异因果律）探针**：`axiom3_cargo_probe.py` / `axiom3_results.json`；
- **公理 IV（经验自免疫 / 记忆投毒）全部工件**：
  - 8 份预注册计划：`EXPERIMENT_PLAN_AXIOM4_*.md`（SUPERCRITICAL / H1AC_BOOST / KIMI_BOOST / CROSS_MODEL / CROSS_TASK 等）；
  - 原始会话 JSON：`axiom4_results_*.json`（C0/C1/C3-full、W4/W8/W12/W32、selective 对照、跨模型/跨任务族批次）；
  - 判读脚本与判读 JSON：`e_*_judge.py` → `e_*_judgement*.json`；
  - 状态重扫分片：`_mc_state_rescan_W{4,8,12}_{s1,s2}.json`（含 r0–r11 子片）与 `_mc_state_rescan_judge.py/.txt`；
  - 传播仿真：`axiom4_gw_sim.py` / `axiom4_gw_sim*.json`。

生产现场实验（模式 23/24，预注册 + 判读）见 `experiments/field_test/`。
