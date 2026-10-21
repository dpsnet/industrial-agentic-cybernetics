# -*- coding: utf-8 -*-
"""DCU 注意力后端探针：判定 sdpa 是否有非 math 后端，并测得分块注意力的 32k/128k 可行性与耗时。"""
import os, time, math, gc
import torch
import torch.nn.functional as F
import torch.nn.attention as A

print("torch", torch.__version__, "hip", getattr(torch.version, "hip", None), flush=True)
print("dev", torch.cuda.get_device_name(0), "cap", torch.cuda.get_device_properties(0), flush=True)

for mod in ("flash_attn", "xformers", "flash_attn_2_cuda"):
    try:
        m = __import__(mod)
        print(f"[pkg] {mod} OK {getattr(m,'__version__','?')}", flush=True)
    except Exception as e:
        print(f"[pkg] {mod} MISSING: {type(e).__name__}: {str(e)[:100]}", flush=True)

print("SDPBackend members:", [b.name for b in A.SDPBackend], flush=True)

S = 8192
q = torch.randn(1, 12, S, 128, dtype=torch.bfloat16, device="cuda")
for name in ("FLASH_ATTENTION", "EFFICIENT_ATTENTION", "CUDNN_ATTENTION", "MATH"):
    be = getattr(A.SDPBackend, name)
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    try:
        with A.sdpa_kernel(be):
            o = F.scaled_dot_product_attention(q, q, q, is_causal=True)
        torch.cuda.synchronize()
        print(f"[sdpa] {name} OK shape={tuple(o.shape)} peak={torch.cuda.max_memory_allocated()/2**30:.2f}GiB",
              flush=True)
    except Exception as e:
        print(f"[sdpa] {name} FAIL {type(e).__name__}: {str(e)[:140]}", flush=True)
del q; gc.collect(); torch.cuda.empty_cache()

# ---- 分块注意力：以 1.5B 头配置 (H=12, KVH=2, Dh=128) 测 32k / 128k 的峰值与耗时 ----
def chunked(q_, k_, v_, C=1024):
    bsz, H, S, Dh = q_.shape
    KVH = k_.shape[1]; G = H // KVH
    out = torch.empty_like(q_)
    kidx = torch.arange(S, device=q_.device)
    for s0 in range(0, S, C):
        e0 = min(s0 + C, S)
        qc = q_[:, :, s0:e0].reshape(bsz, KVH, G, e0 - s0, Dh)
        kt = k_.unsqueeze(2).transpose(-1, -2)
        sc = torch.matmul(qc, kt) / math.sqrt(Dh)
        sc = sc.reshape(bsz, H, e0 - s0, S)
        allowed = kidx[None, :] <= torch.arange(s0, e0, device=q_.device)[:, None]
        sc = sc.masked_fill(~allowed[None, None], float("-inf"))
        p = torch.softmax(sc.float(), dim=-1).to(v_.dtype).reshape(bsz, KVH, G, e0 - s0, S)
        out[:, :, s0:e0] = torch.matmul(p, v_.unsqueeze(2)).reshape(bsz, H, e0 - s0, Dh)
    return out

for S in (32768, 131072):
    H, KVH, Dh = 12, 2, 128
    try:
        q = torch.randn(1, H, S, Dh, dtype=torch.bfloat16, device="cuda")
        k = torch.randn(1, KVH, S, Dh, dtype=torch.bfloat16, device="cuda")
        v = torch.randn(1, KVH, S, Dh, dtype=torch.bfloat16, device="cuda")
        torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
        t0 = time.time(); o = chunked(q, k, v, 1024); torch.cuda.synchronize()
        dt = time.time() - t0
        print(f"[chunk] S={S} OK t={dt:.1f}s peak={torch.cuda.max_memory_allocated()/2**30:.2f}GiB "
              f"sum={o.float().abs().mean().item():.4f}", flush=True)
        del q, k, v, o; gc.collect(); torch.cuda.empty_cache()
    except Exception as e:
        print(f"[chunk] S={S} FAIL {type(e).__name__}: {str(e)[:150]}", flush=True)
        gc.collect(); torch.cuda.empty_cache()

print("PROBE_DONE", flush=True)
