"""
B.8 租约锁实证验证
===================
模式 10：分布式物理底座租约锁与看门狗。
验证定理：互斥安全性、看门狗活性、到期写权限消灭、心跳防护。
验证方式：离散时钟状态机模拟，多智能体并发场景。
"""
import json, random

SEED = 2026
random.seed(SEED)
N_TRIALS = 10000
TTL = 10  # 租约 TTL（tick 数）

class LeaseLock:
    """离散时钟租约锁模拟器。"""
    def __init__(self):
        self.clock = 0
        self.lease = None  # (holder_id, expire_tick)

    def tick(self):
        self.clock += 1
        if self.lease and self.clock > self.lease[1]:
            self.lease = None  # 到期回收

    def acquire(self, agent_id):
        if self.lease is None:
            self.lease = (agent_id, self.clock + TTL)
            return True
        return False

    def heartbeat(self, agent_id):
        if self.lease and self.lease[0] == agent_id:
            self.lease = (agent_id, self.clock + TTL)
            return True
        return False

    def can_write(self, agent_id):
        return self.lease is not None and self.lease[0] == agent_id and self.clock <= self.lease[1]

# ---------- 定理 1：互斥安全性 ----------
def test_mutual_exclusion():
    """同一时刻至多一个智能体持有写权限。"""
    for _ in range(N_TRIALS):
        lock = LeaseLock()
        agents = [0, 1, 2]
        for t in range(50):
            lock.tick()
            for a in agents:
                lock.acquire(a)
            writers = [a for a in agents if lock.can_write(a)]
            if len(writers) > 1:
                return False
    return True

# ---------- 定理 2：看门狗活性（无永久锁死） ----------
def test_no_permanent_lockout():
    """崩溃持有者的租约必然在 TTL 到期后回收。"""
    for _ in range(N_TRIALS):
        lock = LeaseLock()
        # agent 0 获取租约后"崩溃"（不再心跳）
        lock.acquire(0)
        # 快进 TTL + 1 tick
        for _ in range(TTL + 1):
            lock.tick()
        # agent 1 应能获取
        if not lock.acquire(1):
            return False
    return True

# ---------- 定理 3：到期写权限消灭 ----------
def test_expired_write_revoked():
    """到期后原持有者写权限消灭。"""
    for _ in range(N_TRIALS):
        lock = LeaseLock()
        lock.acquire(0)
        for _ in range(TTL + 1):
            lock.tick()
        if lock.can_write(0):
            return False
    return True

# ---------- 定理 4：心跳防护 ----------
def test_heartbeat_protection():
    """非持有者心跳被拒绝；持有者续约不缩短租约。"""
    for _ in range(N_TRIALS):
        lock = LeaseLock()
        lock.acquire(0)
        expire_before = lock.lease[1]
        # 非持有者心跳
        if lock.heartbeat(1):
            return False
        # 持有者续约
        lock.tick()
        lock.heartbeat(0)
        expire_after = lock.lease[1]
        if expire_after < expire_before:
            return False
    return True

# ---------- 定理 5：并发写写冲突不可能 ----------
def test_concurrent_write_impossible():
    """失效场景 A：两个可写者必为同一人。"""
    for _ in range(N_TRIALS):
        lock = LeaseLock()
        agents = list(range(5))
        for t in range(100):
            lock.tick()
            random.shuffle(agents)
            for a in agents:
                lock.acquire(a)
                if random.random() < 0.3:
                    lock.heartbeat(a)
            writers = [a for a in agents if lock.can_write(a)]
            if len(writers) > 1:
                return False
    return True

results = {
    "mutual_exclusion": test_mutual_exclusion(),
    "no_permanent_lockout": test_no_permanent_lockout(),
    "expired_write_revoked": test_expired_write_revoked(),
    "heartbeat_protection": test_heartbeat_protection(),
    "concurrent_write_impossible": test_concurrent_write_impossible(),
}

all_pass = all(results.values())

summary = {
    "theorem": "B.8 租约锁（模式 10）",
    "date": "2026-10-21",
    "trials_per_test": N_TRIALS,
    "results": results,
    "verdict": "PASS" if all_pass else "FAIL",
}

with open("b8_lease_lock_sim.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"B.8 verdict: {summary['verdict']}")
for k, v in results.items():
    print(f"  {k}: {'PASS' if v else 'FAIL'}")
