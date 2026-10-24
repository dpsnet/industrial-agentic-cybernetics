# -*- coding: utf-8 -*-
path = r"E:\workspace\industrial-agentic-cybernetics\monograph\manuscript-latex.md"
text = open(path, encoding="utf-8").read()

def replace_block(text, pat_no, repl_line):
    h = text.index("# 模式 %s：" % pat_no)
    sec = text.index("### 2. 动机与工业失效场景", h)
    ms = text.index("```mermaid", sec)
    line_start = text.rindex("\n", 0, ms) + 1
    code_start = ms + len("```mermaid")
    code_end = text.index("```", code_start)
    line_end = text.index("\n", code_end)
    block = text[line_start:line_end+1]
    assert "flowchart TD" in block, "not flowchart block"
    assert block.count("```") == 2, "block boundary unexpected: %s" % block[:60]
    print("pat%s block: %d lines, from L%d" % (pat_no, block.count("\n"), text.count("\n", 0, line_start)+1))
    return text[:line_start] + repl_line + text[line_end+1:]

# 先模式24后模式23
text = replace_block(text, "24", "![模式 24：缺陷萃取-验证-晋升-免疫闭环流程 示意](figures/m53.jpg){width=50%}\n")
text = replace_block(text, "23", "![模式 23：隔离环境审计与三维异常嗅探维度流程 示意](figures/m52.jpg){width=45%}\n")

open(path, "w", encoding="utf-8", newline="\n").write(text)
print("after: flowchart TD =", text.count("flowchart TD"), "| mermaid blocks =", text.count("```mermaid"), "| subgraph =", text.count("subgraph"))
