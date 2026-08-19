# AI Agent 可委托性（Delegatability）专题调研

> 调研日期：2026-08。全文基于一手来源（论文、官方工程博客、原始 benchmark 文档），每条关键论断附来源链接。凡属本文作者的综合判断，均以 **[综合判断]** 明确标注，与来源支持的结论区分。

## 前置观察

很多团队做了大量 agent，但实际不解决业务问题：agent 做了一遍，人还要再做一遍。人工复核成本没有降低，总成本反而更高；因为做不到高置信度交付，任务始终无法真正"委托"给 agent。本调研回答三个问题：(1) 为什么当前 agent 无法被真正委托？(2) 可委托性如何定义与度量？(3) 有哪些被验证或正在探索的提升路径？

---

## 1. 问题定义：什么是"可委托"

### 1.1 委托的本质：放弃过程控制，换取结果保证

委托（delegation）与"使用工具"的根本区别在于：委托意味着**放弃对过程的逐步管理，只对结果负责**。一篇关于人机委托的研究表述得很直白："如果你在委托时必须指定每一步细节，那你还不如自己做。委托是关于 relinquishing control——交出对整个过程的管理需求"（[A Framework for Studying AI Agent Behavior, arXiv:2509.25609](https://arxiv.org/html/2509.25609v2)）。

一个任务被"真正委托"的充要条件可以表述为 **[综合判断]**：

> **委托收益 = 人亲自做的成本 −（agent 执行成本 + 复核/验证成本 + 错误期望损失）> 0**

"人还要再做一遍"的症状，正是复核成本 ≈ 亲自做的成本，使净收益归零甚至为负。

### 1.2 "再做一遍"的三个结构性原因

1. **错误不可见**。自动化领域的经典研究（Bainbridge, *Ironies of Automation*, 1983, [DOI:10.1016/0005-1098(83)90046-8](https://doi.org/10.1016/0005-1098(83)90046-8)）在四十年前就指出：自动化并不消除人，而是把人变成监控者；而监控一个通常正确的系统恰恰是人最不擅长的事。自动化程度越高，人的手动操作经验越少，一旦系统出错，人反而更没有能力接管。LLM agent 的输出流畅、自信，错误（幻觉、违反约束、静默偏离）混在正确内容中，复核者必须逐字验证——这就是"复核成本 ≈ 重做成本"的来源 **[结合 Bainbridge 的论证与当前 agent 输出的特性做出的综合判断]**。

2. **信任未被校准（miscalibrated trust）**。信任校准研究的奠基性文献（Lee & See, *Trust in Automation: Designing for Appropriate Reliance*, Human Factors, 2004, [DOI:10.1518/hfes.46.1.50.30392](https://doi.org/10.1518/hfes.46.1.50_30392)）提出"适当依赖"（appropriate reliance）：问题不在于信任太低或太高，而在于信任与系统实际能力不匹配。对 agent 的过度信任导致漏检错误，信任不足导致全量复核——两种情况都破坏委托的经济性。近期 HCI 综述（[*Do People Appropriately Rely on AI-Advice?*, CHI 2026](https://dl.acm.org/doi/10.1145/3772318.3791467)）确认，即便给出了 AI 的置信度信息，人类用户的依赖行为仍然普遍校准不良。

3. **agent 无法可靠地"知道自己不知道"**。OpenAI 的 agent 构建指南把"识别失败并优雅地把控制权交还给人"列为 agent 的核心特征之一（[A Practical Guide to Building Agents, OpenAI, 2025](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)）——这反过来承认：当前 agent 需要外部的失败检测机制（重试次数上限、高风险动作强制人工审批）来兜底，而不是靠自我判断。

### 1.3 工作定义

**[综合判断]** 本调研采用如下定义：

> 一个 agent 对某类任务**可委托**，当且仅当：对该类任务，委托方可以在**不逐一复核过程**的前提下，以可接受的总成本获得可接受质量的结果。这意味着（a）成功率足够高，或（b）失败能被系统自动、廉价地检测出来（错误可见），且（c）残余错误造成的损失有界。

条件 (b) 是关键：可委托性 ≠ 高成功率。一个 95% 成功率但失败自动可见的 agent 通常比 99% 成功率但失败静默的 agent 更可委托 **[综合判断]**。

---

## 2. 现状与根因：为什么当前 agent 达不到可委托门槛

### 2.1 成功率随任务长度快速衰减（最直接的能力根因）

METR 对 2019–2025 年前沿模型的测量（[*Measuring AI Ability to Complete Long Tasks*, arXiv:2503.14499](https://arxiv.org/abs/2503.14499)；[METR 官方博客](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/)）给出了最量化的现状图景：

- 当前模型对"人类 4 分钟内能完成"的任务成功率接近 100%，但对"人类需要 4 小时以上"的任务成功率 **低于 10%**。
- 以 50% 成功率定义的"任务时间跨度"（time horizon），以约 **每 7 个月翻倍**的速度指数增长（2019 年起；2024 年后可能加速；稳健区间估计为每年 1–4 次翻倍）。在 SWE-bench Verified 这一真实任务子集上拟合出的翻倍速度甚至更快（约 3 个月以内）。
- 论文同时指出矛盾点：最好的模型**偶尔**能完成专家级数小时的任务，但**只能可靠地完成几分钟量级的任务**。"能做"与"能可靠地做"之间的鸿沟正是不可委托的鸿沟 **[综合判断]**。

含义：委托的"任务边界"目前大约就在分钟级到小时级任务之间；想要委托更长的任务，成功率会跌破经济上可接受的阈值。

### 2.2 一致性缺陷：pass^k 揭示的"可靠性悬崖"

Sierra 的 τ-bench（[*τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains*, arXiv:2406.12045](https://arxiv.org/abs/2406.12045)）模拟真实业务场景（零售、航空客服），要求 agent 在多轮对话中调用 API 并遵守书面政策，以最终数据库状态判分。其核心发现：

- 即使最强的 function-calling agent（gpt-4o），单次任务成功率也 **低于 50%**；
- 更严重的是**不一致性**：用 pass^k（同一任务独立运行 k 次全部成功的概率）衡量，retail 域 **pass^8 < 25%**。

单次成功率掩盖了方差，而真实业务部署需要的是"每次都做对"。pass^k 直接度量了委托场景下的可靠性 **[综合判断]**。后续对 τ-bench 的日志分析（[arXiv:2605.08545](https://arxiv.org/pdf/2605.08545)）还发现，排除有错误或歧义的任务后，平均 pass^5 大致翻倍（20.8% → 约 40%）——说明相当一部分"agent 不可靠"其实是**任务定义不清**导致的，这对企业内部部署尤其重要：政策文档的歧义会先被记到 agent 头上。

### 2.3 错误的复利效应（compounding errors）

Anthropic 在构建多 agent 研究系统的复盘（[How we built our multi-agent research system, Anthropic Engineering](https://www.anthropic.com/engineering/built-multi-agent-research-system)）中反复强调："agent 是有状态的，错误会复利累积……传统软件里的小问题对 agent 可能是灾难性的；一步失败会让 agent 走向完全不同的轨迹。"

**[综合判断]** 用简单的乘法模型：若单步可靠性为 p，则 n 步链条的端到端成功率上界约为 p^n。p=0.95、n=20 时，端到端成功率仅约 36%。这解释了 METR 观察到的成功率随任务长度的陡峭衰减，也说明为什么"延长链条"比"提升单步智能"难得多——可靠性必须趋近 1 才能支撑长任务。

### 2.4 上下文与协调失败（架构层面的根因）

Cognition（Devin 团队）的复盘（[Don't Build Multi-Agents, Cognition, 2025](https://cognition.com/blog/dont-build-multi-agents)）指出多 agent 架构的两类系统性失败：

- **上下文断裂**：子 agent 只拿到任务片段，对任务的理解产生偏差（"Flappy Bird 变成 Mario 背景"）；
- **隐式决策冲突**：不同子 agent 基于各自未声明的假设行动，产出互相矛盾的结果（"动作携带隐式决策，冲突的决策产生坏结果"）。

其结论是默认采用**单线程线性 agent**、共享完整上下文轨迹，只有上下文溢出时才引入带交接（handoff）的子 agent。

### 2.5 评测与实践脱节（"看起来行"与"真的行"的差距）

Princeton 的 *AI Agents That Matter*（[arXiv:2407.01502](https://arxiv.org/abs/2407.01502)）系统梳理了 agent 评测的四大缺陷：只优化准确率而忽视成本；模型开发与下游部署的评测需求被混为一谈；holdout 集不足导致 agent 对 benchmark 过拟合、"走捷径"；评测缺乏标准化、普遍不可复现。其实验显示，简单的 baseline agent 在成本-准确率 Pareto 前沿上优于多个复杂的 SOTA agent。

含义：benchmark 分数普遍**高估**了 agent 在真实业务中的可委托性 **[综合判断]**。

### 2.6 验证不对称是双刃的

Jason Wei（OpenAI）的 *asymmetry of verification*（[博客原文](https://www.jasonwei.net/blog/asymmetry-of-verification-and-verifiers-law)）指出：有些任务"验证远难于求解"——典型如事实核查一篇文章（Brandolini 定律：驳斥胡说八道所需的能量比制造它高一个数量级）。当一个业务流程中"确认 agent 做对了"比"自己做"还贵时，委托在经济上永远不成立。这是"人还要再做一遍"现象在某些任务类别上**难以根除**的根本原因 **[综合判断]**。

---

## 3. 度量：如何量化可委托性

现有研究提供了五把互补的"尺子" **[综合判断：将以下分散来源组织为度量框架]**：

### 3.1 时间跨度（time horizon）——能力的刻度

METR（[arXiv:2503.14499](https://arxiv.org/abs/2503.14499)）：用"人类完成该任务所需时长"标定任务难度，拟合模型成功率随任务长度的 logistic 曲线，报告"x% 成功率对应的任务时长"。
- 用法：先给你的候选委托任务估算"人类时长"，再对照当前模型的 time horizon 曲线粗判可行性。注意论文强调 80%、95% 等高可靠性阈值的 horizon 远短于 50% 的 horizon——委托决策应看高置信度曲线而非 50% 曲线 **[综合判断]**。

### 3.2 pass^k —— 一致性的刻度

τ-bench（[arXiv:2406.12045](https://arxiv.org/abs/2406.12045)）：pass^k = 同一任务 k 次独立尝试全部成功的概率。
- 用法：对要委托的任务类型做 k 次重复评测。pass^1 高而 pass^k 低说明输出方差大，需配合验证机制才能委托。这是比单次准确率更贴近"委托"语义的指标 **[综合判断]**。

### 3.3 cost-of-pass —— 经济性的刻度

Stanford 的 cost-of-pass 框架（[Erol et al., arXiv:2504.13359](https://arxiv.org/abs/2504.13359)）：cost-of-pass = 产出一个正确解的期望货币成本（准确率与推理成本的联合度量）；frontier cost-of-pass = 所有可用模型（含人类专家外包价）中的最低值。
- 关键发现：以多数投票、自我精炼等"性能导向"的推理技巧，其微小性能提升 rarely justify 其成本。
- 用法：只有当 agent 的 frontier cost-of-pass（含复核成本）低于人力成本时，委托才成立 **[综合判断：原框架不含复核成本，此处为扩展]**。

### 3.4 验证不对称度 —— 复核成本的刻度

Jason Wei 的 verifier's law（[博客](https://www.jasonwei.net/blog/asymmetry-of-verification-and-verifiers-law)）：一个任务越"可验证"，AI 解决它的速度越快。可验证任务的五个性质：客观真值、验证快速、验证可规模化、低噪声、奖励连续。
- 用法：给每个候选任务评估"验证成本 / 求解成本"比值。比值越低越适合委托；比值 ≥ 1 的任务（如创意写作的事实核查）当前不宜全委托 **[综合判断]**。

### 3.5 信任校准度 —— 人机侧的刻度

Lee & See（[2004](https://doi.org/10.1518/hfes.46.1.50_30392)）与后续 HCI 研究：度量人的依赖行为与系统实际能力的匹配度（过度依赖率 / 依赖不足率）。近期实验（[Confidence-Based Trust Calibration in Human-AI Teams, 2025](https://thesai.org/Downloads/Volume16No12/Paper_122-Confidence_Based_Trust_Calibration_in_Human_AI_Teams.pdf)）表明，基于置信度阈值的条件委托策略（AI 置信度高于阈值则采用，否则转人）可使团队准确率（84.1%）超过 AI 单独（77.7%）和人单独的表现。

---

## 4. 提升路径

### 4.1 任务选择与分解：先委托"窄而可验证"的任务

- **从最简方案开始，逐级增加复杂度。** Anthropic（[Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)）的核心建议："找到尽可能简单的方案，只在必要时增加复杂度——这可能意味着根本不构建 agentic 系统。"对定义明确的任务用 workflow（预定义代码路径），对需要灵活决策的任务才用 agent。
- **用 prompt chaining 把任务切成可插"门"的固定子任务**，在步骤间加入程序化检查（gate），用延迟换准确率（[同上](https://www.anthropic.com/engineering/building-effective-agents)）。
- **OpenAI 的任务筛选三标准**（[Practical Guide](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)）：优先选择传统规则引擎做不好的流程——复杂判断（如退款审批）、规则集难维护（如供应商安全审查）、重度依赖非结构化数据（如保险理赔）；不满足这三条的，确定性方案往往就够。
- **控制单 agent 的任务半径。** 12-Factor Agents 的 Factor 10（[Small, Focused Agents](https://github.com/humanlayer/12-factor-agents)）：agent 保持小而专注；社区经验（"dumb zone"）是上下文/步数膨胀后错误率显著上升。

### 4.2 验证与自检机制

- **evaluator-optimizer 模式**：一个 LLM 生成、另一个按明确验收标准评估并反馈，循环迭代。适用前提：存在清晰的评估标准 + 迭代能产生可度量的改进（[Anthropic, Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)）。
- **把验证前置为工程资产**：verifier's law 的重要推论是验证不对称可以被"改善"——提前写好的测试集、答案键、形式化约束能把验证成本从 O(重做) 降到 O(运行测试)（[Jason Wei](https://www.jasonwei.net/blog/asymmetry-of-verification-and-verifiers-law)）。**[综合判断]** 这是提升可委托性杠杆率最高的工程动作之一：为任务建验证器 ≈ 为委托买保险。
- **端到端终态评测**：Anthropic 多 agent 系统的经验是对改变持久状态的 agent 采用 end-state evaluation（比对最终数据库/世界状态），而非逐步过程检查；复杂流程拆成离散检查点（[Anthropic Engineering](https://www.anthropic.com/engineering/built-multi-agent-research-system)）。τ-bench 的判分方式（比对终态数据库）正是这一思想的 benchmark 化（[arXiv:2406.12045](https://arxiv.org/abs/2406.12045)）。
- **确定性兜底 + 模型自适应**：错误处不重启而是可恢复执行（checkpoint + resume），配合重试逻辑；工具失败时明确告知 agent 让其自适应处理，"效果出乎意料地好"（[Anthropic Engineering](https://www.anthropic.com/engineering/built-multi-agent-research-system)）。
- **工具工程**：Anthropic 报告用 agent 自动测试并重写工具描述，使后续 agent 任务完成时间下降 40%；坏工具描述会把 agent 带上完全错误的路径（[同上](https://www.anthropic.com/engineering/built-multi-agent-research-system)）。

### 4.3 上下文工程与架构

- **共享完整上下文轨迹，而不只是消息**；警惕多 agent 间的隐式决策冲突；默认单线程线性 agent，上下文将溢出时用"压缩 + 交接"而非任意拆分（[Cognition, Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents)）。
- **多 agent 只在高价值、可并行、信息超出单上下文窗口的任务上划算**：Anthropic 内部评测中多 agent 研究系统比单 agent 高 90.2%，但 token 消耗约为普通对话的 15 倍；性能方差的 80% 由 token 用量解释；编码类任务并行度低、目前不适合多 agent（[Anthropic Engineering](https://www.anthropic.com/engineering/built-multi-agent-research-system)）。
- **12-Factor Agents 的工程纪律**（[repo](https://github.com/humanlayer/12-factor-agents)）：own your prompts / own your context window / 工具即结构化输出 / 把错误压缩进上下文 / 无状态 reducer 等。作者访谈了 100+ 团队，常见失败路径是"框架快速搭到 70–80% 质量线 → 发现 80% 对生产不够 → 推翻重写"——教训是尽早掌握底层控制而非依赖框架抽象。
- **内存与计划持久化**：长任务中把计划写入外部记忆、阶段总结后开新上下文，防止 200k 截断丢失关键信息（[Anthropic Engineering](https://www.anthropic.com/engineering/built-multi-agent-research-system)）。

### 4.4 评测驱动开发（evals）

- **立刻用小样本开始评测**：约 20 条真实查询即可在早期看到 30%→80% 级别的效应量，不要等到能建几百条的大评测集（[Anthropic Engineering](https://www.anthropic.com/engineering/built-multi-agent-research-system)）。
- **LLM-as-judge 用单一 prompt、0.0–1.0 打分 + pass/fail 最稳定**；rubric 覆盖事实准确性、引用准确性、完整性、来源质量、工具效率（[同上](https://www.anthropic.com/engineering/built-multi-agent-research-system)）。
- **人工评测不可省**：自动评测漏掉的边界案例（如 agent 偏爱 SEO 内容农场而非权威 PDF）只有人工测试能抓到（[同上](https://www.anthropic.com/engineering/built-multi-agent-research-system)）。
- **防 benchmark 过拟合**：按 *AI Agents That Matter* 的处方——分开模型评测与下游部署评测、保证 holdout、同时报告成本与准确率（[arXiv:2407.01502](https://arxiv.org/abs/2407.01502)）。
- **用 pass^k 而非 pass@1 报告生产就绪度**（[τ-bench](https://arxiv.org/abs/2406.12045)）。

### 4.5 人机协作设计

- **分层护栏 + 明确的人机交接触发器**：OpenAI 指南建议两类人工介入触发器——超过失败阈值（重试/动作次数上限）和高风险动作（支付、删除、外发）强制人工批准；人工介入机制本身就是"在不牺牲体验的前提下提升真实表现"的手段（[Practical Guide](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)）。
- **用工具调用来联系人类**：12-Factor Agents Factor 7——agent 通过结构化输出请求人类输入，使"介入点"成为一等公民的 API 而非特殊路径（[repo](https://github.com/humanlayer/12-factor-agents)）。
- **置信度阈值条件委托**：模拟实验显示，按 AI 置信度阈值决定"采用还是转人"，团队表现可超过任一方单独作战（[Confidence-Based Trust Calibration, 2025](https://thesai.org/Downloads/Volume16No12/Paper_122-Confidence_Based_Trust_Calibration_in_Human_AI_Teams.pdf)）。注意：这要求 agent 的置信度本身经过校准，而当前 LLM 的置信度校准普遍不佳（相关综述：[A Survey of Confidence Estimation and Calibration in LLMs, arXiv:2311.08298](https://arxiv.org/abs/2311.08298)，经上引文献转引确认其存在）。
- **警惕自动化悖论**：Bainbridge 警告——把常规操作全部自动化后，人类失去练习机会，在需要接管的罕见时刻反而更无能（[Ironies of Automation, 1983](https://doi.org/10.1016/0005-1098(83)90046-8)）。**[综合判断]** 对需要保留人工兜底能力的岗位，应有意识地保留一部分人工操作或演练，否则"human-in-the-loop"会退化成"human-nominally-in-the-loop"。
- **自主性分级**：Mitchell 等人的立场论文（[*Fully Autonomous AI Agents Should Not be Developed*, arXiv:2502.02649](https://arxiv.org/abs/2502.02649)）系统论证：让渡给 agent 的控制越多，对人（尤其安全）的风险越大；应按任务风险选择自主性级别，而非默认追求全自动。

### 4.6 组织与流程：哪些流程先被 agent 化

- **真实采用数据**：Anthropic Economic Index 基于约百万条真实对话分析发现：当前 AI 使用中增强（augmentation，人机协作）占 57%，自动化（automation，AI 直接执行）占 43%；采用集中在软件开发与技术写作（计算机/数学类占查询量的 37.2%）；中高薪知识工作使用最多，最低与最高薪岗位都低（[The Anthropic Economic Index](https://www.anthropic.com/news/the-anthropic-economic-index)）。**[综合判断]** 这与能力证据一致：市场已经"用脚投票"——可验证、数字化、有快速反馈环的任务（代码）先被委托。
- **先选"验证便宜"的流程**：结合 verifier's law 与 cost-of-pass，流程筛选顺序应为——有自动化测试/终态可校验的 > 有人工抽检样本的 > 验证需专家重做的 **[综合判断]**。
- **成本结构透明化**：多 agent 系统的 token 成本可达对话的 15 倍（[Anthropic](https://www.anthropic.com/engineering/built-multi-agent-research-system)）；按 *AI Agents That Matter* 的建议，把准确率与成本放在同一 Pareto 面上决策（[arXiv:2407.01502](https://arxiv.org/abs/2407.01502)）。
- **部署形态渐进**：OpenAI——"Start small, validate with real users, grow capabilities over time"；12-Factor Agents Factor 6/11——agent 可暂停/恢复、从任意渠道触发，使人能在流程中自然嵌入（[OpenAI](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)；[12-factor-agents](https://github.com/humanlayer/12-factor-agents)）。

---

## 5. 可操作的判断框架：什么任务现在就能委托

**[本节为综合判断，依据前述来源整合]** 用四个问题给任务打分：

| 维度 | 现在就能委托 | 需要人机协作 | 暂不可委托 |
|---|---|---|---|
| **任务长度**（对照 METR horizon） | 人类几分钟–十几分钟可完成 | 人类数十分钟–1 小时 | 人类数小时以上 |
| **验证成本**（对照 verifier's law） | 有自动化测试/终态校验，验证 ≈ 免费 | 抽检可发现大部分错误 | 验证 ≈ 重做（如长文事实核查） |
| **一致性**（对照 pass^k） | pass^k 高（多次重复稳定成功） | pass^1 高但 pass^k 低 → 需验证器兜底 | pass^1 本身就低 |
| **错误代价** | 可逆、低损（草稿、内部文档） | 中等，有人工闸门（高风险动作需批准） | 不可逆、高损（资金、对外承诺、安全） |

经验法则：

1. **委托公式**：`人力成本 > agent 执行成本 + 验证成本 + 失败率 × 失败损失` 时才委托。
2. **优先顺序**：软件工程中有测试覆盖的部分 > 结构化数据处理 > 有终态校验的业务操作 > 检索/研究类（用多 agent + 引用核查）> 创意/事实密集型写作（验证太贵，保持增强模式）。
3. **凡是 pass^k 上不去的任务，先修任务定义**（τ-bench 的教训：排除歧义任务后 pass^5 翻倍），再修 agent。
4. **把"建验证器"当作 agent 项目的第一期工程**，它同时服务于训练/评测/运行时三层。
5. **保留人的接管能力**（Bainbridge 悖论）：关键岗位定期人工演练，否则兜底名存实亡。

---

## 6. 参考来源列表

一手来源（本报告主要依据）：

1. METR, *Measuring AI Ability to Complete Long Tasks* — https://arxiv.org/abs/2503.14499 ；官方博客 https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/
2. Anthropic, *Building Effective Agents* — https://www.anthropic.com/engineering/building-effective-agents
3. Anthropic, *How we built our multi-agent research system* — https://www.anthropic.com/engineering/built-multi-agent-research-system
4. Yao et al. (Sierra), *τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains* — https://arxiv.org/abs/2406.12045
5. HumanLayer (Dex Horthy), *12-Factor Agents* — https://github.com/humanlayer/12-factor-agents
6. Cognition (Walden Yan), *Don't Build Multi-Agents* — https://cognition.com/blog/dont-build-multi-agents
7. OpenAI, *A Practical Guide to Building Agents* — https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
8. Kapoor et al. (Princeton), *AI Agents That Matter* — https://arxiv.org/abs/2407.01502
9. Erol et al. (Stanford), *Cost-of-Pass: An Economic Framework for Evaluating Language Models* — https://arxiv.org/abs/2504.13359
10. Jason Wei, *Asymmetry of verification and verifier's law* — https://www.jasonwei.net/blog/asymmetry-of-verification-and-verifiers-law
11. Anthropic, *The Anthropic Economic Index* — https://www.anthropic.com/news/the-anthropic-economic-index
12. Mitchell et al., *Fully Autonomous AI Agents Should Not be Developed* — https://arxiv.org/abs/2502.02649
13. Bainbridge, *Ironies of Automation* (1983) — https://doi.org/10.1016/0005-1098(83)90046-8
14. Lee & See, *Trust in Automation: Designing for Appropriate Reliance* (2004) — https://doi.org/10.1518/hfes.46.1.50_30392
15. *Do People Appropriately Rely on AI-Advice?* (CHI 2026) — https://dl.acm.org/doi/10.1145/3772318.3791467
16. *Confidence-Based Trust Calibration in Human-AI Teams* (IJACSA 2025) — https://thesai.org/Downloads/Volume16No12/Paper_122-Confidence_Based_Trust_Calibration_in_Human_AI_Teams.pdf
17. SWE-bench 原论文 — https://arxiv.org/abs/2310.06770 ；SWE-bench Verified（OpenAI，500 条人工校验样本）— https://openai.com/index/introducing-swe-bench-verified/（经 METR 论文及 o1 System Card 转引确认）
18. τ-bench 日志分析（benchmark 可信度威胁）— https://arxiv.org/pdf/2605.08545
19. *A Framework for Studying AI Agent Behavior* — https://arxiv.org/html/2509.25609v2

二手来源仅用于线索发现，未作为论断依据。
