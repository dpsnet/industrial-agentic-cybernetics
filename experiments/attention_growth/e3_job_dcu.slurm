#!/bin/bash
# ============================================================================
# E3 注意力增长律测量 · scnet 华中一区 DCU 作业体（单分片，容器路线）
# ----------------------------------------------------------------------------
# 运行方式与 e3_smoke2_dcu.slurm 完全一致：SIF → 节点本地沙盒 → apptainer exec。
# Slurm 不展开 #SBATCH 中的 shell 变量，故分区/卡型固定在文件头部（本分区只此
# 一种形态：hx1hdnormal + --gres=dcu:1），其余全部经 sbatch --export 注入。
#
# 必需环境变量：
#   IAC_RHO_B64   ρ 档列表的 **base64** 编码（内容形如 0,500,1000,2000）。
#                 必须编码：sbatch --export 用逗号分隔变量，直接传逗号列表会被
#                 截成第一段（曾实测把 "0,500,..." 变成仅 [0]，静默跑出废数据）。
#                 base64 字母表不含逗号/空格，故单 token 安全传递。
#   IAC_OUT       本分片结果 JSON 的绝对路径
# 可选（默认值见下）：
#   IAC_MODEL=/e3/models/Qwen2.5-7B-Instruct
#   IAC_ROPE_FACTOR（ρ>32k 必需，Qwen2.5 用 4.0 → 131072）
#   IAC_REPS=1  IAC_MAX_CTX=140000  IAC_DTYPE=bf16
#   （填充类型与位置档固定用预注册设计：F1 F2 F3 × 0.1 0.5 0.9）
# ============================================================================
#SBATCH -J e3attn
#SBATCH -A acc3z87n7t
#SBATCH -p hx1hdnormal
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=dcu:1
#SBATCH -t 12:00:00
#SBATCH -o /public/home/acc3z87n7t/e3/logs/e3attn.%j.out

set -euo pipefail

: "${IAC_RHO_B64:?需要 IAC_RHO_B64（ρ 档列表的 base64）}"
: "${IAC_OUT:?需要 IAC_OUT（结果 JSON 绝对路径）}"
RHO=$(printf '%s' "$IAC_RHO_B64" | base64 -d | tr ',' ' ')
[ -n "$RHO" ] || { echo "FATAL: RHO 解码为空"; exit 2; }
echo "[rho] decoded: $RHO"

AP=/public/software/apps/apptainer/1.3.4/bin/apptainer
export APPTAINER_CACHEDIR=/tmp/apcache
export APPTAINER_TMPDIR=/tmp/aptmp
mkdir -p $APPTAINER_CACHEDIR $APPTAINER_TMPDIR
SIF=/public/home/acc3z87n7t/e3/minimax2_5_dcu.sif
ROOT=/tmp/rootfs
LDP=/opt/dtk/lib:/opt/dtk/lib64:/opt/hyhal/lib:/opt/hyhal/lib64:/opt/hostdtk/lib:/opt/hostdtk/lib64:/opt/dtk/hip/lib:/opt/dtk/llvm/lib:/opt/dtk/dcc/gcvm/lib:/opt/dtk/dushmem/lib
BINDS="--bind /opt/hyhal:/opt/hyhal --bind /opt/dtk-25.04.4:/opt/hostdtk --bind /public/home/acc3z87n7t/e3:/e3"

MODEL="${IAC_MODEL:-/e3/models/Qwen2.5-7B-Instruct}"
REPS="${IAC_REPS:-1}"
EXTRA=""
if [[ -n "${IAC_ROPE_FACTOR:-}" ]]; then EXTRA="--rope-factor $IAC_ROPE_FACTOR"; fi
SHARD=""
if [[ -n "${IAC_SHARD_I:-}" ]]; then SHARD="--shard-i $IAC_SHARD_I --shards-n ${IAC_SHARDS_N:?}"; fi

echo "HOST=$(hostname) MODEL=$MODEL RHO=$RHO OUT=$IAC_OUT ROPE=$EXTRA $SHARD REP=$REPS"

echo "=== step0: SIF -> sandbox ==="
rm -rf $ROOT
time timeout 1800 $AP build --sandbox $ROOT $SIF 2>&1 | tail -3

run() { timeout 43200 $AP exec --rocm $BINDS $ROOT env LD_LIBRARY_PATH=$LDP \
          TRANSFORMERS_VERBOSITY=error HF_HUB_OFFLINE=1 bash -c "$1"; }

echo "=== measure ==="
# --attn-impl 必须为 flash_attention_2：本卡（gfx936）无高效 SDPA 后端，
# transformres 传入 4D 因果掩码会让 flash 后端静默退回 math 实现并物化
# [1,H,S,S]（1.5B@32k 即 51.5 GB）→ OOM。
run "cd /e3/work && time python3 measure_growth_law_e3.py \
  --model $MODEL --rho $RHO \
  --reps $REPS --max-ctx ${IAC_MAX_CTX:-140000} \
  --dtype ${IAC_DTYPE:-bf16} --attn-impl flash_attention_2 --device cuda $EXTRA $SHARD \
  --out $IAC_OUT" 2>&1 | grep -a -v -E 'Loading weights|it/s\]'

echo "[done] $IAC_OUT"
ls -la "$IAC_OUT"
