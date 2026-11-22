# AGENTS.md — SQLite 源码解剖仓库维护约束

## 目的与源范围
本仓库是 SQLite **源码阅读课程**，不是 SQLite 的上游代码仓库，也不是 SQLite 的非官方发布分支。读者从任意单页进入，都必须能独立理解上下文、关键名词、真实命令、预期结果及限制。

- 上游权威源码与文档：https://sqlite.org/src 、https://sqlite.org/arch.html 、https://sqlite.org/howtocompile.html
- GitHub mirror：https://github.com/sqlite/sqlite （镜像，不是上游开发治理的事实来源）
- 使用的版式原则：https://github.com/1998x-stack/Olah-style-posts/tree/main/skills/olah-style-paper-posts/SKILL.md
- 仅借鉴渐进解释、事实先于图、证据台账和浏览器验收的教学方法；不得复制第三方插图、文案或代码资产。

## 仓库边界
- `index.html` 是 GitHub Pages 首页；`chapters/NN.html` 是章节唯一正文。
- 根目录 `01.html` … `28.html` 只是旧链接兼容重定向，**不要在这里写文章内容**。
- `chapters/06.html` … `28.html` 是尚待逐章技术审计的历史正文，不得标记为已验证。
- 新版文章 CSS 只维护在 `assets/css/site.css`；旧版页面暂用 `chapters/theme.css`，下一轮迁移后可以逐步淘汰。
- 每张原创 SVG 存在 `assets/svg/` 并登记到 `assets/svg/manifest.json`。示意箭头、单位与 caption 必须与真实执行关系一致。
- `courses.json` 是章节清单的事实单源，章节状态字段取值 `revised`、`legacy`。新增、改名、迁移同步修改首页链接。
- `evidence/NN.json` 为每篇文章的主张台账，`examples/` 为可复现实验，`scripts/` 为质量门禁，`.github/workflows/` 为 CI 和部署。

## 每篇文章强制叙事顺序
1. 开场用**一个具体困惑**引出问题，不写“本讲义介绍了……”这类课程介绍。
2. 给出端到端的正确总体路径，再拆解最少必要的局部对象。
3. 每个小节填完整上下文、输入/输出、控制流、内部结构与因果关系。
4. 关键图至少两幅，每幅应有独立 SVG、title、desc、明确箭头语义、足够大的标签和非重复的 figcaption。
5. 放置源码定位（模块 + 函数或符号 + 版本边界）与真实可运行的 SQL/C 实验。
6. 告知读者哪些结论来自上游文档，哪些属于教学简化、推导或尚待核验。
7. 讲清错误情况、版本差异和不能从单次实验推出的结论；最后给出延伸实验与官方来源。
8. 章节必须有唯一 H1、有可跳转标题 ID、相邻章节导航、skip link、无需 JS 的可阅读主内容。

## SQLite 技术真实性
- 必须区分 **prepare 编译** 与 **step 运行**，以及 VDBE / B-Tree / Pager / PCache / VFS 的职责。
- 不要把 WAL、rollback journal、锁及 page cache 当成一个简单的“脏页 LRU”算法。
- 不得把内部结构体字段、opcode 数量、版本中的新特性、默认 lookaside 配置写成跨版本不变量。
- 不得继续传播固定 lookaside 命中率的示例表、虚构的内存优化提升、未证实的新版本行为。
- Scratch allocator 的历史资料不得冒充当前版本默认体系。新特性必须附 SQLite release note 与对应源版本。
- 测试输出必须明确：固定断言、版本相关输出、示意数据、未执行示例。
- 优先官方 `sqlite.org`、源码实际版本和 SQLite 测试；二手博客只能辅佐理解，不能单独验证细节。
- 不要在文章标题/页眉写制作用语，例如“原创 SVG / 单文件 / AI 生成 / 风格来源 / 本文借鉴某某”。

## HTML / CSS / SVG 标准
- 主色：墨绿 `#147f80`，计算路径辅色：陶土 `#c76743`，状态/运行时：紫 `#7161b5`。颜色必须与文字同时标示意义。
- 内容列最大约 820px，中文正文约 17px / 1.8–1.95；移动端 360px/390px 无文档横向溢出。
- 图表独立 SVG 必须有 `xmlns`、`viewBox`、`title`、`desc`；图形中最小关键标签应可读，不能纯靠颜色表达。
- 使用真实 `<main><article><section>`、`nav`、`figure`、`figcaption`、`:focus-visible`，提供 reduced-motion 和打印样式。
- 复杂公式用本地原生 MathML 或清晰文本公式，标明单位、变量和条件；禁止依赖远程 CDN 渲染公式。
- 交互是渐进增强：关闭 JS 时正文和核心图必须可读。按钮/summary 要能键盘操作，不能是空交互。
- 不允许用 CSS 的 `overflow-x:hidden` 掩盖布局错误。

## Evidence 台账与改动流程
- 每条重要断言进入 `evidence/NN.json`：`id`、`claim`、`kind`、`source_url`、`locator`、`status`、`notes`。状态只能是 `verified` / `derived` / `illustrative` / `unverified`。
- 指向官方的引用放在对应段落附近，页末另列资料；不以“已查阅文档”代替版本事实核验。
- 在 PR 里记录：为什么改、对应哪个 SQLite 版本、改了哪些技术主张、实验命令、截图宽度、自动化检查结果、未验证项。
- 必须运行 `python scripts/check_site.py`；若环境有 Playwright 再运行 `python scripts/browser_smoke.py` 检查 1440 / 390 / 360 以及 print。
- 浏览器检查未执行时只能写“未执行”，不能凭文件存在就宣称“Pages 已上线”或“移动端通过”。
- 不直接删除长期使用的外部地址；迁移章节时保留根目录的兼容跳转。
- 发布在单独分支提 PR；合并前复核 diff 与 CI；只有确认 Actions 部署和 Pages 域名响应正常，才标记已发布。

## 完成定义
正确（版本/接口）＋好懂（读者可复述因果）＋可复现（实验/输出边界）＋可访问（页面/图/键盘）＋可维护（目录/台账/CI/兼容）。任何一项未完成都应在 PR 明示。
