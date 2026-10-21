#!/bin/bash
#SBATCH -J e3diag
#SBATCH -A acc3z87n7t
#SBATCH -p hx1hdnormal
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=dcu:1
#SBATCH -t 00:30:00
#SBATCH -o /public/home/acc3z87n7t/e3/logs/e3diag.%j.out

AP=/public/software/apps/apptainer/1.3.4/bin/apptainer
export APPTAINER_CACHEDIR=/tmp/apcache
export APPTAINER_TMPDIR=/tmp/aptmp
mkdir -p $APPTAINER_CACHEDIR $APPTAINER_TMPDIR
SIF=/public/home/acc3z87n7t/e3/minimax2_5_dcu.sif
ROOT=/tmp/rootfs
LDP=/opt/dtk/lib:/opt/dtk/lib64:/opt/hyhal/lib:/opt/hyhal/lib64:/opt/hostdtk/lib:/opt/hostdtk/lib64:/opt/dtk/hip/lib:/opt/dtk/llvm/lib:/opt/dtk/dcc/gcvm/lib:/opt/dtk/dushmem/lib
BINDS="--bind /opt/hyhal:/opt/hyhal --bind /opt/dtk-25.04.4:/opt/hostdtk --bind /public/home/acc3z87n7t/e3:/e3"

rm -rf $ROOT
timeout 1800 $AP build --sandbox $ROOT $SIF 2>&1 | tail -3

$AP exec --rocm $BINDS $ROOT env LD_LIBRARY_PATH=$LDP bash -c '
python3 - <<PY 2>&1 | tail -120
import torch, transformers, inspect
from transformers import AutoModel, AutoConfig
print("tf", transformers.__version__)
cfg = AutoConfig.from_pretrained("/e3/models/Qwen2.5-1.5B-Instruct")
d = cfg.to_dict()
for k in ["num_attention_heads","num_key_value_heads","head_dim","hidden_size","num_hidden_layers",
          "max_position_embeddings","rope_scaling","_attn_implementation","model_type","attn_implementation"]:
    print("cfg.%-24s = %r" % (k, d.get(k, "<absent>")))
m = AutoModel.from_pretrained("/e3/models/Qwen2.5-1.5B-Instruct", dtype=torch.bfloat16,
                              attn_implementation="sdpa")
from collections import OrderedDict
seen = OrderedDict()
for name, mod in m.named_modules():
    cn = type(mod).__name__
    if ("Attn" in cn or "Attention" in cn) and cn not in seen:
        attrs = {}
        for a in dir(mod):
            if a.startswith("_"): continue
            try: v = getattr(mod, a)
            except Exception: continue
            if isinstance(v, (int, float, bool, str, type(None))):
                attrs[a] = v
        submods = [n for n, _ in mod.named_children()] if hasattr(mod, "named_children") else []
        seen[cn] = (name, attrs, submods)
for cn, (name, attrs, submods) in seen.items():
    print("----", cn, "first_path=", name)
    print("   scalar_attrs:", attrs)
    print("   children:", submods)
print("layer0 type:", type(m.model.layers[0]).__name__)
print("layer0 children:", [n for n, _ in m.model.layers[0].named_children()])
lay0 = m.model.layers[0]
for n, mod in lay0.named_children():
    print("   ", n, type(mod).__name__, "children=", [x for x, _ in mod.named_children()])
att = None
for n, mod in m.named_modules():
    if type(mod).__name__.endswith("Attention"):
        att = mod; print("attn mod path", n, type(mod).__name__); break
if att is not None:
    print("attn sig:", inspect.signature(att.forward))
    print("has rotary_emb:", hasattr(att, "rotary_emb"))
PY'
echo "diag_done rc=$?"
