"""
E4 辅线：Kimi 难任务逼近 W*
============================
在单 needle 正确率 ≈100%（1M 内）的基础上，升级任务难度：
  1. 多 needle 检索：上下文中插入 N 个不同颜色的事实句，问"列出所有魔法颜色"
  2. 语义干扰 filler：与 needle 同主题（颜色）的干扰句

目标：找到 Kimi 的 W*（正确率陡降点），或确认 W*_Kimi >= 1M。
"""
import os, sys, json, time, random, requests

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
API_KEY = env["KIMI_API_KEY"]
BASE_URL = env["KIMI_BASE_URL"]
MODEL = env["KIMI_MODEL"]

random.seed(2026)

# 颜色池（needle 用）
COLORS = ["periwinkle blue", "crimson red", "forest green", "sunset orange",
          "royal purple", "teal", "magenta", "golden yellow", "navy blue", "emerald"]

# 语义干扰 filler 模板（与颜色主题相关但取值不同）
DISTRACTOR_TEMPLATES = [
    "The artist mixed {c1} and {c2} to create a new shade for the mural.",
    "Researchers observed that {c1} light penetrates deeper than {c2} in water.",
    "The flag featured stripes of {c1}, {c2}, and white.",
    "Ancient cultures associated {c1} with prosperity and {c2} with mourning.",
    "The flower's petals shift from {c1} at dawn to {c2} at dusk.",
    "The gemstone displays a rare {c1} hue with {c2} undertones.",
    "Photographers use {c1} filters to enhance {c2} tones in portraits.",
    "The bird's plumage is predominantly {c1} with {c2} markings.",
]
DISTRACTOR_COLORS = ["pink", "brown", "gray", "cyan", "violet", "amber",
                     "indigo", "scarlet", "turquoise", "lavender"]

# 中性 filler（非颜色主题）
NEUTRAL_TEMPLATES = [
    "The {adj} {noun} {verb} across the {place} while {ing} {thing}.",
    "Researchers found that {thing} can {verb} when exposed to {adj} conditions.",
    "In {year}, the {noun} was first {verb}ed by scientists studying {thing}.",
]
A = ["rapid", "slow", "complex", "simple", "ancient", "modern"]
N = ["system", "process", "mechanism", "structure", "pattern"]
V = ["move", "change", "grow", "shrink", "expand"]
P = ["forest", "ocean", "desert", "mountain", "river"]
I = ["absorbing", "releasing", "transforming", "conducting"]
T = ["energy", "water", "heat", "light", "carbon"]
Y = list(range(1800, 2024))


def make_neutral_para():
    sents = []
    for _ in range(5):
        t = random.choice(NEUTRAL_TEMPLATES)
        sents.append(t.format(adj=random.choice(A), noun=random.choice(N),
            verb=random.choice(V), place=random.choice(P), ing=random.choice(I),
            thing=random.choice(T), year=random.choice(Y)))
    return " ".join(sents)


def make_distractor_para():
    sents = []
    for _ in range(5):
        t = random.choice(DISTRACTOR_TEMPLATES)
        c1, c2 = random.sample(DISTRACTOR_COLORS, 2)
        sents.append(t.format(c1=c1, c2=c2))
    return " ".join(sents)


def build_context(target_tokens, n_needles, distractor_ratio=0.5, pos=0.5):
    """构造多 needle 上下文。
    n_needles: 插入的 needle 数量
    distractor_ratio: filler 中语义干扰句的比例（其余为中性）
    pos: needle 簇的中心位置
    """
    para_tokens = 50
    n_total = max(1, target_tokens // para_tokens)

    # needle 均匀分布在 pos 附近的一个小区间内
    needle_spread = max(1, n_needles)
    needle_positions = []
    for i in range(n_needles):
        frac = pos - 0.05 + (0.1 * i / max(1, n_needles - 1)) if n_needles > 1 else pos
        needle_positions.append(int(n_total * frac))
    needle_positions = sorted(set(needle_positions))

    needles = random.sample(COLORS, n_needles)
    parts = []
    needle_idx = 0
    for i in range(n_total):
        if needle_idx < len(needle_positions) and i == needle_positions[needle_idx]:
            parts.append(f"[FACT {needle_idx+1}] The secret magic color #{needle_idx+1} is {needles[needle_idx]}.")
            needle_idx += 1
        else:
            if random.random() < distractor_ratio:
                parts.append(f"[Doc {i}] " + make_distractor_para())
            else:
                parts.append(f"[Doc {i}] " + make_neutral_para())
    return "\n\n".join(parts), needles


def call_api(context, question, max_tokens=300):
    url = f"{BASE_URL}/chat/completions"
    h = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    p = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Answer the question using only information from the context. List all items asked for."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        "max_tokens": max_tokens,
        "temperature": 1.0,
    }
    t0 = time.time()
    last_err = None
    for attempt in range(3):
        try:
            r = requests.post(url, headers=h, json=p, timeout=600)
            dt = time.time() - t0
            return r, dt
        except requests.exceptions.RequestException as e:
            last_err = e
            print(f"    [network retry {attempt+1}/3] {type(e).__name__}: {str(e)[:120]}")
            time.sleep(5 * (attempt + 1))
    raise ConnectionError(f"network failed after retries: {last_err}")


