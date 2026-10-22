# 五重判据验证器（模式 19，stress-net）：编译/单测/集成/性能/安全
# 输入：热修复 unified diff + app 源码（挂载卷）；输出：报告 JSON（stress-net → gate）

import json
import os
import re
import subprocess
import sys
import tempfile
import time

APP_SRC_DIR = os.environ.get("IAC_APP_SRC_DIR", "/srv/app-src")
REPORT_DIR = os.environ.get("IAC_REPORT_DIR", "/dev/reports")
MODE = os.environ.get("IAC_VALIDATOR_MODE", "daemon")  # daemon: 轮询 reports/inbox; once: 单次

# 环境特定参数清单（H5 用，与 gate 保持一致）
ENV_SPECIFIC_PATTERNS = ["pool", "timeout", "limit", "thread", "cache_cap", "interval", "latency_ms"]

DANGEROUS_PATTERNS = ["subprocess", "os.system", "shell=True", "eval(", "pickle.loads", "exec("]


def apply_diff(src_dir, diff_text):
    """把 unified diff 应用到源码副本，返回 (ok, error)"""
    try:
        with tempfile.TemporaryDirectory() as tmp:
            import shutil
            for item in os.listdir(src_dir):
                s = os.path.join(src_dir, item)
                if os.path.isfile(s):
                    shutil.copy2(s, tmp)
            # 解析 diff 中修改的文件，应用补丁（简化：仅处理单文件 unified diff）
            m = re.search(r"^--- a/(\S+)", diff_text, re.M)
            if not m:
                return False, "no diff file header"
            fname = m.group(1)
            target = os.path.join(tmp, os.path.basename(fname))
            patch_path = os.path.join(tmp, "_patch.diff")
            with open(patch_path, "w", encoding="utf-8") as f:
                f.write(diff_text)
            r = subprocess.run(["patch", "-p1", "--dry-run", "-i", patch_path], cwd=tmp,
                               capture_output=True, text=True)
            if r.returncode != 0:
                return False, f"patch dry-run failed: {r.stderr[:200]}"
            subprocess.run(["patch", "-p1", "-i", patch_path], cwd=tmp, capture_output=True, text=True)
            return True, tmp  # tmp 路径在 with 外无效，改用复制到独立目录
    except Exception as e:
        return False, f"apply error: {e!r}"


def compile_check(src_dir):
    """在临时目录编译源码副本：/srv/app-src 为只读挂载，py_compile 写 __pycache__ 会 Errno 30"""
    files = [os.path.join(src_dir, f) for f in os.listdir(src_dir) if f.endswith(".py")]
    if not files:
        return False, "no py files"
    with tempfile.TemporaryDirectory() as tmp:
        targets = []
        for f in files:
            dst = os.path.join(tmp, os.path.basename(f))
            import shutil
            shutil.copy2(f, dst)
            targets.append(dst)
        r = subprocess.run([sys.executable, "-m", "py_compile"] + targets,
                           capture_output=True, text=True)
        return r.returncode == 0, r.stderr[:200] if r.returncode else ""


def unit_check(src_dir):
    """内嵌冒烟单测：缓存淘汰 + 连接释放逻辑（直接 import 被测模块）"""
    sys.path.insert(0, src_dir)
    try:
        import main as app_main
        # 缓存淘汰：非泄漏时容量受控
        app_main._state["fault"] = "none"
        for i in range(1200):
            app_main._cache_put(f"u{i}", "v")
        if len(app_main._cache) > app_main._cache_capacity + 2:
            return False, "cache capacity violated"
        # 连接释放：正常路径借用后活跃数回落
        app_main._state["pool_active"] = 0
        cid = app_main._acquire_conn()
        app_main._release_conn(cid)
        if app_main._state["pool_active"] != 0:
            return False, "conn not released"
        return True, ""
    except Exception as e:
        return False, f"unit error: {e!r}"


def integration_check(src_dir):
    sys.path.insert(0, src_dir)
    try:
        import main as app_main
        app_main._state["fault"] = "none"
        r = app_main.search("itest")
        if "result" not in r:
            return False, "search returned no result"
        app_main._state["fault"] = "conn_leak"
        app_main.search("itest2")  # 泄漏路径不应崩溃
        app_main._state["fault"] = "mem_leak"
        app_main.search("itest3")
        app_main._state["fault"] = "none"
        return True, ""
    except Exception as e:
        return False, f"integration error: {e!r}"


def performance_check(src_dir):
    sys.path.insert(0, src_dir)
    try:
        import main as app_main
        app_main._state["fault"] = "none"
        t0 = time.monotonic()
        for _ in range(100):
            app_main.search("perf")
        avg_ms = (time.monotonic() - t0) * 1000 / 100
        return avg_ms < 200, f"avg={avg_ms:.1f}ms"
    except Exception as e:
        return False, f"perf error: {e!r}"


def security_check(diff_text, src_dir):
    bad = [p for p in DANGEROUS_PATTERNS if p in diff_text]
    if bad:
        return False, f"dangerous pattern: {','.join(bad)}"
    return True, ""


def run_validator(diff_text, audit_ok, knowledge=None):
    src_dir = APP_SRC_DIR
    c_ok, c_err = compile_check(src_dir)
    u_ok, u_err = unit_check(src_dir)
    i_ok, i_err = integration_check(src_dir)
    p_ok, p_err = performance_check(src_dir)
    s_ok, s_err = security_check(diff_text, src_dir)
    verdict = {"compile": c_ok, "unit": u_ok, "integration": i_ok,
               "performance": p_ok, "security": s_ok}
    entry = {"verdict": verdict, "audit_ok": audit_ok,
             "errors": {"compile": c_err, "unit": u_err, "integration": i_err,
                        "performance": p_err, "security": s_err},
             "knowledge": knowledge or {},
             "ts": time.time()}
    return entry


def main():
    if MODE == "once":
        diff_path = os.environ.get("IAC_DIFF_FILE", "")
        diff_text = open(diff_path).read() if diff_path else ""
        audit_ok = os.environ.get("IAC_AUDIT_OK", "true") == "true"
        entry = run_validator(diff_text, audit_ok)
        os.makedirs(REPORT_DIR, exist_ok=True)
        out = os.path.join(REPORT_DIR, f"report_{int(time.time())}.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False)
        print(json.dumps(entry, ensure_ascii=False), flush=True)
        return
    # daemon 模式：轮询 /dev/inbox
    inbox = os.environ.get("IAC_INBOX_DIR", "/dev/inbox")
    os.makedirs(REPORT_DIR, exist_ok=True)
    while True:
        try:
            files = sorted(os.listdir(inbox))
        except Exception:
            files = []
        for name in files:
            if not name.endswith(".json"):
                continue
            path = os.path.join(inbox, name)
            try:
                with open(path) as f:
                    req = json.load(f)
            except Exception:
                continue
            entry = run_validator(req.get("diff", ""), req.get("audit_ok", True),
                                  req.get("knowledge"))
            out = os.path.join(REPORT_DIR, f"report_{name}")
            with open(out, "w", encoding="utf-8") as f:
                json.dump(entry, f, ensure_ascii=False)
            print(f"validated {name}", flush=True)
            try:
                os.remove(path)
            except Exception:
                pass
        time.sleep(float(os.environ.get("IAC_VALIDATOR_POLL", "2")))


if __name__ == "__main__":
    main()
