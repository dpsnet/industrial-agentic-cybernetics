# -*- coding: utf-8 -*-
"""探针 v4：定位 transformers 5.3 中 YaRN 外推的正确配置方式，并实测 128k 前向耗时。

背景：probe3 中设 cfg.rope_parameters / cfg.rope_scaling 后仍在
Qwen2RotaryEmbedding.__init__ 报 KeyError: 'rope_type'，说明赋值路径被框架改写。
本探针逐变体打印 cfg 内部状态并试加载，找出可行写法。
"""
import time

import torch
from transformers import AutoConfig, AutoModel, AutoTokenizer

MID = "/e3/models/Qwen2.5-1.5B-Instruct"
YARN = {"rope_type": "yarn", "factor": 4.0, "original_max_position_embeddings": 32768}


def show(tag, cfg):
    rp = getattr(cfg, "rope_parameters", "<absent>")
    rs = getattr(cfg, "rope_scaling", "<absent>")
    print(f"[cfg {tag}] rope_parameters={rp!r} rope_scaling={rs!r}", flush=True)


base = AutoConfig.from_pretrained(MID)
show("default", base)

variants = {}
c1 = AutoConfig.from_pretrained(MID)
c1.rope_parameters = dict(YARN)
variants["V1 flat_only"] = c1

c2 = AutoConfig.from_pretrained(MID)
rp = dict(getattr(c2, "rope_parameters", None) or {})
rp.update(YARN)
c2.rope_parameters = rp
variants["V2 copy_update"] = c2

c3 = AutoConfig.from_pretrained(MID)
c3.rope_scaling = {"type": "yarn", "factor": 4.0,
                   "original_max_position_embeddings": 32768}
variants["V3 rope_scaling_only"] = c3

c4 = AutoConfig.from_pretrained(MID)
rp = dict(getattr(c4, "rope_parameters", None) or {})
rp.update(YARN)
c4.rope_parameters = rp
try:
    c4.rope_scaling = None
except Exception as e:
    print("[V4] set rope_scaling=None raised", e, flush=True)
variants["V4 params_plus_none"] = c4

# V5: 直接把 YARN 作为 rope_scaling 传入 from_pretrained（不经 cfg 赋值）
c5 = AutoConfig.from_pretrained(MID)
variants["V5 pass_rope_scaling_kw"] = c5

ok_variants = []
for tag, cfg in variants.items():
    show(tag, cfg)
    try:
        from transformers import Qwen2RotaryEmbedding  # 触发读取 rope_parameters
        Qwen2RotaryEmbedding(config=cfg)
        print(f"[{tag}] RotaryEmbedding OK", flush=True)
        ok_variants.append(tag)
    except Exception as e:
        print(f"[{tag}] RotaryEmbedding FAIL {type(e).__name__}: {str(e)[:120]}", flush=True)

# 对可行变体做真实加载 + 128k 前向
tok = AutoTokenizer.from_pretrained(MID)
head = tok("Important: the access code is 7X4Q.", return_tensors="pt").input_ids
fill = tok(" The quarterly logistics report mentions routine maintenance schedules.",
           return_tensors="pt", return_attention_mask=False).input_ids[:, 1:]
for tag in ok_variants:
    cfg = variants[tag]
    try:
        model = AutoModel.from_pretrained(MID, config=cfg, dtype=torch.bfloat16,
                                          attn_implementation="flash_attention_2",
                                          low_cpu_mem_usage=True)
        model.eval().cuda()
        tail = tok(" Question: what is the access code?", return_tensors="pt",
                   return_attention_mask=False).input_ids
        target = 131072
        body = target - head.shape[1] - tail.shape[1]
        rep = fill.repeat(1, body // fill.shape[1] + 2)[:, :body]
        ids = torch.cat([head, rep, tail], dim=1).cuda()
        torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
        t0 = time.time()
        with torch.inference_mode():
            out = model(input_ids=ids)
        torch.cuda.synchronize()
        print(f"[{tag}] S={ids.shape[1]} fwd={time.time()-t0:.1f}s "
              f"peak={torch.cuda.max_memory_allocated()/2**30:.2f}GiB "
              f"h_last={float(out.last_hidden_state[0,-1].float().abs().mean()):.4f}", flush=True)
        del model
        import gc; gc.collect(); torch.cuda.empty_cache()
        break
    except Exception as e:
        print(f"[{tag}] LOAD/FWD FAIL {type(e).__name__}: {str(e)[:160]}", flush=True)

print("PROBE4_DONE", flush=True)
