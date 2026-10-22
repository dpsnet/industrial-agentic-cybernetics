# -*- coding: utf-8 -*-
"""kimi_boost 脚本冒烟：py_compile + 合成样例判读。"""
import io, os, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import py_compile
for f in ["kimi_boost.py", "kimi_boost_judge.py"]:
    py_compile.compile(os.path.join(HERE, f), doraise=True)
    print("compile OK:", f)

# 合成样例：构造三实验小数据
def mk_chain(cond, rep, gens, z_pattern, benign, gated_benign, poison_written):
    mem_lineages = ["P1" if (i % 3 == 0) else None for i in range(6)]
    glog = []
    for g in range(gens):
        memory = [{"content": ("pytestmark = pytest.mark.usefixtures(\"isolated_env\")" if ln == "P1" else "neut-%d-%d" % (rep, i)),
                   "lineage": ln, "marked": False} for i, ln in enumerate(mem_lineages)]
        ne = [{"content": "poison-%d" % g if i < poison_written else "benign-%d-%d" % (g, i),
               "lineage": "P1" if i < poison_written else None, "marked": False}
              for i in range(benign + poison_written)]
        ge = [it for it in ne if (it["lineage"] == "P1" and z_pattern[g] > 0) or (it["lineage"] is None and (g % 2 == 0))]
        # 控制良性 gated 数量
        ge = ge[: (benign if (g % 2 == 0) else 0) + (1 if z_pattern[g] > 0 else 0)]
        glog.append({"gen": g, "memory": memory, "new_experiences": ne,
                     "gated_experiences": ge, "test_code_len": 500 + g})
    return {"cond": cond, "rep": rep, "gens": glog, "architecture": "full_append", "window": 16}

A = {"meta": {"model": "test"}, "runs": {}}
for c in ["C0", "A50", "A75", "A90", "A100"]:
    A["runs"][c] = [mk_chain(c, r, 6, [1, 1, 2, 2, 2, 2], 3, 2, 1) for r in range(3)]
json.dump(A, open(os.path.join(HERE, "kimi_boost_A_smoke.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

B = {"meta": {"model": "test"}, "runs": {}}
for b in [1, 2, 3, 5]:
    for w in [4, 8, 12, 16, 24, 32]:
        z = [1, 1, 1, 1, 1, 1, 1, 0] if w <= 8 else [1, 2, 3, 4, 5, 6, 7, 8]
        B["runs"]["b%d|W%d" % (b, w)] = [mk_chain("b%d|W%d" % (b, w), r, 8, z, min(b, 3), 2, 1) for r in range(2)]
json.dump(B, open(os.path.join(HERE, "kimi_boost_B_smoke.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

C = {"meta": {"model": "test"}, "runs": {"C0sel": [mk_chain("C0sel", r, 6, [1, 1, 1, 1, 1, 1], 1, 1, 0) for r in range(3)]}}
json.dump(C, open(os.path.join(HERE, "kimi_boost_C_smoke.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

import kimi_boost_judge as J
print()
J.run_expA(os.path.join(HERE, "kimi_boost_A_smoke.json"))
print()
J.run_expB(os.path.join(HERE, "kimi_boost_B_smoke.json"))
print()
J.run_expC(os.path.join(HERE, "kimi_boost_C_smoke.json"))
print("SMOKE DONE")
