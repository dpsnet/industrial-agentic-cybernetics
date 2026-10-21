# -*- coding: utf-8 -*-
"""
E1 扩大验证脚本（v2）：无关上下文注意力质量增长律与 SNR 衰减互反关系
=====================================================================

相对 v1（measure_growth_law.py）的改造：
  1. 逐层输出：每个测量点保留逐层（头均值）a、b 序列，检验稀释是否集中于特定层；
  2. 三类填充：F1 中性自然文本 / F2 近义对抗（同模板异取值）/ F3 重复填充；
  3. needle 位置控制：10% / 50% / 90%（控制 Lost in the Middle 位置效应）；
  4. 增长律四模型判别：几何 / 线性 / 幂律 / 饱和，AIC + BIC 双重判据；
  5. bootstrap 95% CI：按 (needle, seed) 单元重抽样，给出 ĉ、γ̂ 及互反偏差的区间；
  6. 预注册证伪量：H1/H2 违反率（a 上升或 b 不增的样本比例）。

与形式化的对应见 EXPERIMENT_PLAN.md 第 1、7 节。
本脚本只做注意力层测量（H1–H5）；任务正确率（H6）在 E4 黑盒阶段处理。

用法（GPT-2 回归冒烟）：
  python measure_growth_law_v2.py --smoke
完整矩阵示例：
  python measure_growth_law_v2.py --model Qwen/Qwen2.5-1.5B-Instruct \
      --rho 0 500 1000 2000 4000 8000 16000 --reps 5 --out results_qwen15b.json
"""

import argparse
import json
import math
import os

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ---------------- 文本材料 ----------------

NEEDLE_TEMPLATES = [
    "The secret access code is {code}.",
    "The hidden password is {code}.",
    "The confidential PIN number is {code}.",
]
CODES = ["7391", "4820", "9156", "2274", "6688"]

F1_FILLER = (
    "The weather that afternoon was mild and unremarkable. "
    "A few pedestrians crossed the quiet street near the old library. "
    "Nobody seemed to be in a hurry, and the shops were half empty. "
)
F3_SENTENCE = "The committee reviewed the quarterly logistics report. "

QUESTION = " Question: What is the secret access code? Answer:"


def adversarial_sentence(rng: np.random.Generator, avoid_code: str) -> str:
    """F2 近义对抗句：与 needle 同语义模板、不同取值。"""
    templates = [
        "The access code for the storage room is {c}.",
        "The password of the backup account is {c}.",
        "The PIN written on the old notebook is {c}.",
        "The temporary door code is {c}.",
        "The test system login code is {c}.",
    ]
    while True:
        c = f"{rng.integers(0, 10000):04d}"
        if c != avoid_code:
            break
    return templates[rng.integers(0, len(templates))].format(c=c)


def filler_text(kind: str, n_tokens: int, tokenizer, rng, avoid_code: str) -> str:
    """按 token 预算生成填充文本。kind ∈ {F1, F2, F3}。"""
    if n_tokens <= 0:
        return ""
    if kind == "F1":
        base = tokenizer.encode(F1_FILLER, add_special_tokens=False)
        reps = math.ceil(n_tokens / len(base))
        ids = (base * reps)[:n_tokens]
    elif kind == "F3":
        base = tokenizer.encode(F3_SENTENCE, add_special_tokens=False)
        reps = math.ceil(n_tokens / len(base))
        ids = (base * reps)[:n_tokens]
    elif kind == "F2":
        ids: list[int] = []
        while len(ids) < n_tokens:
            ids += tokenizer.encode(" " + adversarial_sentence(rng, avoid_code),
                                    add_special_tokens=False)
        ids = ids[:n_tokens]
    else:
        raise ValueError(kind)
    return tokenizer.decode(ids)


# ---------------- 提示构造（needle 位置控制） ----------------

def build_ids(tokenizer, needle: str, n_filler: int, kind: str,
              position_frac: float, rng, avoid_code: str):
    """返回 (input_ids, needle_span, filler_positions, query_positions)。
    needle 位于填充流的 position_frac 处；查询为末尾问题。"""
    n_before = int(n_filler * position_frac)
    n_after = n_filler - n_before
    before_ids = tokenizer.encode(filler_text(kind, n_before, tokenizer, rng, avoid_code),
                                  add_special_tokens=False)
    after_ids = tokenizer.encode(filler_text(kind, n_after, tokenizer, rng, avoid_code),
                                 add_special_tokens=False)
    needle_ids = tokenizer.encode(" " + needle, add_special_tokens=False)
    q_ids = tokenizer.encode(QUESTION, add_special_tokens=False)
    ids = before_ids + needle_ids + after_ids + q_ids
    n0 = len(before_ids)
    needle_span = (n0, n0 + len(needle_ids))
    filler_pos = list(range(0, n0)) + list(range(n0 + len(needle_ids),
                                                 n0 + len(needle_ids) + len(after_ids)))
    q_pos = list(range(len(ids) - len(q_ids), len(ids)))
    return ids, needle_span, filler_pos, q_pos


