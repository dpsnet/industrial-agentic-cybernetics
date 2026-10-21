# -*- coding: utf-8 -*-
"""
E3 扩大验证脚本：长上下文（32k–128k）无关注意力质量增长律与 SNR 互反关系
=========================================================================

与 v2（measure_growth_law_v2.py）的**本质区别**：
  v2 通过 forward hook 读取 `output_attentions=True` 生成的 [1,H,S,S] 全注意力矩阵，
  在 S≤4k 时可行；但在 S=128k、头数 28 时单层矩阵 ≈ 1.1 TB，任何加速卡都无法驻留。

本脚本改用**查询行重算（query-row recompute）**方案：
  1. 前向走 `attn_implementation="flash_attention_2"`（本卡实测可用：7B 头配置 @128k
     仅 2.0 GB、0.64 s），因此不物化 [1,H,S,S]，长上下文显存有界。
     —— **不能**依赖 SDPA 的自动派发：transformers 会传入 4D 因果掩码，flash 后端
     不接受显式 mask 便静默回退到 math 实现，物化 [1,H,S,S] 后 OOM
     （1.5B@32k 即 51.5 GB；作业 941735 实测复现）；
  2. flash 内核不暴露注意力分布，故在每层注意力模块的 `forward_pre_hook` 中截获
     该层输入 hidden_states 与 position_embeddings（cos, sin），按
     Qwen2Attention.forward 的数学仅重算查询位 q_pos 的 Q 行、对全位置重算 K，
     单独 softmax 得 [1,H,n_q,S] 行子矩阵，fp32 计算后立即聚合为标量 (a,b) 释放。

这样在 128k 上下文下显存峰值仅由模型权重 + 单层 hidden_states + 行子矩阵决定，
可在单张 64GB 卡（海光 DCU）上完成。

数值纪律（沿用 E2 教训）：
  - 默认在 GPU 上强制 **bf16**（fp16 在注意力行求和时会下溢产生全 NaN）；
  - 行子矩阵在 fp32 下计算 softmax，保证长程数值稳定；
  - K 重算在 fp32 下进行，代价为前向的次要项（约数分钟/128k 前向），换来与
    eager 真值 ~1e-6 的等价性（见 --validate 第一项）。

分片与合并（面向 scnet array job）：
  - `--shard-i / --shards-n`（或按 ρ 档显式切分）把矩阵拆为多个独立任务，
    分别写到 `results_e3_<tag>_shard<i>.json`；
  - `--merge <files...>` 读入各分片 JSON，合并 rows 后统一做聚合与 bootstrap，
    输出最终报告。分片按 ρ 划分，便于把 ≤32k 与 ≥64k 档分别投放 4090 / DCU。

用法（本地冒烟回归，重算 vs eager 全矩阵真值）：
  python measure_growth_law_e3.py --validate
用法（单分片完整矩阵，GPU）：
  python measure_growth_law_e3.py --model Qwen/Qwen2.5-7B-Instruct \
      --rho 0 500 1000 2000 4000 8000 16000 32000 --dtype bf16 \
      --out results_e3_qwen7b_shard0.json
合并：
  python measure_growth_law_e3.py --merge results_e3_qwen7b_shard0.json \
      results_e3_qwen7b_shard1.json --out results_e3_qwen7b.json
"""

import argparse
import glob
import json
import math
import os
import sys
import time

import numpy as np
import torch

# 复用 v2 的文本材料、提示构造与统计函数（单一事实来源，避免两份实现漂移）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from measure_growth_law_v2 import (  # noqa: E402
    NEEDLE_TEMPLATES, CODES, build_ids, aggregate, bootstrap_reciprocity,
)

try:
    from transformers import AutoModel, AutoTokenizer
except ImportError:  # pragma: no cover
    AutoModel = AutoTokenizer = None


# ---------------- 注意力行重算 ----------------

def _rotate_half(x):
    """与 transformers.models.qwen2/llama 的 rotate_half 等价（避免版本内私有导入）。"""
    x1 = x[..., : x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2:]
    return torch.cat((-x2, x1), dim=-1)


