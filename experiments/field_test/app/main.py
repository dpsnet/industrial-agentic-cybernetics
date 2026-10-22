# 被测服务：FastAPI + 连接池 + LRU 缓存 + /metrics
# 对应计划 §3 prod-net app；缺陷注入经 /admin/fault 动态开关（F1 连接泄漏 / F3 内存泄漏）
# F2 下游延迟经 toxiproxy 注入（本服务 /downstream 客户端指向 toxiproxy 代理）

import json
import os
import threading
import time
import uuid
from collections import OrderedDict
from urllib.request import urlopen

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Gauge, Histogram, generate_latest

app = FastAPI(title="iac-field-app")

FAULT_NONE = "none"
FAULT_CONN_LEAK = "conn_leak"
FAULT_MEM_LEAK = "mem_leak"

_state = {
    "fault": os.environ.get("IAC_FAULT", FAULT_NONE),
    "pool_active": 0,
    "pool_total": 0,
    "downstream_latency": 0.0,   # 最近一次下游调用延迟（经 toxiproxy）
}

_lock = threading.Lock()
_pool = OrderedDict()          # 自实现连接池：id -> 借用状态
_pool_size = int(os.environ.get("IAC_POOL_SIZE", "20"))
_downstream_url = os.environ.get("IAC_DOWNSTREAM_URL", "http://toxiproxy:8474/downstream")

# ---- LRU 缓存（正常有淘汰；F3 内存泄漏时无淘汰）----
_cache = OrderedDict()
_cache_capacity = int(os.environ.get("IAC_CACHE_CAP", "500"))
_cache_created = {}

# ---- metrics ----
METRIC_POOL_ACTIVE = Gauge("connection_pool_active", "active borrowed connections")
METRIC_POOL_TOTAL = Gauge("connection_pool_total", "total pool size")
METRIC_MEM_BYTES = Gauge("memory_usage_bytes", "estimated process memory usage bytes")
METRIC_P99_MS = Gauge("p99_latency_ms", "p99 latency in ms (sliding window)")
_LAT_WINDOW = deque_lock = None


def _now():
    return time.monotonic()


class SlidingLatency:
    """滑动窗口延迟采样（p99 估计）"""

    def __init__(self, window_s=120):
        self.window_s = window_s
        self._samples = []
        self._lock = threading.Lock()

    def add(self, ms):
        with self._lock:
            self._samples.append((time.monotonic(), ms))
            self._trim()

    def _trim(self):
        cutoff = time.monotonic() - self.window_s
        while self._samples and self._samples[0][0] < cutoff:
            self._samples.pop(0)

    def p99(self):
        with self._lock:
            self._trim()
            if not self._samples:
                return 0.0
            vals = sorted(s[1] for s in self._samples)
            idx = min(len(vals) - 1, int(0.99 * len(vals)))
            return vals[idx]

    def mean(self):
        with self._lock:
            self._trim()
            if not self._samples:
                return 0.0
            return sum(s[1] for s in self._samples) / len(self._samples)


latency = SlidingLatency()


def _mem_estimate():
    """估算进程内存：RSS + 缓存对象名义大小"""
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    rss_kb = int(line.split()[1])
                    return rss_kb * 1024 + len(_cache) * 2048
    except Exception:
        pass
    return len(_cache) * 2048


def _acquire_conn():
    with _lock:
        if _state["fault"] == FAULT_CONN_LEAK:
            _state["pool_active"] += 1
            return "leaked"
        if _state["pool_active"] < _pool_size:
            _state["pool_active"] += 1
            return "ok"
        return "full"


def _release_conn(cid):
    with _lock:
        if cid != "leaked" and _state["pool_active"] > 0:
            _state["pool_active"] -= 1


def _cache_get(key):
    with _lock:
        if key in _cache:
            _cache.move_to_end(key)
            return _cache[key]
        return None


def _cache_put(key, value):
    with _lock:
        if _state["fault"] == FAULT_MEM_LEAK:
            # F3：无淘汰策略，键空间持续增长
            _cache[key] = value
            _cache_created[key] = time.time()
            return
        _cache[key] = value
        _cache_created[key] = time.time()
        while len(_cache) > _cache_capacity:
            k, _ = _cache.popitem(last=False)
            _cache_created.pop(k, None)


def _fake_db_query(q):
    """模拟数据库查询（内存 mock），返回 128 字节结果"""
    time.sleep(0.001)
    return {"id": uuid.uuid4().hex, "q": q, "blob": "x" * 128}


@app.get("/healthz")
def healthz():
    return {"status": "ok", "fault": _state["fault"]}


@app.post("/admin/fault")
async def set_fault(req: Request):
    body = await req.json()
    f = body.get("fault", FAULT_NONE)
    if f not in (FAULT_NONE, FAULT_CONN_LEAK, FAULT_MEM_LEAK):
        return JSONResponse({"error": "unknown fault"}, status_code=400)
    _state["fault"] = f
    if f == FAULT_MEM_LEAK:
        # 预填充缓存模拟"已发生的泄漏"：3σ 判据对线性漂移不敏感，需要一次性暴涨信号
        # 台阶高度可由编排递增（prefill 递增 → 每 rep 相对前台阶突跳 → 逐 rep 触发）
        n = int(body.get("prefill", os.environ.get("IAC_MEM_LEAK_PREFILL", "50000")))
        _mem_leak_prefill(n)
    # 泄漏注入不可逆：支持编排侧重置状态，保证每个 rep 从干净基线开始
    if body.get("reset_pool"):
        _state["pool_active"] = 0
    if body.get("reset_cache"):
        _cache.clear()
        _state["cache_keys"] = len(_cache)
    return _state


def _mem_leak_prefill(n=None):
    if n is None:
        n = int(os.environ.get("IAC_MEM_LEAK_PREFILL", "50000"))
    for i in range(n):
        k = f"leak_prefill_{i}"
        if k not in _cache:
            _cache[k] = "x" * 128
            _cache_created[k] = time.time()


@app.get("/search")
def search(q: str = "default"):
    t0 = time.monotonic()
    cached = _cache_get("k:" + q)
    if cached is not None:
        lat_ms = (time.monotonic() - t0) * 1000
        latency.add(lat_ms)
        return {"cached": True, "q": q, "result": cached}
    cid = _acquire_conn()
    try:
        row = _fake_db_query(q)
        _cache_put("k:" + q, row["id"])
    finally:
        _release_conn(cid)
    lat_ms = (time.monotonic() - t0) * 1000
    latency.add(lat_ms)
    return {"cached": False, "q": q, "result": row["id"]}


@app.get("/downstream")
def downstream():
    """模拟对下游服务的调用（经 toxiproxy 代理，F2 延迟由此注入）"""
    t0 = time.monotonic()
    try:
        with urlopen(_downstream_url, timeout=10) as r:
            _ = r.read()
    except Exception:
        pass
    lat_ms = (time.monotonic() - t0) * 1000
    _state["downstream_latency"] = lat_ms
    latency.add(lat_ms)
    return {"downstream_ms": lat_ms}


@app.get("/metrics")
def metrics():
    METRIC_POOL_ACTIVE.set(_state["pool_active"])
    METRIC_POOL_TOTAL.set(_pool_size)
    METRIC_MEM_BYTES.set(_mem_estimate())
    METRIC_P99_MS.set(latency.p99())
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/state")
def state():
    return {
        "fault": _state["fault"],
        "pool_active": _state["pool_active"],
        "cache_keys": len(_cache),
        "downstream_latency": _state["downstream_latency"],
        "p99_ms": latency.p99(),
    }
