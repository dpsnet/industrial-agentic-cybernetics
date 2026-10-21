#!/bin/bash
# E4 主线：Qwen needle 正确率测量（复用 E3 容器流程）
#SBATCH -J e4qwen
#SBATCH -A acc3z87n7t
#SBATCH -p hx1hdnormal
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=dcu:1
#SBATCH -t 06:00:00
#SBATCH -o /public/home/acc3z87n7t/e3/logs/e4qwen.%j.out

set -euo pipefail

AP=/public/software/apps/apptainer/1.3.4/bin/apptainer
export APPTAINER_CACHEDIR=/tmp/apcache
export APPTAINER_TMPDIR=/tmp/aptmp
mkdir -p $APPTAINER_CACHEDIR $APPTAINER_TMPDIR /public/home/acc3z87n7t/e3/logs
SIF=/public/home/acc3z87n7t/e3/minimax2_5_dcu.sif
ROOT=/tmp/rootfs
LDP=/opt/dtk/lib:/opt/dtk/lib64:/opt/hyhal/lib:/opt/hyhal/lib64:/opt/hostdtk/lib:/opt/hostdtk/lib64:/opt/dtk/hip/lib:/opt/dtk/llvm/lib:/opt/dtk/dcc/gcvm/lib:/opt/dtk/dushmem/lib
BINDS="--bind /opt/hyhal:/opt/hyhal --bind /opt/dtk-25.04.4:/opt/hostdtk --bind /public/home/acc3z87n7t/e3:/e3"

echo "=== step0: SIF -> sandbox ==="
rm -rf $ROOT
time timeout 1800 $AP build --sandbox $ROOT $SIF 2>&1 | tail -3

run() { timeout 21600 $AP exec --rocm $BINDS $ROOT env LD_LIBRARY_PATH=$LDP \
          TRANSFORMERS_VERBOSITY=error HF_HUB_OFFLINE=1 bash -c "$1"; }

echo "=== 7B YaRN 4.0 ==="
run "cd /e3 && python3 -u e4_qwen_needle.py \
  --model /e3/models/Qwen2.5-7B-Instruct \
  --rope-factor 4.0 \
  --rho 0 2000 8000 32000 64000 131072 \
  --positions 0.5 \
  --reps 10 \
  --filler F1 \
  --out /e3/e4_7b_yarn4.json" 2>&1 | grep -a -v -E 'Loading weights|it/s\]'

echo "=== 1.5B YaRN 4.0 ==="
run "cd /e3 && python3 -u e4_qwen_needle.py \
  --model /e3/models/Qwen2.5-1.5B-Instruct \
  --rope-factor 4.0 \
  --rho 0 2000 8000 32000 64000 131072 \
  --positions 0.5 \
  --reps 10 \
  --filler F1 \
  --out /e3/e4_1p5b_yarn4.json" 2>&1 | grep -a -v -E 'Loading weights|it/s\]'

echo "ALL DONE"
