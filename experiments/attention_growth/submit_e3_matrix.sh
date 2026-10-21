#!/bin/bash
# ============================================================================
# E3 全矩阵提交（scnet 华中一区 DCU）· 在登录节点通过 bash -ls 执行
# ----------------------------------------------------------------------------
# ρ 列表以 **base64** 传入：sbatch --export 以逗号分隔变量，直接传逗号列表会被
# 截成第一段（曾把 "0,500,..." 静默变成仅 [0]，产出废数据）。base64 单 token 安全。
#
# 并发提示：本账号 GRES 限额为 1 张 DCU（排队理由 AssocGrpGRES），作业**串行**执行，
# 故 wall-clock 约等于各作业耗时之和；单卡时消耗 = 各作业耗时之和（预算 50 卡时）。
#
# 变量：
#   IAC_REPS（默认 15，预注册设计）
#   IAC_MODE=matrix|calib|validate|all（默认 all）
# ============================================================================
set -u

WORK=/public/home/acc3z87n7t/e3
SLURM=$WORK/work/e3_job_dcu.slurm
VALSLURM=$WORK/work/e3_validate_dcu.slurm
M15=/e3/models/Qwen2.5-1.5B-Instruct
M7=/e3/models/Qwen2.5-7B-Instruct

SHORT="0,500,1000,2000,4000,8000,16000,32000"
FULL="0,500,1000,2000,4000,8000,16000,32000,64000,131072"
CALIB="2000,8000,32000,64000,131072"
REPS=${IAC_REPS:-15}
MODE=${IAC_MODE:-all}

b64() { printf '%s' "$1" | base64 -w0; }

sub() {  # $1=model $2=rho(csv) $3=out [$4=rope] [$5=reps]
  local r; r=$(b64 "$2")
  if [ -n "${4:-}" ]; then
    sbatch --parsable --export=ALL,IAC_MODEL="$1",IAC_RHO_B64="$r",\
IAC_OUT="$3",IAC_ROPE_FACTOR="$4",IAC_REPS="${5:-$REPS}" "$SLURM"
  else
    sbatch --parsable --export=ALL,IAC_MODEL="$1",IAC_RHO_B64="$r",\
IAC_OUT="$3",IAC_REPS="${5:-$REPS}" "$SLURM"
  fi
}

if [ "$MODE" = "all" ] || [ "$MODE" = "validate" ]; then
  echo "[J-V] validate（1.5B，flash vs eager 判据 + 重算数学等价）"
  echo "  JID=$(sbatch --parsable "$VALSLURM")"
fi

if [ "$MODE" = "all" ] || [ "$MODE" = "calib" ]; then
  echo "[J-C] 标定：7B YaRN 单格耗时（ρ=2k/8k/32k/64k/128k, F2, pos0.5, reps=1）"
  echo "  JID=$(sub $M7 "$CALIB" "$WORK/results/calib7b.json" 4.0 1)"
fi

if [ "$MODE" = "all" ] || [ "$MODE" = "matrix" ]; then
  echo "[J1] 7B  原生RoPE ρ≤32k  reps=$REPS（对照，可量化 YaRN 短程偏移）"
  echo "  JID=$(sub $M7  "$SHORT" "$WORK/results/e3_qwen7b_native.json" "" "$REPS")"
  echo "[J2] 7B  YaRN4.0   全档     reps=$REPS（主结论数据）"
  echo "  JID=$(sub $M7  "$FULL"  "$WORK/results/e3_qwen7b_yarn4.json" 4.0 "$REPS")"
  echo "[J3] 1.5B 原生RoPE ρ≤32k   reps=$REPS（跨尺度对照）"
  echo "  JID=$(sub $M15 "$SHORT" "$WORK/results/e3_qwen15b_native.json" "" "$REPS")"
  echo "[J4] 1.5B YaRN4.0  全档     reps=$REPS（跨尺度主数据）"
  echo "  JID=$(sub $M15 "$FULL"  "$WORK/results/e3_qwen15b_yarn4.json" 4.0 "$REPS")"
fi

echo
squeue -u acc3z87n7t -o '%.8i %.2t %.8M %.4C %R'
