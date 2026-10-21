"""
E4 快速冒烟 v3：测 256k/512k 衰减趋势 + 调查空回复
"""
import os, json, time, random, requests

def load_env(path):
    env = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env

env = load_env(r"E:\workspace\DevForge-AI\.env")
API_KEY = env["KIMI_API_KEY"]; BASE_URL = env["KIMI_BASE_URL"]; MODEL = env["KIMI_MODEL"]
random.seed(1020)

NEEDLE_FACT = "The secret magic color is periwinkle blue."
QUESTION = "What is the secret magic color? Answer with only the color word."

FILLER_TEMPLATES = [
    "The {adj} {noun} {verb} across the {place} while {ing} {thing}.",
    "Researchers found that {thing} can {verb} when exposed to {adj} conditions.",
    "In {year}, the {noun} was first {verb}ed by scientists studying {thing}.",
    "The {adj} properties of {thing} make it suitable for {place} applications.",
    "Many {noun}s rely on {thing} to {verb} during {season} months.",
]
ADJS=["rapid","slow","complex","simple","ancient","modern","natural","artificial","stable","variable"]
NOUNS=["system","process","mechanism","structure","pattern","phenomenon","element","component","method","approach"]
VERBS=["move","change","grow","shrink","expand","contract","evolve","adapt","respond","interact"]
PLACES=["forest","ocean","desert","mountain","river","valley","coast","plain","tundra","wetland"]
INGS=["absorbing","releasing","transforming","conducting","regulating","generating","storing","transmitting"]
THINGS=["energy","water","heat","light","carbon","oxygen","nitrogen","minerals","nutrients","signals"]
YEARS=list(range(1800,2024)); SEASONS=["spring","summer","autumn","winter"]

def make_filler_paragraph():
    sents=[]
    for _ in range(5):
        t=random.choice(FILLER_TEMPLATES)
        sents.append(t.format(adj=random.choice(ADJS),noun=random.choice(NOUNS),verb=random.choice(VERBS),
            place=random.choice(PLACES),ing=random.choice(INGS),thing=random.choice(THINGS),
            year=random.choice(YEARS),season=random.choice(SEASONS)))
    return " ".join(sents)

def build_context(target_tokens, pos=0.5):
    pt=50; n=max(1,target_tokens//pt); nb=int(n*pos); na=n-nb
    parts=[]
    for i in range(nb): parts.append(f"[Doc {i}] "+make_filler_paragraph())
    parts.append(f"[FACT] {NEEDLE_FACT}")
    for i in range(na): parts.append(f"[Doc {nb+1+i}] "+make_filler_paragraph())
    return "\n\n".join(parts), "periwinkle blue"

def call_api(context, question, max_tokens=200):
    url=f"{BASE_URL}/chat/completions"
    h={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"}
    p={"model":MODEL,"messages":[{"role":"system","content":"Answer the question using only information from the context. Give a short answer."},
        {"role":"user","content":f"Context:\n{context}\n\nQuestion: {question}"}],"max_tokens":max_tokens,"temperature":1.0}
    t0=time.time(); r=requests.post(url,headers=h,json=p,timeout=300); dt=time.time()-t0
    return r, dt

def run_one(target_tokens, pos=0.5):
    context,answer=build_context(target_tokens,pos)
    r,dt=call_api(context,QUESTION)
    if r.status_code!=200: return {"ok":False,"status":r.status_code,"error":r.text[:300],"dt":dt}
    d=r.json(); u=d.get("usage",{})
    reply=d["choices"][0]["message"]["content"].strip()
    finish=d["choices"][0].get("finish_reason","")
    correct=answer.lower() in reply.lower()
    return {"ok":True,"dt":dt,"correct":correct,"reply":reply[:120],"finish":finish,
            "prompt_tokens":u.get("prompt_tokens"),"completion_tokens":u.get("completion_tokens")}

for ctx in [256000, 512000]:
    print(f"\n=== {ctx} tokens target, reps=2 ===")
    for i in range(2):
        r=run_one(ctx,0.5)
        if r["ok"]:
            print(f"  run {i+1}: correct={r['correct']} finish={r['finish']} "
                  f"completion_tokens={r['completion_tokens']} reply='{r['reply']}' "
                  f"prompt_tokens={r['prompt_tokens']} dt={r['dt']:.1f}s")
        else:
            print(f"  run {i+1}: ERROR {r['status']} {r['error']}")
