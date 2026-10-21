"""E4 冒烟 v4：测 1M 上下文（Kimi 标称上限）"""
import os, time, random, requests

def load_env(path):
    env={}
    with open(path,encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            k,v=line.split("=",1); env[k.strip()]=v.strip()
    return env

env=load_env(r"E:\workspace\DevForge-AI\.env")
API_KEY=env["KIMI_API_KEY"]; BASE_URL=env["KIMI_BASE_URL"]; MODEL=env["KIMI_MODEL"]
random.seed(1021)

NEEDLE_FACT="The secret magic color is periwinkle blue."
QUESTION="What is the secret magic color? Answer with only the color word."

F=["The {adj} {noun} {verb} across the {place} while {ing} {thing}.",
   "Researchers found that {thing} can {verb} when exposed to {adj} conditions.",
   "In {year}, the {noun} was first {verb}ed by scientists studying {thing}.",
   "The {adj} properties of {thing} make it suitable for {place} applications.",
   "Many {noun}s rely on {thing} to {verb} during {season} months."]
A=["rapid","slow","complex","simple","ancient","modern","natural","artificial","stable","variable"]
N=["system","process","mechanism","structure","pattern","phenomenon","element","component","method","approach"]
V=["move","change","grow","shrink","expand","contract","evolve","adapt","respond","interact"]
P=["forest","ocean","desert","mountain","river","valley","coast","plain","tundra","wetland"]
I=["absorbing","releasing","transforming","conducting","regulating","generating","storing","transmitting"]
T=["energy","water","heat","light","carbon","oxygen","nitrogen","minerals","nutrients","signals"]
Y=list(range(1800,2024)); S=["spring","summer","autumn","winter"]

def mkfp():
    s=[]
    for _ in range(5):
        t=random.choice(F)
        s.append(t.format(adj=random.choice(A),noun=random.choice(N),verb=random.choice(V),
            place=random.choice(P),ing=random.choice(I),thing=random.choice(T),
            year=random.choice(Y),season=random.choice(S)))
    return " ".join(s)

def build(target_tokens,pos=0.5):
    pt=50; n=max(1,target_tokens//pt); nb=int(n*pos); na=n-nb
    parts=[]
    for i in range(nb): parts.append(f"[Doc {i}] "+mkfp())
    parts.append(f"[FACT] {NEEDLE_FACT}")
    for i in range(na): parts.append(f"[Doc {nb+1+i}] "+mkfp())
    return "\n\n".join(parts),"periwinkle blue"

def call(context,question,max_tokens=200):
    url=f"{BASE_URL}/chat/completions"
    h={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"}
    p={"model":MODEL,"messages":[{"role":"system","content":"Answer the question using only information from the context. Give a short answer."},
        {"role":"user","content":f"Context:\n{context}\n\nQuestion: {question}"}],"max_tokens":max_tokens,"temperature":1.0}
    t0=time.time(); r=requests.post(url,headers=h,json=p,timeout=600); dt=time.time()-t0
    return r,dt

def run(target,pos=0.5):
    ctx,ans=build(target,pos)
    r,dt=call(ctx,QUESTION)
    if r.status_code!=200: return {"ok":False,"status":r.status_code,"err":r.text[:300],"dt":dt}
    d=r.json(); u=d.get("usage",{})
    reply=d["choices"][0]["message"]["content"].strip()
    finish=d["choices"][0].get("finish_reason","")
    return {"ok":True,"dt":dt,"correct":ans.lower() in reply.lower(),"reply":reply[:120],
            "finish":finish,"pt":u.get("prompt_tokens"),"ct":u.get("completion_tokens")}

for ctx in [700000]:
    print(f"=== {ctx} tokens target (~1M actual), reps=2 ===")
    for i in range(2):
        r=run(ctx,0.5)
        if r["ok"]:
            print(f"  run {i+1}: correct={r['correct']} finish={r['finish']} ct={r['ct']} "
                  f"reply='{r['reply']}' pt={r['pt']} dt={r['dt']:.1f}s")
        else:
            print(f"  run {i+1}: ERROR {r['status']} {r['err']}")
