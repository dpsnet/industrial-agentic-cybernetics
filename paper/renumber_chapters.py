# -*- coding: utf-8 -*-
"""Renumber chapters after promoting former §7.6 to independent §7.

New order: §7 capacity regulation (new file, hand-written, skipped),
§8 Discussion (was §7), §9 mechanism revision (was §8), §10 scope (was §9),
§11 limitations (was §10), §12 conclusion (was §11).

Safe placeholder sequence per file:
  1. §7.6.1-4 -> §X1-4, §7.6 -> §X0          (old 7.6 subsections -> new §7.x)
  2. §7.1-5 -> §Y1-5                          (old Discussion subsections -> new §8.x)
  3. §11->§12, §10->§11, §9->§10, §8->§9      (chapter renumber, high-to-low)
  4. §Y1->§8.1 .. §Y5->§8.5; §X1->§7.1 .. §X4->§7.4; §X0->§7
  5. Discussion title: "# §7 Discussion" -> "# §8 Discussion" (after step 3, since
     step 3 would otherwise hit the already-renumbered "# §8 Discussion").
     So first revert that title to §7, run steps, then set to §8.
"""
import io, os, glob

SKIP = {"07-capacity-regulation.md"}  # hand-written in final form already
DISCUSSION_FILES = {"08-discussion.md"}

def files():
    out = []
    for d in ("sections", "sections_en"):
        for p in sorted(glob.glob(os.path.join(d, "*.md"))):
            if os.path.basename(p) not in SKIP:
                out.append(p)
    for name in ("abstract.md", "abstract_en.md", "appendix.md", "appendix_en.md"):
        out.append(name)
    out.append(os.path.join("..", "experiments", "attention_growth",
                            "EXPERIMENT_PLAN_AXIOM4_KIMI_BOOST.md"))
    return out

def transform(s, is_discussion):
    if is_discussion:
        s = s.replace("# §8 Discussion", "# §7 Discussion")  # revert premature title
    # 1. old 7.6 subsection refs
    for n in (1, 2, 3, 4):
        s = s.replace("§7.6.%d" % n, "§X%d" % n)
    s = s.replace("§7.6", "§X0")
    # 2. old Discussion subsection refs
    for n in (1, 2, 3, 4, 5):
        s = s.replace("§7.%d" % n, "§Y%d" % n)
    # 3. chapter renumber high-to-low
    for old, new in (("§11", "§12"), ("§10", "§11"), ("§9", "§10"), ("§8", "§9")):
        s = s.replace(old, new)
    # 4. restore placeholders
    for n in (1, 2, 3, 4, 5):
        s = s.replace("§Y%d" % n, "§8.%d" % n)
    for n in (1, 2, 3, 4):
        s = s.replace("§X%d" % n, "§7.%d" % n)
    s = s.replace("§X0", "§7")
    if is_discussion:
        s = s.replace("# §7 Discussion", "# §8 Discussion")
    return s

changed = []
for f in files():
    if not os.path.exists(f):
        print("MISSING:", f)
        continue
    is_discussion = os.path.basename(f) in DISCUSSION_FILES
    s = io.open(f, encoding="utf-8").read()
    t = transform(s, is_discussion)
    if t != s:
        io.open(f, "w", encoding="utf-8", newline="\n").write(t)
        changed.append(f)
print("changed %d files:" % len(changed))
for f in changed:
    print("  ", f)
