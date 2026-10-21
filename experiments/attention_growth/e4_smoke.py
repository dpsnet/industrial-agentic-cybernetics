"""
E4 冒烟测试：Kimi needle-in-haystack 长上下文检索
验证 API 连通性 + 任务可行性 + 输出可解析性
"""
import os
import json
import time
import random
import string
import requests

# 从 .env 加载（手动解析，避免 python-dotenv 依赖）
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
BASE_URL = env["KIMI_BASE_URL"]  # https://api.kimi.com/coding/v1
MODEL = env["KIMI_MODEL"]        # kimi-for-coding

random.seed(42)

NEEDLE_FACT = "The secret magic color is periwinkle blue."
QUESTION = "What is the secret magic color? Answer with only the color."


def make_filler_paragraph(idx):
    """生成一段无关的英文段落。"""
    topics = [
        "the history of paper clips",
        "migratory patterns of arctic terns",
        "the chemical composition of seawater",
        "ancient roman concrete recipes",
        "the physics of bubble formation",
        "biodiversity in tropical rainforests",
        "the evolution of typewriter keyboards",
        "properties of non-newtonian fluids",
        "the mathematics of origami folding",
        "viking navigation techniques",
    ]
    t = topics[idx % len(topics)]
    sentences = []
    for _ in range(4):
        words = []
        for _ in range(random.randint(8, 16)):
            words.append("".join(random.choices(string.ascii_lowercase, k=random.randint(3, 8))))
        sentences.append(" ".join(words).capitalize() + ".")
    return f"[Doc {idx}] On {t}: " + " ".join(sentences)


def build_context(total_tokens_approx, needle_pos_ratio=0.5):
    """构造上下文：filler 段落 + needle（在 needle_pos_ratio 位置）。
    返回 (messages, needle_answer)。token 数用字符/4 粗估。
    """
    # 每段约 80 tokens（~320 chars）
    chars_per_para = 320
    target_chars = total_tokens_approx * 4
    n_filler_before = int(target_chars / chars_per_para * needle_pos_ratio)
    n_filler_after = int(target_chars / chars_per_para * (1 - needle_pos_ratio))

    parts = []
    for i in range(n_filler_before):
        parts.append(make_filler_paragraph(i))
    parts.append(f"[IMPORTANT FACT] {NEEDLE_FACT}")
    for i in range(n_filler_after):
        parts.append(make_filler_paragraph(n_filler_before + 1 + i))

    context = "\n\n".join(parts)
    return context, "periwinkle blue"


def call_api(context, question, max_tokens=50, temperature=1.0):
    url = f"{BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a precise question-answering assistant. Answer the user's question based on the provided context."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    t0 = time.time()
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    dt = time.time() - t0
    return r, dt


def main():
    print(f"Model: {MODEL}")
    print(f"Base URL: {BASE_URL}")
    print()

    # 冒烟：8k 上下文，1 次
    print("=== Smoke test: 8k context, needle at 50% ===")
    context, answer = build_context(8000, 0.5)
    est_tokens = len(context) // 4
    print(f"Context length: {len(context)} chars (~{est_tokens} tokens)")
    print(f"Needle answer: {answer}")
    print()

    r, dt = call_api(context, QUESTION)
    print(f"HTTP {r.status_code} in {dt:.1f}s")
    if r.status_code != 200:
        print(f"Error: {r.text[:500]}")
        return
    data = r.json()
    usage = data.get("usage", {})
    print(f"Usage: prompt_tokens={usage.get('prompt_tokens')}, completion_tokens={usage.get('completion_tokens')}")
    reply = data["choices"][0]["message"]["content"].strip()
    print(f"Reply: {reply}")
    correct = answer.lower() in reply.lower()
    print(f"Correct: {correct}")
    print()

    # 再测 32k
    print("=== Smoke test: 32k context, needle at 50% ===")
    context, answer = build_context(32000, 0.5)
    est_tokens = len(context) // 4
    print(f"Context length: {len(context)} chars (~{est_tokens} tokens)")
    r, dt = call_api(context, QUESTION)
    print(f"HTTP {r.status_code} in {dt:.1f}s")
    if r.status_code == 200:
        data = r.json()
        usage = data.get("usage", {})
        print(f"Usage: prompt_tokens={usage.get('prompt_tokens')}, completion_tokens={usage.get('completion_tokens')}")
        reply = data["choices"][0]["message"]["content"].strip()
        print(f"Reply: {reply}")
        correct = answer.lower() in reply.lower()
        print(f"Correct: {correct}")
    else:
        print(f"Error: {r.text[:500]}")


if __name__ == "__main__":
    main()
