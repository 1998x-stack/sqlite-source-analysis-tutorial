# SQLite 源码解剖：从一条 SQL 理解数据库内核

> 28 章 SQLite 内核原理与源码分析的中文阅读路线。已重构 **01–28**；全部章节均有独立叙事、图解、证据台账与可复现实验。

**课程首页**（GitHub Pages 已部署）：https://1998x-stack.github.io/sqlite-source-analysis-tutorial/

## 路线
| 章节 | 主题 | 维护状态 |
|---|---|---|
| 01 | 从 SQL 出发：获取源码与路径 | 深度重构 |
| 02 | 编译体系：canonical / amalgamation / 宏 | 深度重构 |
| 03 | SQL 编译与存储层完整架构 | 深度重构 |
| 04 | sqlite3、Parse、Expr、Select、Vdbe | 深度重构 |
| 05 | Lookaside / 通用分配 / Page Cache | 深度重构 |
| 06 | 错误码、step 状态与调用链传播 | 深度重构 |
| 07 | EQP、VDBE 生成期/执行期调试 | 深度重构 |
| 08 | 手写词法扫描、Token、fallback | 深度重构 |
| 09 | Lemon、parse.y、shift/reduce | 深度重构 |
| 10 | Expr 代码生成、NULL、CAST 和 affinity | 深度重构 |
| 11 | VDBE 程序、寄存器、Cursor、step/reset | 深度重构 |
| 12 | SQLite B-Tree 页格式、rowid/index 区别与平衡 | 深度重构 |
| 13 | Pager 状态、PCache 与缓存观测 | 深度重构 |
| 14 | VFS 对象、I/O 方法表、sync/lock 与文件实验 | 深度重构 |
| 15 | Rollback commit、hot journal、事务锁与可见性 | 深度重构 |
| 16 | WAL frame、end mark、checkpoint 与 snapshot 实验 | 深度重构 |
| 17 | Rollback/WAL 并发、BUSY_SNAPSHOT 实验 | 深度重构 |
| 18 | Planner、N3、索引前缀、ANALYZE | 深度重构 |
| 19 | 标量、聚合与窗口 C API | 深度重构 |
| 20 | sqlite3_module 与可执行的 C 虚拟表 | 深度重构 |
| 21 | FTS5、倒排索引、segment merge、tokenizer 与 BM25 | 深度重构 |
| 22 | 表达式索引、stale index、自修复与 REINDEX EXPRESSIONS | 深度重构 |
| 23 | CLI 输入分流、点命令、shell.c.in 与 QRF | 深度重构 |
| 24 | TCL、TH3、SQL Logic Test、dbsqlfuzz 与故障注入 | 深度重构 |
| 25 | EQP、stmt_status、PRAGMA optimize 与可重复 benchmark | 深度重构 |
| 26 | SQLite WASM、OO1、Worker、OPFS / opfs-wl / sahpool | 深度重构 |
| 27 | 3.52 撤回、3.53–3.54 版本演进、浮点转换与 C API | 深度重构 |
| 28 | canonical build、Extension API、VFS 与加密安全边界 | 深度重构 |

章节清单和真实相对路径以 [courses.json](courses.json) 为准。首页既是学习入口，也展示完整 28 章路线、图解数量和统一质量门禁。

## 项目结构

```text
.
├── index.html                 # GitHub Pages 首页（根目录发布）
├── chapters/
│   ├── 01.html ... 28.html   # 全部完成独立叙事 + 图解 + 实验
│   ├── index.html            # 旧章内“返回首页”兼容跳转
│   └── theme.css             # 原版页面暂用的兼容主题
├── assets/
│   ├── css/site.css          # 重构版视觉系统
│   └── svg/*.svg             # 83 张原创可访问的独立 SVG
├── evidence/01.json ... 28.json
├── examples/                 # SQL / Python / C / JavaScript 实验（不复制上游 SQLite）
├── scripts/                  # 静态检查、浏览器 QA、部署打包
├── courses.json              # 28 章导航数据和重构状态
├── AGENTS.md                 # 内容技术标准和维护约束
├── .github/workflows/        # 质量门禁和 Pages 部署
└── 01.html ... 28.html       # 兼容旧外部链接的重定向存根
```