def _attn_layers(model):
    """按执行顺序返回注意力子模块（兼容 Qwen2Attention / Qwen2SdpaAttention / LlamaAttention）。"""
    mods = [m for m in model.modules()
            if type(m).__name__.endswith("Attention")
            and hasattr(m, "q_proj") and hasattr(m, "k_proj")]
    if not mods:
        raise RuntimeError("未找到带 Q/K 投影的注意力子模块；本脚本仅支持 RoPE 类架构"
                           "（Qwen2 / Llama 家族）")
    return mods


def _attn_meta(module):
    """返回 (num_heads, num_key_value_heads, head_dim)。

    transformers 5.x 起注意力子模块不再暴露 num_heads / num_key_value_heads 属性，
    故头数一律由投影层输出维度与 head_dim 反推，避免依赖版本私有字段。
    """
    q_out, k_out = module.q_proj.out_features, module.k_proj.out_features
    dh = getattr(module, "head_dim", None)
    if dh is None:
        cfg = getattr(module, "config", None)
        dh = q_out // int(getattr(cfg, "num_attention_heads", 1))
    dh = int(dh)
    return q_out // dh, k_out // dh, dh


# ---------------- 注意力行重算（在 flash_attention_2 前向之上） ----------------
#
# 前向用 `attn_implementation="flash_attention_2"`：本卡实测可用且显存有界
# （7B 头配置 @128k 仅 2.0 GB、0.64 s）。**不能**依赖 SDPA 的自动派发——transformers
# 会传入 4D 因果掩码，flash 后端不接受显式 mask 便静默回退到 math 实现，物化
# [1,H,S,S] 后 OOM（1.5B@32k 即 51.5 GB；作业 941735 已实测复现）。
# flash 内核不暴露注意力分布，故在每层注意力模块的 forward_pre_hook 中按
# Qwen2Attention.forward 的数学重算查询位 q_pos 的行分布（见 _row_attention_weights）。


def _extract_hs_pe(module, args, kwargs):
    """从 forward_pre_hook 的 args/kwargs 中取出 (hidden_states, position_embeddings)。"""
    hs = kwargs.get("hidden_states", args[0] if args else None)
    pe = kwargs.get("position_embeddings")
    if pe is None:
        # position_embeddings 也可能是位置参数（decoder layer 透传时）
        for a in args:
            if (isinstance(a, (tuple, list)) and len(a) == 2
                    and all(torch.is_tensor(t) and t.dim() == 3 for t in a)):
                pe = a
                break
    if pe is None:  # 旧路径：由模块内部 rotary_emb 现算
        pos_ids = kwargs.get("position_ids")
        if pos_ids is None:
            pos_ids = torch.arange(hs.shape[1], device=hs.device)[None, :]
        pe = module.rotary_emb(hs, pos_ids)
    return hs, pe


@torch.inference_mode()
def _row_attention_weights(module, hs, pe, q_pos):
    """仅重算查询位 q_pos 对全部 key 的注意力行，返回 [1, H, n_q, S]（fp32）。

    与 Qwen2Attention.forward 的数学严格一致：
      q = q_proj(hs[q_pos]) → 分头 → RoPE; k = k_proj(hs) → 分头 → RoPE;
      scores = q·kᵀ·scaling, 施加因果掩码（key_idx ≤ q_idx）, softmax(fp32)。
    GQA 通过把 q 分组（[KVH, G]）与 k 广播相乘实现，避免 repeat_kv 物化 K 的放大副本。
    """
    bsz, S, _ = hs.shape
    H, KVH, Dh = _attn_meta(module)
    G = H // KVH
    qpos_t = torch.as_tensor(q_pos, dtype=torch.long, device=hs.device)
    nq = qpos_t.numel()

    q = module.q_proj(hs.index_select(1, qpos_t)).reshape(bsz, nq, H, Dh).transpose(1, 2)
    k = module.k_proj(hs).reshape(bsz, S, KVH, Dh).transpose(1, 2)

    cos, sin = pe
    cos = cos.to(q.dtype)
    sin = sin.to(q.dtype)
    cos_q = cos.index_select(1, qpos_t).unsqueeze(1)   # [1,1,nq,Dh]
    sin_q = sin.index_select(1, qpos_t).unsqueeze(1)
    cos_k = cos.unsqueeze(1)                            # [1,1,S,Dh]
    sin_k = sin.unsqueeze(1)
    q = (q * cos_q + _rotate_half(q) * sin_q).float()
    k = (k * cos_k + _rotate_half(k) * sin_k).float()

    q2 = q.reshape(bsz, KVH, G, nq, Dh)                 # [1,KVH,G,nq,Dh]
    kt = k.unsqueeze(2).transpose(-1, -2)               # [1,KVH,1,Dh,S]
    # 缩放因子跨版本取法：transformers 5.x 暴露 module.scaling；4.x 无该属性，
    # 其 forward 写作 `/ math.sqrt(head_dim)`（等价于 head_dim**-0.5）。
    scaling = getattr(module, "scaling", None)
    if scaling is None:
        scaling = Dh ** -0.5
    scores = torch.matmul(q2, kt) * float(scaling)      # [1,KVH,G,nq,S]
    scores = scores.reshape(bsz, H, nq, S)

    kidx = torch.arange(S, device=hs.device)
    allowed = kidx[None, :] <= qpos_t[:, None]           # [nq,S] 因果可见性
    scores = scores.masked_fill(~allowed[None, None], float("-inf"))
    return torch.softmax(scores, dim=-1), k              # ([1,H,n_q,S], [1,KVH,S,Dh])


