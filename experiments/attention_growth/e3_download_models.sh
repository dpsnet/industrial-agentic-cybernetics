#!/bin/bash
# 登录节点后台下载 Qwen2.5 模型（优先 ModelScope，回退 hf-mirror 并禁用 Xet）
exec > /public/home/acc3z87n7t/e3/logs/dl2.log 2>&1
echo "START $(date)"
export PIP_CACHE_DIR=/public/home/acc3z87n7t/e3/pip
PIP=/usr/local/python3.12/bin/pip3
PY=/usr/local/python3.12/bin/python3

echo "=== reachability ==="
for u in https://www.modelscope.cn https://hf-mirror.com; do
  printf "%-30s " "$u"; timeout 20 curl -s -o /dev/null -w "%{http_code}\n" "$u"
done

echo "=== install modelscope ==="
$PIP install --user -q -U modelscope -i https://pypi.tuna.tsinghua.edu.cn/simple 2>&1 | tail -3
$PY -c "import modelscope;print('ms',modelscope.__version__)" 2>&1

echo "=== download via modelscope ==="
$PY - <<'PY'
from modelscope import snapshot_download
pairs = [("Qwen/Qwen2.5-1.5B-Instruct", "/public/home/acc3z87n7t/e3/models/Qwen2.5-1.5B-Instruct"),
         ("Qwen/Qwen2.5-7B-Instruct",   "/public/home/acc3z87n7t/e3/models/Qwen2.5-7B-Instruct")]
for mid, dst in pairs:
    print("=== start", mid, flush=True)
    try:
        p = snapshot_download(mid, local_dir=dst)
        print("=== done", mid, p, flush=True)
    except Exception as e:
        print("=== FAIL", mid, repr(e)[:600], flush=True)
PY
echo "ms_rc=$?"

echo "=== fallback: hf-mirror (Xet disabled) ==="
$PY - <<'PY'
import os, glob
need = []
for d in glob.glob("/public/home/acc3z87n7t/e3/models/*"):
    files = set(os.path.basename(f) for f in glob.glob(d + "/*"))
    if {"vocab.json", "tokenizer.json", "tokenizer_config.json"} - files:
        need.append(d)
if not need:
    print("all models complete", flush=True)
else:
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
    os.environ["HF_HUB_DISABLE_XET"] = "1"
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"
    from huggingface_hub import snapshot_download
    for d in need:
        repo = "Qwen/" + os.path.basename(d)
        print("=== hf start", repo, flush=True)
        try:
            p = snapshot_download(repo_id=repo, local_dir=d, max_workers=4)
            print("=== hf done", p, flush=True)
        except Exception as e:
            print("=== hf FAIL", repo, repr(e)[:400], flush=True)
PY
echo "hf_rc=$?"
echo "=== sizes ==="
du -sh /public/home/acc3z87n7t/e3/models/* 2>/dev/null
for d in /public/home/acc3z87n7t/e3/models/*; do echo "--- $d"; ls "$d"; done
echo "DL_ALL_DONE $(date)"