# ---------------- 单次测量（逐层） ----------------

@torch.no_grad()
def measure_once(model, tokenizer, ids, needle_span, filler_pos, q_pos, max_ctx: int):
    """返回 (a_layers, b_layers)：逐层（头均值）目标/无关注意力质量。

    内存纪律（32k 级上下文的关键）：transformers 在 output_attentions=True 时会把
    每一层的 [1, H, S, S] 注意力矩阵保留在 out.attentions 元组中直至前向结束，
    28 层 × 32768² × fp32 ≈ 150GB，不可用。改为逐层 forward hook：每层算完后
    立即提取查询位行向量的两个子区间和（标量），随即释放整层矩阵。
    峰值内存 ≈ 单层矩阵（约 12–17GB，视头数而定）。"""
    if len(ids) > max_ctx:
        return None
    lo, hi = needle_span
    a_layers, b_layers = [], []

    def make_hook(a_list, b_list):
        def hook(_module, _inputs, outputs):
            attn = outputs[1] if isinstance(outputs, tuple) else outputs
            if attn is None:
                return
            w = attn[0][:, q_pos, :]          # [H, n_q, S]
            w = w.mean(dim=1)                 # [H, S] 查询位平均
            a_list.append(w[:, lo:hi].sum(dim=-1).mean().item())
            if filler_pos:
                b_list.append(w[:, filler_pos].sum(dim=-1).mean().item())
            else:
                b_list.append(float("nan"))
        return hook

    layers = _attention_layers(model)
    handles = [ly.register_forward_hook(make_hook(a_layers, b_layers)) for ly in layers]
    try:
        model(input_ids=torch.tensor([ids]))
    finally:
        for h in handles:
            h.remove()
    return a_layers, b_layers


def _attention_layers(model):
    """取出模型的注意力子模块列表（兼容 GPT2 / Llama / Qwen2 命名）。"""
    # transformers 的注意力类名通常以 'Attention' 结尾
    mods = [m for m in model.modules() if type(m).__name__.endswith("Attention")
            and hasattr(m, "forward")]
    if not mods:
        raise RuntimeError("未找到注意力子模块，模型结构不在支持列表内")
    return mods


# ---------------- 增长律模型判别 ----------------

def _lstsq_stats(y, yhat, k):
    n = len(y)
    rss = float(np.sum((y - yhat) ** 2))
    r2 = 1.0 - rss / float(np.sum((y - y.mean()) ** 2)) if n > 1 else float("nan")
    aic = n * math.log(rss / n) + 2 * k if rss > 0 else float("-inf")
    bic = n * math.log(rss / n) + k * math.log(n) if rss > 0 else float("-inf")
    return {"r2": r2, "aic": aic, "bic": bic, "rss": rss}


def fit_growth_models(rhos, bvals):
    """四类模型拟合 b(ρ)：几何 / 线性 / 幂律 / 饱和。返回各模型统计量与参数。"""
    x = np.asarray(rhos, float)
    y = np.asarray(bvals, float)
    mask = (x > 0) & np.isfinite(y) & (y > 0)
    x, y = x[mask], y[mask]
    out = {}
    if len(x) < 3:
        return out
    # 几何：log b = log(1+γ) ρ + log b0
    k, c = np.polyfit(x, np.log(y), 1)
    out["geometric"] = {"gamma": math.exp(k) - 1.0, "b0": math.exp(c),
                        **_lstsq_stats(y, np.exp(c + k * x), 2)}
    # 线性：b = k ρ + c
    k, c = np.polyfit(x, y, 1)
    out["linear"] = {"slope": k, "intercept": c, **_lstsq_stats(y, c + k * x, 2)}
    # 幂律：log b = β log ρ + log β0
    k, c = np.polyfit(np.log(x), np.log(y), 1)
    out["power"] = {"beta": k, "b0": math.exp(c),
                    **_lstsq_stats(y, np.exp(c) * x ** k, 2)}
    # 饱和：b = b_inf (1 - exp(-λρ))；λ 网格 + 对 b_inf 的最小二乘
    best = None
    for lam in np.logspace(-7, -2, 60):
        g = 1.0 - np.exp(-lam * x)
        binf = float(np.dot(y, g) / np.dot(g, g))
        if binf <= 0:
            continue
        st = _lstsq_stats(y, binf * g, 2)
        if best is None or st["rss"] < best[1]["rss"]:
            best = ((binf, lam), st)
    if best:
        (binf, lam), st = best
        out["saturating"] = {"b_inf": binf, "lambda": lam, **st}
    return out


