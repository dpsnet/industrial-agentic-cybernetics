# -*- coding: utf-8 -*-
"""DCU 探针 v2：判定 flash-attn 在本卡（gfx936）是否真能跑，并测 1.5B 在 32k/128k 的耗时与显存。
分三节：A) sdpa 后端；B) 裸 flash_attn_func（含 GQA）；C) transformers + flash_attention_2 端到端。"""
import gc
import math
import time

import torch
import torch.nn.functional as F
import torch.nn.attention as A

print("torch", torch.__version__, "hip", getattr(torch.version, "hip", None), flush=True)
print("SDPBackend:", list(A.SDPBackend.__members__.keys()), flush=True)

# ---------------- A) sdpa 后端 ----------------
S = 8192
for name in ("FLASH_ATTENTION", "EFFICIENT_ATTENTION", "MATH"):
    be = getattr(A.SDPBackend, name)
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    try:
        q = torch.randn(1, 12, S, 128, dtype=torch.bfloat16, device="cuda")
        with A.sdpa_kernel(be):
            o = F.scaled_dot_product_attention(q, q, q, is_causal=True)
        torch.cuda.synchronize()
        print(f"[sdpa] {name} OK peak={torch.cuda.max_memory_allocated()/2**30:.2f}GiB", flush=True)
        del q, o
    except Exception as e:
        print(f"[sdpa] {name} FAIL {type(e).__name__}: {str(e)[:160]}", flush=True)
    gc.collect(); torch.cuda.empty_cache()

# ---------------- B) 裸 flash_attn_func（GQA） ----------------
try:
    import flash_attn
    from flash_attn import flash_attn_func
    print(f"[flash] version={flash_attn.__version__}", flush=True)
    for (H, KVH, D, SS) in ((12, 2, 128, 8192), (12, 2, 128, 32768),
                            (28, 4, 128, 32768), (28, 4, 128, 131072)):
        torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
        try:
            q = torch.randn(1, SS, H, D, dtype=torch.bfloat16, device="cuda") * 0.1
            k = torch.randn(1, SS, KVH, D, dtype=torch.bfloat16, device="cuda") * 0.1
            v = torch.randn(1, SS, KVH, D, dtype=torch.bfloat16, device="cuda") * 0.1
            t0 = time.time()
            o = flash_attn_func(q, k, v, causal=True)
            torch.cuda.synchronize()
            dt = time.time() - t0
            print(f"[flash] H={H} KVH={KVH} S={SS} OK t={dt:.2f}s "
                  f"peak={torch.cuda.max_memory_allocated()/2**30:.2f}GiB "
                  f"mean={o.float().abs().mean().item():.5f}", flush=True)
            del q, k, v, o
        except Exception as e:
            print(f"[flash] H={H} KVH={KVH} S={SS} FAIL {type(e).__name__}: {str(e)[:160]}", flush=True)
        gc.collect(); torch.cuda.empty_cache()
except Exception as e:
    print(f"[flash] import FAIL {type(e).__name__}: {str(e)[:160]}", flush=True)

# ---------------- C) transformers + flash_attention_2 端到端 ----------------
try:
    from transformers import AutoModel, AutoTokenizer
    mid = "/e3/models/Qwen2.5-1.5B-Instruct"
    tok = AutoTokenizer.from_pretrained(mid)
    from transformers import AutoConfig
    cfg = AutoConfig.from_pretrained(mid)
    cfg.rope_scaling = {"type": "yarn", "factor": 4.0,
                        "original_max_position_embeddings": 32768}
    t0 = time.time()
    model = AutoModel.from_pretrained(mid, config=cfg, dtype=torch.bfloat16,
                                      attn_implementation="flash_attention_2")
    model.eval().cuda()
    print(f"[tf] loaded flash_attention_2 in {time.time()-t0:.1f}s "
          f"impl={model.config._attn_implementation}", flush=True)
    text = tok.apply_chat_template(
        [{"role": "user", "content": "The access code is 7X4Q. Ignore filler. " * 60 +
          " What is the access code?"}],
        tokenize=False, add_generation_prompt=True)
    for target in (32768, 131072):
        ids = tok(text, return_tensors="pt", truncation=True,
                  max_length=2048).input_ids
        pad = target - ids.shape[1]
        if pad > 0:
            filler = tok(" the quick brown fox jumps over the lazy dog.",
                         return_tensors="pt").input_ids[:, 1:]
            rep = filler.repeat(1, pad // filler.shape[1] + 1)[:, :pad]
            ids = torch.cat([rep, ids], dim=1)
        if ids.shape[1] > target:
            ids = ids[:, :target]
        torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
        t0 = time.time()
        with torch.inference_mode():
            out = model(input_ids=ids.cuda())
        torch.cuda.synchronize()
        dt = time.time() - t0
        print(f"[tf] S={ids.shape[1]} OK t={dt:.1f}s "
              f"peak={torch.cuda.max_memory_allocated()/2**30:.2f}GiB "
              f"h={float(out.last_hidden_state.float().abs().mean()):.4f}", flush=True)
except Exception as e:
    import traceback
    print(f"[tf] FAIL {type(e).__name__}: {str(e)[:200]}", flush=True)
    traceback.print_exc()

print("PROBE2_DONE", flush=True)