def run_one(target_tokens, n_needles, distractor_ratio=0.5):
    context, needles = build_context(target_tokens, n_needles, distractor_ratio)
    question = f"List all {n_needles} secret magic colors mentioned in the context, numbered 1 to {n_needles}."
    try:
        r, dt = call_api(context, question)
    except ConnectionError as e:
        return {"ok": False, "status": -1, "err": str(e)[:200], "dt": 0.0}
    if r.status_code != 200:
        return {"ok": False, "status": r.status_code, "err": r.text[:200], "dt": dt}
    d = r.json()
    u = d.get("usage", {})
    reply = d["choices"][0]["message"]["content"].strip()
    # 判分：needle 颜色是否都出现在回复中
    found = sum(1 for c in needles if c.lower() in reply.lower())
    correct = found == n_needles
    return {
        "ok": True, "dt": dt, "correct": correct, "found": found,
        "total": n_needles, "needles": needles, "reply": reply[:200],
        "prompt_tokens": u.get("prompt_tokens"),
    }


def main():
    # 实验矩阵：(target_tokens, n_needles, distractor_ratio)
    configs = [
        # 先测多 needle（5 个）在不同长度下的表现
        (128000, 5, 0.5),
        (256000, 5, 0.5),
        (512000, 5, 0.5),
        (700000, 5, 0.5),  # ~1M actual
    ]
    # 可选：命令行指定档位（target_tokens），如 python e4_kimi_hard.py 256000 512000 700000
    tiers = {int(a) for a in sys.argv[1:]}
    if tiers:
        configs = [c for c in configs if c[0] in tiers]
    reps = 10

    all_rows = []
    out = os.path.join(os.path.dirname(__file__),
                       "e4_kimi_hard_ext.json" if tiers else "e4_kimi_hard.json")

    # 断点续跑：加载已有结果，跳过已完成的 (target, rep)
    done = set()
    if os.path.exists(out):
        with open(out, encoding="utf-8") as f:
            all_rows = json.load(f).get("rows", [])
        done = {(r["target_tokens"], r["rep"]) for r in all_rows if r.get("ok")}
        if done:
            print(f"resume: {len(all_rows)} rows loaded, {len(done)} done")

    def save():
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"model": MODEL, "rows": all_rows}, f, ensure_ascii=False, indent=2)

    quota_exhausted = False
    for target, n_needles, dr in configs:
        if quota_exhausted:
            break
        print(f"\n=== target={target} n_needles={n_needles} distractor={dr} reps={reps} ===")
        for i in range(reps):
            if (target, i) in done:
                print(f"  run {i+1}: skip (already done)")
                continue
            r = run_one(target, n_needles, dr)
            if r["ok"]:
                print(f"  run {i+1}: correct={r['correct']} found={r['found']}/{r['total']} "
                      f"pt={r['prompt_tokens']} dt={r['dt']:.1f}s")
                r.update({"target_tokens": target, "n_needles": n_needles,
                          "distractor_ratio": dr, "rep": i})
                all_rows.append(r)
                save()
            else:
                print(f"  run {i+1}: ERROR {r['status']} {r['err']}")
                if r["status"] == 429:
                    print("  配额超限（HTTP 429），中止本轮后续请求。")
                    quota_exhausted = True
                    break
        save()

    print(f"\nSaved {len(all_rows)} rows to {out}")


if __name__ == "__main__":
    main()
