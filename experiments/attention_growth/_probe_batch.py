"""探针校准协议执行：8 个探针批次（独立 API 会话、串行 + 60s 间隔）。
每个探针 = 1 条链 C0-full W=16 6 代 scnet-flash，测毒株转写率 p_probe。
"""
import json, subprocess, sys, time, os

HERE = r"E:\workspace\industrial-agentic-cybernetics\experiments\attention_growth"
PY = r"D:\pyenv\pyenv-win\versions\3.11.8\python.exe"
SCRIPT = os.path.join(HERE, "axiom4_memory_propagation.py")
N_PROBES = 8
GAP_S = 60

names = ["P1", "P2", "P3"]
probe_summary = []

for i in range(1, N_PROBES + 1):
    out = os.path.join(HERE, f"probe_{i:02d}.json")
    if os.path.exists(out):
        os.remove(out)
    cmd = [PY, SCRIPT, "main", "--provider=scnet-flash", "--conds=C0",
           "--architecture=full_append", "--window=16", "--gens=6",
           "--reps=1", f"--out={out}"]
    print(f"[probe {i}/{N_PROBES}] start {time.strftime('%H:%M:%S')}", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    # 结果可能写默认文件：检查 out 是否存在，无则查默认名
    if not os.path.exists(out):
        for f in os.listdir(HERE):
            if f.endswith(".json") and "probe" not in f and "axiom4_results" in f:
                cand = os.path.join(HERE, f)
                if os.path.getmtime(cand) > time.time() - 60:
                    out = cand
    if not os.path.exists(out):
        print(f"[probe {i}] FAILED no output; rc={r.returncode} tail={r.stderr[-300:]}",
              flush=True)
        probe_summary.append({"probe": i, "pw": None, "error": r.stderr[-300:]})
    else:
        d = json.load(open(out, encoding="utf-8"))
        run = d["runs"]["C0"][0]
        pw = sum(sum(1 for it in g["new_experiences"] if it.get("lineage") in names)
                 for g in run["gens"])
        print(f"[probe {i}] pw={pw}/6  p_probe={pw/6:.3f}  file={os.path.basename(out)}",
              flush=True)
        probe_summary.append({"probe": i, "pw": pw, "p_probe": pw / 6,
                              "time": time.strftime("%Y-%m-%d %H:%M:%S")})
    if i < N_PROBES:
        time.sleep(GAP_S)

with open(os.path.join(HERE, "_probe_summary.json"), "w", encoding="utf-8") as f:
    json.dump(probe_summary, f, ensure_ascii=False, indent=1)
print("=== DONE: %d probes ===" % len(probe_summary), flush=True)
