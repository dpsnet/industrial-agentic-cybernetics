"""毒株转写率批次漂移模型：分层 Beta-Binomial 观测模型。
链级 pw ~ Binomial(T=8, p_batch)；批次级 p_batch ~ Beta(alpha, beta)。
用 4 批 W=8 数据 MLE 估计 (alpha, beta)，给出下一批次毒株转写率的后验预测区间。
"""
import json
from math import lgamma, exp, log
from scipy.optimize import minimize
from scipy.stats import beta, betabinom

HERE = r"E:\workspace\industrial-agentic-cybernetics\experiments\attention_growth"
T = 8  # 代数


def load_pw(label, path, key):
    d = json.load(open(path, encoding="utf-8"))
    runs = d["runs"][key]
    names = ["P1", "P2", "P3"]
    out = []
    for r in runs:
        pw = sum(sum(1 for it in g["new_experiences"] if it.get("lineage") in names)
                 for g in r["gens"])
        out.append(pw)
    print("  %s n=%d mean_pw=%.2f pw=%s" % (label, len(out), sum(out) / len(out), out))
    return out


def bb_loglik(theta, data):
    """Beta-Binomial 负对数似然（数据=每条链 8 代中毒株写入次数）。"""
    a, b = theta
    if a <= 0 or b <= 0:
        return 1e18
    nll = 0.0
    for k in data:
        # log P(pw=k) = log C(T,k) + log B(a+k, b+T-k) - log B(a,b)
        nll -= (lgamma(T + 1) - lgamma(k + 1) - lgamma(T - k + 1)
                + lgamma(a + k) + lgamma(b + T - k) - lgamma(a + b + T)
                - (lgamma(a) + lgamma(b) - lgamma(a + b)))
    return nll


def main():
    batches = [
        ("MAIN 10-22 (n=6)", HERE + r"\axiom4_results_supercritical_W8.json", "A|C0"),
        ("MAIN 10-23 (n=12)", HERE + r"\axiom4_results_supercritical_W8_repro.json", "C0"),
        ("EXP-B 10-23 orig (n=12)", HERE + r"\kimi_boost_B.json", "b3|W8"),
        ("EXP-B 10-23 repro (n=12)", HERE + r"\kimi_boost_B_W8_repro.json", "b3|W8"),
    ]
    print("=== 毒株转写率批次漂移模型（Beta-Binomial，T=8）===")
    data = []
    for label, path, key in batches:
        data.extend(load_pw(label, path, key))

    # MLE（矩估计起步：p^=mean/T; var 匹配）
    n = len(data)
    mean_p = sum(data) / (n * T)
    var_p = sum((k - mean_p * T) ** 2 for k in data) / n / (T * T)
    # Beta 矩估计
    a0 = mean_p * (mean_p * (1 - mean_p) / var_p - 1)
    b0 = (1 - mean_p) * (mean_p * (1 - mean_p) / var_p - 1)
    a0 = max(a0, 0.05); b0 = max(b0, 0.05)
    res = minimize(bb_loglik, [a0, b0], args=(data,), method="Nelder-Mead",
                   options={"maxiter": 5000, "xatol": 1e-10, "fatol": 1e-10})
    a, b = res.x
    print("MLE: alpha=%.3f beta=%.3f (p_hat=alpha/(alpha+beta)=%.3f)" % (a, b, a / (a + b)))

    # 后验预测分布：下一批次 p_batch ~ Beta(a, b)，毒株写入率 pw ~ Beta-Binomial
    ppf_lo, ppf_hi = beta.ppf([0.025, 0.975], a, b)
    print("批次毒株转写率 p_batch 后验预测 95%% 区间: [%.3f, %.3f] (每代均值)" % (ppf_lo, ppf_hi))
    print("对应 8 代毒株写入总数预测区间: [%.1f, %.1f]" % (ppf_lo * T, ppf_hi * T))

    # W=8 存活率预测：近似 存活 = P(末代 Z>0)。给定 p_batch，链存活概率 ≈ 1 - P(8 代无转写且初始被挤出)
    # 保守近似（毒株链断裂即亡）：存活 ≈ 1 - (1-p)^T（每代至少转写 1 次）
    print("W=8 存活率近似预测区间（1-(1-p)^T）: [%.2f, %.2f]" % (
        1 - (1 - ppf_hi) ** T, 1 - (1 - ppf_lo) ** T))
    # 观测对比
    print("观测: MAIN10-22 surv 0.00, 10-23 各批 surv 0.58/0.92/0.58（漂移区间 0.00-0.92）")


if __name__ == "__main__":
    main()
