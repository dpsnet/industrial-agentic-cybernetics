"""
模式 22 补测：原生 Provider 直连的首字时延（TTFT）实测
=====================================================
被检验的宣称（模式 22 正文）："首字时延 < 800ms"。

口径（预注册）：
- 直连 provider 的 /chat/completions，stream=True，记录两个时刻：
  (a) 首字节到达；(b) 首个非空 delta.content 到达。TTFT 取 (b)。
- n = 30 次串行请求，短提示（≤ 20 输出 token），取中位数为主判据，p90 为稳健性参考。
- 判据：median_TTFT ≤ 800ms 为"支持"，否则"不支持（本网络/本 provider 下）"。

说明：本测只覆盖"直连"一侧，不含"CLI 包装"对照，故只能检验绝对阈值，
不能检验"相对 CLI 降低 3~5 倍"的比较宣称。
"""
import json, os, time, requests

HERE = os.path.dirname(__file__)
ENV_PATHS = [
    r"E:\workspace\DevForge-AI\.env",
    os.path.join(os.path.dirname(os.path.dirname(HERE)), ".env"),
]
N = 30

PROVIDERS = {
    "deepseek": ("DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL", "DEEPSEEK_MODEL"),
    "scnet": ("scnet_api_key", "scnet_api_base", "scnet_api_model"),
    "kimi": ("KIMI_API_KEY", "KIMI_BASE_URL", "KIMI_MODEL"),
}
PROVIDER = os.environ.get("P22_PROVIDER", "deepseek")
OUT = os.path.join(HERE, f"e_p22_ttft_probe_{PROVIDER}.json")


def load_env():
    env = {}
    for p in ENV_PATHS:
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def probe_once(env):
    k_key, k_url, k_model = PROVIDERS[PROVIDER]
    url = env[k_url].rstrip("/") + "/chat/completions"
    h = {"Authorization": f"Bearer {env[k_key]}",
         "Content-Type": "application/json"}
    p = {"model": env[k_model], "stream": True,
         # kimi 为推理型：16 token 会被 reasoning 吃光，content 永不出现
         "max_tokens": 512 if PROVIDER == "kimi" else 16,
         # kimi-for-coding 仅接受 temperature=1.0
         "temperature": 1.0 if PROVIDER == "kimi" else 0.0,
         "messages": [{"role": "user", "content": "只回复一个词：ok"}]}
    t0 = time.perf_counter()
    first_byte = None
    first_any = None
    first_token = None
    with requests.post(url, headers=h, json=p, stream=True, timeout=60) as r:
        r.raise_for_status()
        for raw in r.iter_lines():
            if first_byte is None:
                first_byte = time.perf_counter() - t0
            if not raw:
                continue
            s = raw.decode("utf-8", "ignore")
            if not s.startswith("data:"):
                continue
            data = s[5:].strip()
            if data == "[DONE]":
                break
            try:
                j = json.loads(data)
            except Exception:
                continue
            ch = (j.get("choices") or [{}])[0]
            delta = ch.get("delta") or {}
            content = delta.get("content") or ""
            reasoning = delta.get("reasoning_content") or delta.get("reasoning") or ""
            if first_any is None and (content.strip() or reasoning.strip()):
                first_any = time.perf_counter() - t0
            if content.strip():
                first_token = time.perf_counter() - t0
                break
    return first_byte, first_any, first_token


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    idx = min(len(xs) - 1, int(round(q * (len(xs) - 1))))
    return xs[idx]


def main():
    env = load_env()
    fb, fa, ft, errs = [], [], [], 0
    for _ in range(N):
        try:
            a, b, c = probe_once(env)
            if a is not None:
                fb.append(a)
            if b is not None:
                fa.append(b)
            if c is not None:
                ft.append(c)
        except Exception as e:
            errs += 1
            print("err:", type(e).__name__, str(e)[:80])
        time.sleep(0.5)
    med = pct(ft, 0.5)
    k_key, k_url, k_model = PROVIDERS[PROVIDER]
    rec = {
        "provider": PROVIDER,
        "model": env.get(k_model),
        "base_url": env.get(k_url),
        "n_requested": N, "n_content_ok": len(ft), "n_any_delta": len(fa), "n_err": errs,
        "first_byte_ms": {"median": round((pct(fb, .5) or 0) * 1000, 1),
                          "p90": round((pct(fb, .9) or 0) * 1000, 1)},
        "first_any_delta_ms": {"median": round((pct(fa, .5) or 0) * 1000, 1),
                               "p90": round((pct(fa, .9) or 0) * 1000, 1)},
        "ttft_ms": {"median": round((med or 0) * 1000, 1),
                    "p90": round((pct(ft, .9) or 0) * 1000, 1),
                    "min": round(min(ft) * 1000, 1) if ft else None,
                    "max": round(max(ft) * 1000, 1) if ft else None},
        "criterion": "median_ttft <= 800ms",
        "pass": bool(med is not None and med <= 0.8),
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=2)
    print(json.dumps(rec, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