def fit_snr_decay(rhos, snr):
    x = np.asarray(rhos, float)
    s = np.asarray(snr, float)
    mask = (x > 0) & np.isfinite(s) & (s > 0)
    if mask.sum() < 3:
        return None
    k, c = np.polyfit(x[mask], np.log(s[mask]), 1)
    return {"log_c": k, "c_hat": math.exp(k)}


# ---------------- 主流程 ----------------

def run_matrix(model_name: str, rho_levels, fillers, positions, reps: int,
               max_ctx: int, seed0: int = 0, dtype=None):
    tok = AutoTokenizer.from_pretrained(model_name)
    # 默认 fp32；CPU 长上下文建议 dtype=torch.float16 减半单层注意力矩阵内存
    if dtype is None:
        dtype = torch.float32
        if torch.cuda.is_available():
            dtype = torch.float16 if not torch.cuda.is_bf16_supported() else torch.bfloat16
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_name, attn_implementation="eager", torch_dtype=dtype)
    except TypeError:
        model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=dtype)
    # hook 模式下由 config 强制各层输出注意力矩阵，前向签名不再传 output_attentions
    model.config.output_attentions = True
    model.eval()

    rows = []
    for kind in fillers:
        for pos in positions:
            for rho in rho_levels:
                for rep in range(reps):
                    rng = np.random.default_rng(seed0 + 1000 * rep + rho)
                    needle = NEEDLE_TEMPLATES[rep % len(NEEDLE_TEMPLATES)]
                    code = CODES[rep % len(CODES)]
                    needle_txt = needle.format(code=code)
                    ids, span, fpos, qpos = build_ids(
                        tok, needle_txt, rho, kind, pos, rng, code)
                    res = measure_once(model, tok, ids, span, fpos, qpos, max_ctx)
                    if res is None:
                        continue
                    a_l, b_l = res
                    a = float(np.mean(a_l))
                    b = float(np.mean(b_l))
                    rows.append({
                        "filler": kind, "position": pos, "rho": rho, "rep": rep,
                        "n_tokens": len(ids), "a": a, "b": b,
                        "a_layers": a_l, "b_layers": b_l,
                    })
                    print(f"  [{kind} pos={pos:.1f} rho={rho} rep={rep}] "
                          f"tok={len(ids)} a={a:.4f} b={b:.4f}", flush=True)
    return rows


def aggregate(rows, fillers, positions, rho_levels):
    """按 (filler, position) 聚合成序列 + 拟合 + 违反率。"""
    results = {}
    for kind in fillers:
        for pos in positions:
            cell = [r for r in rows if r["filler"] == kind and r["position"] == pos]
            if not cell:
                continue
            rhos, a_m, b_m, snr_m = [], [], [], []
            for rho in rho_levels:
                sub = [r for r in cell if r["rho"] == rho and math.isfinite(r["b"]) and r["b"] > 0]
                if not sub:
                    continue
                rhos.append(rho)
                a_m.append(float(np.mean([r["a"] for r in sub])))
                b_m.append(float(np.mean([r["b"] for r in sub])))
                snr_m.append(float(np.mean([r["a"] / r["b"] for r in sub])))
            # H1/H2 违反率：相邻 ρ 档间 a 上升 / b 不增 的样本对比例
            h1_viol = h2_viol = pairs = 0
            for r1 in cell:
                for r2 in cell:
                    if r2["rho"] == next((x for x in rho_levels if x > r1["rho"]), None) \
                            and r1["rep"] == r2["rep"]:
                        pairs += 1
                        h1_viol += int(r2["a"] > r1["a"])
                        if math.isfinite(r1["b"]) and math.isfinite(r2["b"]):
                            h2_viol += int(r2["b"] < r1["b"])
            gm = fit_growth_models(rhos, b_m)
            sd = fit_snr_decay(rhos, snr_m)
            entry = {"rho": rhos, "a_mean": a_m, "b_mean": b_m, "snr_mean": snr_m,
                     "growth_models": gm, "snr_decay": sd,
                     "h1_violation_rate": h1_viol / pairs if pairs else None,
                     "h2_violation_rate": h2_viol / pairs if pairs else None,
                     "n_pairs": pairs}
            if sd and "geometric" in gm:
                entry["reciprocity"] = {
                    "c_hat": sd["c_hat"],
                    "c_theory": 1.0 / (1.0 + gm["geometric"]["gamma"]),
                }
            results[f"{kind}@pos{pos}"] = entry
    return results


