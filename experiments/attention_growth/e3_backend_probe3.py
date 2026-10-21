# -*- coding: utf-8 -*-
"""探针 v3：flash_attention_2 端到端可行性 + 耗时/显存（1.5B 与 7B，32k 与 128k）。

目的：确认 transformers 5.3 + flash_attn 2.6.1 在本卡（gfx936）上可加载并可跑长上下文，
并给出单次前向耗时——这是 50 卡时预算下矩阵规模决策的直接输入。
"""
import time

import torch
from transformers import AutoConfig, AutoModel, AutoTokenizer

MODELS = [("/e3/models/Qwen2.5-1.5B-Instruct", (32768, 131072)),
          ("/e3/models/Qwen2.5-7B-Instruct", (32768, 131072))]
NEEDLE = "Important: the access code is 7X4Q."
FILLER = " The quarterly logistics report mentions routine maintenance schedules."


def build(tok, target):
    head = tok(NEEDLE + FILLER, return_tensors="pt").input_ids
    tail = tok(" Question: what is the access code?", return_tensors="pt",
               return_attention_mask=False).input_ids
    body_n = target - head.shape[1] - tail.shape[1]
    fill = tok(FILLER, return_tensors="pt", return_attention_mask=False).input_ids[:, 1:]
    rep = fill.repeat(1, body_n // fill.shape[1] + 2)[:, :body_n]
    ids = torch.cat([head, rep, tail], dim=1)
    return ids


def yarn(cfg, factor, orig):
    rp = dict(getattr(cfg, "rope_parameters", None) or {})
    rp.update({"rope_type": "yarn", "factor": float(factor),
               "original_max_position_embeddings": int(orig)})
    cfg.rope_parameters = rp
    cfg.rope_scaling = {"type": "yarn", "factor": float(factor),
                        "original_max_position_embeddings": int(orig)}
    return cfg


for mid, ctxs in MODELS:
    name = mid.split("/")[-1]
    tok = AutoTokenizer.from_pretrained(mid)
    orig = 32768
    for target in ctxs:
        kwargs = {}
        if target > orig:
            cfg = AutoConfig.from_pretrained(mid)
            cfg = yarn(cfg, 4.0, orig)
            kwargs["config"] = cfg
        torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
        t0 = time.time()
        try:
            model = AutoModel.from_pretrained(
                mid, dtype=torch.bfloat16, attn_implementation="flash_attention_2",
                low_cpu_mem_usage=True, **kwargs)
            model.eval()
            if next(model.parameters()).device.type != "cuda":
                model = model.cuda()
            t_load = time.time() - t0
        except Exception as e:
            print(f"[{name} S={target}] LOAD FAIL {type(e).__name__}: {str(e)[:200]}", flush=True)
            continue
        ids = build(tok, target)
        torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
        t0 = time.time()
        try:
            with torch.inference_mode():
                out = model(input_ids=ids.cuda())
            torch.cuda.synchronize()
            dt = time.time() - t0
            peak = torch.cuda.max_memory_allocated() / 2**30
            h = out.last_hidden_state
            print(f"[{name} S={ids.shape[1]}] OK load={t_load:.0f}s fwd={dt:.1f}s "
                  f"peak={peak:.2f}GiB h_mean={float(h.float().abs().mean()):.4f} "
                  f"h_last={float(h[0, -1].float().abs().mean()):.4f}", flush=True)
        except Exception as e:
            print(f"[{name} S={target}] FWD FAIL {type(e).__name__}: {str(e)[:200]}", flush=True)
        del model
        import gc; gc.collect(); torch.cuda.empty_cache()

print("PROBE3_DONE", flush=True)
