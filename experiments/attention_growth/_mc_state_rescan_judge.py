"""探针门控重扫判读（KIMI 四轮作业 2）：高转写态下 W∈{4,8,12} 各 12 链。
判据（预注册 §1.2e，写死）：高转写态下 W=8 存活率 >=0.5 ⟹ M_c 改述为状态条件量。
存活率 = 末代 memory 中 lineage∈{P1,P2,P3} 条目数 >0 的链比例（与 _w8_repro_judge.py 同口径）。
"""
import json, os, glob, re

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ("P1", "P2", "P3")

rows = {}
for W in (4, 8, 12):
    rows[W] = {"n": 0, "surv": 0, "pw_total": 0, "zf_total": 0}

for fp in sorted(glob.glob(os.path.join(HERE, "_mc_state_rescan_W*_s*.json"))):
    m = re.search(r"_W(\d+)_s\d+\.json$", os.path.basename(fp))
    if not m:
        continue
    W = int(m.group(1))
    d = json.load(open(fp, encoding="utf-8"))
    for run in d["runs"]["C0"]:
        pw = sum(sum(1 for it in g["new_experiences"] if it.get("lineage") in NAMES)
                 for g in run["gens"])
        zf = sum(1 for it in run["gens"][-1]["memory"] if it.get("lineage") in NAMES)
        rows[W]["n"] += 1
        if zf > 0:
            rows[W]["surv"] += 1
        rows[W]["pw_total"] += pw
        rows[W]["zf_total"] += zf

lines = ["=== 探针门控重扫判读（高转写态 2026-10-23 19:0x 窗口，探针 2/2 p=1.000） ==="]
for W in (4, 8, 12):
    r = rows[W]
    lines.append(f"  W={W}: n={r['n']} surv={r['surv']}/{r['n']} ({r['surv']/r['n']:.3f}) "
                 f"pw/chain={r['pw_total']/r['n']:.2f} zf_mean={r['zf_total']/r['n']:.2f}")
w8 = rows[8]
hit = w8["surv"] / w8["n"] >= 0.5
lines.append(f"=== 判据：高转写态下 W=8 存活率 {w8['surv']/w8['n']:.3f} >= 0.5 ? {hit} "
             f"=> M_c 改述为 (b, M, 毒株转写状态) 条件量（高态 M_c in (4,8) vs 低态 (8,16)） ===")
lines.append("数据文件：_mc_state_rescan_W{4,8,12}_{s1,s2}.json（36 链）")

with open(os.path.join(HERE, "_mc_state_rescan_judge.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
