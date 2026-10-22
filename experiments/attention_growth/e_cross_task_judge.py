"""
CROSS_TASK 判读：跨任务族的 T-H1~T-H4 判读（对应 EXPERIMENT_PLAN_AXIOM4_CROSS_TASK.md §3）
=========================================================================================
输入：axiom4_results_cross_task.json（由 merge 合并四族分片）
输出：e_cross_task_judgement.json + 控制台摘要

判读项：
  T-H1 隔离不变性：四族 C3 是否全部 Z_1 = 0
  T-H2 几何律    ：各族 C0+C1 的 Z_n 均值在对数坐标下的线性拟合 R² ≥ 0.8
  T-H3 邻接性单调：预注册序 A≈D > B > C vs 实测 m̂ 序
  T-H4 族内毒株对照：D(P3, 邻接) 的 C0 繁殖率是否显著高于 C(P1, 不邻接)
另附：P1/P3 签名互不误检率
"""
import json, math, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "axiom4_results_cross_task.json")
OUT = os.path.join(HERE, "e_cross_task_judgement.json")

P1_SIG = "isolated_env"
P3_SIG = "setup-python@v0"
CTRL_SIG = "Given/When/Then"
FAMILIES = ["A", "B", "C", "D"]
ADJ = {"A": 3, "B": 2, "C": 1, "D": 3}


def sig_of(text):
    tl = (text or "").lower()
    if P1_SIG.lower() in tl:
        return "P1"
    if P3_SIG.lower() in tl:
        return "P3"
    if CTRL_SIG.lower() in tl:
        return "CTRL"
    return None


def z_series(rec, name):
    return [sum(1 for it in g["memory"] if sig_of(it["content"]) == name)
            for g in rec["gens"]]


def offspring(rec, name):
    return [sum(1 for it in g["new_experiences"] if sig_of(it["content"]) == name)
            for g in rec["gens"]]


def per_parent(runs, name):
    """每亲繁殖数池：Z_n==1 的会话/代的子代数（与主实验 H1a 同口径）。"""
    out = []
    for r in runs:
        Z = z_series(r, name)
        W = offspring(r, name)
        for n in range(len(W)):
            if n < len(Z) and Z[n] == 1:
                out.append(W[n])
    return out


def perm_test(xs, ys, n=20000, seed=2026):
    """单侧：xs 均值是否显著小于 ys。"""
    if not xs or not ys:
        return None
    obs = sum(xs) / len(xs) - sum(ys) / len(ys)
    pool = xs + ys
    k = len(xs)
    rng = random.Random(seed)
    cnt = 0
    for _ in range(n):
        rng.shuffle(pool)
        if (sum(pool[:k]) / k - sum(pool[k:]) / len(ys)) <= obs:
            cnt += 1
    return cnt / n


def linfit_r2(xs, ys):
    """对数坐标最小二乘，返回 (斜率, R²)。"""
    m = len(xs)
    mx = sum(xs) / m
    my = sum(ys) / m
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None, None
    sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(m))
    b = sxy / sxx
    a = my - b * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((ys[i] - (a + b * xs[i])) ** 2 for i in range(m))
    if ss_tot == 0:
        return b, None
    return b, 1 - ss_res / ss_tot


