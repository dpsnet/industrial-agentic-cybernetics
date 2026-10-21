#!/bin/bash
#SBATCH -J e3probe2
#SBATCH -A acc3z87n7t
#SBATCH -p hx1hdnormal
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=dcu:1
#SBATCH -t 01:00:00
#SBATCH -o /public/home/acc3z87n7t/e3/logs/e3probe2.%j.out

AP=/public/software/apps/apptainer/1.3.4/bin/apptainer
export APPTAINER_CACHEDIR=/tmp/apcache
export APPTAINER_TMPDIR=/tmp/aptmp
mkdir -p $APPTAINER_CACHEDIR $APPTAINER_TMPDIR
SIF=/public/home/acc3z87n7t/e3/minimax2_5_dcu.sif
ROOT=/tmp/rootfs
LDP=/opt/dtk/lib:/opt/dtk/lib64:/opt/hyhal/lib:/opt/hyhal/lib64:/opt/hostdtk/lib:/opt/hostdtk/lib64:/opt/dtk/hip/lib:/opt/dtk/llvm/lib:/opt/dtk/dcc/gcvm/lib:/opt/dtk/dushmem/lib
BINDS="--bind /opt/hyhal:/opt/hyhal --bind /opt/dtk-25.04.4:/opt/hostdtk --bind /public/home/acc3z87n7t/e3:/e3"

echo "HOST=$(hostname)"
echo "=== step0: SIF -> sandbox ==="
rm -rf $ROOT
time timeout 1800 $AP build --sandbox $ROOT $SIF 2>&1 | tail -3

echo "=== probe2 ==="
timeout 3000 $AP exec --rocm $BINDS $ROOT env LD_LIBRARY_PATH=$LDP \
  TRANSFORMERS_VERBOSITY=error HF_HUB_OFFLINE=1 bash -c \
  'cd /e3/work && python3 e3_backend_probe2.py' 2>&1

echo "=== ALL DONE ==="
