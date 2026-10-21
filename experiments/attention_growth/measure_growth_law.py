# -*- coding: utf-8 -*-
"""
经验验证：无关上下文注意力质量 b(rho) 的增长律实测
====================================================

对应专著《Industrial Agentic Cybernetics》公理 II 的形式化前提
（formal_proof/IACFormalization/src/IACFormalization/Axiom2_AttentionDilution.lean）：

  AttentionMechanism 结构：
    a(rho)   : 目标 token 的注意力质量
    b(rho)   : 全部无关 token 的注意力总质量
    snr(rho) := a(rho) / b(rho)
  结构前提（本实验待验证的经验命题）：
    b(rho+1) >= (1+gamma) * b(rho)   （几何膨胀）
  定理结论（若前提成立）：
    snr(rho+1) <= (1/(1+gamma)) * snr(rho)

实验操作化：
  - 模型：GPT-2 小模型（output_attentions=True 可取得逐层逐头注意力权重）
  - 目标（needle）：一句含特定事实的句子，位置固定
  - 无关上下文：中性填充句，按 rho 递增注入
  - 查询位：末尾提问句的最后若干位置
  - a(rho)：查询位对 needle token 的注意力质量（层×头平均）
  - b(rho)：查询位对无关 token 的注意力总质量（层×头平均）
  - 判别：
      几何律  log b ~ rho 线性（斜率 log(1+gamma)）
      线性律  b ~ rho 线性
    以 R^2 比较；并检验理论关系  snr 衰减率 c ?= 1/(1+gamma)
"""

import json
import math
import os
import sys

import numpy as np
import torch
from transformers import GPT2LMHeadModel, GPT2TokenizerFast

MODEL_NAME = os.environ.get("IAC_MODEL", "gpt2")
DEVICE = "cpu"

NEEDLE_TEMPLATES = [
    "The secret access code is {code}.",
    "The hidden password is {code}.",
    "The confidential PIN number is {code}.",
]
CODES = ["7391", "4820", "9156"]

FILLER = (
    "The weather that afternoon was mild and unremarkable. "
    "A few pedestrians crossed the quiet street near the old library. "
    "Nobody seemed to be in a hurry, and the shops were half empty. "
)

QUESTION = " Question: What is the secret access code? Answer:"

RHO_LEVELS = [0, 25, 50, 100, 150, 200, 300, 400, 500, 600, 700, 800]


def build_prompt(tokenizer, needle: str, n_filler_tokens: int) -> str:
    """构造提示：needle 固定在前部，随后注入约 n_filler_tokens 个无关 token。"""
    filler_ids = tokenizer.encode(FILLER)
    reps = max(0, math.ceil(n_filler_tokens / max(1, len(filler_ids))))
    filler_text = tokenizer.decode((filler_ids * reps)[:n_filler_tokens]) if n_filler_tokens > 0 else ""
    return needle + " " + filler_text + QUESTION


def measure_once(model, tokenizer, prompt: str, needle: str):
    """单次前向：返回 (a, b)——查询位对 needle / 无关 token 的层头平均注意力质量。"""
    enc = tokenizer(prompt, return_tensors="pt")
    ids = enc["input_ids"][0]
    with torch.no_grad():
        out = model(**enc, output_attentions=True)

    needle_ids = tokenizer.encode(needle)
    n_needle = len(needle_ids)
    q_text = QUESTION
    q_ids = tokenizer.encode(q_text)
    n_q = len(q_ids)
    seq = ids.shape[0]
    q_pos = list(range(seq - n_q, seq))
    filler_pos = list(range(n_needle + 1, seq - n_q))

    a_layers, b_layers = [], []
    for attn in out.attentions:  # [1, heads, seq, seq]
        w = attn[0].mean(dim=0)  # 头平均 -> [seq, seq]
        wq = w[q_pos, :].mean(dim=0)  # 查询位平均 -> [seq]
        a_layers.append(wq[: n_needle + 1].sum().item())  # +1: needle 后的空格并入目标区
        b_layers.append(wq[filler_pos].sum().item() if filler_pos else 0.0)
    return float(np.mean(a_layers)), float(np.mean(b_layers))