def _gram_streamed(k, chunk=16384):
    """KᵀK 分块累加：k [1,KVH,S,Dh] → [KVH,Dh,Dh]（float64）。
    数学上 gram = Σ_chunks (k_chunk)ᵀ·k_chunk，与一次性乘积严格一致；
    分块避免物化 [S,S] 中间张量（945254 在 131k 档 OOM 的根因，
    单次 [S,S] bf16 即 34 GB）。"""
    kd = k[0].double()                                          # [KVH,S,Dh]
    KVH, S, Dh = kd.shape
    gram = torch.zeros(KVH, Dh, Dh, dtype=torch.float64, device=kd.device)
    for s0 in range(0, S, chunk):
        kc = kd[:, s0:s0 + chunk, :]
        gram += kc.transpose(-1, -2) @ kc
    return gram


def _row_struct_metrics(w, gram_f64):
    """T8 结构量（§8.2）：在查询行分布 w 与 key 的 Gram 矩阵上计算三个候选代理量。

    返回 (entropy, top1pct, top10, erank) 四个**层内聚合标量**：
    - `entropy`：查询行注意力熵 -Σ p·log p（头×查询位均值）；`torch.xlogy` 处理 p=0；
    - `top1pct` / `top10`：softmax 行中质量最大的 ⌈S/100⌉ / 10 个位置的总质量
      （attention sink 强度；E3b 已证 sink 为动态通道）；
    - `erank`：key 有效秩 exp(-Σ p̃ᵢ log p̃ᵢ)，p̃ 为 KᵀK（Dh×Dh，恒 128×128）
      归一化特征值；KVH 头均值。gram 由 `_gram_streamed` 分块累加（float64，
      保 131k 项数值稳定，峰值显存为块大小而非全长）。
    """
    nqS = w.shape[-1]
    ent = -torch.xlogy(w, w).sum(dim=-1).mean().item()          # 头×nq 均值
    k1 = max(1, nqS // 100)
    top1pct = w.topk(k1, dim=-1).values.sum(dim=-1).mean().item()
    top10 = w.topk(min(10, nqS), dim=-1).values.sum(dim=-1).mean().item()
    ev = torch.linalg.eigvalsh(gram_f64).clamp_min(0)           # [KVH,Dh]
    p = ev / ev.sum(dim=-1, keepdim=True).clamp_min(1e-45)
    erank = torch.exp(-torch.xlogy(p, p).sum(dim=-1)).mean().item()
    return ent, top1pct, top10, erank


def measure_once_rows(model, ids, needle_span, filler_pos, q_pos, max_ctx,
                      with_struct=False):
    """查询行重算版：返回 (a_layers, b_layers, r_layers, a_heads, b_heads)；
    `with_struct=True` 时追加第 6 元 `struct`（T8 结构量逐层序列，§8.2）。

    - `a_layers` / `b_layers`：逐层（头×查询位均值）目标/无关注意力质量；
    - `r_layers`：逐层**残差通道** `r := 1 - a - b`——softmax 行的总质量为 1，
      而 `a+b` 只覆盖 needle 段与填充段，其余质量（BOS/attention sink、指令 token）
      即残差。这是 EXPERIMENT_PLAN.md §3.3「三通道分解」要求的补记量；
    - `a_heads` / `b_heads`：逐层**逐头**的 a、b（每层长度 H 的列表），
      用于 §7 接口约定的「逐头 a,b 序列」。

    用 forward_pre_hook 截获每层注意力模块的输入 hidden_states 与 position_embeddings，
    重算查询行分布。与 attention 实现无关（flash / sdpa / eager 均可）。
    """
    if len(ids) > max_ctx:
        return None
    lo, hi = needle_span
    a_layers, b_layers, r_layers, a_heads, b_heads = [], [], [], [], []
    struct = {"entropy": [], "top1pct": [], "top10": [], "erank": []}

    def make_hook():
        def hook(module, args, kwargs):
            hs, pe = _extract_hs_pe(module, args, kwargs)
            w, kmat = _row_attention_weights(module, hs, pe, q_pos)   # [1,H,nq,S]
            nH = w.shape[1]
            s_a = w[..., lo:hi].sum(dim=-1)                     # [1,H,nq]
            a_layers.append(s_a.mean().item())
            a_heads.append(s_a.mean(dim=-1)[0].tolist())        # [H]
            if filler_pos:
                s_b = w[..., filler_pos].sum(dim=-1)            # [1,H,nq]
                b_layers.append(s_b.mean().item())
                b_heads.append(s_b.mean(dim=-1)[0].tolist())
                r_layers.append(1.0 - s_a.mean().item() - s_b.mean().item())
            else:
                b_layers.append(float("nan"))
                b_heads.append([float("nan")] * nH)
                r_layers.append(float("nan"))
            if with_struct:
                ent, t1p, t10, erk = _row_struct_metrics(w, _gram_streamed(kmat))
                struct["entropy"].append(ent)
                struct["top1pct"].append(t1p)
                struct["top10"].append(t10)
                struct["erank"].append(erk)
        return hook

    handles = [ly.register_forward_pre_hook(make_hook(), with_kwargs=True)
               for ly in _attn_layers(model)]
    try:
        dev = next(model.parameters()).device
        with torch.inference_mode():
            model(input_ids=torch.tensor([ids], device=dev))
    finally:
        for h in handles:
            h.remove()
    if with_struct:
        return a_layers, b_layers, r_layers, a_heads, b_heads, struct
    return a_layers, b_layers, r_layers, a_heads, b_heads


@torch.no_grad()
def measure_once_eager(model, ids, needle_span, filler_pos, q_pos, max_ctx):
    """真值版（仅用于小 S 冒烟比对）：读 eager 全矩阵，取查询位行后聚合。

    返回与 `measure_once_rows` 同构的 5 元组 (a_layers, b_layers, r_layers,
    a_heads, b_heads)，以便冒烟检查能同时覆盖新增的残差通道与逐头序列。

    轴序更正（本轮修复）：注意力模块的 `outputs[1]` 是 [bsz, H, q, kv] 的 4 维张量。
    原实现写作 `attn[0][:, q_pos, :]`——`attn[0]` 已丢掉 batch 轴，再以 `q_pos`
    索引 dim0 实际切的是**头轴**，当 `max(q_pos) ≥ H` 时抛 IndexError
    （GPT-2 探针实测：H=12、S=120、q=117 → IndexError）。正确写法是
    `attn[:, :, q_pos, :]`（索引 query 轴），再对头取均值。"""
    if len(ids) > max_ctx:
        return None
    lo, hi = needle_span
    a_layers, b_layers, r_layers, a_heads, b_heads = [], [], [], [], []

    def make_hook():
        def hook(_module, _inputs, outputs):
            attn = outputs[1] if isinstance(outputs, tuple) else outputs
            if attn is None:
                return
            if isinstance(attn, (tuple, list)):   # 某些实现把权重再包一层
                attn = attn[-1]
            w = attn[:, :, q_pos, :].float()      # [1,H,nq,S]
            nH = w.shape[1]
            s_a = w[..., lo:hi].sum(dim=-1)       # [1,H,nq]
            a_layers.append(s_a.mean().item())
            a_heads.append(s_a.mean(dim=-1)[0].tolist())
            if filler_pos:
                s_b = w[..., filler_pos].sum(dim=-1)
                b_layers.append(s_b.mean().item())
                b_heads.append(s_b.mean(dim=-1)[0].tolist())
                r_layers.append(1.0 - s_a.mean().item() - s_b.mean().item())
            else:
                b_layers.append(float("nan"))
                b_heads.append([float("nan")] * nH)
                r_layers.append(float("nan"))
        return hook

    handles = [ly.register_forward_hook(make_hook()) for ly in _attn_layers(model)]
    try:
        dev = next(model.parameters()).device
        ids_t = torch.tensor([ids], device=dev)
        try:
            model(input_ids=ids_t, output_attentions=True)
        except TypeError:  # 旧版本仅接受 config.output_attentions
            model(input_ids=ids_t)
    finally:
        for h in handles:
            h.remove()
    return a_layers, b_layers, r_layers, a_heads, b_heads


# ---------------- 模型加载 ----------------

def load_model(model_name, dtype, attn_impl, device, rope_factor=None):
    if AutoModel is None:
        raise RuntimeError("transformers 未安装")
    cfg = None
    if rope_factor and rope_factor > 1.0:
        # Qwen2.5 / Llama 原生 max_position_embeddings=32768；ρ>32k 时若不启用 YaRN
        # 外推，位置编码超出训练范围会导致长程注意力分布退化，故必须显式开启。
        #
        # 版本差异（实测确认，见 e3_backend_probe4.py 输出）：
        #   transformers 5.x：rope_parameters 与 rope_scaling 是**同一个对象**，
        #     且读的是键 "rope_type"。若写 rope_scaling={"type":"yarn"}，会把
        #     rope_parameters 整体覆盖成只有 "type" 的字典，随后
        #     Qwen2RotaryEmbedding 读 rope_parameters["rope_type"] 直接 KeyError。
        #     故 5.x 必须只写 rope_parameters（就地更新以保留 rope_theta）。
        #   transformers 4.x：无 rope_parameters，只有 rope_scaling 且用键 "type"。
        from transformers import AutoConfig
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
        print(f"[rope] YaRN factor={rope_factor} orig_max_pos={orig} "
              f"→ {int(orig * rope_factor)}", flush=True)
    kw = {"config": cfg} if cfg is not None else {}
    # 精度参数键名随 transformers 版本而变（4.x: torch_dtype / 5.x: dtype）。
    # attn_implementation 必须被接受：若静默退回默认实现，长上下文会因物化 [1,H,S,S] 而 OOM
    # （本卡无高效 SDPA 后端），故此处不做“丢弃 attn_implementation”的回退。
    model = err = None
    for extra in ({"attn_implementation": attn_impl, "dtype": dtype},
                  {"attn_implementation": attn_impl, "torch_dtype": dtype}):
        try:
            model = AutoModel.from_pretrained(model_name, **extra, **kw)
            break
        except (TypeError, ValueError) as e:
            err = e
    if model is None:
        raise err
    got_impl = getattr(model.config, "_attn_implementation", None)
    if got_impl != attn_impl:
        raise RuntimeError(f"注意力实现未被采纳：请求 {attn_impl}，实得 {got_impl}")
    if next(model.parameters()).dtype != dtype:
        raise RuntimeError(f"精度未被采纳：请求 {dtype}，实得 {next(model.parameters()).dtype}")
    model.config.output_attentions = False   # 禁止 eager 路径物化全矩阵
    model.config.use_cache = False
    model.eval()
    model.to(device)
    return model


def resolve_dtype(name, device):
    if name != "auto":
        return {"fp32": torch.float32, "fp16": torch.float16,
                "bf16": torch.bfloat16}[name]
    if device == "cpu":
        return torch.float32
    # GPU 默认 bf16（fp16 长程会全 NaN）
    ok = torch.cuda.is_bf16_supported() if torch.cuda.is_available() else False
    return torch.bfloat16 if ok else torch.float32


# ---------------- 矩阵执行 ----------------

def run_matrix(model_name, rho_levels, fillers, positions, reps, max_ctx,
               dtype_name, attn_impl, seed0=0, device="cpu", rope_factor=None,
               with_struct=False):
    dtype = resolve_dtype(dtype_name, device)
    tok = AutoTokenizer.from_pretrained(model_name)
    model = load_model(model_name, dtype, attn_impl, device, rope_factor)
    n_layers = len(_attn_layers(model))
    print(f"[load] {model_name} layers={n_layers} dtype={dtype} "
          f"attn={attn_impl} device={device}", flush=True)

    rows = []
    for kind in fillers:
        for pos in positions:
            for rho in rho_levels:
                for rep in range(reps):
                    rng = np.random.default_rng(seed0 + 1000 * rep + rho)
                    needle = NEEDLE_TEMPLATES[rep % len(NEEDLE_TEMPLATES)]
                    code = CODES[rep % len(CODES)]
                    needle_txt = needle.format(code=code)
                    t0 = time.time()
                    ids, span, fpos, qpos = build_ids(
                        tok, needle_txt, rho, kind, pos, rng, code)
                    res = measure_once_rows(model, ids, span, fpos, qpos, max_ctx,
                                            with_struct=with_struct)
                    dt = time.time() - t0
                    if res is None:
                        print(f"  [skip] tokens={len(ids)} > max_ctx={max_ctx}", flush=True)
                        continue
                    a_l, b_l, r_l, a_h, b_h = res[:5]
                    a = float(np.mean(a_l))
                    b = float(np.mean(b_l))
                    r = float(np.mean(r_l))
                    row = {
                        "filler": kind, "position": pos, "rho": rho, "rep": rep,
                        "n_tokens": len(ids), "a": a, "b": b, "r": r,
                        "a_layers": a_l, "b_layers": b_l, "r_layers": r_l,
                        "a_heads": a_h, "b_heads": b_h,
                        "elapsed_s": round(dt, 3),
                    }
                    if with_struct:
                        st = res[5]
                        row["struct"] = st
                        row["entropy"] = float(np.mean(st["entropy"]))
                        row["top1pct"] = float(np.mean(st["top1pct"]))
                        row["top10"] = float(np.mean(st["top10"]))
                        row["erank"] = float(np.mean(st["erank"]))
                    rows.append(row)
                    print(f"  [{kind} pos={pos:.1f} rho={rho} rep={rep}] "
                          f"tok={len(ids)} a={a:.5f} b={b:.5f} r={r:.5f} t={dt:.1f}s",
                          flush=True)
    return rows


# ---------------- 冒烟回归：重算 vs eager 真值 ----------------

def validate(model_name, device="cpu", rope_factor=None):
    """冒烟校验：分两项，各自对应一条会出错的假设。

    (1) **重算数学等价**（fp32，小 S）：真值取注意力模块自身算出的全矩阵（eager），
        测试取 pre-hook 重算行。两者在同一模型上同时采集，故差异只可能来自重算公式。
        除 a、b 外，同时比对**残差通道 r** 与**逐头序列**（E3b 新增量）；
    (2) **flash 前向一致性**（bf16，GPU）：生产路径用的是 flash 内核，它不产出注意力
        矩阵，故只能间接校验——在 bf16 下分别用 eager 模型（真值路径）与 flash 模型
        （生产路径）测同一输入的同一条 query 行，比较 (a,b)。若 flash 前向有误，
        hidden_states 会偏离，重算值随之偏离，此项即失败。
    """
    tok = AutoTokenizer.from_pretrained(model_name)
    cases = [("F1", 0.5, 200), ("F2", 0.1, 200), ("F3", 0.9, 300)]
    worst_math = 0.0
    worst_head = 0.0

    # ---- (1) 重算数学等价 ----
    m32 = load_model(model_name, torch.float32, "eager", device, rope_factor)
    m32.config.output_attentions = True
    for kind, pos, rho in cases:
        rng = np.random.default_rng(7 + rho)
        needle, code = NEEDLE_TEMPLATES[0], CODES[0]
        ids, span, fpos, qpos = build_ids(tok, needle.format(code=code), rho, kind,
                                          pos, rng, code)
        got = measure_once_eager(m32, ids, span, fpos, qpos, 10 ** 6)
        rec = measure_once_rows(m32, ids, span, fpos, qpos, 10 ** 6)
        if got is None or rec is None:
            print(f"[validate-M {kind} pos={pos} rho={rho}] 未采样，跳过", flush=True)
            continue
        da = max(abs(x - y) for x, y in zip(got[0], rec[0]))
        db = max(abs(x - y) for x, y in zip(got[1], rec[1]))
        dr = max(abs(x - y) for x, y in zip(got[2], rec[2]))
        # 逐头序列：真值与重算应逐层逐头一致
        dh = max((abs(x - y) for gl, rl in zip(got[3], rec[3])
                  for x, y in zip(gl, rl)), default=0.0)
        worst_math = max(worst_math, da, db, dr)
        worst_head = max(worst_head, dh)
        # 自洽性：逐头均值应还原 a_layers（防止头轴与查询轴被写反）
        self_dev = max((abs(float(np.mean(rl)) - av) for rl, av in zip(rec[3], rec[0])),
                       default=0.0)
        print(f"[validate-M {kind} pos={pos} rho={rho} tok={len(ids)}] layers={len(got[0])} "
              f"max|Δa|={da:.3e} max|Δb|={db:.3e} max|Δr|={dr:.3e} "
              f"max|Δhead|={dh:.3e} head_self_dev={self_dev:.3e}", flush=True)
    print(f"[validate-M] worst(a,b,r) = {worst_math:.3e} worst(head) = {worst_head:.3e} → "
          f"{'PASS' if max(worst_math, worst_head) < 1e-3 else 'FAIL'} (阈值 1e-3)", flush=True)

    # ---- (2) flash 前向一致性（仅 GPU）----
    # 判据用**实际汇报的聚合量**（逐层均值的 a、b）而非"某单层的最大相对偏差"：
    # b 在部分层可能小到 ~1/S（无关位置本就没多少质量），此时相对误差会被放大为噪声。
    worst_f = 0.0
    if device != "cpu":
        eag = load_model(model_name, torch.bfloat16, "eager", device, rope_factor)
        eag.config.output_attentions = True
        fla = load_model(model_name, torch.bfloat16, "flash_attention_2", device, rope_factor)
        rng = np.random.default_rng(11)
        needle, code = NEEDLE_TEMPLATES[0], CODES[0]
        ids, span, fpos, qpos = build_ids(tok, needle.format(code=code), 1500, "F2",
                                          0.5, rng, code)
        g = measure_once_eager(eag, ids, span, fpos, qpos, 10 ** 6)
        f = measure_once_rows(fla, ids, span, fpos, qpos, 10 ** 6)
        for tag, gg, ff in (("a", g[0], f[0]), ("b", g[1], f[1])):
            gm, fm = float(np.mean(gg)), float(np.mean(ff))
            amb = max(abs(x - y) for x, y in zip(gg, ff))
            rel = abs(gm - fm) / max(abs(gm), 1e-12)
            print(f"[validate-F {tag}] agg eager={gm:.6f} flash={fm:.6f} "
                  f"agg_rel={rel:.3e} max_layer_abs={amb:.3e}", flush=True)
            worst_f = max(worst_f, rel)
        print(f"[validate-F tok={len(ids)} bf16] 聚合相对偏差 max={worst_f:.3e} → "
              f"{'PASS' if worst_f < 5e-2 else 'FAIL'} (阈值 5e-2)", flush=True)

    ok = max(worst_math, worst_head) < 1e-3 and (device == "cpu" or worst_f < 5e-2)
    print(f"[validate] overall {'PASS' if ok else 'FAIL'}", flush=True)
    return ok


# ---------------- Ansatz 合并 ----------------

def merge_shards(paths, out, rho_levels, fillers, positions, bootstrap=500):
    rows = []
    srcs = []
    for p in paths:
        for f in sorted(glob.glob(p)) if ("*" in p or "?" in p) else [p]:
            with open(f, "r", encoding="utf-8") as fh:
                rep = json.load(fh)
            rows.extend(rep.get("rows", []))
            srcs.append(f)
    agg = aggregate(rows, fillers, positions, rho_levels)
    boot = bootstrap_reciprocity(rows, rho_levels, B=bootstrap)
    report = {"merged_from": srcs, "n_rows": len(rows),
              "config": {"rho": rho_levels, "fillers": fillers,
                         "positions": positions},
              "cells": agg, "bootstrap": boot, "rows": rows}
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    print(f"[merge] {len(srcs)} 分片 → {len(rows)} rows → {out}", flush=True)
    return report


# ---------------- 主流程 ----------------

def main():
    ap = argparse.ArgumentParser(description="E3 长上下文注意力增长律测量（查询行重算）")
    ap.add_argument("--model", default=os.environ.get("IAC_MODEL", "Qwen/Qwen2.5-1.5B-Instruct"))
    ap.add_argument("--rho", type=int, nargs="+",
                    default=[0, 500, 1000, 2000, 4000, 8000, 16000, 32000])
    ap.add_argument("--fillers", nargs="+", default=["F1", "F2", "F3"])
    ap.add_argument("--positions", type=float, nargs="+", default=[0.1, 0.5, 0.9])
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--max-ctx", type=int, default=131072)
    ap.add_argument("--dtype", choices=["auto", "fp32", "fp16", "bf16"], default="auto")
    ap.add_argument("--attn-impl", default="flash_attention_2",
                    help="sdpa | eager | flash_attention_2（长上下文必须用 flash_attention_2，"
                         "否则会物化 [1,H,S,S] 而 OOM）")
    ap.add_argument("--device", default=None, help="cuda | cpu；默认自动")
    ap.add_argument("--bootstrap", type=int, default=500)
    ap.add_argument("--rope-factor", type=float, default=None,
                    help="启用 YaRN 外推因子（ρ>32k 必需，如 4.0 → 131072）")
    ap.add_argument("--shard-i", type=int, default=None, help="本分片序号（从 0 起）")
    ap.add_argument("--shards-n", type=int, default=None, help="总分片数（按 rho 档轮转切分）")
    ap.add_argument("--out", default=None)
    ap.add_argument("--merge", nargs="+", default=None, help="合并若干分片 JSON（支持通配）")
    ap.add_argument("--validate", action="store_true",
                    help="冒烟回归：查询行重算 vs eager 全矩阵真值（小 S）")
    ap.add_argument("--with-struct", action="store_true",
                    help="T8（§8.2）：加记注意力熵/top-k 集中度/key 有效秩逐层序列")
    args = ap.parse_args()

    if args.merge:
        merge_shards(args.merge, args.out or "results_e3_merged.json", args.rho,
                     args.fillers, args.positions, args.bootstrap)
        return

    if args.validate:
        device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
        ok = validate(args.model, device, args.rope_factor)
        sys.exit(0 if ok else 1)

    rho_levels = args.rho
    if args.shards_n and args.shard_i is not None:
        rho_levels = [r for k, r in enumerate(args.rho) if k % args.shards_n == args.shard_i]
        print(f"[shard] {args.shard_i}/{args.shards_n} → rho={rho_levels}", flush=True)

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    rows = run_matrix(args.model, rho_levels, args.fillers, args.positions, args.reps,
                      args.max_ctx, args.dtype, args.attn_impl, device=device,
                      rope_factor=args.rope_factor, with_struct=args.with_struct)
    agg = aggregate(rows, args.fillers, args.positions, rho_levels)

    out = args.out
    if out is None:
        tag = args.model.replace("/", "_")
        out = os.path.join(os.path.dirname(__file__), f"results_e3_{tag}.json")
        if args.shard_i is not None:
            out = out.replace(".json", f"_shard{args.shard_i}.json")

    report = {"model": args.model,
              "config": {"rho": rho_levels, "fillers": args.fillers,
                         "positions": args.positions, "reps": args.reps,
                         "max_ctx": args.max_ctx, "dtype": args.dtype,
                         "attn_impl": args.attn_impl, "device": device,
                         "rope_factor": args.rope_factor,
                         "with_struct": args.with_struct},
              "cells": agg, "rows": rows}
    # 单分片内也做 bootstrap（需该分片覆盖全部 reps × rho）
    if not (args.shards_n and args.shard_i is not None):
        report["bootstrap"] = bootstrap_reciprocity(rows, rho_levels, B=args.bootstrap)

    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    print("\n===== 逐 cell 摘要 =====")
    for name, e in agg.items():
        gm = e["growth_models"]
        best = min(gm, key=lambda k: gm[k]["aic"]) if gm else None
        print(f"[{name}] best={best} H1违反率={e['h1_violation_rate']} "
              f"H2违反率={e['h2_violation_rate']}")
        if "reciprocity" in e:
            r = e["reciprocity"]
            print(f"    ĉ={r['c_hat']:.6f}  1/(1+γ̂)={r['c_theory']:.6f}")
    print(f"[saved] {out}")


if __name__ == "__main__":
    main()
