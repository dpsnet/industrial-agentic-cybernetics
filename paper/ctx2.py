# -*- coding: utf-8 -*-
import io
pairs = [
    ("07-capacity-regulation.md", [8, 12, 16, 20]),
    ("08-discussion.md", [7, 17]),
    ("10-scope.md", [8]),
]
base = r"E:\workspace\industrial-agentic-cybernetics\paper\sections"
for fn, lns in pairs:
    lines = io.open(base + "\\" + fn, encoding="utf-8").read().splitlines()
    for l in lns:
        i = l - 1
        print("=== %s L%d" % (fn, l))
        print("  %d: %s" % (l, lines[i][:120]))
        if i + 1 < len(lines):
            print("  %d: %s" % (l + 1, lines[i + 1][:150]))
        if i + 2 < len(lines):
            print("  %d: %s" % (l + 2, lines[i + 2][:150]))
