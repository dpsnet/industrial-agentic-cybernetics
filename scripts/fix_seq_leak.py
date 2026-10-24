# -*- coding: utf-8 -*-
import re

files = {
    r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md": [
        ("m50.jpg", "模式 23：生产环境异常嗅探协作时序", "60%"),
        ("m51.jpg", "模式 24：缺陷萃取与热修复闭环协作时序", "70%"),
    ],
    r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-merged.md": [
        ("m50.jpg", "模式 23：生产环境异常嗅探协作时序", "60%"),
        ("m51.jpg", "模式 24：缺陷萃取与热修复闭环协作时序", "70%"),
    ],
}

pat = re.compile(
    r"### 5\. 协作协议与因果约束 \(Collaborations\)\n+```\n+> 注：该图为源稿中的截断示例片段，无法机器渲染，保留原码。\nmermaid\n.*?\n```\n",
    re.S,
)

for path, repls in files.items():
    text = open(path, encoding="utf-8").read()
    count = 0
    def do(m):
        global count
        return repls[count][1] + "替换占位"
    # 用迭代替换
    for i in range(len(repls)):
        m = pat.search(text)
        if not m:
            print("NO MATCH #%d in %s" % (i, path))
            continue
        fig, title, w = repls[i]
        new = "### 5. 协作协议与因果约束 (Collaborations)\n\n![%s 示意](figures/%s){width=%s}\n" % (title, fig, w)
        text = text[:m.start()] + new + text[m.end():]
        print("REPLACED #%d in %s -> %s %s" % (i, path, fig, title))
    open(path, "w", encoding="utf-8", newline="\n").write(text)
    print("remaining leak markers:", text.count("截断示例片段"), "|", text.count("无法机器渲染"))
