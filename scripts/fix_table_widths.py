# -*- coding: utf-8 -*-
"""专著宽表列宽修复（B 修订管线，可复现）。

pandoc 对 7 列 pipe table 均分列宽（1/7），导致编号列过宽、Lean 模块列不足。
本脚本把全书唯一的 7 列均分块（24 模式可追溯矩阵，pandoc 0.1429）替换为
自定义列宽比例：编号 0.06 / 模式 0.12 / 正文锚点 0.11 / Lean模块 0.28 /
实证证据 0.20 / 文中指标 0.11 / 类型 0.12（和 = 1.00）。

用法: python fix_table_widths.py <manuscript-latex.tex>
在 pandoc 生成 tex 之后、xelatex 编译之前运行。
"""
import re
import sys
import pathlib

TEX = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else
                   r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.tex")

COL = r">{\raggedright\arraybackslash}p{(\linewidth - 12\tabcolsep) * \real{0.1429}}"
COL_LAST = COL + r"@{}}"
NEW_COLS = [0.06, 0.12, 0.11, 0.28, 0.20, 0.11, 0.12]

lines = TEX.read_text(encoding="utf-8").split("\n")
n = 0
for idx, ln in enumerate(lines):
    stripped = ln.strip()
    if stripped.startswith(r"\begin{longtable}") and stripped.endswith(r"{@{}"):
        # pandoc 7 列结构：6 行纯列定义 + 第 7 行带 @{}} 后缀
        if (idx + 7 < len(lines)
                and all(lines[idx + 1 + k].strip() == COL for k in range(6))
                and lines[idx + 7].strip() == COL_LAST):
            for k in range(7):
                w = NEW_COLS[k]
                body = r">{\raggedright\arraybackslash}p{(\linewidth - 12\tabcolsep) * \real{" + f"{w:.4f}" + r"}}"
                if k < 6:
                    lines[idx + 1 + k] = "  " + body
                else:
                    lines[idx + 7] = "  " + body + r"@{}}"
            n += 1
            break

print(f"replaced blocks: {n}")
if n != 1:
    sys.exit(1)
TEX.write_text("\n".join(lines), encoding="utf-8")
print("written:", TEX)
