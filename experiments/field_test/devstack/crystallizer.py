# 缺陷模式萃取器（模式 24 前段）：LLM（DeepSeek-V4.1-Flash-1017 via scnet 网关）
# 输入：审计通过的异常事件（指标信号 + 状态），禁止透露场景标签（F1/F2/F3）
# 输出：缺陷模式 JSON（type / evidence / root_cause_hypothesis / fix_hint）

import json
import os
import time
import urllib.request

ALERT_FILE = os.environ.get("IAC_ALERT_FILE", "/dev/audit/alerts.jsonl")
PATTERN_FILE = os.environ.get("IAC_PATTERN_FILE", "/dev/audit/patterns.jsonl")
LLM_API_KEY = os.environ.get("IAC_LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("IAC_LLM_BASE_URL", "")
LLM_MODEL = os.environ.get("IAC_LLM_MODEL", "DeepSeek-V4.1-Flash-1017")
TEMPERATURE = float(os.environ.get("IAC_LLM_TEMPERATURE", "0.7"))
POLL = float(os.environ.get("IAC_CRYST_POLL", "3"))

APP_CODE_SNIPPET = """被测服务代码要点（app/main.py 摘要）：
- 连接池：_acquire_conn()/_release_conn(cid)，池上限 IAC_POOL_SIZE（20）
- 缓存：LRU OrderedDict，_cache_capacity；_cache_put 正常时淘汰最旧键
- /search 路径：查缓存 → 借用连接 → 伪 DB 查询 → 缓存写入 → 释放连接
- /downstream：经 toxiproxy 代理调用下游（F2 的延迟在此注入）
- /metrics：connection_pool_active / p99_latency_ms / memory_usage_bytes"""

PROMPT_TEMPLATE = """你是生产系统的缺陷分析工程师。下面是一次运行时异常事件（已通过独立审计，指标真实）。
请基于指标信号与代码要点，识别可能的缺陷类型、证据与根因假设，并给出修复方向。
只允许依据事件数据与代码要点推断，不要编造事件中不存在的信号。

异常事件（JSON）：
{event_json}

代码要点：
{code_snippet}

输出严格为 JSON：
{{"type": "<缺陷类型: conn_leak|downstream_latency|mem_leak|unknown>",
 "evidence": ["<支持证据1>", ...],
 "root_cause_hypothesis": "<一句话根因假设>",
 "fix_hint": "<修复方向，如 try-with-resources/缓存淘汰策略/超时设置>"}}"""


def call_llm(messages):
    body = json.dumps({
        "model": LLM_MODEL, "messages": messages, "temperature": TEMPERATURE,
        "max_tokens": 2000, "response_format": {"type": "json_object"},
    }).encode()
    req = urllib.request.Request(f"{LLM_BASE_URL}/chat/completions", data=body,
                                 headers={"Authorization": f"Bearer {LLM_API_KEY}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        j = json.loads(r.read().decode())
    content = j["choices"][0]["message"]["content"]
    return json.loads(content)


def main():
    if not LLM_API_KEY:
        print("crystallizer: IAC_LLM_API_KEY not set, standby", flush=True)
        return
    offset = 0
    while True:
        try:
            with open(ALERT_FILE) as f:
                lines = f.readlines()
        except Exception:
            lines = []
        new_lines = lines[offset:]
        offset = len(lines)
        for line in new_lines:
            try:
                alert = json.loads(line)
            except Exception:
                continue
            event_json = json.dumps(alert, ensure_ascii=False)
            prompt = PROMPT_TEMPLATE.format(event_json=event_json, code_snippet=APP_CODE_SNIPPET)
            try:
                pattern = call_llm([{"role": "user", "content": prompt}])
                pattern["_event"] = alert.get("event", "")
                pattern["_model"] = LLM_MODEL
                pattern["_ts"] = time.time()
                with open(PATTERN_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(pattern, ensure_ascii=False) + "\n")
                print(f"pattern: {pattern.get('type')} for {pattern['_event']}", flush=True)
            except Exception as e:
                print(f"crystallize error: {e!r}", flush=True)
        time.sleep(POLL)


if __name__ == "__main__":
    main()
