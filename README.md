# 🗄️ SQLite源码分析 · 从入门到精通

> 📘 28章 实战体系

一套完整的 **SQLite源码分析 · 从入门到精通** 全中文实战课程体系，共 **28 章**。本课程以 HTML 可视化的形式呈现，从基础原理到工程实践循序渐进，适合系统性学习与复习。

## 🚀 快速开始

无需安装任何依赖，直接用浏览器打开 `index.html` 即可在线阅读全部章节：

```bash
open index.html   # macOS
# 或在浏览器中直接打开 index.html
```

## 📖 章节目录

| # | 章节 | 核心主题 |
|---|------|----------|
| 01 | 概览与源码获取 | 历史演进、版本号体系、三种源码获取方式、目录结构鸟瞰 |
| 02 | 编译体系深度解析 | Autotools/Makefile.msc/CMake、SQLITE_* 编译选项、合并版生成内幕、自定义编译实战 |
| 03 | 源码整体架构 | 10层架构管线、src/目录文件映射、核心头文件关系、生成文件的角色 |
| 04 | 核心数据结构 | sqlite3连接对象、Parse编译上下文、Table/Index模式对象、Select/Expr查询树 |
| 05 | 内存管理机制 | Lookaside allocator、Page cache分配策略、Scratch pool、内存统计与调试 |
| 06 | 错误处理与断言 | 错误码体系、rc传播链、assert使用哲学、日志与诊断 |
| 07 | 调试基础设施 | SQLITE_DEBUG模式、AST可视化打印、VDBE跟踪、gdb调试技巧 |
| 08 | 词法分析器 | tokenize.c概览、关键词完美哈希、Token类型系统、词法错误恢复 |
| 09 | Lemon解析器与语法 | LALR(1)解析器、parse.y文件结构、Shift/Reduce过程、Parse上下文 |
| 10 | 表达式编译 | Expr树构建、递归代码生成、类型推导与Affinity、IN/CASE/CAST编译 |
| 11 | VDBE虚拟机 | 虚拟机设计哲学、主执行循环、寄存器模型、191个opcode详解 |
| 12 | B-Tree存储引擎 | B+Tree与B-Tree、数据库文件格式、页面内部布局、分裂与合并算法 |
| 13 | Pager与页缓存 | Pager状态机、PCache LRU缓存、脏页管理与回刷、I/O聚合与延迟写 |
| 14 | VFS抽象层 | 可插拔VFS设计、sqlite3_io_methods、Unix/Windows实现、自定义VFS实战 |
| 15 | 原子提交与事务 | ACID实现、Rollback journal格式、事务类型选择、崩溃恢复流程 |
| 16 | WAL模式深度解析 | WAL文件格式、Checkpoint算法、读写并发模型、3.51.3 WAL bug修复 |
| 17 | 锁机制与并发 | 五级文件锁、POSIX锁实现、Windows SRWL新锁、死锁预防策略 |
| 18 | 查询规划器 | WhereLoop构建、Cost估算模型、连接顺序优化、3.53星型JOIN改进 |
| 19 | 内置函数实现 | 函数注册机制、标量与聚合函数、Window函数框架、日期时间函数 |
| 20 | 虚拟表与扩展 | sqlite3_module接口、虚拟表生命周期、carray扩展示例、实现KV存储虚拟表 |
| 21 | FTS全文搜索 | FTS3/4/5演进、倒排索引结构、分词器实现、FTS5 ranking |
| 22 | 表达式索引与自修复 | 表达式索引原理、索引到期原因、3.53自修复机制、REINDEX EXPRESSIONS |
| 23 | CLI shell源码 | shell.c.in架构、点命令分发表、QRF格式化库、自定义点命令 |
| 24 | 测试框架 | 100%分支覆盖、TH3测试套件、TCL测试脚本、Fuzz测试 |
| 25 | 性能分析与优化 | EXPLAIN解读、PRAGMA调优、编译时剪裁、批处理优化实战 |
| 26 | SQLite WASM与JS绑定 | WASM编译流程、OPFS/opfs-wl VFS、浏览器端SQLite、ext/wasm目录 |
| 27 | 2026新特性源码解读 | 自修复索引、浮点数17位精度、SRWL锁迁移、O_TMPFILE支持 |
| 28 | 实战：定制SQLite | 功能剪裁、加密VFS实现、Extension编写、课程总结 |

## 📂 项目结构

```text
sqlite-source-analysis-tutorial/
├── index.html      # 课程主入口（在线阅读全部章节）
├── 01.html ~ 28.html   # 各章节正文
├── courses.json    # 课程元数据（标题/章节/主题）
└── theme.css       # 统一主题样式
```

## ✨ 课程特色

- **全中文实战体系**：面向中文读者，由浅入深，覆盖原理与工程实践
- **28 章完整内容**：系统化章节编排，形成完整知识闭环
- **可视化呈现**：HTML 图文并茂，适合快速浏览与重点回顾
- **即开即用**：无需构建、无需服务器，纯静态页面随开随看

---
*本课程由 `sqlite-source-analysis-tutorial/` 项目维护。*