def fit(x, y):
    """一元最小二乘 y = k x + c，返回 (k, c, R^2)。"""
    x = np.asarray(x, float); y = np.asarray(y, float)
    k, c = np.polyfit(x, y, 1)
    ss_res = float(np.sum((y - (k * x + c)) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return k, c, r2


def main():
    print(f"[load] {MODEL_NAME} on {DEVICE}", flush=True)
    tok = GPT2TokenizerFast.from_pretrained(MODEL_NAME)
    model = GPT2LMHeadModel.from_pretrained(MODEL_NAME).to(DEVICE).eval()

    rows = []
    for tpl, code in zip(NEEDLE_TEMPLATES, CODES):
        needle = tpl.format(code=code)
        for rho in RHO_LEVELS:
            prompt = build_prompt(tok, needle, rho)
            n_tok = len(tok.encode(prompt))
            if n_tok > 1000:  # gpt2 上下文 1024，留余量
                continue
            a, b = measure_once(model, tok, prompt, needle)
            rows.append({"needle": needle, "rho": rho, "n_tokens": n_tok,
                         "a": a, "b": b, "snr": a / b if b > 0 else None})
            print(f"  rho={rho:4d} tok={n_tok:4d} a={a:.4f} b={b:.4f} snr={a/b if b>0 else float('nan'):.4f}",
                  flush=True)

    # 聚合：同一 rho 下对 needle 取平均
    agg = {}
    for r in rows:
        agg.setdefault(r["rho"], []).append(r)
    rhos = sorted(agg)
    a_m = [float(np.mean([r["a"] for r in agg[p]])) for p in rhos]
    b_m = [float(np.mean([r["b"] for r in agg[p]])) for p in rhos]
    snr_m = [a / b if b > 0 else float("nan") for a, b in zip(a_m, b_m)]

    # 增长律判别（仅 rho>0 的点，b 才有定义意义）
    idx = [i for i, p in enumerate(rhos) if p > 0 and b_m[i] > 0]
    x = [rhos[i] for i in idx]
    bvals = [b_m[i] for i in idx]
    logb = [math.log(v) for v in bvals]
    snr_vals = [snr_m[i] for i in idx if snr_m[i] and snr_m[i] > 0]
    logsnr = [math.log(v) for v in snr_vals]

    kg, cg, r2g = fit(x, logb)          # 几何律: log b = log(1+g) rho + c
    kl, cl, r2l = fit(x, bvals)         # 线性律: b = k rho + c
    xs = [rhos[i] for i in idx if snr_m[i] and snr_m[i] > 0]
    ks, cs, r2s = fit(xs, logsnr)       # snr 衰减: log snr = log(c) rho + c

    gamma_hat = math.exp(kg) - 1.0
    c_hat = math.exp(ks)
    c_theory = 1.0 / (1.0 + gamma_hat)

    report = {
        "model": MODEL_NAME,
        "rows": rows,
        "rho": rhos, "a_mean": a_m, "b_mean": b_m, "snr_mean": snr_m,
        "geometric_fit": {"log1p_gamma": kg, "r2": r2g, "gamma_hat": gamma_hat},
        "linear_fit": {"slope": kl, "r2": r2l},
        "snr_decay_fit": {"log_c": ks, "r2": r2s, "c_hat": c_hat},
        "theory_relation": {"c_measured": c_hat, "c_theory_from_gamma": c_theory},
    }
    out_path = os.path.join(os.path.dirname(__file__), "results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n===== 增长律判别 =====")
    print(f"几何律 log b ~ rho : slope={kg:.6f}  R^2={r2g:.4f}  -> gamma_hat={gamma_hat:.6f}")
    print(f"线性律 b ~ rho     : slope={kl:.6f}  R^2={r2l:.4f}")
    print(f"===== SNR 衰减 =====")
    print(f"log snr ~ rho      : slope={ks:.6f}  R^2={r2s:.4f}  -> c_hat={c_hat:.6f}")
    print(f"理论关系检验        : c_theory = 1/(1+gamma_hat) = {c_theory:.6f}")
    print(f"[saved] {out_path}")


if __name__ == "__main__":
    sys.exit(main())
