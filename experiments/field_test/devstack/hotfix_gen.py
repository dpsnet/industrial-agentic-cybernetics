# 热修复生成器（模式 24 后段）：LLM 生成 unified diff（默认 DRAFT_SUSPECT）
# 输入：缺陷模式 + app 源码关键片段；输出：unified diff → validator（五重判据）

import json
import os
import time
import urllib.request

PATTERN_FILE = os.environ.get("IAC_PATTERN_FILE", "/dev/audit/patterns.jsonl")
INBOX_DIR = os.environ.get("IAC_INBOX_DIR", "/dev/inbox")
LLM_API_KEY = os.environ.get("IAC_LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("IAC_LLM_BASE_URL", "")
LLM_MODEL = os.environ.get("IAC_LLM_MODEL", "DeepSeek-V4.1-Flash-1017")
TEMPERATURE = float(os.environ.get("IAC_LLM_TEMPERATURE", "0.7"))
POLL = float(os.environ.get("IAC_HOTFIX_POLL", "3"))

APP_CODE = """被测服务代码要点（app/main.py 摘要）：
- 连接池：_acquire_conn() 在 fault==conn_leak 时不计数/不释放；正常路径 _release_conn(cid) 仅释放非 "leaked"
- 缓存：LRU OrderedDict _cache_put；fault==mem_leak 时无淘汰（键空间持续增长）
- /downstream：经 toxiproxy 代理调用下游（延迟由代理注入，非代码缺陷）
- /metrics：connection_pool_active / p99_latency_ms / memory_usage_bytes"""

PROMPT_TEMPLATE = """你是资深后端工程师。下面是生产系统的一个缺陷模式（已由分析器萃取、事件已审计）。
请生成修复该缺陷的 **unified diff**（只针对 app/main.py，格式：--- a/main.py / +++ b/main.py）。
要求：
1. 修复必须是针对缺陷根因的最小改动；
2. 不得改变正常路径的行为（缓存淘汰、连接释放、/metrics 输出格式）；
3. 输出严格为 JSON：{{"diff": "<完整 unified diff 文本>"}}。

缺陷模式（JSON）：
{pattern_json}

代码要点：
{code}"""


def call_llm(messages):
    body = json.dumps({
        "model": LLM_MODEL, "messages": messages, "temperature": TEMPERATURE,
        "max_tokens": 4000, "response_format": {"type": "json_object"},
    }).encode()
    req = urllib.request.Request(f"{LLM_BASE_URL}/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {LLM_API_KEY}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        j = json.loads(r.read().decode())
    return json.loads(j["choices"][0]["message"]["content"])


def main():
    if not LLM_API_KEY:
        print("hotfix-gen: IAC_LLM_API_KEY not set, standby", flush=True)
        return
    os.makedirs(INBOX_DIR, exist_ok=True)
    offset = 0
    while True:
        try:
            with open(PATTERN_FILE) as f:
                lines = f.readlines()
        except Exception:
            lines = []
        new_lines = lines[offset:]
        offset = len(lines)
        for line in new_lines:
            try:
                pattern = json.loads(line)
            except Exception:
                continue
            prompt = PROMPT_TEMPLATE.format(pattern_json=json.dumps(pattern, ensure_ascii=False),
                                            code=APP_CODE)
            try:
                res = call_llm([{"role": "user", "content": prompt}])
                diff = res.get("diff", "")
                knowledge = {k: v for k, v in pattern.items() if not k.startswith("_")}
                req = {"diff": diff, "audit_ok": True, "knowledge": knowledge,
                       "pattern_event": pattern.get("_event", ""),
                       "_model": LLM_MODEL, "_ts": time.time()}
                out = os.path.join(INBOX_DIR, f"hotfix_{pattern.get('_event', 'x')}.json")
                with open(out, "w", encoding="utf-8") as f:
                    json.dump(req, f, ensure_ascii=False)
                print(f"hotfix written for {req['pattern_event']} (diff {len(diff)} chars)", flush=True)
            except Exception as e:
                print(f"hotfix error: {e!r}", flush=True)
        time.sleep(POLL)


if __name__ == "__main__":
    main()
