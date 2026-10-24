# scripts/ — 构建·修订·验证脚本总目录

本书《工业智能体控制论》（IAC）的过程性脚本统一收拢于此，按四组组织。
**运行约定**：全部脚本以仓库根（`E:\workspace\industrial-agentic-cybernetics`）为工作目录运行；
数值/PDF 处理脚本一律用 `D:\pyenv\pyenv-win\versions\3.11.8\python.exe`（pyenv 3.11.8）。
本目录 README 是各脚本的引用声明——任何脚本不得成为孤儿文件。

---

## A. 构建管线组（mermaid → 图片 → 编译嵌入）

| 脚本 | 用途 |
| --- | --- |
| `wire_mmdc.py` | 无缩进 mermaid 代码块 → mmdc（.tools 中的 mermaid-cli，puppeteer）渲染为 PNG |
| `wire_png.py` | 渲染产物 PNG 落地与命名管线 |
| `mmd_core.py` | mermaid 渲染核心封装（puppeteer.json 配置于 monograph/） |
| `extract_seq.py` / `extract_seq2.py` / `extract_seq3.py` | 抽取时序图 mermaid 源码（v6 修复轮，三代迭代） |
| `extract_flow.py` | 抽取流程图 mermaid 源码（模式 23/24） |
| `png2jpg_seq.py` / `png2jpg_flow.py` | PNG → JPG 白底化（供 LaTeX 嵌入） |

## B. 修订管线组（评审修复，可审计复现）

| 脚本 | 用途 |
| --- | --- |
| `apply_terms.py` / `apply_terms2.py` | v8 术语修订：必然而无条件 4 处条件化、彻底 24→0、注意力稀释改名、借喻锚定、导读块 |
| `apply_kimi.py` / `apply_kimi2.py` | v9 KIMI 四项落地：证据等级表、同行现状、『工业级』口径声明、附录 B 目录措辞 |
| `dedup_evt.py` | 证据等级表嵌套去重（apply_kimi 崩溃残留修复） |
| `fix_chars.py` / `fix_chars2.py` | 字符/编码修正（窄列换行假阴性处置轮） |
| `fix_p0.py` | 评审 P0 措辞修复 |
| `fix_bi3.py` | 术语锚定补充（公理 II 生物免疫借喻） |
| `fix_seq_leak.py` / `fix_leak.py` | 时序图源码泄漏修复（v5/v6 残码清零） |
| `fix_width_anchor.py` | 表格宽度与锚点防御（防批量替换连锁误伤） |
| `fix_figsize.py` | 图片尺寸统一 |
| `fix_flow.py` / `fix_flow2.py` | 模式 23/24 flowchart 修复 |
| `fix_import.py` | apply_kimi.py 缺 import 崩溃修复 |
| `add_refs.py` | 文献表补录（A.5 20→25 条） |
| `set_caps.py` / `sync_caps.py` / `map_caps.py` | 图注语义化与三源同步（54 条实义化） |

## C. 版本验证组（每版 PDF 文本层回验）

| 脚本 | 用途 |
| --- | --- |
| `verify_v6.py` / `verify_v6b.py` | v6 残码/术语回验 |
| `verify_v7.py` / `verify_v7b.py` / `verify_v7c.py` | v7 文献表/图注回验 |
| `verify_v8.py` / `verify_v8b.py` | v8 断言词归零回验 |
| `verify_kimi.py` / `verify_kimi2.py` | v9 KIMI 四项落地 PDF 层回验 |

## D. scnet 通道（远程计算/大模型 API 接入）

| 文件 | 说明 |
| --- | --- |
| `scnet/.env` | scnet API 凭证（api_key/api_base/模型名），**绝密，不入库**（.gitignore 已约束） |
| `scnet/scnet_help.md` | scnet 通道使用帮助 |
| `scnet/scnet-rsa-expiry-2026-11-18.txt` | scnet RSA 证书到期提醒（2026-11-18） |

---

## 维护纪律

1. 任何评审修复落地后，对应脚本连同改动一并提交（脚本=修订证据链）。
2. 一次性诊断脚本（qa_*/probe_*/scan_*/locate_*/find_pages* 等）用完即删，不进本目录。
3. 临时输出（*_out*.txt、QA 渲染 PNG、_qa/）不入库，见根 .gitignore。
4. 三源同步（docs 权威源 / manuscript-latex.md / manuscript-merged.md）与云盘覆盖上传+SHA256 回验为每轮发布的固定闭环。
