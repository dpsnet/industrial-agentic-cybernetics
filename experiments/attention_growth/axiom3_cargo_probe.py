#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公理 III（变异因果单调）Cargo 实证脚本（v2）
对应 EXPERIMENT_PLAN_AXIOM3.md §4（预注册判读标准 2026-10-20 修订版）

重建判据：cargo build 输出中的 "Compiling <pkg>" 行（v1 的 Dirty/Fresh 行解析不适用于 build），
并以产物 sha 变化、bin stdout 作为行为佐证。

H1：可观测性充要条件（observable_iff_mtime_strict_mono）
  1a 内容变 + mtime 递增   → 预期重建，产物 stdout 更新
  1b 内容变 + mtime 停滞   → 预期跳过，产物 stdout 保持旧值（静默丢失，决定性检验）
  1c 内容变 + mtime 回拨   → 预期跳过（判别谓词形态：严格 >）
  1d 内容不变 + mtime +5s  → 预期重建且产物 stdout 不变（触发与时钟有关、与内容无关；
                             v1 运行发现参考时钟 R ≈ 上次构建完成时刻，故跳变量取 5s > R）

H2：日志幂等性（log_append_apply_idempotent）
  2a baseline 后连续 5 次无变化 build → 全部跳过，产物 sha 不变
  2b git init/commit → 改 v1 → build → stash 回退 → build → stash pop → build
      → 两次恢复后重建，产物 sha 与对应版本一致（重试不污染）
  2c WAL 回放模拟（对应 Lean 的 Journal / applyLoggedMutation 语义）
      → 首次应用 hashVerified=True；对已记日志的重复回放 hashVerified=False 且内容不变

输出：axiom3_results.json（与本脚本同目录）
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

PKG_BASE = "axiom3_probe"
ENV = {**os.environ, "CARGO_NET_OFFLINE": "true"}
NS = 1_000_000_000  # 1 second in nanoseconds
ANSI = re.compile(r"\x1b(?:\[[0-9;]*[A-Za-z]|\]8;;[^\x1b]*\x1b\\)")


def sh(cmd, cwd=None, timeout=120):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                          errors="replace", timeout=timeout, env=ENV)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def set_mtime_ns(p, ns):
    os.utime(p, ns=(ns, ns))


def get_mtime_ns(p):
    return os.stat(p).st_mtime_ns


class Proj:
    """最小 Cargo 项目：单文件 bin，产物 stdout 即内容标记"""

    def __init__(self, root, tag):
        self.pkg = f"{PKG_BASE}_{tag}"
        self.dir = root / self.pkg
        r = sh(["cargo", "new", "--quiet", "--vcs", "none", str(self.dir)])
        assert r.returncode == 0, f"cargo new failed: {r.stderr}"
        self.main = self.dir / "src" / "main.rs"
        self.exe = self.dir / "target" / "debug" / f"{self.pkg}.exe"
        self.write("v0")

    def write(self, tag):
        # write_text 会把 mtime 更新为当前时间
        self.main.write_text(f'fn main() {{ println!("{tag}"); }}\n', encoding="utf8")

    def build(self):
        before = sha256_file(self.exe) if self.exe.exists() else None
        t0 = time.perf_counter()
        r = sh(["cargo", "build", "-v"], cwd=self.dir)
        el = time.perf_counter() - t0
        if r.returncode != 0:
            # exe 可能被 AV/索引器短暂锁定，重试一次
            time.sleep(0.5)
            t0 = time.perf_counter()
            r = sh(["cargo", "build", "-v"], cwd=self.dir)
            el = time.perf_counter() - t0
        out = ANSI.sub("", (r.stdout or "") + (r.stderr or ""))
        stdout, sha = None, None
        if self.exe.exists():
            c = sh([str(self.exe)])
            stdout = (c.stdout or "").strip()
            sha = sha256_file(self.exe)
        # 重建判据：Compiling 行（ANSI 剥离后）为主，产物 sha 变化为辅
        rebuilt = (f"Compiling {self.pkg}" in out
                   or (sha is not None and before is not None and sha != before))
        return {"rebuilt": rebuilt, "elapsed_s": round(el, 3), "rc": r.returncode,
                "bin_stdout": stdout, "sha256": sha,
                "sha_changed": (sha != before) if (sha and before) else None}