## 本地阅读

纯静态站点，无 Node、Jekyll、数据库后端或在线脚本依赖。直接打开 `index.html` 即可阅读。建议用本地服务器模拟 Pages 路径：

```bash
python3 -m http.server 8000
# 浏览 http://localhost:8000
python3 scripts/check_site.py
```

要运行 SQLite 实验，需要本机 SQLite CLI；C 程序需有 C 编译器、SQLite 的 `sqlite3.c` 或对应的系统开发库。

```bash
sqlite3 :memory: < examples/01_sql_path.sql
sqlite3 :memory: < examples/03_explain.sql
# 下载 SQLite amalgamation 后，在其含 sqlite3.c/sqlite3.h 的目录中
cc examples/05_lookaside_status.c sqlite3.c -I. -ldl -lpthread -lm -o lookaside-demo
./lookaside-demo
```

上述 C 命令是 Unix-like 示例，需确保 `examples/05_lookaside_status.c` 的路径正确；其他平台链接参数不同。

## 质量与维护

```bash
python3 scripts/check_site.py
pip install playwright
python -m playwright install chromium
python3 scripts/browser_smoke.py
python3 scripts/build_site.py
```

浏览器 QA 输出到 `qa-local/`（不提交），部署输出在 `dist/`。CI 将校验链接、章节完整性、SVG XML 可解析性、证据台账、响应式布局和交互。Pages 工作流已预置；**是否上线以仓库 Pages 设置和部署结果为准**。

请优先参照 [AGENTS.md](AGENTS.md) 改写章节；不要把旧页对特定版本的新特性或固定性能指标的断言误认为已复核。

## 主要上游资料

- SQLite 规范源码（Fossil）：https://sqlite.org/src
- 官方源码镜像：https://github.com/sqlite/sqlite
- 官方架构：https://sqlite.org/arch.html
- 官方编译：https://sqlite.org/howtocompile.html
- 内存分配：https://sqlite.org/malloc.html
- 字节码引擎：https://sqlite.org/opcode.html

