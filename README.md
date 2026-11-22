# SQLite 源码解剖：从一条 SQL 理解数据库内核

> 28 章 SQLite 内核原理与源码分析的中文阅读路线。首批重构 **01–05**；**06–28 保留原版**，后续将逐章核对、绘制可解释的 SVG，并补充可复现实验。

**课程首页**（GitHub Pages 配置完成后）：https://1998x-stack.github.io/sqlite-source-analysis-tutorial/

## 路线
| 章节 | 主题 | 维护状态 |
|---|---|---|
| 01 | 从 SQL 出发：获取源码与路径 | 深度重构 |
| 02 | 编译体系：canonical / amalgamation / 宏 | 深度重构 |
| 03 | SQL 编译与存储层完整架构 | 深度重构 |
| 04 | sqlite3、Parse、Expr、Select、Vdbe | 深度重构 |
| 05 | Lookaside / 通用分配 / Page Cache | 深度重构 |
| 06–28 | 错误码、解析、VDBE、B-Tree、Pager、WAL、优化器、扩展、CLI、WASM 等 | 原版迁移，待复核 |

章节清单和真实相对路径以 [courses.json](courses.json) 为准。首页既是学习入口，也清楚标记哪些章节还未完成技术复审。

## 项目结构

```text
.
├── index.html                 # GitHub Pages 首页（根目录发布）
├── chapters/
│   ├── 01.html ... 05.html   # 首批新叙事 + 图解 + 实验
│   ├── 06.html ... 28.html   # 从根目录迁移的原版
│   ├── index.html            # 旧章内“返回首页”兼容跳转
│   └── theme.css             # 原版页面暂用的兼容主题
├── assets/
│   ├── css/site.css          # 重构版视觉系统
│   └── svg/*.svg             # 11 张原创可访问的独立 SVG
├── evidence/01.json ... 05.json
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
