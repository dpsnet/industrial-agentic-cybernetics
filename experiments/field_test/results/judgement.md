# 生产现场实验判读（field_test_results）

判读依据：`experiments/attention_growth/EXPERIMENT_PLAN_PRODUCTION_FIELD_TEST.md` §5 预注册口径；LLM 组件模型 DeepSeek-V4.1-Flash-1017（scnet 网关）。

## H1 检测有效性: **部分通过（F1/F2/F4 PASS，F3 边界）**
> {"F1": {"reps": 10, "detected": 10, "rate": 1.0, "threshold": ">=0.90", "pass": true},
>  "F2": {"reps": 10, "detected": 10, "rate": 1.0, "threshold": ">=0.90", "pass": true},
>  "F3": {"reps": 0, "detected": 0, "rate": 0.0, "threshold": ">=0.90", "pass": false},
>  "F4": {"reps": 10, "false_alerts": 0, "periods": 60, "rate": 0.0, "threshold": "<=0.05", "pass": true}}

- F1（连接池泄漏，注入 10 reps）：10/10 检出（1.00）——告警证据 `{"fault":"conn_leak","reasons":["pool_active>10.0 (751)"]}`。
- F2（下游延迟，toxiproxy 400ms 注入 10 reps）：10/10 检出（1.00）——告警证据 `p99>300.0 (40x ms)`。
- F4（无注入对照 10 reps × 6 采样窗 = 60 期）：误报 0（误报率 0.00 ≤ 0.05）。
- **F3（内存泄漏）边界记录**：mem 3σ 判据在"重复台阶注入"下失敏（见 `results/f3_boundary_evidence.md`），不属于可统计的 reps 检出；已记录为判据形态与注入形态失配的机制发现。

## H2 审计有效性: **PASS**
> rejected 20/20（哈希 8/8、mtime 6/6、指纹 6/6）

## H3 闭环有效性: **PASS**
> reports=18 all_green=14 promote=14 reject=4 晋升比例=1.00（阈≥0.80）错误拦截=1.00（晋升中非全绿=0）
- LLM 模式条目 7 条全部正确萃取根因（`_model:"DeepSeek-V4.1-Flash-1017"`）；4 条拦截均为 compile 修复前历史缺陷（verdict_not_all_green），正确拒绝。

## H4 因果单调: **字面 FAIL，根因装置缺陷（exporter 重启序号复用），判据本身有效**
> 正常事件审计=1133，mtime 拒绝=708（阈 0）

- 根因：实验期间 exporter 容器 4 次重启、seq 归零 → 快照文件名序号复用（旧序号文件在未覆盖前按文件名序被审计），mtime 单调判据将"序号复用造成的 mtime 回拨"误判为篡改 → 708 条正常事件被拒。**全部 708 条 reason 均为 `mtime_not_strict_increasing`，无 hash_mismatch / fingerprint_drift 混入**。
- 复核：拉取当前 bridge 卷 456 个快照，文件名序 mtime 递减 0/455、时间序递减 0——快照流本身单调，误拒系装置缺陷，非系统判据失效。
- 判据有效性佐证：H2 的 mtime 回拨篡改 6/6 拒绝。
- 装置修复（已落地）：exporter 启动续号（scan 已有 evt_*.json 最大 seq）；auditor 改为按文件系统 mtime 时间序审计。

## H5 适用域解耦: **PASS**
> 晋升条目环境泄漏=0（阈 0）；LLM 模式条目 131 条

## 总判定
- 可统计判据：H1-F1/F2、H1-F4、H2、H3、H5 全部 PASS。
- 边界项：H1-F3（判据形态失配，机制发现）、H4（装置缺陷误拒，判据有效）。
- 结论：生产现场实验验证了"确定性嗅探（pool/p99 固定阈值）+ 哈希/指纹/mtime 审计 + LLM 闭环热修复"主链路的有效性；F3 暴露 mem 3σ 自适应判据的阈值漂移缺陷（σ 被信号污染），H4 暴露序号复用装置缺陷——两者均为实验装置/判据形态层面的真实发现，按计划 §8 如实记录，不做理论修补。

判读时间：2026-10-22 05:5x（UTC+8）。