站点图解与文章为独立撰写；教学编排参考 [Olah-style-posts](https://github.com/1998x-stack/Olah-style-posts) 中的渐进解释和证据审核方法，不复制其图像或文本。

## 第二轮：06–10 技术深入

本批在原来的 11 幅之外新增 15 张可独立打开的 SVG，重点解释：错误结果码层次、step 状态机、API 错误传播、调试输出层次、addoptrace / vdbe_trace 的时间界限、token 扫描与 fallback、Lemon shift/reduce、运算符优先级、表达式生成、三值逻辑与亲和性。每章配官方来源与独立实验。

```bash
python scripts/test_examples.py
python examples/09_toy_reduce.py
sqlite3 :memory: < examples/08_lexical.sql
sqlite3 :memory: < examples/09_parser_semantics.sql
sqlite3 :memory: < examples/10_expressions.sql
for id in 06_error_codes 07_trace_events 08_token_boundary 10_expr_prepared; do
  cc -std=c11 -Wall -Wextra -Werror -O2 "examples/${id}.c" -lsqlite3 -o "/tmp/sqlite-${id}"
  "/tmp/sqlite-${id}"
done
```

注意 `examples/07_debug.sql` 包含 `.eqp` / `.echo` 等 CLI 点命令，不能用 Python 的 `executescript()` 来运行；调试专用 `TREETRACE` / `WHERETRACE` 功能需配套编译宏。命令示例以 Linux 为基线，Windows/macOS 需按工具链调整。

## 第三轮：11–15 存储内核与事务

新增 15 张图解（累计 41 张），五章分别沿 VDBE 执行器、B-Tree page bytes、Pager/PCache、VFS methods 与 rollback journal 崩溃恢复分层解释。严禁把“教学用指令表”“B-Tree 平衡演示”“Pager 状态箭头”“rollback 提交序列”冒充固定源码指令或跨日志模式的统一轨迹。

```bash
python3 examples/12_file_inspect.py
python3 examples/15_transactions.py
python3 scripts/test_examples.py
cc -std=c11 -Wall -Wextra -Werror -O2 examples/11_vdbe_steps.c -lsqlite3 -o /tmp/11-vdbe && /tmp/11-vdbe
cc -std=c11 -Wall -Wextra -Werror -O2 examples/13_cache_stats.c -lsqlite3 -o /tmp/13-cache && /tmp/13-cache
cc -std=c11 -Wall -Wextra -Werror -O2 examples/14_vfs_select.c -lsqlite3 -o /tmp/14-vfs && /tmp/14-vfs /tmp/sqlite-14-vfs-demo.sqlite
```

C 程序的链接参数为 Unix-like 示例；页面检查和事务测试使用 Python 标准库，不需要下载 SQLite 私有 C 文件。事务脚本只验证回滚和锁冲突，**不是实际断电模拟**。

## 第四轮：16–20 快照、规划与扩展
本批增加 15 张新的专业 SVG，累计 56 张。五篇分别从 WAL 帧与 end mark、锁错误、N3 路径搜索、SQL 函数回调和虚拟表约束协商切入。源码与实验均优先使用 SQLite 官方文档和公开 C API。

```bash
python examples/16_wal_snapshot.py
python examples/16_wal_inspect.py
python examples/17_lock_matrix.py
python examples/18_plan_experiment.py
cc -std=c11 -Wall -Wextra -Werror -O2 examples/19_functions.c -lsqlite3 -o /tmp/19-functions && /tmp/19-functions
cc -std=c11 -Wall -Wextra -Werror -O2 examples/20_vtab_rows.c -lsqlite3 -o /tmp/20-vtab && /tmp/20-vtab
python scripts/check_site.py
```
`generate_series` 是 SQLite CLI 常见扩展而非所有核心库默认函数。新增 `examples/20_json_virtual.sql` 为可选 JSON 表值函数练习，主 CI 则运行无需特定扩展安装的 C 模块实验。

## 第五轮：21–25 全文检索、CLI、测试与性能
本批新增 15 张 SVG，累计 71 张；重写 FTS5、表达式索引、SQLite CLI、测试体系和性能诊断五篇文章。源码定位固定在 SQLite 3.54.1 快照，公开接口与内部实现分别标注。

重点纠偏：
- FTS5 的 unicode61 不会自动做中文词典分词；automerge 发生在写入路径，不是后台常驻线程。
- SQLite 3.53.0 确实加入 stale expression index 的有限自修复和 REINDEX EXPRESSIONS，但不是通用 corruption repair。
- CLI 的 dot commands 属于 Shell，不是 SQL；QRF 的真实接口是 sqlite3_qrf_spec / sqlite3_format_query_result()。
- TH3 和 dbsqlfuzz 为专有测试工具；fuzzcheck 是 corpus 回放工具，不是 SQL 结果验证器。
- EQP 是诊断输出；性能对比要记录 source id、数据、参数、事务、缓存和计数器。

```bash
python scripts/test_examples.py
python examples/21_tokenizer_probe.py
python examples/24_test_contracts.py
python examples/25_benchmark.py
sqlite3 :memory: < examples/23_cli_workflow.sql
cc -std=c11 -Wall -Wextra -Werror -O2 examples/25_stmt_status.c -lsqlite3 -o /tmp/25-status
/tmp/25-status
python scripts/check_site.py
```

## 第六轮：26–28 浏览器运行时、版本演进与定制交付
本批新增 12 张原创 SVG，全站累计 83 张；至此 28 章全部完成独立叙事重构。新增 SQLite WASM 的 Node/Worker 实验、版本门控的 REINDEX EXPRESSIONS 探针、动态 Extension host 和可运行 tracing VFS。新增 26–28 三份证据台账，内部实现以 SQLite 3.54.1 为基线。

本轮关键纠偏：
- OPFS VFS 运行在 Worker；标准 OPFS 依赖 COOP/COEP，opfs-wl 需要 Web Locks / Atomics.waitAsync，sahpool 有不同并发合同。
- 官方 SQLite WASM npm 包的 Node.js 支持限定为内存数据库；不能把浏览器 OPFS 示例直接当成 Node 文件持久化。
- Worker1 / Promiser API 已标记 deprecated；新应用在自建 Worker 中定义消息协议。
- 3.52.0 曾撤回；3.53.0 重发并修复 WAL-reset 问题；3.54.1 修复部分 32 位构建中的 heap-buffer overflow。
- sqlite3_result_str() 接收 sqlite3_str* 和所有权标志，不是普通 char* + 长度。
- SQLITE_OMIT_* 多数不受支持；VFS tracing 示例只记录 xOpen 并委托父 VFS，明确不是加密实现。AES-ECB 旧方案不再作为生产加密示例。

```bash
python scripts/test_examples.py
python examples/27_release_probe.py
(cd examples/26_wasm && npm install && npm run test:node && npm run build)
cc -std=c11 -Wall -Wextra -Werror -O2 examples/28_vfs_trace.c -lsqlite3 -o /tmp/vfs-trace
(cd /tmp && /tmp/vfs-trace)
cc -std=c11 -Wall -Wextra -Werror -O2 -fPIC -shared examples/28_course_ext.c -o /tmp/course_ext.so
cc -std=c11 -Wall -Wextra -Werror -O2 examples/28_extension_host.c -lsqlite3 -o /tmp/extension-host
/tmp/extension-host /tmp/course_ext.so
python scripts/check_site.py
python scripts/svg_visual_audit.py
python scripts/browser_smoke.py
python scripts/wasm_browser_smoke.py
```

## 第七轮：28 篇全文站精细化审计（2026-11-22）

本轮不新增章节，重点修复“已经重构但系统元数据仍留在旧进度”的缺陷，并建立可重复运行的工程审计。

- **知识依赖导航**：`data/reading_paths.json` 保存 28 篇的 56 条人工策划的机制级关系。文章文末“知识关联”说明为什么关联，并指向另一章的准确小节锚点；首页增加编译、执行、存储、事务链路导航。
- **高清 SVG**：文章内 SVG 图解均可通过图片链接单独打开矢量原图；360px/390px 屏幕优先保持标签可读并允许局部横向滚动。
- **独立网页身份**：每章含 canonical、独立 description、Open Graph 元数据以及上一章 / 下一章的 head 关系。28 个旧路径重定向页面使用有效 HTML，并指定正式 canonical。
- **质量门禁**：`scripts/audit_content.py` 检查首页数据同步、全站链接 fragment、知识图谱、独立 SVG、evidence claim id、元数据唯一性及历史 URL；`scripts/check_site.py` 负责基础结构检查，`scripts/svg_visual_audit.py` 在真实 Chromium 中检测 SVG 文本越界。
- **证据与实验可公开追溯**：Pages 构建现在包含 `evidence/`、`examples/`、`data/`、`audits/`，提供 [技术证据索引](https://1998x-stack.github.io/sqlite-source-analysis-tutorial/evidence/) 与 [实验源文件索引](https://1998x-stack.github.io/sqlite-source-analysis-tutorial/examples/)；每篇文章都能打开对应的 JSON 证据台账。
- **真实实验及部署验证**：原有 SQL/Python/C/Node/Chromium 实验继续保留；首页、28 篇文章和两张资源索引页分别在 1440/390/360 测试，共 93 个视口。`scripts/audit_deployment.py` 核验 Pages 实际包含 28 个兼容地址、83 张 SVG、28 份台账、实验和审计记录。详见 `audits/2026-11-22.md`。

```bash
python scripts/check_site.py
python scripts/audit_content.py --output qa-local/editorial-audit.json
python scripts/build_site.py && python scripts/audit_deployment.py
python scripts/test_examples.py
python scripts/browser_smoke.py
python scripts/wasm_browser_smoke.py
```

**验证边界**：静态审计只保证链接、结构和证据记录的一致性；它不自动证明每个 SQLite 技术主张正确，也不等同于人工逐像素视觉检查或实时校验全部外部网站。外部事实仍须以版本化 SQLite 官方资料复核。
