# -*- coding: utf-8 -*-
"""
E4 主线：Qwen needle-in-haystack 正确率测量
============================================
目标：测 p_correct(rho)，与 E3 的 snr(rho) 对齐，检验 W* 补偿阈值模型。

复用 E3 的 needle 模板、filler 生成器、模型加载路径，确保口径一致。
只测正确率（不重算注意力权重），因此比 E3 快得多。

用法：
  python e4_qwen_needle.py --model /e3/models/Qwen2.5-7B-Instruct \
      --rope-factor 4.0 --rho 0 2000 8000 32000 64000 131072 \
      --positions 0.5 --reps 10 --out e4_7b_yarn4.json
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure_growth_law_v2 import (
    NEEDLE_TEMPLATES, CODES, filler_text, build_ids, QUESTION,
)

from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig


def build_rope_config(model_name, rope_factor):
    """处理 transformers 4.x/5.x 的 rope_scaling 差异（复用 E3 逻辑）。"""
    cfg = AutoConfig.from_pretrained(model_name)
    orig = int(getattr(cfg, "max_position_embeddings", 32768))
    yarn = {"factor": float(rope_factor), "original_max_position_embeddings": orig}
    if getattr(cfg, "rope_parameters", None):
        rp = dict(cfg.rope_parameters)
        rp.update(yarn)
        rp["rope_type"] = "yarn"
        cfg.rope_parameters = rp
    else:
        cfg.rope_scaling = dict(yarn, type="yarn")
    print(f"[rope] YaRN factor={rope_factor} orig_max_pos={orig} → {int(orig * rope_factor)}", flush=True)
    return cfg


def generate_answer(model, tok, input_ids, max_new_tokens=20):
    """用 model.generate 取答案。"""
    input_ids = torch.tensor([input_ids], device=model.device)
    with torch.no_grad():
        out = model.generate(
            input_ids,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=None,
            pad_token_id=tok.eos_token_id,
        )
    gen = out[0][input_ids.shape[1]:]
    return tok.decode(gen, skip_special_tokens=True).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--rope-factor", type=float, default=None,
                    help="YaRN scaling factor; None = native RoPE")
    ap.add_argument("--rho", type=int, nargs="+", required=True)
    ap.add_argument("--positions", type=float, nargs="+", default=[0.5])
    ap.add_argument("--reps", type=int, default=10)
    ap.add_argument("--filler", default="F1", choices=["F1", "F2", "F3"])
    ap.add_argument("--dtype", default="bf16")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    torch.manual_seed(2026)
    rng = np.random.default_rng(2026)

    print(f"Loading {args.model} ...")
    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)

    model_kwargs = dict(
        torch_dtype=torch.bfloat16 if args.dtype == "bf16" else torch.float16,
        trust_remote_code=True,
    )
    if args.rope_factor is not None:
        model_kwargs["config"] = build_rope_config(args.model, args.rope_factor)

    # transformers 4.x: torch_dtype / 5.x: dtype
    model = None
    for dtype_key in ("torch_dtype", "dtype"):
        try:
            kw = dict(model_kwargs)
            kw[dtype_key] = kw.pop("torch_dtype")
            model = AutoModelForCausalLM.from_pretrained(args.model, **kw)
            break
        except TypeError:
            continue
    if model is None:
        raise RuntimeError("Failed to load model (transformers dtype key issue)")
    model = model.to("cuda")
    model.eval()
    print(f"  dtype={model.dtype}, device={model.device}", flush=True)

    rows = []
    for rho in args.rho:
        for pos in args.positions:
            correct_count = 0
            for rep in range(args.reps):
                needle_tpl = NEEDLE_TEMPLATES[rep % len(NEEDLE_TEMPLATES)]
                code = CODES[rep % len(CODES)]
                needle_txt = needle_tpl.format(code=code)
                ids, span, fpos, qpos = build_ids(
                    tok, needle_txt, rho, args.filler, pos, rng, code)
                t0 = time.time()
                answer = generate_answer(model, tok, ids)
                dt = time.time() - t0
                correct = code in answer
                if correct:
                    correct_count += 1
                rows.append({
                    "rho": rho, "position": pos, "rep": rep,
                    "filler": args.filler, "code": code,
                    "answer": answer[:80], "correct": correct,
                    "n_tokens": len(ids), "dt": round(dt, 2),
                })
                print(f"  rho={rho:>6} pos={pos} rep={rep:2d} "
                      f"correct={correct} answer='{answer[:40]}' "
                      f"ntok={len(ids):>6} dt={dt:.1f}s")
            acc = correct_count / args.reps
            print(f"  => rho={rho:>6} pos={pos} acc={acc:.2f}")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({
            "model": args.model,
            "rope_factor": args.rope_factor,
            "filler": args.filler,
            "reps": args.reps,
            "rows": rows,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
