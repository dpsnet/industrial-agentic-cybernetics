#!/bin/bash
# ============================================================================
# E3 分片提交器 · 在 scnet 登录节点（E-Shell）执行
# ----------------------------------------------------------------------------
# 路线（已实测确认，见 e3_backend_probe*.py 与 e3_smoke3_dcu.slurm）：
#   全部在华中一区 BW（海光 DCU，64GB）上跑，容器路线：
#     SIF → 节点本地沙盒 → apptainer exec
#   前向用 flash_attention_2（本卡实测可用：7B 头配置 @128k 仅 2.0GB、0.64s），
#   **不能**用 sdpa：本卡无高效 SDPA 后端，transformers 传 4D 因果掩码会让 flash
#   后端静默退回 math 实现并物化 [1,H,S,S]（1.5B@32k 即 51.5GB）→ OOM。
#
# RoPE 处理（**跨档必须一致**）：所有 ρ 档统一启用 YaRN factor 4.0（→131072）。
#   理由：若仅 ρ>32k 才启用，则 ρ=32k 处会出现一次"位置编码处理突变"，H3/H5
#   （增长律形态、饱和点）会把人为的不连续误判为饱和点。统一处理消除该混淆，
#   代价是与 E2（原生 RoPE）的 1.5B 数据不直接可比——故 E3 的 1.5B 对照档也
#   用同一 factor 复跑，E2 数据仅作为独立基线记录。
#
# 分片策略（按 ρ 切，便于并行与按预算裁剪）：
#   shard0   ρ≤32k（8 档，单格秒级）
#   shard1   ρ=64k
#   shard2   ρ=128k（最贵，按 smoke3 实测耗时决定 reps/positions）
# ============================================================================
set -u

WORK=/public/home/acc3z87n7t/e3
SLURM=$WORK/work/e3_job_dcu.slurm
MODEL7=/e3/models/Qwen2.5-7B-Instruct
MODEL15=/e3/models/Qwen2.5-1.5B-Instruct
ROPE=4.0

# ---- 矩阵规模（按 smoke3 的 7B@128k 单格耗时调整 reps/positions）----
FILLERS="${IAC_FILLERS:-F1 F2 F3}"
POSITIONS="${IAC_POSITIONS:-0.1 0.5 0.9}"
REPS="${IAC_REPS:-1}"

RHO_SMALL="0 500 1000 2000 4000 8000 16000 32000"
RHO_64K="64000"
RHO_128K="131072"

submit() {  # $1=rho $2=out $3=reps $4=positions
  sbatch --parsable --export=ALL,IAC_MODEL="$MODEL7",IAC_RHO="$1",IAC_OUT="$2",\
IAC_ROPE_FACTOR=$ROPE,IAC_REPS="$3",IAC_FILLERS="$FILLERS",IAC_POSITIONS="$4" "$SLURM"
}

echo "[submit] shard0 (7B, ρ≤32k, YaRN)"
J0=$(submit "$RHO_SMALL" "$WORK/results/e3_qwen7b_shard0.json" "$REPS" "$POSITIONS")
echo "  JID=$J0"

echo "[submit] shard1 (7B, ρ=64k, YaRN)"
J1=$(submit "$RHO_64K" "$WORK/results/e3_qwen7b_shard1.json" "$REPS" "$POSITIONS")
echo "  JID=$J1"

echo "[submit] shard2 (7B, ρ=128k, YaRN)  —— 最贵"
J2=$(submit "$RHO_128K" "$WORK/results/e3_qwen7b_shard2.json" "$REPS" "$POSITIONS")
echo "  JID=$J2"

if [ "${IAC_WITH15B:-1}" = "1" ]; then
  echo "[submit] 1.5B 全档对照（同 YaRN，用于跨尺度比较）"
  J3=$(sbatch --parsable --export=ALL,IAC_MODEL="$MODEL15",\
IAC_RHO="$RHO_SMALL $RHO_64K $RHO_128K",\
IAC_OUT="$WORK/results/e3_qwen15b.json",IAC_ROPE_FACTOR=$ROPE,\
IAC_REPS="$REPS",IAC_FILLERS="$FILLERS",IAC_POSITIONS="$POSITIONS" "$SLURM")
  echo "  JID=$J3"
fi

cat <<EOF

# ---- 查看 / 释放 ----
#   squeue -u acc3z87n7t
#   scancel <JOBID>
#   tail -f $WORK/logs/e3attn.<JOBID>.out

# ---- 全部分片跑完后合并（--rho 必须列全档位，否则大档行不进 cells）----
#   cd $WORK/work && python3 measure_growth_law_e3.py \\
#     --rho 0 500 1000 2000 4000 8000 16000 32000 64000 131072 \\
#     --merge $WORK/results/e3_qwen7b_shard0.json \\
#             $WORK/results/e3_qwen7b_shard1.json \\
#             $WORK/results/e3_qwen7b_shard2.json \\
#     --out $WORK/results/e3_qwen7b.json
EOF