def run_h1(root, group, reps=5):
    """H1 四组：每组建新项目，baseline build 记录 T0，再做 5 次操控"""
    p = Proj(root, group)
    base = p.build()
    T0 = get_mtime_ns(p.main)  # baseline build 后文件的 mtime
    rows = [{"rep": 0, "phase": "baseline", "mtime_ns": T0, **base}]
    for i in range(1, reps + 1):
        if group == "1a":
            p.write(f"v{i}")                    # mtime 自然递增（当前时间）
            time.sleep(0.002)
            expect = "rebuild_new_output"
        elif group == "1b":
            p.write(f"w{i}")                    # 内容变化
            set_mtime_ns(p.main, T0)            # mtime 恢复为 baseline 值（停滞）
            expect = "skip_silent_loss"
        elif group == "1c":
            p.write(f"x{i}")                    # 内容变化
            set_mtime_ns(p.main, T0 - 3600 * NS)  # mtime 回拨 1 小时
            expect = "skip_silent_loss"
        elif group == "1d":
            # 内容不变，mtime +5s（跳过参考时钟 R ≈ 上次构建完成时刻）
            set_mtime_ns(p.main, get_mtime_ns(p.main) + 5 * NS)
            expect = "rebuild_same_output"
        rec = p.build()
        ok = ((expect == "rebuild_new_output" and rec["rebuilt"] and rec["bin_stdout"] == f"v{i}")
              or (expect == "skip_silent_loss" and not rec["rebuilt"] and rec["bin_stdout"] == "v0")
              or (expect == "rebuild_same_output" and rec["rebuilt"] and rec["bin_stdout"] == "v0"))
        rows.append({"rep": i, "expect": expect, "mtime_ns": get_mtime_ns(p.main),
                     **rec, "pass": ok})
    return rows


def run_h2a(root, n=5):
    """2a：baseline 后连续 n 次无变化 build，预期全部跳过且 sha 不变"""
    p = Proj(root, "h2a")
    first = p.build()
    rows = [{"rep": 0, "phase": "baseline", **first}]
    for i in range(1, n + 1):
        rec = p.build()
        ok = (not rec["rebuilt"]) and rec["sha256"] == first["sha256"]
        rows.append({"rep": i, "phase": "noop_rebuild", "expect": "skip_same_sha",
                     **rec, "pass": ok})
    return rows


def run_h2b(root):
    """2b：git stash 回退 → build → stash pop 恢复 → build，重试后产物与对应版本一致"""
    p = Proj(root, "h2b")

    def g(*a):
        return sh(["git", *a], cwd=p.dir)

    g("init", "--quiet")
    g("config", "user.email", "probe@example.com")
    g("config", "user.name", "probe")
    (p.dir / ".gitignore").write_text("/target\n", encoding="utf8")  # 构建产物不入库，否则 stash pop 冲突
    p.build()                       # v0 baseline
    g("add", "-A")
    g("commit", "-q", "-m", "v0")
    p.write("v1")
    b1 = p.build()                  # 重建 → v1
    st = g("stash")                 # 内容回退到 v0（mtime 被 git 改写）
    b0 = p.build()                  # 重建 → v0
    pop = g("stash", "pop")         # 恢复 v1（mtime 再次改写）
    b1p = p.build()                 # 重建 → v1
    # 注：Windows PE 头含编译时间戳，同源码重编译的 sha 必然不同，
    # 故幂等性判据用"重试后语义输出恢复"而非字节级 sha 相等
    ok = (b1["rebuilt"] and b1["bin_stdout"] == "v1"
          and b0["rebuilt"] and b0["bin_stdout"] == "v0"
          and b1p["rebuilt"] and b1p["bin_stdout"] == "v1")
    git_out = lambda r: ((r.stdout or "") + (r.stderr or "")).strip()
    return {"scenario": "2b_stash_retry",
            "stash_out": git_out(st), "pop_out": git_out(pop),
            "b1": b1, "b0_after_stash": b0, "b1_after_pop": b1p, "pass": ok}


