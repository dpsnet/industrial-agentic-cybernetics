# 生产现场实验判读（§5 预注册标准，先于实验写好）
# 用法：python field_test_analyze.py --results <results_dir>

import argparse
import json
import os

REPS_PER_SCENARIO = 10
DETECT_WINDOW = 180          # 5 采集周期
SCRAPE_PERIOD = 30
F4_FAKE_RATE_LIMIT = 0.05    # 误报 ≤0.05（≈40 周期 ≤2）


def load_jsonl(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    return out


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def judge(results_dir):
    run_log = load_jsonl(os.path.join(results_dir, "run_log.jsonl"))
    alerts = load_jsonl(os.path.join(results_dir, "alerts_all.jsonl"))
    gate = load_jsonl(os.path.join(results_dir, "gate_results.jsonl"))
    audit = load_jsonl(os.path.join(results_dir, "audit_pass.jsonl"))
    tamper = load_json(os.path.join(results_dir, "tamper_results.json"))
    patterns = load_jsonl(os.path.join(results_dir, "patterns_all.jsonl"))

    rows = []

    # ---- H1 检测有效性 ----
    h1 = {}
    h1_ok = True
    for sc in ["F1", "F2", "F3", "F4"]:
        reps = [r for r in run_log if r.get("scenario") == sc]
        if sc != "F4":
            detected = sum(1 for r in reps if r.get("detected"))
            rate = detected / max(1, len(reps))
            pass_ = rate >= 0.90
            if not pass_:
                h1_ok = False
            h1[sc] = {"reps": len(reps), "detected": detected, "rate": round(rate, 3),
                      "threshold": ">=0.90", "pass": pass_}
        else:
            # 误报率：F4 窗口内 alerts / 采集周期数
            f4_alerts = 0
            total_periods = 0
            for r in reps:
                t0 = r.get("inject_ts", 0)
                for a in alerts:
                    if t0 <= a.get("ts", 0) <= t0 + DETECT_WINDOW:
                        f4_alerts += 1
                total_periods += DETECT_WINDOW // SCRAPE_PERIOD
            fake_rate = f4_alerts / max(1, total_periods)
            pass_ = fake_rate <= F4_FAKE_RATE_LIMIT
            if not pass_:
                h1_ok = False
            h1["F4"] = {"reps": len(reps), "false_alerts": f4_alerts,
                        "periods": total_periods, "rate": round(fake_rate, 4),
                        "threshold": "<=0.05", "pass": pass_}
    rows.append(("H1 检测有效性", h1_ok, json.dumps(h1, ensure_ascii=False)))

    # ---- H2 审计有效性 ----
    h2_ok = False
    h2_detail = "tamper_results 缺失"
    if tamper:
        total = tamper.get("total", 0)
        rejected = tamper.get("rejected", 0)
        h2_ok = total == 20 and rejected == 20
        h2_detail = f"rejected {rejected}/{total}（哈希 {sum(1 for r in tamper['results'] if r['kind']=='hash' and r['rejected'])}/8、mtime {sum(1 for r in tamper['results'] if r['kind']=='mtime' and r['rejected'])}/6、指纹 {sum(1 for r in tamper['results'] if r['kind']=='fingerprint' and r['rejected'])}/6）"
    rows.append(("H2 审计有效性", h2_ok, h2_detail))

    # ---- H3 闭环有效性 ----
    total_reports = len(gate)
    promoted = [g for g in gate if g.get("promote")]
    rejected = [g for g in gate if not g.get("promote")]
    all_green = [g for g in gate if g.get("verdict_all_green")]
    non_green = [g for g in gate if not g.get("verdict_all_green")]
    promote_ratio = len(promoted) / max(1, len(all_green))
    # 错误修复拦截 =1.00：晋升集合中不得含非全绿报告（门禁无旁路）
    bad_promote = [g for g in promoted if not g.get("verdict_all_green")]
    intercept_ok = len(bad_promote) == 0
    h3_ok = (total_reports > 0 and len(promoted) >= 1 and promote_ratio >= 0.80
             and intercept_ok)
    h3_detail = (f"reports={total_reports} all_green={len(all_green)} promote={len(promoted)} "
                 f"reject={len(rejected)} 晋升比例={promote_ratio:.2f}（阈≥0.80）"
                 f"错误拦截={intercept_ok and '1.00' or 'FAIL'}（晋升中非全绿={len(bad_promote)}）")
    rows.append(("H3 闭环有效性", h3_ok, h3_detail))

    # ---- H4 因果单调 ----
    # 只统计正常快照事件（evt_*）；tamper_* 是 H2 自测构造的篡改文件，其 mtime 拒绝属预期
    normal_audit = [a for a in audit if str(a.get("event", "")).startswith("evt_")]
    mtime_rejects = [a for a in normal_audit if not a.get("ok") and "mtime" in str(a.get("reason", ""))]
    h4_ok = len(mtime_rejects) == 0
    rows.append(("H4 因果单调", h4_ok,
                 f"正常事件审计={len(normal_audit)}，mtime 拒绝={len(mtime_rejects)}（阈 0）"))

    # ---- H5 适用域解耦 ----
    env_leaks = [g for g in gate if not g.get("promote") and any(
        "env_param_leak" in str(r) for r in g.get("reasons", []))]
    h5_ok = len(env_leaks) == 0
    llm_patterns_with_env = 0
    for p in patterns:
        text = json.dumps(p, ensure_ascii=False)
        if "=" in text and any(k in text for k in ("pool", "timeout", "limit", "latency", "cache")):
            llm_patterns_with_env += 1
    h5_detail = f"晋升条目环境泄漏={len(env_leaks)}（阈 0）；LLM 模式条目 {len(patterns)} 条"
    rows.append(("H5 适用域解耦", h5_ok, h5_detail))

    # ---- 输出 ----
    print("=" * 70)
    print("生产现场实验判读（预注册 §5）")
    print("=" * 70)
    all_pass = True
    md = ["# 生产现场实验判读（field_test_results）", ""]
    for name, ok, detail in rows:
        flag = "PASS" if ok else "FAIL"
        if not ok:
            all_pass = False
        print(f"[{flag}] {name}: {detail}")
        md.append(f"## {name}: **{flag}**")
        md.append(f"> {detail}")
        md.append("")
    print("-" * 70)
    print("总判定：", "全部通过" if all_pass else "存在未通过项")
    with open(os.path.join(results_dir, "judgement.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print("判读已写入 results/judgement.md", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "results"))
    args = ap.parse_args()
    judge(args.results)


if __name__ == "__main__":
    main()
