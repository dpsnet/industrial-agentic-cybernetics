"""
E4 冒烟测试 v2：Kimi needle-in-haystack
改进：自然语言 filler、max_tokens=200、多次重复
"""
import os
import json
import time
import random
import requests

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

NEEDLE_FACT = "The secret magic color is periwinkle blue."
QUESTION = "What is the secret magic color? Answer with only the color word."

# 自然语言 filler 模板（取自通用主题，避免与 needle 混淆）
FILLER_TEMPLATES = [
    "The {adj} {noun} {verb} across the {place} while {ing} {thing}.",
    "Researchers found that {thing} can {verb} when exposed to {adj} conditions.",
    "In {year}, the {noun} was first {verb}ed by scientists studying {thing}.",
    "The {adj} properties of {thing} make it suitable for {place} applications.",
    "Many {noun}s rely on {thing} to {verb} during {season} months.",
]
ADJS = ["rapid", "slow", "complex", "simple", "ancient", "modern", "natural", "artificial", "stable", "variable"]
NOUNS = ["system", "process", "mechanism", "structure", "pattern", "phenomenon", "element", "component", "method", "approach"]
VERBS = ["move", "change", "grow", "shrink", "expand", "contract", "evolve", "adapt", "respond", "interact"]
PLACES = ["forest", "ocean", "desert", "mountain", "river", "valley", "coast", "plain", "tundra", "wetland"]
INGS = ["absorbing", "releasing", "transforming", "conducting", "regulating", "generating", "storing", "transmitting"]
THINGS = ["energy", "water", "heat", "light", "carbon", "oxygen", "nitrogen", "minerals", "nutrients", "signals"]
YEARS = list(range(1800, 2024))
SEASONS = ["spring", "summer", "autumn", "winter"]


def make_filler_paragraph():
    sentences = []
    for _ in range(5):
        t = random.choice(FILLER_TEMPLATES)
        s = t.format(
            adj=random.choice(ADJS), noun=random.choice(NOUNS), verb=random.choice(VERBS),
            place=random.choice(PLACES), ing=random.choice(INGS), thing=random.choice(THINGS),
            year=random.choice(YEARS), season=random.choice(SEASONS),
        )
        sentences.append(s)
    return " ".join(sentences)


def build_context(target_tokens, needle_pos_ratio=0.5):
    """构造上下文，按 token 粗控（每段约 50 tokens）。"""
    para_tokens = 50
    n_total = max(1, target_tokens // para_tokens)
    n_before = int(n_total * needle_pos_ratio)
    n_after = n_total - n_before

    parts = []
    for i in range(n_before):
        parts.append(f"[Doc {i}] " + make_filler_paragraph())
    parts.append(f"[FACT] {NEEDLE_FACT}")
    for i in range(n_after):
        parts.append(f"[Doc {n_before + 1 + i}] " + make_filler_paragraph())
    return "\n\n".join(parts), "periwinkle blue"


def call_api(context, question, max_tokens=200):
    url = f"{BASE_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Answer the question using only information from the context. Give a short answer."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        "max_tokens": max_tokens,
        "temperature": 1.0,
    }
    t0 = time.time()
    r = requests.post(url, headers=headers, json=payload, timeout=180)
    dt = time.time() - t0
    return r, dt


def run_one(target_tokens, pos=0.5):
    context, answer = build_context(target_tokens, pos)
    r, dt = call_api(context, QUESTION)
    if r.status_code != 200:
        return {"ok": False, "status": r.status_code, "error": r.text[:200], "dt": dt}
    data = r.json()
    usage = data.get("usage", {})
    reply = data["choices"][0]["message"]["content"].strip()
    correct = answer.lower() in reply.lower()
    return {
        "ok": True, "dt": dt, "correct": correct, "reply": reply[:100],
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
    }


def main():
    print(f"Model: {MODEL}")
    for ctx in [8000, 32000, 128000]:
        print(f"\n=== {ctx} tokens target, needle at 50%, reps=3 ===")
        results = []
        for i in range(3):
            r = run_one(ctx, 0.5)
            if r["ok"]:
                print(f"  run {i+1}: correct={r['correct']} reply='{r['reply']}' "
                      f"prompt_tokens={r['prompt_tokens']} dt={r['dt']:.1f}s")
                results.append(r)
            else:
                print(f"  run {i+1}: ERROR {r['status']} {r['error']}")
        if results:
            acc = sum(r["correct"] for r in results) / len(results)
            avg_tokens = sum(r["prompt_tokens"] for r in results) / len(results)
            print(f"  -> acc={acc:.2f} avg_prompt_tokens={avg_tokens:.0f}")


if __name__ == "__main__":
    main()
