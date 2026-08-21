# 会话交接：打磨并撰写《白天别写代码了，写 goal》

> 交接时间：2026-08-21
> 状态：**文章初稿完成，但实战案例尚未真实跑通，需下次继续实证**
> 本文件供下次会话快速恢复上下文，不用重读所有对话。

---

## 一、这是什么

打磨并撰写一篇技术文章，主题是"让 AI 在夜间任务（无人值守）中高质量地产出代码"。文章最终定位为三篇系列文的第二篇（姊妹篇：`article-context-engineering.md`《别建知识库了，做上下文工程》）。

- **文章正文**：`article-overnight-goal.md`（814 行，约 3.7 万字）
- **HTML 预览**：`article-overnight-goal.html`
- **文章规划框架**：`research/goal-command-plan.md`（含顶层框架 v3 + 四份 subagent 审查修复记录）
- **研究档案**：`research/overnight-agent-research.md`（跨对话研究证据全集）

## 二、文章核心立意（已定稿，别再跑偏）

标题：《白天别写代码了，写 goal——loop 负责看，goal 负责做，让 AI 替你过夜》

主轴经过多轮修正，最终确立为 **"思考与执行的分离"**：

> **不是"AI 兜质量"，不是"AI 替你多干活"，而是"追求写出高质量产出本身"。** 人白天思考（拆解 goal、组织上下文、设计验证手段），AI 晚上执行（把需求真正实现出来，且实现带着验证，作为一个整体高质量地完成）。**质量是产出的一部分，验证设计前移——不把质量后置到测试阶段再加倍偿还。** 夜里做的是需求的编码，不是"补质量"。

关键红线（用户在打磨中反复强调，务必遵守）：
- **不要吹牛，要真实**——案例必须是真实可验证的，不能是编的。
- **标题夸张，内容扎实**——标题挑衅，正文用证据和反方证据把可信度挣回来。
- **站在工程师立场**，全文禁"效率/提效/产能/降本"这类企业视角词汇。
- **原理讲透，拒绝机械执行**——每个概念给到机制层（为什么），再落到坑与避法。

## 三、文章结构（11 章）

1. 开篇（对比痛点 + 克制愿景 + 标题非字面含义 + 思考/执行分离）
2. 你敢不敢信？（第一原理 + 推理链 + 四维定义）
3. 模型原理性问题（RLHF 说得自信/自评非测量/残余缺口）
4-7. 四维：终点 / 边界 / 预算 / 反馈（每维独立成章）
8. 机制：loop 传感 + goal 执行（三工具实证分层）
9. 判据：两层判据（敢不敢信 → 用什么跑）
10. 实战：用"一个晚上的心智模型"规划 goal（思考/执行分离 + 目标流水线）
11. 环境与运维：权限/休眠/断网/恢复/保活/移动端
12. 收尾（三个可带走判断 + 三篇关系表）

## 四、当前状态与遗留问题（下次重点）

### 已定稿
- 标题、立意、框架、全文初稿、HTML 生成、四维/机制/判据/实战/环境各章

### ✅ 已解决：实战案例真实性问题（已真跑）

用户指出"没有真实的跑这个案例"后，本会话**真的跑了一次 Now in Android**，实证结果已写入文章实战章的"实证"小节。真实运行记录：

- **环境**：JDK 17（NIA 要求 17+，实测满足，无需 21）、Android SDK（`/home/peter/Android/Sdk`，android-36 匹配 NIA compileSdk 36）、gradle wrapper 9.4.0
- **`./gradlew :core:model:test`** → BUILD SUCCESSFUL（15s，纯 JVM 模块，无测试所以 NO-SOURCE）
- **`:feature:foryou:impl:testDemoDebugUnitTest`** → **ForYouViewModelTest 12 个测试全绿**；ForYouScreenScreenshotTests 1 个失败（Roborazzi 截图测试在无头环境 `UnsupportedOperationException`）——真实环境坑
- **agent 真实编码闭环**：agent 给 `:core:common` 的 `asResult()` 补 Success 分支测试，跑 `./gradlew :core:common:test` → BUILD SUCCESSFUL，**tests=2, failures=0**（git diff + 测试报告 XML 双重确认）
- **重要命令发现**：`:feature:foryou:impl` 真实测试任务是 `testDemoDebugUnitTest`（不是想当然的 `testDemoDebug`，真跑才发现）；纯 JVM 模块（`:core:model`/`:core:common`）用 `test`

**文章已修正**：
- 所有 `testDemoDebug` → `testDemoDebugUnitTest`（真实命令）
- 实战章新增"实证"小节（真实运行记录 + 截图测试坑 + 诚实边界说明）
- 明确区分"示例"（加收藏角标，未实证）与"实证"（补测试，已跑通）——没有把示例当实证

### 下次可继续（可选，非必须）
- 如需更完整实证：可让 agent 真实现一个较大的 NIA 功能（如"加收藏角标"，涉及 Hilt/Repository/状态流，工程量大、耗时数小时）并跑测试
- 或实证 `:core:data` 等更多模块的测试任务名
- 或实证 `:app:assembleDebug`（完整 APK 构建，更重）

## 五、已完成的工作细节（供回顾）

### 框架打磨（多轮用户纠正）
- 从"三个原理并列"→"因果链 + 三问"→"写 goal 四维"→"信任是主线"→"质量是产出内在部分"→"思考与执行的分离"
- loop 定位：不是"残缺版 goal"，而是"解决触发（持久性）"，goal 补判断层；小任务用 loop，大任务用 goal；loop 传感 + goal 执行

### 四份 subagent 审查（已修复全部 MUST-FIX）
- oracle（逻辑）：§3 vs §3.5 矛盾（已通过"四维=把判断权转移给确定性检查"重定义解决）、四维不是并列（2+2）、"工具选择是最后一位"
- librarian（事实）：sycophancy 引文疑似造假（已改真实表述）、False Success 75.8% 分母、Apidog"所有厂商"过度声称、$6000 账单背景
- 标题审查者（bait-and-switch）：标题 60% 挣到，需开篇给非字面含义
- 读者体验（general）：术语统一、Boris 引文归因、工具排名限定、阅读合同前置

### 三工具实证（已真实验证，来自官方文档+源码+issue）
- 触发层（loop 传感）三工具都生产可用：Claude（GitHub Action/Channels/cron）、Codex（exec/GitHub Action）、OpenCode（serve API/插件）
- goal 层成熟度：Claude（原生生产级）> Codex（无 --goal exec，被官方拒绝）> OpenCode（fork PR 未合并，靠插件）
- 关键推论：Codex/OpenCode 官方建议"外部 loop 自己实现判断层"→ 印证"判断层必须外部定义"

### 调研（librarian 已验证的真实 Android 项目）
- **Now in Android**（首选）：`android/nowinandroid`，21696 星，AGP 9.0.0/Kotlin 2.3.0/Compose，模块 `:feature:foryou:impl` 等，测试 `./gradlew testDemoDebug`，CI 真实
- Todo-MVVM（备选，更轻）：`android/architecture-samples`，45795 星，2 模块，`./gradlew :app:connectedCheck`
- Pokedex（非 Compose）：`skydoves/Pokedex`，8351 星

## 六、git 提交信息

本次提交只包含：文章正文、HTML、规划框架、研究档案、本交接文档。不包含 `.omc/`（如需要再决定）。

## 七、下次恢复步骤

1. 读本交接文档 + `research/goal-command-plan.md` 的 v3 框架 + `research/overnight-agent-research.md`
2. 处理实战案例真实性问题（第三节第一项）
3. 确认方向后继续
