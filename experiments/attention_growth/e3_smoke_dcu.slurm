#!/bin/bash
#SBATCH -J e3smoke
#SBATCH -A acc3z87n7t
#SBATCH -p hx1hdnormal
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=dcu:1
#SBATCH -t 01:00:00
#SBATCH -o /public/home/acc3z87n7t/e3/logs/e3smoke.%j.out

AP=/public/software/apps/apptainer/1.3.4/bin/apptainer
export APPTAINER_CACHEDIR=/tmp/apcache
export APPTAINER_TMPDIR=/tmp/aptmp
mkdir -p $APPTAINER_CACHEDIR $APPTAINER_TMPDIR
SIF=/public/home/acc3z87n7t/e3/minimax2_5_dcu.sif
ROOT=/tmp/rootfs
LDP=/opt/dtk/lib:/opt/dtk/lib64:/opt/hyhal/lib:/opt/hyhal/lib64:/opt/hostdtk/lib:/opt/hostdtk/lib64:/opt/dtk/hip/lib:/opt/dtk/llvm/lib:/opt/dtk/dcc/gcvm/lib:/opt/dtk/dushmem/lib
BINDS="--bind /opt/hyhal:/opt/hyhal --bind /opt/dtk-25.04.4:/opt/hostdtk --bind /public/home/acc3z87n7t/e3:/e3"

echo "HOST=$(hostname)"
echo "=== step1: SIF -> sandbox on node-local disk ==="
rm -rf $ROOT
time timeout 1800 $AP build --sandbox $ROOT $SIF 2>&1 | tail -4
du -sh $ROOT 2>&1

echo "=== step2: version/signature check ==="
$AP exec --rocm $BINDS $ROOT env LD_LIBRARY_PATH=$LDP bash -c '
python3 - <<PY 2>&1
import torch, transformers, inspect
print("torch", torch.__version__, "hip", torch.version.hip, "avail", torch.cuda.is_available())
print("transformers", transformers.__version__)
from transformers import AutoModel
sig = inspect.signature(AutoModel.from_pretrained)
ps = list(sig.parameters)
print("has_torch_dtype", "torch_dtype" in ps, "has_dtype", "dtype" in ps)
print("sdpa_ok", hasattr(__import__("torch.nn.functional",fromlist=["x"]), "scaled_dot_product_attention"))
PY'

echo "=== step3: validate (recompute vs eager) on DCU ==="
timeout 1800 $AP exec --rocm $BINDS $ROOT env LD_LIBRARY_PATH=$LDP bash -c '
cd /e3/work
python3 measure_growth_law_e3.py --validate --model /e3/models/Qwen2.5-1.5B-Instruct --device cuda 2>&1 | tail -20'

echo "=== step4: tiny matrix end-to-end ==="
mkdir -p /public/home/acc3z87n7t/e3/results
timeout 1800 $AP exec --rocm $BINDS $ROOT env LD_LIBRARY_PATH=$LDP bash -c '
cd /e3/work
python3 measure_growth_law_e3.py --model /e3/models/Qwen2.5-1.5B-Instruct \
  --rho 500 2000 8000 --fillers F1 F2 F3 --positions 0.5 --reps 1 \
  --max-ctx 100000 --dtype bf16 --device cuda --out /e3/results/smoke15b.json 2>&1 | tail -25'

echo "=== done rc=$? ==="