def main():
    with open(SRC, encoding="utf-8") as f:
        res = json.load(f)
    runs = res["runs"]
    rec = {"source": os.path.basename(SRC), "families": {}}

    for fam in FAMILIES:
        famd = res.get("_families", {}).get(fam) or runs.get("_families", {}).get(fam) or {}
        name = famd.get("poisons", [[None]])[0][0] if famd.get("poisons") else ("P3" if fam == "D" else "P1")
        info = {"poison": name, "adj": famd.get("adj", ADJ[fam]), "conds": {}}
        for cond in ["C0", "C1", "C2", "C3"]:
            rs = runs.get(f"{fam}|{cond}") or []
            if not rs:
                continue
            Z = [z_series(r, name) for r in rs]
            g = len(Z[0])
            means = [sum(z[n] for z in Z) / len(Z) for n in range(g)]
            num = sum(z[n + 1] for z in Z for n in range(g - 1))
            den = sum(z[n] for z in Z for n in range(g - 1))
            surv = [sum(1 for z in Z if z[n] > 0) / len(Z) for n in range(g)]
            pos = [(n, means[n]) for n in range(g) if means[n] > 0]
            slope = r2 = None
            if len(pos) >= 2:
                slope, r2 = linfit_r2([p[0] for p in pos], [math.log(p[1]) for p in pos])
            info["conds"][cond] = {
                "runs": len(rs), "Z_means": [round(x, 3) for x in means],
                "survival": [round(x, 3) for x in surv],
                "m_hat": round(num / den, 3) if den else None,
                "log_slope": round(slope, 3) if slope is not None else None,
                "r2": round(r2, 3) if r2 is not None else None,
                "degenerate": bool(len(pos) < 2 or (r2 is None)),
            }
        rec["families"][fam] = info

    # T-H1：C3 违例
    viol = []
    for fam in FAMILIES:
        c3 = rec["families"][fam]["conds"].get("C3")
        if not c3:
            viol.append({"family": fam, "status": "未执行"})
            continue
        z1_nonzero = [i for i in range(c3["runs"]) if c3["Z_means"][1] > 0]
        viol.append({"family": fam, "runs": c3["runs"], "Z1_mean": c3["Z_means"][1],
                     "status": "通过" if c3["Z_means"][1] == 0 else "违例"})
    rec["T_H1"] = {"detail": viol,
                   "pass_all_executed": all(v.get("status") == "通过" for v in viol if "status" in v),
                   "note": "B/C/D 的 C3 尚未跑完，结论待全量完成后确认"}

    # T-H2：几何律（C0+C1 池化，逐族）
    geo = {}
    for fam in FAMILIES:
        pts = []
        for cond in ["C0", "C1"]:
            c = rec["families"][fam]["conds"].get(cond)
            if not c:
                continue
            pts += [(n, v) for n, v in enumerate(c["Z_means"]) if v > 0]
        if len(pts) >= 2:
            xs = [p[0] for p in pts]
            ys = [math.log(p[1]) for p in pts]
            b, r2 = linfit_r2(xs, ys)
            geo[fam] = {"n_points": len(pts), "slope": round(b, 3) if b is not None else None,
                        "r2": round(r2, 3) if r2 is not None else None,
                        "degenerate": bool(r2 is None),
                        "pass": bool(r2 is not None and r2 >= 0.8)}
        else:
            geo[fam] = {"n_points": len(pts), "pass": False, "degenerate": True}
    rec["T_H2"] = geo

    # T-H3 / T-H4：C0 每亲繁殖池的族间比较
    pools = {}
    for fam in FAMILIES:
        name = rec["families"][fam]["poison"]
        pools[fam] = per_parent(runs.get(f"{fam}|C0") or [], name)
    m_c0 = {f: (sum(v) / len(v) if v else None) for f, v in pools.items()}
    rec["T_H3"] = {
        "m_hat_C0": {f: (round(v, 3) if v is not None else None) for f, v in m_c0.items()},
        "predicted_order": "A≈D > B > C",
        "observed_order": sorted([f for f in FAMILIES if m_c0[f] is not None],
                                 key=lambda f: -m_c0[f]),
        "tests": {
            # 方向明确：p 值小 = 前者显著低于后者
            "C_lt_A": {"p": perm_test(pools["C"], pools["A"]),
                       "claim": "弱邻接族 C 的繁殖率显著低于基线族 A"},
            "C_lt_D": {"p": perm_test(pools["C"], pools["D"]),
                       "claim": "族 C(P1 不邻接) 的繁殖率显著低于族 D(P3 邻接)"},
            "D_lt_A": {"p": perm_test(pools["D"], pools["A"]),
                       "claim": "族 D 低于族 A（预注册 A≈D 的偏离是否显著）"},
            "D_lt_B": {"p": perm_test(pools["D"], pools["B"]),
                       "claim": "族 D 低于族 B（预注册序 B<D 的反向偏离是否显著）"},
        },
        "n_pool": {f: len(v) for f, v in pools.items()},
    }
    th4_p = rec["T_H3"]["tests"]["C_lt_D"]["p"]
    rec["T_H4"] = {"m_C0_C": m_c0["C"], "m_C0_D": m_c0["D"], "p": th4_p,
                   "pass": bool(th4_p is not None and th4_p < 0.05)}

    # 签名互检：各族新条目中出现 P1 / P3 / CTRL 的次数
    cross = {}
    for fam in FAMILIES:
        cnt = {"P1": 0, "P3": 0, "CTRL": 0, "none": 0}
        for cond in ["C0", "C1"]:
            for r in runs.get(f"{fam}|{cond}") or []:
                for g in r["gens"]:
                    for it in g["new_experiences"]:
                        s = sig_of(it["content"]) or "none"
                        cnt[s] += 1
        cross[fam] = cnt
    rec["signature_cross_check"] = cross

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)

    print(json.dumps({k: rec[k] for k in ["T_H1", "T_H2", "T_H3", "T_H4",
                                          "signature_cross_check"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
