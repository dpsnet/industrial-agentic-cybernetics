#!/bin/bash
# E3 收口冒烟：一次作业完成 ①口径校验 ②1.5B 32k 小矩阵 ③7B 32k 耗时 ④7B 128k 耗时(含 YaRN)
#SBATCH -J e3smoke3
#SBATCH -A acc3z87n7t
#SBATCH -p hx1hdnormal
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --gres=dcu:1
#SBATCH -t 03:00:00
#SBATCH -o /public/home/acc3z87n7t/e3/logs/e3smoke3.%j.out

AP=/public/software/apps/apptainer/1.3.4/bin/apptainer
export APPTAINER_CACHEDIR=/tmp/apcache
export APPTAINER_TMPDIR=/tmp/aptmp
mkdir -p $APPTAINER_CACHEDIR $APPTAINER_TMPDIR
SIF=/public/home/acc3z87n7t/e3/minimax2_5_dcu.sif
ROOT=/tmp/rootfs
LDP=/opt/dtk/lib:/opt/dtk/lib64:/opt/hyhal/lib:/opt/hyhal/lib64:/opt/hostdtk/lib:/opt/hostdtk/lib64:/opt/dtk/hip/lib:/opt/dtk/llvm/lib:/opt/dtk/dcc/gcvm/lib:/opt/dtk/dushmem/lib
BINDS="--bind /opt/hyhal:/opt/hyhal --bind /opt/dtk-25.04.4:/opt/hostdtk --bind /public/home/acc3z87n7t/e3:/e3"
M15=/e3/models/Qwen2.5-1.5B-Instruct
M7=/e3/models/Qwen2.5-7B-Instruct

echo "HOST=$(hostname)"
echo "=== step0: SIF -> sandbox ==="
rm -rf $ROOT
time timeout 1800 $AP build --sandbox $ROOT $SIF 2>&1 | tail -3

run() { timeout $1 $AP exec --rocm $BINDS $ROOT env LD_LIBRARY_PATH=$LDP \
          TRANSFORMERS_VERBOSITY=error HF_HUB_OFFLINE=1 bash -c "$2" 2>&1 \
        | grep -a -v -E 'Loading checkpoint|it/s\]'; }

echo "=== stepA: 口径校验（重算数学等价 + flash 前向一致性）==="
run 2400 "cd /e3/work && python3 measure_growth_law_e3.py --validate --model $M15 --device cuda"

echo "=== stepB: 1.5B @32k 小矩阵（ρ=500/2k/8k/32k × F1/F2/F3 × pos0.5 × rep1）==="
run 2400 "cd /e3/work && python3 measure_growth_law_e3.py --model $M15 \
  --rho 500 2000 8000 32000 --fillers F1 F2 F3 --positions 0.5 --reps 1 \
  --max-ctx 32768 --dtype bf16 --device cuda --out /e3/results/smoke15b_32k.json"

echo "=== stepC: 7B @32k 单格耗时 ==="
run 2400 "cd /e3/work && python3 measure_growth_law_e3.py --model $M7 \
  --rho 32768 --fillers F1 --positions 0.5 --reps 1 \
  --max-ctx 32768 --dtype bf16 --device cuda --out /e3/results/probe7b_32k.json"

echo "=== stepD: 7B @128k 单格耗时（YaRN factor 4.0）==="
run 5400 "cd /e3/work && python3 measure_growth_law_e3.py --model $M7 \
  --rho 131072 --fillers F1 --positions 0.5 --reps 1 \
  --max-ctx 140000 --dtype bf16 --device cuda --rope-factor 4.0 \
  --out /e3/results/probe7b_128k.json"

echo "=== results ==="
ls -la /public/home/acc3z87n7t/e3/results/
echo "=== ALL DONE ==="
