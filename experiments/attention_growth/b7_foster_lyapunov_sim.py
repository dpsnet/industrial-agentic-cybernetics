"""
B.7 随机 Foster-Lyapunov 期望停时界实证验证
==============================================
定理：E[τ] <= V(x0)/δ，其中 τ 是命中 {V < b} 的停时。
验证方式：随机核仿真——满足强漂移条件时，蒙特卡洛估计 E[τ] 并与界比较。
"""
import json, random, math

SEED = 2026
random.seed(SEED)
N_TRIALS = 100000

def simulate_stopping_time(V0, delta, b, noise_std=0.0):
    """
    随机强漂移：E[V(step)] <= V - delta，但每步实际下降 = delta + N(0, noise_std)。
    噪声可为负（下降更多）或正（下降更少但期望仍 <= V - delta）。
    """
    V = float(V0)
    steps = 0
    while V >= b and steps < 10000:
        # 实际下降量：期望 delta，有噪声
        actual = delta + random.gauss(0, noise_std)
        V -= max(actual, 0.01)  # 保证至少微降
        steps += 1
    return steps

results = []
for V0 in [10, 50, 100]:
    for delta in [0.5, 1.0, 2.0]:
        for noise_std in [0.0, 0.1, 0.3]:
            taus = [simulate_stopping_time(V0, delta, b=delta, noise_std=noise_std)
                    for _ in range(N_TRIALS)]
            E_tau = sum(taus) / len(taus)
            bound = V0 / delta
            within = E_tau <= bound
            results.append({
                "V0": V0, "delta": delta, "noise_std": noise_std,
                "E_tau": round(E_tau, 2), "bound": round(bound, 2),
                "within_bound": within,
                "max_tau": max(taus), "min_tau": min(taus),
            })

all_pass = all(r["within_bound"] for r in results)

# 验证截断停时的一致有界性：对任意 N，E[τ_N] <= V0/delta
truncated_pass = True
for V0 in [50]:
    for delta in [1.0]:
        for N in [10, 50, 100, 500]:
            taus = [min(simulate_stopping_time(V0, delta, b=delta), N)
                    for _ in range(N_TRIALS)]
            E_tau_N = sum(taus) / len(taus)
            bound = V0 / delta
            if E_tau_N > bound:
                truncated_pass = False

summary = {
    "theorem": "B.7 随机 Foster-Lyapunov 期望停时界",
    "date": "2026-10-21",
    "main_bound": {
        "description": "E[τ] <= V0/δ（蒙特卡洛验证，含噪声扰动）",
        "trials_per_config": N_TRIALS,
        "configs": len(results),
        "pass": all_pass,
        "details": results,
    },
    "truncated_uniform_bound": {
        "description": "截断停时 τ_N 的期望对所有 N 一致有界",
        "pass": truncated_pass,
    },
    "verdict": "PASS" if all_pass and truncated_pass else "FAIL",
}

with open("b7_foster_lyapunov_sim.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"B.7 verdict: {summary['verdict']}")
print(f"  main bound (E[τ] <= V0/δ): {all_pass} ({len(results)} configs)")
print(f"  truncated uniform bound: {truncated_pass}")
