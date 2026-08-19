# 委托是成本不等式，不是能力问题

> 主题：为什么 agent 做了一遍，人还要再做一遍——以及为什么"等模型再强一点"是错的答案。

---

观察到的现象：很多团队做了大量 agent，但实际不解决业务问题。典型症状是 agent 做了一遍，人还要再做一遍——复核一份 agent 写的报告，和自己写这份报告，花的时间差不多。总成本没有下降，有时反而更高。

常见的诊断是：模型还不够强，等下一代模型就好了。

本文的论点：**这个诊断是错的。委托能否成立，取决于一个成本不等式，而不是取决于模型能力这个单一变量。在这个不等式里，杠杆率最高的项不是"让 agent 做得更对"，而是"让确认它做对变得更便宜"。** 看不懂这个不等式的团队，会把钱花在等模型上；看懂了的团队，会把钱花在验证上。

---

## 一、先想清楚"委托"是什么意思

委托（delegation）和"使用工具"是两回事。用工具时，你仍然控制过程；委托时，你**放弃对过程的管理，只对结果负责**。一篇研究人机委托的论文说得很直白："如果你在委托时必须指定每一步细节，那还不如自己做。委托是关于交出对整个过程的管理需求"（[A Framework for Studying AI Agent Behavior](https://arxiv.org/html/2509.25609v2)）。

所以"用 agent 帮我起草，我再逐句改"不是委托，那只是换了个更贵的工具。真正的委托发生在你不需要逐句改的时候。

一个任务值不值得委托，可以用一个不等式判断：

> **委托收益 = 人亲自做的成本 −（agent 执行成本 + 复核成本 + 失败率 × 失败损失）**

只有这个值大于零，委托才成立。

"人还要再做一遍"的含义用不等式说就是：**复核成本 ≈ 亲自做的成本**，收益归零。Agent 把不等式里的"执行成本"降到了接近于零，但复核成本纹丝不动——这就是现在大多数 agent 项目的真实处境。

---

## 二、为什么复核这么贵：错误是不可见的

复核贵，不是因为我们懒，而是有结构性原因的。

第一个原因，四十年前就有人讲清楚了。1983 年，Bainbridge 在《自动化的讽刺》（[Ironies of Automation](https://doi.org/10.1016/0005-1098(83)90046-8)）中指出：自动化并不消除人，而是把人变成监控者——**而监控一个通常正确的系统，恰恰是人最不擅长的事**。人的注意力无法长时间维持在"大概率没问题"的输入上。工业自动化的这个老毛病，在 LLM agent 身上变本加厉：agent 的输出流畅、自信、格式漂亮，错误（幻觉、违反约束、静默偏离）均匀地混在正确内容里，外表上看不出任何区别。于是复核者只能逐字验证——复核成本自然逼近重做成本。

第二个原因是信任没有被校准。信任校准研究的经典文献（Lee & See, [Trust in Automation, 2004](https://doi.org/10.1518/hfes.46.1.50_30392)）提出"适当依赖"：问题不在于人太信任或太不信任系统，而在于**信任与系统实际能力不匹配**。对 agent 过度信任 → 漏检错误，代价是事故；信任不足 → 全量复核，代价是委托失去意义。近年的 HCI 综述（[CHI 2026](https://dl.acm.org/doi/10.1145/3772318.3791467)）确认：即便把 AI 的置信度直接告诉人，人的依赖行为仍然普遍校准不良。

由此得到一个反直觉但极重要的结论：

> **可委托 ≠ 高成功率。一个 95% 成功率但失败自动可见的 agent，比一个 99% 成功率但失败静默的 agent 更可委托。**

因为前者的复核成本 ≈ 零（系统自己报错，人只处理异常），后者的复核成本 ≈ 重做（你必须检查每一次输出，才能抓住那 1%）。委托公式里，**错误的可见性比错误的发生率更值钱。**

---

## 三、"等模型变强"为什么不是完整答案

不是说模型能力不重要。而是要看清楚能力这条曲线到底长什么样——它支持的结论和流行叙事不一样。

METR 对 2019–2025 年前沿模型的测量（[Measuring AI Ability to Complete Long Tasks](https://arxiv.org/abs/2503.14499)）给出了最量化的图景：

- 当前模型对"人类 4 分钟内能完成"的任务，成功率接近 100%；对"人类需要 4 小时以上"的任务，成功率**低于 10%**。
- 以 50% 成功率衡量的"任务时间跨度"（time horizon）确实在以约每 7 个月翻倍的速度增长。这是"模型在变强"叙事的事实基础。
- 但论文同时指出：最好的模型**偶尔**能完成专家级数小时的任务，却**只能可靠地完成几分钟量级的任务**。

请注意"偶尔能"和"可靠地能"之间的鸿沟。委托恰恰买在"可靠地能"上——你委托一个任务，是因为你相信它**每次**都会被完成，而不是它有相当概率被完成。论文里高置信度（80%–95%）对应的时间跨度，远短于媒体热衷引用的 50% 曲线。**用 50% 曲线做委托决策，是在用赌博的心态做生产决策。**

Sierra 的 τ-bench（[arXiv:2406.12045](https://arxiv.org/abs/2406.12045)）从另一个角度量化了同一件事：一致性。它用 pass^k 衡量"同一任务独立运行 k 次、每次都成功"的概率——这才是"可委托"的正确度量。实测结果：最强的 function-calling agent，单次成功率低于 50%；跑 8 次全都成功的概率（pass^8）低于 25%。单次成功是演示，次次成功才是委托。两者之间不是量的差距，是质的差距。

还有错误复利。Anthropic 在构建多 agent 系统的复盘（[How we built our multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system)）里反复强调："agent 是有状态的，错误会复利累积。"用一个简单的乘法模型：单步可靠性 95%，连续 20 步，端到端成功率只剩约 36%。链条越长，对单步可靠性的要求越苛刻——这解释了为什么成功率随任务长度断崖式下跌。

这些证据合起来说的是：**能力曲线确实在涨，但委托门槛站在曲线很高的位置上。"等模型"是一个被动策略，而且等的可能是相当久。**

---

## 四、被忽略的那半边：验证可以前置为资产

现在看不等式的另一边——复核成本。这是本文真正想说的重点。

Jason Wei 提出的"验证不对称"（[asymmetry of verification / verifier's law](https://www.jasonwei.net/blog/asymmetry-of-verification-and-verifiers-law)）指出：任务和任务之间，"验证一个解"和"求出一个解"的成本比值天差地别。解数独，验证免费；写代码，验证≈跑测试；而核查一篇长文的每个事实，验证≈重做（Brandolini 定律：驳斥胡说八道所需的能量比制造它高一个数量级）。

验证不对称决定了一个任务可委托性的上限：**凡是"确认做对了"比"自己做"还贵的任务，委托在经济上永远不成立，无论模型多强。**

但 verifier's law 还有一个常被忽略的推论：**验证成本不是任务的固有属性，它可以被工程手段降低。** 提前写好的测试集、标准答案、终态校验、结构化约束——这些东西能把验证成本从 O(重做) 降到 O(跑一遍检查)。验证一旦被前置为工程资产，复核就从"人逐字读"变成"机器跑断言 + 人看红绿灯"。

这就是为什么软件工程是目前唯一被大规模真正委托的领域：不是模型最擅长代码，而是**代码自带验证器**——编译器、测试、类型系统，都是现成的终态校验。Anthropic 的真实使用数据（[The Anthropic Economic Index](https://www.anthropic.com/news/the-anthropic-economic-index)）证实了这一点：当前 AI 使用中，增强（人机协作）占 57%，自动化占 43%，且采用高度集中在软件开发。市场已经用脚投了票：先被委托的，是可验证、有快速反馈环的任务。

τ-bench 的另一个发现则指出了提升验证性的第一步，它便宜得出乎意料：对 benchmark 日志的分析（[arXiv:2605.08545](https://arxiv.org/pdf/2605.08545)）发现，排除掉定义错误或含歧义的任务后，agent 的 pass^5 大致翻倍。也就是说，**相当一部分"agent 不可靠"，其实是任务定义不清**——政策文档的歧义、验收标准的缺失，先被记到了 agent 头上。对企业内部部署，这个教训非常直接：很多 agent 项目的第一期工程不应该是调 prompt，而应该是把任务定义和验收标准写清楚。这些东西写出来，既是给 agent 的指令，也是给验证器的判据。

---

## 五、推论：重新表述一个 agent 项目的目标

如果接受"委托是成本不等式"，那么一个 agent 项目的目标就不再是"让 agent 能做这件事"，而是**"让这个任务的不等式成立"**。这改变了钱的去向：

1. **先算不等式，再选任务。** 候选任务按"验证成本 / 执行成本"排序，从比值最低的开始。有自动化测试的 > 有终态可校验的 > 只能人工抽检的 > 验证≈重做的。最后一类（典型如事实密集的长文写作），当前就应坦率地定位为"增强"（agent 出草稿，人负责），而不是假装在"自动化"。

2. **把建验证器当作第一期工程。** 测试集、答案键、终态校验，同时服务于三层：开发期的评测、上线前的验收、运行时的护栏。一份投入，三份产出。这是整个 agent 工程里杠杆率最高的动作。

3. **先修任务定义，再修 agent。** pass^k 上不去的时候，先怀疑任务定义和验收标准，再怀疑模型。τ-bench 的证据是这一步可能值一倍的一致性。

4. **用对的指标报告进展。** 单次成功率是演示指标；pass^k（重复运行的一致性）和 cost-of-pass（产出一个正确结果的期望成本，[Stanford, arXiv:2504.13359](https://arxiv.org/abs/2504.13359)）才是委托指标。向管理层汇报 pass@1，是在制造"快要能委托了"的幻觉。

5. **给信任装上闸门，而不是呼吁信任。** 实验证据（[Confidence-Based Trust Calibration, 2025](https://thesai.org/Downloads/Volume16No12/Paper_122-Confidence_Based_Trust_Calibration_in_Human_AI_Teams.pdf)）表明，按置信度阈值做条件委托——高于阈值自动执行，低于阈值转人工——可以让团队表现超过人或 AI 任何一方单独作战。OpenAI 的 agent 实践指南（[A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)）给出的落地方案是分层护栏：失败次数超阈值转人工，高风险动作（支付、删除、外发）强制人工批准。

6. **保留人接管的能力。** Bainbridge 的警告还有后半段：自动化程度越高，人练习得越少，一旦需要接管就越无能。如果 human-in-the-loop 是认真的设计而不是公关措辞，就要有意识地保留一部分人工操作和演练，否则它迟早退化成 human-nominally-in-the-loop。

---

## 六、结语：换一个问法

"agent 什么时候能真正解决业务问题"这个问题，流行版本问的是：**模型什么时候足够强？**

本文给出的版本是：**这个任务的不等式里，各项现在是多少？哪一项能被工程手段压低？**

第一个问法把人变成等待者——等待下一代模型，等待别人的 benchmark 分数。第二个问法把人变成工程师——任务定义、验证器、护栏、一致性指标，每一项都是今天就可以动工的东西。

模型会继续变强，这不以人的意志为转移。但委托时代的到来速度，取决于有多少人开始算那道不等式。

---

## 参考来源

- Bainbridge, *Ironies of Automation* (1983) — https://doi.org/10.1016/0005-1098(83)90046-8
- Lee & See, *Trust in Automation* (2004) — https://doi.org/10.1518/hfes.46.1.50_30392
- METR, *Measuring AI Ability to Complete Long Tasks* — https://arxiv.org/abs/2503.14499
- Yao et al. (Sierra), *τ-bench* — https://arxiv.org/abs/2406.12045 ；日志可信度分析 https://arxiv.org/pdf/2605.08545
- Anthropic, *How we built our multi-agent research system* — https://www.anthropic.com/engineering/built-multi-agent-research-system
- Anthropic, *The Anthropic Economic Index* — https://www.anthropic.com/news/the-anthropic-economic-index
- Jason Wei, *Asymmetry of verification and verifier's law* — https://www.jasonwei.net/blog/asymmetry-of-verification-and-verifiers-law
- OpenAI, *A Practical Guide to Building Agents* — https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
- Erol et al. (Stanford), *Cost-of-Pass* — https://arxiv.org/abs/2504.13359
- *Do People Appropriately Rely on AI-Advice?* (CHI 2026) — https://dl.acm.org/doi/10.1145/3772318.3791467
- *Confidence-Based Trust Calibration in Human-AI Teams* (2025) — https://thesai.org/Downloads/Volume16No12/Paper_122-Confidence_Based_Trust_Calibration_in_Human_AI_Teams.pdf
- *A Framework for Studying AI Agent Behavior* — https://arxiv.org/html/2509.25609v2

> 本文的论证细节与完整证据链见同目录调研报告：`research/agent-delegatability.md`。
