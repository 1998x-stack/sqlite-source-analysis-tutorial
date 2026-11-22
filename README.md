# SQLite 源码解剖：从一条 SQL 理解数据库内核

> 28 章 SQLite 内核原理与源码分析的中文阅读路线。已重构 **01–20**；**21–28 保留原版**，后续将逐章核对、绘制可解释的 SVG，并补充可复现实验。

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
| 21–28 | 后续优化、扩展、CLI、WASM 等 | 原版迁移，待复核 |

章节清单和真实相对路径以 [courses.json](courses.json) 为准。首页既是学习入口，也清楚标记哪些章节还未完成技术复审。

## 项目结构

```text
.
├── index.html                 # GitHub Pages 首页（根目录发布）
├── chapters/
│   ├── 01.html ... 20.html   # 已完成独立叙事 + 图解 + 实验
│   ├── 21.html ... 28.html   # 从根目录迁移的原版
│   ├── index.html            # 旧章内“返回首页”兼容跳转
│   └── theme.css             # 原版页面暂用的兼容主题
├── assets/
│   ├── css/site.css          # 重构版视觉系统
│   └── svg/*.svg             # 56 张原创可访问的独立 SVG
├── evidence/01.json ... 20.json
├── examples/                 # SQL / C 实验（不复制上游 SQLite）
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