def bootstrap_reciprocity(rows, rho_levels, B: int = 500, seed: int = 42):
    """按 rep 重抽样，给出 ĉ、γ̂、互反偏差 |ĉ - 1/(1+γ̂)| 的 95% CI（全 cell 合并）。"""
    rng = np.random.default_rng(seed)
    reps = sorted({r["rep"] for r in rows})
    diffs, cs, gammas = [], [], []
    for _ in range(B):
        sample_reps = rng.choice(reps, size=len(reps), replace=True)
        rhos, b_m, snr_m = [], [], []
        for rho in rho_levels:
            sub = [r for r in rows if r["rho"] == rho and r["rep"] in sample_reps
                   and math.isfinite(r["b"]) and r["b"] > 0]
            if not sub:
                continue
            rhos.append(rho)
            b_m.append(float(np.mean([r["b"] for r in sub])))
            snr_m.append(float(np.mean([r["a"] / r["b"] for r in sub])))
        gm = fit_growth_models(rhos, b_m)
        sd = fit_snr_decay(rhos, snr_m)
        if sd and "geometric" in gm:
            g = gm["geometric"]["gamma"]
            if g > 0:
                cs.append(sd["c_hat"])
                gammas.append(g)
                diffs.append(abs(sd["c_hat"] - 1.0 / (1.0 + g)))
    def ci(v):
        return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if v else None
    return {"B": B, "n_ok": len(diffs),
            "c_hat_ci": ci(cs), "gamma_ci": ci(gammas), "reciprocity_abs_dev_ci": ci(diffs)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.environ.get("IAC_MODEL", "gpt2"))
    ap.add_argument("--rho", type=int, nargs="+",
                    default=[0, 25, 50, 100, 200, 400, 800])
    ap.add_argument("--fillers", nargs="+", default=["F1", "F2", "F3"])
    ap.add_argument("--positions", type=float, nargs="+", default=[0.1, 0.5, 0.9])
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--max-ctx", type=int, default=1000)
    ap.add_argument("--dtype", choices=["fp32", "fp16", "bf16"], default="fp32",
                    help="CPU 长上下文建议 fp16 减半单层注意力矩阵内存")
    ap.add_argument("--bootstrap", type=int, default=500)
    ap.add_argument("--out", default=None)
    ap.add_argument("--smoke", action="store_true",
                    help="GPT-2 小矩阵回归验证（v1 兼容性检查）")
    args = ap.parse_args()

    if args.smoke:
        args.model = "gpt2"
        args.rho = [0, 50, 100, 200, 400]
        args.fillers = ["F1", "F2"]
        args.positions = [0.5]
        args.reps = 2
        args.bootstrap = 100

    print(f"[load] {args.model}", flush=True)
    dtype_map = {"fp32": torch.float32, "fp16": torch.float16, "bf16": torch.bfloat16}
    rows = run_matrix(args.model, args.rho, args.fillers, args.positions,
                      args.reps, args.max_ctx, dtype=dtype_map[args.dtype])
    agg = aggregate(rows, args.fillers, args.positions, args.rho)
    boot = bootstrap_reciprocity(rows, args.rho, B=args.bootstrap)

    report = {"model": args.model,
              "config": {"rho": args.rho, "fillers": args.fillers,
                         "positions": args.positions, "reps": args.reps},
              "cells": agg, "bootstrap": boot, "rows": rows}
    out = args.out or os.path.join(os.path.dirname(__file__),
                                   f"results_v2_{args.model.replace('/', '_')}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n===== 逐 cell 摘要 =====")
    for name, e in agg.items():
        gm = e["growth_models"]
        best = min(gm, key=lambda k: gm[k]["aic"]) if gm else None
        print(f"[{name}] best={best} "
              f"H1违反率={e['h1_violation_rate']} H2违反率={e['h2_violation_rate']}")
        if "reciprocity" in e:
            r = e["reciprocity"]
            print(f"    ĉ={r['c_hat']:.6f}  1/(1+γ̂)={r['c_theory']:.6f}")
    print("===== bootstrap 互反偏差 95% CI =====")
    print(boot["reciprocity_abs_dev_ci"])
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
