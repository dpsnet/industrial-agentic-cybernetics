"""E4 辅线等待器：轮询 Kimi 配额，重置后自动续跑剩余档位（512k × 8 + 700k × 10）"""
import time, subprocess, sys, requests

def load_env(path):
    env = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env

env = load_env(r"E:\workspace\DevForge-AI\.env")
H = {"Authorization": f"Bearer {env['KIMI_API_KEY']}", "Content-Type": "application/json"}
URL = f"{env['KIMI_BASE_URL']}/chat/completions"

while True:
    try:
        r = requests.post(URL, headers=H, json={
            "model": env["KIMI_MODEL"],
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5}, timeout=60)
        print(time.strftime("%m-%d %H:%M:%S"), "probe:", r.status_code, flush=True)
        if r.status_code == 200:
            break
    except Exception as e:
        print(time.strftime("%m-%d %H:%M:%S"), "probe err:", type(e).__name__, flush=True)
    time.sleep(1200)  # 20 min

print("quota restored, resuming E4 aux ...", flush=True)
rc = subprocess.run([sys.executable, "e4_kimi_hard.py", "512000", "700000"]).returncode
print(f"E4 aux finished, exit={rc}", flush=True)