def run_h2c():
    """2c：WAL 回放模拟（直接对应 Lean 的 Journal / applyLoggedMutation 语义）"""
    journal = {"applied": []}

    def log_append(j, m):
        return {"applied": [m["mtApplied"]] + j["applied"]}

    def apply_logged(j, m):
        # 对应 applyLoggedMutation：hashVerified = mtApplied ∉ j.applied
        return {"content": m["content"],
                "hashVerified": m["mtApplied"] not in j["applied"]}

    m = {"target": 1, "content": 42, "mtApplied": 1000}
    assert m["mtApplied"] not in journal["applied"], "mutId 前提"
    first = apply_logged(journal, m)     # 首次应用：日志未含该时刻 → 校验通过
    j2 = log_append(journal, m)          # 记入日志
    second = apply_logged(j2, m)         # 重复回放：日志已含该时刻 → 校验失败，内容不变
    ok = (first["hashVerified"] is True and second["hashVerified"] is False
          and second["content"] == first["content"])
    return {"scenario": "2c_wal_replay_sim", "first": first, "second": second, "pass": ok}


def main():
    root = Path(tempfile.mkdtemp(prefix="axiom3_probe_"))
    print(f"workdir: {root}")
    results = {"meta": {
        "cargo": (sh(["cargo", "--version"]).stdout or "").strip(),
        "rustc": (sh(["rustc", "--version"]).stdout or "").strip(),
        "python": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "workdir": str(root),
        "rebuild_signal": "Compiling <pkg> line in cargo build -v output",
    }, "H1": {}, "H2": {}}

    for grp in ["1a", "1b", "1c", "1d"]:
        print(f"== H1 group {grp} ==")
        results["H1"][grp] = run_h1(root, grp)

    print("== H2 2a ==")
    results["H2"]["2a"] = run_h2a(root)
    print("== H2 2b ==")
    results["H2"]["2b"] = run_h2b(root)
    print("== H2 2c ==")
    results["H2"]["2c"] = run_h2c()

    h1_pass = all(r["pass"] for rows in results["H1"].values() for r in rows if "pass" in r)
    h2_pass = (all(r["pass"] for r in results["H2"]["2a"] if "pass" in r)
               and results["H2"]["2b"]["pass"] and results["H2"]["2c"]["pass"])
    results["verdict"] = {"H1_all_pass": h1_pass, "H2_all_pass": h2_pass}

    # 摘要打印
    for grp, rows in results["H1"].items():
        for r in rows:
            if r.get("rep", 0) == 0:
                continue
            print(f"[{grp}#{r['rep']}] expect={r['expect']:<20} rebuilt={r['rebuilt']!s:<5} "
                  f"stdout={r['bin_stdout']!s:<6} sha_chg={r['sha_changed']!s:<5} "
                  f"t={r['elapsed_s']:>6.3f}s pass={r['pass']}")
    for r in results["H2"]["2a"]:
        if r.get("rep", 0) == 0:
            continue
        print(f"[2a#{r['rep']}] expect={r['expect']:<20} rebuilt={r['rebuilt']!s:<5} "
              f"sha_same={not r['sha_changed']!s:<5} t={r['elapsed_s']:>6.3f}s pass={r['pass']}")
    b = results["H2"]["2b"]
    print(f"[2b] pass={b['pass']} b1={b['b1']['bin_stdout']}/{b['b1']['rebuilt']} "
          f"b0'={b['b0_after_stash']['bin_stdout']}/{b['b0_after_stash']['rebuilt']} "
          f"b1'={b['b1_after_pop']['bin_stdout']}/{b['b1_after_pop']['rebuilt']} "
          f"sha_eq={b['b1_after_pop']['sha256'] == b['b1']['sha256']}")
    print(f"[2c] pass={results['H2']['2c']['pass']} "
          f"first={results['H2']['2c']['first']} second={results['H2']['2c']['second']}")
    print(f"VERDICT: H1={h1_pass} H2={h2_pass}")

    out = Path(__file__).with_name("axiom3_results.json")
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf8")
    print(f"results -> {out}")

    shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
