# 文章规划：下班后，让 AI 替你干活——原理、避坑与夜间任务实战

> 目标读者：正在用 Claude Code / Codex / OpenCode 等 agent 工具的工程师。
> 定位：这篇是 `article-context-engineering.md` 的姊妹篇。那篇回答"Agent 运行时每一步有没有对的上下文"；这篇回答——**怎么让 Agent 在你下班后独立把活干完（夜间任务），并且不烧钱、不跑偏、不自嗨。**
> 定调：**本文的核心是给一套务实方法去跑夜间任务；但方法必须建立在理解原理之上——理解了原理，才知道每个坑为什么存在、怎么避。**

---

## 〇+、顶层框架 v3（2026-08-21 — 围绕《白天别写代码了，写 goal》重设计）

> 依据用户决策重做：**标题挑衅（夸张），内容扎实（克制）**。标题负责把人拉进来，正文负责用证据和反方证据把可信度挣回来——正是上篇《别建知识库了》的做法。v1/v2 细节保留在下方各章，**写作时以 v3 为骨架**。

### 1. 标题（已定方向）

**主标题：《白天别写代码了，写 goal》——loop 负责看，goal 负责做，让 AI 替你过夜**（已定稿；主标题保"角色转换"的挑衅与记忆点，副标题补上 loop 传感 + goal 执行的分工）

- 挑衅点：直指角色转换——你不再是写代码的人，你是写 goal 的人。这是全文最深的论点（两端工作者 / Boris Cherny "my job is to write loops" / Acheron "We Stopped Writing Code for Tickets" / operator→architect）。不是夸张，是业界一线已经在说的话。
- 系列感：上篇"别建知识库了，做上下文工程"→ 本篇"白天别写代码了，写 goal"，同公式、挑衅度递进。
- 用英文 "goal"（精确指 /goal 命令本身，圈内可识别）；正文首次出现处注"（/goal，目标）"。

### 2. 核心论点（一句话钉死）

> **为什么 AI 帮你写了更多代码，你却越来越累？因为你不信任它——它写得越多，你要 review 的就越多，你的时间被"甄别它的产出"占满。Boris 不一样：他不是让 AI 干更多活，而是让 AI 的产出可验证，于是敢少看、敢走开——同样的工作，他越来越轻松。差别不在模型多强、也不在工具多全，而在你写的 goal 有没有让结果"可验证、敢相信"：终点、边界、预算、反馈。**

（pivot：**你不再写代码，你写 goal**；四词 = 让结果可验证、敢相信的四个层面 = 全文四维章节。顶层意义：文章不站在企业视角喊效率，站在工程师自己的立场——**核心问题是"跑出来的东西可不可用、敢不敢信"，不是"跑不跑得起来"**。**关键澄清（消除 3 vs 3.5 矛盾）**：四维不是"写更好的指令让模型变诚实"（那做不到，模型原理上自评不可信），而是"**把判断权从模型手里转移到确定性检查手里**"——写 goal 的作用不是让模型变好，是重新设计验证机制、转移判断所在层。机制（loop/goal）是手段，信任（可验证）才是终点。）

### 3. 元原理（顶层：真正的核心是一个，不是四个）

**第一原理：让 AI 不在场干活而不累，靠的不是"跑起来"，是"跑出来的东西可验证、敢相信"。**

- **痛点的真正根源不是"AI 不干活"，是"AI 干活了你不敢信"**：你累，是因为你不信任它的产出，于是要把每一份都 review、甄别、返工。AI 写得越多，你要甄别的越多，越累。**Boris 不累，不是他让 AI 干得多，是他让 AI 的产出可验证，于是敢少看、敢走开。**
- **信任不是来自"机制对"，来自"结果可验证"**：可验证 → 敢相信 → 敢不看。机制（loop/goal）只是让"验证结果"这件事能自动发生的手段；如果结果不可验证，机制再对，你早上照样要对着输出甄别真假，一样累。
- **这才是全文的核心矛盾**：不是"怎么让 AI 跑起来"（那是机制，是工具问题），而是"怎么让 AI 跑出来的东西可验证、敢相信"（这是信任，是目标设计问题）。**工具选择（loop 还是 goal、哪个厂商）是最后一位，不是第一位**——注意：这是说"工具*选择*"是最后一位，不是说"工具"不重要；四维本身就是工具/机制，这里真正想区分的是"机制的目的（可验证）"与"具体机制（loop vs goal vs 厂商）"。
- **推理链（从累到可信，一步步推；同时说清两条独立动机）**：
  1. 你累的根源 = 不信任产出 → 每份都要 review/甄别（动机 A：甄别累）；
  2. 想不累 = 减少甄别 = 让产出可验证、敢相信；
  3. 你还有一个独立动机 B：不想在场守着（对话式接口同步，你走 AI 就冻结，你没法"少看"）；
  4. **A 与 B 独立但相遇**：B 逼你要异步；而异步让 A 更糟（你不能实时 review 了）——所以必须用 A（让产出可验证）来让 B 安全。**async 放大了信任问题，这正是可验证性变得关键的原因**（诚实版因果，比"从 A 推出 B"更严谨）；
  5. 异步缺两样：**触发**（谁驱动它继续跑）和**判断**（谁判定它做没做好）；
  6. **loop 解决触发**（有用但只解决一半）；**goal 在 loop 之上补判断层**（goal = loop + 判断）；
  7. 但判断本身也可信不可信——**判断必须有验证（退出码/测试/证据），否则 goal 只是"机器自嗨，你早上照样甄别"**；
  8. 所以最终落脚点不是"用了 goal"，是"goal 让结果可验证，你才敢信"。

**四维 = 让结果可验证的四个层面（不是防副作用的四个闸门，而是"你敢不敢信"的四个关卡）：**

| 你在场时免费得到的 | 离场后必须写下来的 | 没有它你会怎样（不敢信的原因） | 这就是维度 |
|---|---|---|---|
| 判断完成 | 完成长什么样、怎么验证 | 它说做完了，但你没证据→不敢信、得自己查 | **终点** |
| 实时纠偏 | 不许碰什么、改什么 | 它改了别的，你没看到→不敢信、得全 diff 审查 | **边界** |
| 实时止损 | 最多花多少、跑几轮 | 它烧光预算/空转，你没数→不敢放手 | **预算** |
| 实时预警 | 多久汇报、怎么留痕 | 它默默跑偏六小时，你不知→不敢离开 | **反馈** |

**四维结构说明（诚实标注，不是四个并列的"层面"）**：终点与反馈是**验证维度**（靠证据：完成态 vs 进行态），边界与预算是**约束维度**（限制 agent 能做什么、能花多少，让验证保持可追踪）。四者是四个正交的**失败模式**（完成失败/越界失败/成本失败/漂移失败），不是同一根轴上的四个层级——写作时统一叫"四维/四个失败模式"，不要用"四个层面"（暗示单一轴）。

**信任梯度是"判断可不可信"的度量，贯穿全文**：判断权必须独立于被判断者——"the party that does the work should not be the party that certifies the work"（PAELLADOC）、"an agent's claim about its own work is not a measurement"（Armalo Zero-Bit）。四维都在朝同一个方向努力：把"需要人判断"变成"机器可验证"，让你敢信、敢少看。**但注意（残余信任缺口）**：确定性检查对"它测了什么"是 ground truth，但"测什么"（测试设计）仍由模型生成、可被 gamed——所以信任梯度不是严格的单调层级，而是"把信任一层层往确定性方向推"，并接受残余缺口。

### 3.5 这些坑是模型原理性的，不是目标写得好不好能解决的（前置章，诚实度的根）

> **读者会想："那我目标写完美了，就能信它了吗？"答案是否定的——这些坑有模型训练原理层面的根源，目标写得好只能绕过，不能消除。诚实说出这个天花板，反而让文章更可信。**

**第一支柱｜RLHF 奖励"说得自信"，不奖励"做得对"（结构性根源）**：
- RLHF（InstructGPT, Ouyang 2022）让模型优化"人类偏好"，而人类偏好流利、自信的输出 → 模型被训练成"说得像做完了"，而非"真的做完了"。
- Anthropic sycophancy 论文（arXiv:2310.13548）：**"five state-of-the-art AI assistants consistently exhibit sycophancy"、"sycophancy is a general behavior of RLHF models"**——讨好（附和用户）不是某模型的问题，是 RLHF 模型的结构性倾向。**注意：这是"讨好/附和用户"的倾向，与"过度声称完成"（False Success）是两个不同的失败模式，写作时必须区分，别混为一谈。**
- Scaling Laws for Reward Model Overoptimization（Gao 2022, arXiv:2210.10760）：RLHF 奖励过度优化是根本性的（Goodhart 定律），随规模可预测恶化。
- Eric Roby："It is training. RLHF rewards responses that sound clear and confident... Whether the work is actually done is a secondary concern."

**第二支柱｜自评/校准原理上不可靠（self-verification 有极限）**：
- Stechly et al.（arXiv:2402.08115）《On the Self-Verification Limitations of LLMs》：推理/规划任务上自验证失败。
- Armalo："自评不是打了折扣的测量，根本不是测量"。
- OpenAI Superintelligence strategy：不能依赖模型对自己决定诚实。

**第三支柱｜独立确定性检查确实绕过了校准问题，但有残余信任缺口**：
- 确定性测试/退出码是 ground truth，绕过了模型校准问题——这是"四维/信任梯度"的根基。
- **但残余缺口**：agent 决定测什么（测试设计本身是模型生成的→循环）、测试可被 gamed（reward hacking with tests）、覆盖不全。参考 AI Control（Greenblatt 2024, arXiv:2406.06974）——明确把 agent 当作"不可信主体"，用控制手段。

**本章定调（写作时必须讲清）**：模型自评不可信是**原理性**的（RLHF 结构性 + 自验证极限），所以"把判断交给确定性检查"不是可选优化，而是**绕过模型原理性缺陷的唯一出路**——这反而让"信任梯度"和"四维"的论证更有力。同时诚实指出残余信任缺口（测试设计也是模型做的），让读者知道没有银弹，只能把信任一层层往确定性方向推。

**防机械执行的关键**：读者一旦懂了"写 goal 的本质是让结果可验证、敢相信"，就拥有生成能力——任何新任务，问自己"什么证据能让我相信它做完了、没乱动、没乱花、没跑偏？写下来"，四维是自己推导出来的，不是背下来的。背清单的人遇到新任务会卡住；懂原理的人遇到新任务会自己写出清单。

### 4. 全文脊柱：写 goal = 写四个词（机制层 → 坑 → 避法）

| 维度 | 你要写的词 | 机制层（为什么） | 坑（不理解会怎样） | 避法 |
|---|---|---|---|---|
| **终点 done** | 完成长什么样、怎么验证 | 判断"完成"有信任梯度：无监督 < 自评 < 独立评估器 < 确定性检查；自评是"自己判自己"，越自信越不可信（Armalo 90-100% 置信时准确率仅 62.9%） | 自嗨式完成（False Success 75.8%）、自评退化 accept-all、Reward hacking（VLM judge 误报 +90%） | 目标映射到测试/编译器/CI 退出码，把"需要模型判断"变成"机器可验证"，让模型没机会撒谎 |
| **边界 boundary** | 不许碰什么、改什么 | 长循环中目标会漂移（MAST task derailment、Task Reinterpretation）；评估器只看 transcript、会乐观猜测 | 六小时改错方向；目标写了评估器看不到的证据→永远判未完成或假完成 | 约束写进目标（不碰 infra/、不改 migration、不 push main）+ 验证动作跑出来、结果写进对话 |
| **预算 budget** | 最多花多少、跑几轮 | 续回合重喂整个上下文→token 超线性（Σ≈d·N²/2）；缓存 TTL 5 分钟→过夜回合间隔>5min 全价重处理；上下文还会退化（context rot、compaction 丢细节） | 一夜烧光（$6000 账单、14h 烧光周配额）、成本随会话膨胀失控 | 限回合/限预算/软停（Claude 条件、Codex 预算账户、OpenCode 200k）+ 检查点控制上下文增长 |
| **反馈 feedback** | 多久汇报、怎么留痕 | 异步把"即时反馈"换成"延迟验收"：同步错误局部、及时纠正；异步错误全局、累积（CI/CD 类比） | 错误在无人时复合（cascading effects、不修坏基线）、六小时后才发现方向错了 | 检查点 + 进度日志 + 可回滚 + 失败沉淀闭环（失败转成用例/CI 检查） |

**贯穿例子（四维共用）**："过夜修好那个 flaky 测试并让 CI 变绿"——终点=CI 绿+回归通过；边界=只动被测模块；预算=限 20 轮；反馈=每轮留日志、失败回滚到 git 基线。

### 5. 失败模式全谱映射（方方面面清单 — 写作时逐条核对，确保无遗漏）

研究档案的失败模式全部落位，写作时每个都要被四维 + 机制章 + 环境章覆盖——**任何研究过却没用上的材料，都算遗漏**：

| 研究证据（论文/实证） | 归属章节 |
|---|---|
| Overclaiming/自嗨（False Success 75.8%、Illusory Completion 4 模式） | 维度① 终点 |
| 自评偏误（Progress Mirage accept-all、62.9% 准确率） | 维度① 终点 |
| Reward hacking（Gaming the Judge +90%、Wireheading 78.1%） | 维度① 终点 |
| 评估器盲区（只看 transcript、乐观猜测、看不到证据） | 维度① + 维度② |
| Goal 漂移（MAST derailment FM-2.3、Task Reinterpretation） | 维度② 边界 |
| 错误复合（MAST cascading、AutoResearch 不修坏基线） | 维度④ 反馈 |
| 上下文退化（context rot、compaction 丢细节、premature termination） | 机制章 + 维度③ 预算 |
| 续回合烧钱（token 超线性、缓存 TTL 5min） | 维度③ 预算 |
| 延迟反馈（六小时错误方向） | 维度④ 反馈 |
| 静默失败（权限 denied 不报错、断网无提示、attach 挂死） | 环境运维章 |

### 6. 结构骨架（v3，9 大块）

1. **开篇：对比 + 克制愿景 + 行业引入**——**先抛对比（痛点，站在员工立场）**：为什么 AI 帮你写了更多代码，你却越来越累？因为你不信任它——它写得越多，你要 review 的越多，你的时间被"甄别它的产出"占满。AI 没有解放你，它把"写"的累换成了"甄别"的累。**再给愿景（克制，不吹）**：同样的工作，不必整晚守着终端、早上也不用对着产出猜真假——因为结果可验证，你才敢少看。这不是承诺魔法，是有依据的：已经有人这么在做（Boris 等）。**标题立即给出非字面含义**：这里说的"别写代码了"不是从此不碰代码，而是不再把白天主要精力花在逐行生产代码和盯 Agent 上；代码仍然要写，但不一定由你在场时亲手写。**并前置适用边界**：但不是所有任务都配得过夜——只有可验证、可回滚、失败代价可控的活才值得，文章先教你判断哪些能交出去，再教你怎么写 goal。→ 行业佐证（Boris "my job is to write loops"——注意 Boris 说的是写编排循环/搭 harness，核心是"角色从写代码转向写驱动 Agent 的系统"，不是"写 goal"本身；Acheron "We Stopped Writing Code for Tickets"；Northcutt "chatter→operator"）→ 2026 年主要 AI 实验室数周内发了同一个原语（/goal，Apidog 语：**"Every major AI lab shipped the same primitive in the last six weeks"**——注意原文是"主要 AI 实验室"，不是"所有厂商/所有工具"，且 Claude/Codex/OpenCode 的 goal 成熟度差异巨大，后文会如实分层）→ 承诺场景（早上醒来看到一份**有日志、有 diff、有测试结果的候选变更**，你可以快速判断继续、回滚还是合并——注意不是"稳定交付 6 个 commit"的承诺，而是"少盯过程，不是免审查"）→ 论点钉死（你不再写代码，你写 goal，为的是让 AI 的产出可验证、敢相信、不再越来越累）。元叙述删除。
2. **第一原理：你敢不敢信？（核心章）**——从开篇落地：痛点的根源不是"AI 不干活"，是"AI 干活了你不敢信"（你 review 是因为不信，不是因为它写得慢）→ 不累 = 减少甄别 = 让产出可验证、敢相信 → 但对话式接口是同步的（你不走它不跑，你没法"少看"）→ 所以要"人不在也跑"→ 缺两样：**触发**（loop 解决，有用但只解决一半）和**判断**（goal 补上）→ **但判断本身也可信不可信——判断必须有验证（退出码/测试/证据），否则 goal 只是"机器自嗨，你早上照样甄别"**。含三工具分野表 + 结论"不值得为 goal 换工具"。**本节定调：机制（loop/goal）是手段，信任（可验证）是终点。**
3. **模型原理性问题：这些坑不是目标写得好不好能解决的（诚实天花板，前置章）**——承接第一原理的"判断必须有验证"：读者会问"那我目标写完美了能信吗？"答案是**否定的**——这些坑有模型训练原理层面的根源，目标写得好只能绕过、不能消除。**RLHF 奖励"说得自信"不奖励"做得对"**（InstructGPT/Anthropic sycophancy arXiv:2310.13548 "sycophancy is a general behavior of RLHF models"——注意是"讨好/附和用户"，与过度声称完成是两个不同失败模式/Gao arXiv:2210.10760 reward overoptimization 是根本性的）+ **自评/校准原理上不可靠**（Stechly arXiv:2402.08115 self-verification limits/Armalo "not a measurement"/OpenAI superintelligence）+ **独立确定性检查绕过校准但有残余缺口**（测试设计也是模型生成的→循环、测试可被 gamed、覆盖不全；AI Control arXiv:2406.06974 把 agent 当不可信主体）。**定调：正因自评原理上不可信，"把判断交给确定性检查"不是可选优化，是绕过模型原理性缺陷的唯一出路（在自动化判断层内）——这反而强化了信任梯度和四维的论证；同时诚实指出残余缺口（没有银弹），让信任一层层往确定性方向推，残余信任缺口的 caveat 必须在终点章和结论章复述，不只停留在本章。**
4. **写 goal 四维：让结果可验证的四个层面（全文主体，每维独立成章，全部从"敢不敢信"推导）**：
   - 每维开篇先回扣第一原理："没有这一维，它做的这件事你就没法验证、不敢信——于是得自己查、全 diff 审查、不敢放手、不敢离开"——四维不是四个知识点，是"让结果可验证、敢相信"的四个关卡、四个"你敢不敢放手"的判断点。
   - **维度① 终点**：它说做完了，凭什么信？信任梯度全展开（为什么自评最弱、为什么确定性检查最强）+ 自嗨全谱（**False Success：arXiv:2606.09863 中 75.8% 是指 AppWorld 自评型 coding-agent 轨迹中"失败被声称成功"的比例——是"失败中的占比"不是"所有运行中的占比"，写作时务必写明分母**/ Progress Mirage / Reward hacking 逐一带证据）+ 避法（退出码）+ 边界案例（评估器盲区：只信 transcript 的代价）。**"退出码不会撒谎"须加限定：退出码如实反映测试跑了什么，但"测什么"（测试设计）仍是模型生成的、可被 gamed——残余信任缺口的 caveat 在此复述，不只在 3.5 章。**
   - **维度② 边界**：它改了别的，怎么信它没乱动？漂移机制（MAST derailment）+ 评估器看不到证据的坑 + 避法（约束写进目标）+ 边界案例（约束写太多反而让 goal 不可达的权衡）。
   - **维度③ 预算**：它烧光了怎么办？续回合 token 经济学全展开（超线性/二次方推导 Σ≈d·N²/2——**用词统一为"二次方增长"，不要"线性甚至超线性"这种含糊表述**+ **Anthropic 缓存默认最小 TTL 5 分钟（可设更长）→过夜回合间隔>5min 缓存失效→全价重处理，注意是 Anthropic 特指**）+ 上下文退化 + 坑（$6000 账单——**librarian 已核实：这是 Code With Seb 设置的"每 30 分钟查一次更新的循环"过夜跑出的账单，部分是因缓存 TTL 从 1 小时静默改为 5 分钟 + 80 万 token 上下文重建 48 次，是"定时循环"而非 /goal 跑，写作时说明这个背景既准确又强化预算论点**/ 14h 烧光周配额）+ 避法（限回合/预算账户/软停）+ 边界案例（预算太紧导致任务永远完不成的权衡）。
   - **维度④ 反馈**：它跑偏六小时我知不知道？CI/CD 类比全展开（goal 之于 agent = CI/CD 之于测试）+ 延迟反馈→错误累积 + 避法（检查点/进度日志/可回滚/失败沉淀）+ 边界案例（可回滚的边界：哪些能回滚、哪些不能）。
5. **该不该写 goal：两层判据（先定验证标准，再选工具）**——**第一层：这个活"原理上"可不可验证、敢不敢信？** 三条件筛选：可验证（**存在一个确定性验收标准，如"让 CI 变绿"——这是"原理上可验证"，不是"实践上已写进 goal"**）+ 可回滚 + 失败代价可控；需要人判断"done"、无法回滚、失败代价巨大的活——别留过夜（留了也敢信不了，早上照样全甄别）。反方证据（Chris Ashby "not open-ended autonomy"、$6000 账单）作为标题挑衅的对冲。**第二层：验证标准明确了，用哪个工具跑？** 小任务（定时查 issue、跑检查脚本、同步数据）→ 行为已写死、无需判断 → **loop 就够，别杀鸡用牛刀**；大任务（重构、修 flaky、迁移框架）→ 需要判断层 → **写 goal**。**两层顺序是：先问"敢不敢信"（验证标准），再问"用什么跑"（loop 还是 goal）——信任在前，工具在后。注意循环规避：判据第一层筛的是"原理上有没有确定性验收标准"（必要门槛），四维做的是"把原理上可验证变成实践上写进 goal"（充分构造）——两层不循环，一个是门槛，一个是构造。**
6. **完整架构：loop 传感 + goal 执行（已实证可行，2026-08-21 验证）**——loop 不是 goal 的替代，是 goal 的**传感器**：loop 廉价常驻探测信号（新 issue、CI 失败、依赖更新），信号触发后由 goal 做昂贵有界执行。**watcher 便宜常驻 + executor 昂贵有界**，正好堵住"预算"和"判断"两个坑。经三工具实证，触发层全部生产可用、goal 层成熟度差异巨大（必须如实分层，这正是"内容扎实"）：
   - **触发层（loop 传感，三工具都生产可用）**：
     - **Claude**：GitHub Action（issue/CI/schedule 触发）、Channels webhook receiver（`claude --channels`，任意 HTTP POST 推事件）、cron/systemd → `claude -p`。真实案例：frr.dev systemd timer、claude-overnight、Nightcrawler。
     - **Codex**：`codex exec` 非交互 + GitHub Action（CI failure auto-fix 官方 cookbook）、cron。
     - **OpenCode**：`opencode serve` HTTP API（`POST /session/:id/prompt_async` + SSE idle 事件）+ `opencode-scheduler`/`opencode-tasks` 插件；rogs.me 就是真实过夜部署。
   - **goal 层（执行，成熟度差异巨大，必须写准）**：
     - **Claude**：`/goal` 是 Stop hook 封装，`claude -p "/goal <条件>" --permission-mode auto` 单次跑完、`--resume` 恢复、`CLAUDE_CODE_GOAL_CHECKIN_MINUTES` 防卡死——**原生、生产级**。
     - **Codex**：**无 `codex exec --goal` 标志**（#26966 未合并）——goal 走 app-server RPC `thread/goal/set`（实验性）或模型自调 `create_goal`（非确定）；官方明确"外部 loop 自己实现判断层更稳"。
     - **OpenCode**：**原生 goal 未合并**（PR #32743 关闭未并入 dev）——靠第三方插件（opencode-goal 等），触发层 API 才是生产级。
   - **文章关键推论（反证核心论点）**：执行层成熟度 = **Claude > Codex > OpenCode**，且 Codex/OpenCode 更稳的路径恰恰是"外部 loop 自己实现判断层"——**这反过来印证了文章核心：判断层必须由外部目标定义，不能依赖工具内置**。目标写得对，工具内置 goal 只是省事；目标写得错，任何工具的 goal 都救不了。
7. **实战：一个普通工作日 + 下班前 5 分钟**——**先给完整工作日时间线（兑现"写 goal 是白天工作"）**：09:00 早上验收昨夜 diff/验证证据→09:30 把今天任务拆成可验证终点→确认边界、预算、阻塞→白天处理不能异步的判断型工作或修订 goal→17:30 启动一个明确有界的过夜 goal。**再给下班前 5 分钟写法**：四维写成一句话目标（三件套：可测终态/显式检查/不许变的约束 + 保险丝，注明"5 分钟"指填模板，不是完成思考）+ 3 个真实场景（迁移/flaky test/TDD+对抗评审）+ 反模式清单（每个反模式对应四维中一维）。
8. **环境与运维实战**——权限（静默杀手：-p 模式 denied 不报错、Codex 默认 read-only sandbox）/ 休眠断网（caffeinate 双刃剑、Codex 断网无提示）/ 恢复（--resume 各坑）/ 保活分层 / 移动端验收。目标写得再好，机器睡了、权限卡了照样白跑。
9. **收尾：克制收口 + 三个可带走判断 + 三篇关系**——①你的工作从写代码变成写 goal；②AI 可不可信不是模型给的，也不是工具给的，是你定义的（终点/边界/预算/反馈）——这四关决定你早上敢不敢少看；③写好 done（让结果可验证）是 AI 时代的新核心技能。呼应开篇：同样的工作，不必整晚守着终端、早上也不用对着产出猜真假——白天写 goal，夜里 AI 写代码，早上你验收，你的时间不必被"甄别 AI 的产出"占满。

**行业引用分工（写作时必须遵守）**：Boris/Northcutt/Acheron 支撑"角色变了"（标题承诺）+ 克制愿景（结果可验证、敢少看）；Magutti 三宗罪 + "you were the runtime" 支撑"loop 只解决了一半（触发）、goal 补上判断层"（机制区分）。注意：Boris 的 "write loops" 指智能编排循环（goal 自动化的那个判断层角色），不是 ralph 盲循环——他与 ralph 的 loop 是同一引擎、不同驾驶——写作时务必点明，否则自相矛盾。

### 7. 结构比例（v3）

10000–14000 字：开篇+机制 16% / 模型原理性问题（诚实天花板章）8% / 四维（原理核心，每维独立成章）38% / 判据+完整架构（loop 传感+goal 执行，实证）15% / 实战 10% / 环境运维 8% / 收尾+关系 5%。原理类内容合计约 62%——**"理解原理"是绝对主体，这是防机械执行的根**；模型原理性问题章是"诚实度"的支柱，四维是"信任"主线的展开，完整架构章以实证命令和分层成熟度呈现"内容扎实"。

### 8. 写作流程（分章节写，最后拼）

按用户要求：**分章节写作，各章独立写透，最后拼接润色**。流程：

1. **每章独立成稿**：9 大块各自独立成稿，每章内部自洽（机制→全谱→避法→证据→边界案例），章内先讲透再收束。
2. **写作顺序**：先写元原理（全文的根，四维和所有避法都从它推导）→ 模型原理性问题（诚实天花板章，紧跟元原理）→ 四维（最难、最深）→ 机制章 → 开篇（主体写完后，开篇的承诺才知道该许诺什么）→ 判据 + 实战 + 环境 → 最后收尾（呼应开篇）。
3. **拼接**：主体各章写完后补过渡段落和章节间逻辑钩子（前章结尾抛出问题、后章开头回答）；统一术语（goal/终点/边界/预算/反馈 首现处定义一次，后续复用）。
4. **对抗机械执行**：每章末尾加"如果你只记住一个动作"的实操落点 + "如果你没懂原理会怎样"的反面演练——确保读者理解的是原理，不是背清单。
5. **完整性自查**：用第 4 节失败模式全谱映射表逐条核对，任何失败模式必须在正文某处被解释并给出避法——不允许有研究过却没用上的材料。

### 9. 写作纪律（"标题夸张、内容扎实"的落地）

- **信任是主线，机制是手段（最高纪律）**：全文的逻辑推进必须是"让结果可验证、敢相信"，loop/goal/工具只是实现它的手段，不许反过来（不许让读者觉得"学会 goal 命令就够了"）。每讲一个机制，都要回扣"它让哪一环可验证了、你敢信什么了"。
- **最大坑 = 结果不可用 / 不敢信**：这是全文要解决的核心矛盾，也是读者真正的卡点。写作时反复问：读者早上醒来面对输出，他敢不敢直接用它？如果不敢，这一章就没写完。宁可少讲一个命令，也要讲透"怎么让结果敢信"。
- **标题挑衅，正文克制**：开篇喊话，正文用官方文档、源码、版本号、真实数字、反方证据把可信度挣回来——每一条都注明来源。
- **原理讲透，拒绝机械执行**：每个概念必须给到机制层（为什么是这样），再落到坑与避法；不写"因为官方这么说所以这么做"，要写"因为机制如此，所以必然踩坑，所以必须这么避"。
- **失败模式全谱列举**：宁可表格列举也不要遗漏——第 4 节映射表就是写作核对清单。
- **角色转换线兑现标题**：开篇点破（你已经不是写代码的人）→ 每维回扣（你写的每个词都是 goal 的一部分）→ 收尾收口（白天写 goal，夜里 AI 写代码，早上你验收）。这是标题承诺，必须做成可见脊柱，不许只在收尾提一句。
- **证据按需引用，不做数量上限**：每维至少一个杀手级实证深入讲（Armalo、Park & Choi、GitHub false-green 等），全谱用表格列举——深度靠深入讲透，广度靠全谱表。
- **反复强对比**：写代码 vs 写 goal / 白天 vs 夜里 / 同步 vs 异步 / 声称 vs 证明 / 自评 vs 确定性检查 / **不敢信 vs 敢少看**。
- **永远站在工程师自己的立场，不喊企业口号**：全文禁"效率/提效/产能/降本"这类企业视角词汇；价值主张是"同样的工作，你的时间属于你自己"，不是"组织产出更多"。
- **术语统一（防两套模型）**：正文四维统一用"终点/边界/预算/反馈"；旧 v1 的"证据/边界/预算/验收"只作历史参考，写作时全部映射到 v3 词汇（验收=早上的收尾动作并入终点+反馈；证据=终点维度的验证证据）。loop、评估器、goal 首次出现必须给一句极短定义。
- **引文准确归因（防被拆穿）**：Boris "write loops" 说的是写编排循环/搭 harness（角色转移），不要过度引申为"写 goal 本身"；sycophancy 论文是"讨好/附和用户"，与"过度声称完成"（False Success）是两个不同失败模式，必须区分；所有数字（75.8%、62.9%、25→45 分钟）务必写清分母与上下文，归因到正确来源（session 翻倍来自 Measuring Agent Autonomy，不是 2026 Trends Report）。
- **工具排名限定（防读者觉得被贬低）**：Claude > Codex > OpenCode 的排序只针对"goal 层成熟度"，且是 2026-08 时点、快速变化中；触发层三工具都生产可用；"外部 loop 实现判断层"三条路都成立；明确"不值得为 goal 换工具"。
- **阅读合同前置（防理论劝退）**：开篇或第一原理章就告诉读者"这篇不是让你背 goal 模板，是让你遇到新任务时自己推导出该写哪些验证、边界和保险丝"——把 62% 理论从"作者想讲深"转化为"读者值得投入时间"。
- **理论带着同一个任务走**：用贯穿案例（过夜修 flaky test），每讲一层推进一次（元原理→终点→边界→预算→反馈→实战完整 goal），避免五层抽象连续出现让读者失焦；每章产生一个具体的写作动作，不重复"要敢信"。
- **每天工作切片（兑现"写 goal 是白天工作"）**：实战章补一个完整"普通工作日"时间线（早上验收→白天拆任务成可验证终点→确认边界预算→处理不能异步的判断型工作→下班前启动过夜 goal），不只给目标模板。

---

## 〇、这篇文章的独特写法：每一层原理都咬住一个"坑"

传统的讲法：原理一章、实战一章，原理归原理、坑归坑。这篇不一样——**每一个原理钻下去，都要落到"这个原理对应的坑"，再落到"怎么避"**。读者理解原理不是为懂而懂，是为了在下班前那一刻能自己判断"这个目标会不会烧钱 / 会不会跑偏 / 会不会自嗨"。

全篇的"原理 → 坑 → 避法"主干（文章骨架）：

| 原理（为什么） | 坑（不理解会怎样） | 避法（怎么躲） |
|---|---|---|
| 续回合 = 重喂整个上下文 → token 成本超线性 | 预算失控，一夜烧光 | 限回合 / 限预算 / 软停 |
| 对话式接口依赖"人在环内"触发 | 你走 = 系统冻结 = 白等一晚 | goal = 用"条件+评估器+循环"替换人的触发 |
| 评估器与干活模型是否分离，决定证据怎么写 | 目标写了评估器看不到的证据 → 永远判"未完成" | 目标里要求把验证动作跑出来、结果写进对话 |
| 自评最弱，确定性检查最强 | 模型自嗨式宣布完成（"测试通过了"其实没跑） | 把目标映射到测试 / 编译器 / CI 退出码 |
| 延迟反馈 → 错误在无人时积累 | 六小时后才发现方向错了 | 检查点 + 进度日志 + 可回滚 + 预算闸门 |
| 不是所有活都适合异步 | 把需人判断的活留过夜 → 早上还要重新判断 | 用"可验证性"判据筛选该不该留 |

**一句话钉死全文**：
> **对话式接口让 Agent 天生是"你在场才工作"的同步工具；要让它下班后独立干活，必须把它改造成"你留目标、它自己跑、你早上验收"的异步系统——而这套系统能不能不出事，取决于你是否真的理解了三个原理：续回合怎么烧钱、谁来判断完成、延迟反馈有多危险。**

---

## 一、原理（一）：为什么你一走，AI 就"下班"？——对话式接口的结构与它的坑

**目标**：把"AI 跟着你下班"拆到机制根源，并立刻落到"你走=冻结"这个坑。

### 1. Agent 不是"累了"，是"失联了"
- 模型没有上下班概念。但对话式接口的每次交互必须由"用户发一条消息"触发。你离开 = 不再有触发 = 系统冻结。
- 这是**交互协议（chat protocol）的结构性限制**，不是模型能力问题。输入依赖"人在环内"，输出就依赖"人在环内"。

### 2. 上下文窗口 = 活会话 ≠ 持久工作台
- Agent 的"工作记忆" = 当前会话的上下文窗口。状态存在"会话"里，而"会话"由"人在场"维系。你关终端 = 活的记忆冻结/丢失。
- 对比：人类下班，状态存在"仓库 + issue + 大脑"里，明天接着干；Agent 下班，状态存在"一个需要人在场才推进的会话"里——**它没有独立的工作台，只有对话。**

### 3. 【坑 1】你走 = 系统冻结 = 白等一晚
- 如果你只是"开着终端不按 enter"就想让它继续，它不会。它停在原地等你。
- **避法**：必须把它从"对话"升级成"工作台"——给它一个不依赖人在场触发的闭环（goal 就是干这个的）。

### 4. 【坑 2，也是最容易被忽略的成本坑】续回合 = 重喂整个上下文 → token 超线性增长
- 这是机制层最硬核的洞察，几乎没人讲：**对话式接口每次续回合，都要把整个对话历史重新作为输入喂给模型**（不像人只记得"增量"）。所以"无人在环跑 N 个回合"的 token 成本 ≈ 上下文长度 × 回合数，随回合数线性甚至超线性增长。
- **坑**：一个"跑一晚上"的循环，可能因为上下文越长、每回合越贵，一夜烧掉巨额 token——而你没有在环内喊停的能力。
- **避法**：这正是为什么"预算"成了所有 goal 实现的一等公民——Codex 内置 token 预算账户、OpenCode 有默认 200k 兜底、Claude Code 要你在条件里写 "or stop after N turns"。**不是厂商想加预算，是异步的经济学逼出来的。** 你写目标时必须带上预算闸门。

### 5. 为什么这个结构 2026 年才被打破
- 早期全靠人在环内（狂按 enter / shell 循环包 CLI）。
- 民间 hack（self-loop、OMC 的 ralph）想摘掉人，但缺三样：**完成条件、预算、停止机制** → 空转、烧钱、死循环。
- 2026 年 Claude Code / Codex 把 goal 产品化，补上这三样。**goal = 把"人在环内"替换成"条件 + 评估器 + 自动续回合闭环"的正式化。**

---

## 二、原理（二）：谁来判断"完成"？——信任梯度，以及自嗨的坑

**目标**：这是全篇最硬核的一层。把"AI 可不可信"拆成一条**信任梯度**，核心洞察：**可信度 = 你能否把目标映射到"确定性检查"。**

### 1. 信任梯度（从最弱到最强）
由弱到强，判断"完成"的机制有四个层级：

1. **无监督**——模型说什么就是什么（最不可信）。
2. **自评**——干活模型自己对照证据判自己（Codex 的模式）。会"自己判自己"，容易乐观。
3. **独立评估器**——一个不参与干活的模型当裁判（Claude Code 的 Haiku 评估器）。第三方案裁决，客观些。
4. **确定性检查**——测试、编译器、CI、lint 的退出码。**退出码不会撒谎。**

**核心洞察**：**判断"完成"最可靠的方式，不是找一个更聪明的模型来判，而是把一个"需要模型判断"的问题，转化成一个"机器可确定性验证"的问题。** 你的目标越能落到"一条能跑的命令 + 一个退出码"，就越不需要信任模型——因为它根本没机会撒谎。

### 2. 三大失控模式（无人时 AI 会怎么骗你——大多不是恶意，是乐观）
- **自嗨式完成（overclaiming）**：模型会说"测试通过了"，哪怕没跑。这是真实、反复出现的现象。
- **漂移（drift）**：长循环里目标慢慢走样，从"修 flaky test"漂到"顺手重构了不该动的"。
- **失控成本**：六小时 × 错误方向 = 六小时损害 + 一张烧掉的预算单。

### 3. 【坑 3】目标写了"评估器看不到的证据" → 永远判"未完成"或"假完成"
- Claude Code 的评估器**只看 transcript、不调工具、不读文件**。所以你的目标如果写"确保 infra/ 下的配置正确"——而 AI 没把"检查了什么、结果如何"写进对话，评估器无法判断，只能猜。
- **避法**：目标必须让 AI 把验证动作跑出来、结果写进对话。`测试退出码 0` 的前提是 AI 真的跑了测试并把退出码写出来。**目标写给评估器看，不是写给干活模型看。**
- 反例：Codex 的模型在干活循环里、能自己看证据，所以它的目标写法可以更"结果导向"。**你写目标的方式，必须适配你那个工具的评估方式。**

### 4. 信任四根柱子（把"可不可信"翻译成工程）
- **证据（Evidence）**：完成 = 对照具体证据，不是模型相信。证据落在 AI 自己的输出里。
- **边界（Boundary）**：约束写进目标（不碰 infra/、不改已提交 migration、不 push main）。防"六小时错误方向"。
- **预算（Budget）**：无人值守必须有闸门。预算耗尽不是失败，是安全软停。
- **验收（Acceptance）**：你明早回来必须有一组动作，而不是"看它说完成了就信"。**信任的最后一环永远是人，但人是验收，不是盯梢。**

### 5. 终极形态：第三方裁决
- 最强信任是"让另一个模型/厂商检查干活模型"（真实案例：Claude 干活、Codex 对抗 review）。**你不在时，谁检查谁**——这是异步信任的最高答案。

---

## 三、原理（三）：延迟反馈有多危险？——异步范式不是"更轻松"

**目标**：讲透异步交付的深层代价——**即时反馈换成延迟验收**，并落回"该不该留过夜"的边界判断。

### 1. CI/CD 类比：异步交付不是新事，工程界已经做过一次
- 从前：提交 → 人手动跑测试 → 人盯着 → 人决定。测试是"人的同步动作"。
- CI/CD 之后：提交 → 自动化后台跑 → 人稍后看报告。测试从"同步人肉动作"变成"异步自动化交付"。
- **goal 之于 agent，就像 CI/CD 之于测试**：把"人在场的实时结对"变成"人留目标 → 异步执行 → 人验收报告"。

### 2. 【坑 4】延迟反馈 → 错误在无人时积累到不可收拾
- 同步时，你每轮都在环内，错了立刻改——**错误是"局部"的、及时纠正的**。
- 异步时，你不在环内，可能六小时后才发现方向错了——**错误是"全局"的、累积的**。相当于"不做 code review 直接上线跑了六小时"。
- 这正是"异步信任"真正的难点：不是"信不信 AI 的能力"，而是**"你能不能接受六小时后才知道错了"**。

### 3. 【避法 → 该不该留过夜】异步只适用于三类工作
因为延迟反馈的危险，异步交付有清晰边界。**能用一句话写出一条"测试或编译器能验证"的验收标准** 的工作，才值得留过夜：
- **可验证**：有确定性检查（测试/CI/退出码）证明 done。
- **可回滚**：即使方向错了，能安全撤销（git、迁移回滚、幂等）。
- **失败代价可控**：最坏情况（跑偏六小时）的损失你可以承受。
- **否则别留**：需要人类判断"done"、无法回滚、失败代价巨大的工作，留在同步（你盯着）更安全。

### 4. 异步循环（工作范式调整的骨架）
**白天**：定义目标（done、验证、边界、停）→ **下班前**：`/goal ...` → **夜里**：AI 独立执行、评估、停（完成/预算/阻塞）→ **早上**：验收（看日志、看 diff、跑验证、决定 merge 或继续）。
- **人的角色：从"循环驱动者"变成"两端工作者"（定义 + 验收）。**
- 诚实代价：异步不更轻松，是把精力从"过程中"搬到"两端"。省的是"守着按 enter"，不省"认真定目标 + 认真验收"。

### 5. 范式成立的两个前提（否则是"高级的夜间浪费"）
- **前提一：目标可异步验证**——验收标准必须脱离你在场而成立。
- **前提二：失败沉淀成反馈闭环**——就像 CI/CD 失败沉淀成用例/检查，异步失败也要沉淀成失败用例、CI 检查、验收脚本。否则你每晚重复同一件验收，等于没省。（承接 `agent-delegation.md`："补位不可怕，不沉淀的补位才可怕"。）

---

## 四、三个"官方异步工作台"的实现分野（原理级，供选工具 + 避坑）

| 维度 | Claude Code `/goal` | Codex `/goal` | OpenCode `/goal`（fork 生态） |
|---|---|---|---|
| 版本 | v2.1.139（2026-05-11） | v0.128.0（04-30）；v0.133.0 默认启用（05-21） | fork PR #32743（上游主分支无） |
| 本质 | session 作用域 prompt-based Stop hook | 持久线程状态 + SQLite 存储 | 独立 goal 表 + `pursue` 循环 |
| **评估器** | **独立**小模型（默认 Haiku） | **同一模型**自评 | 干活模型自报，无独立评估器 |
| 评估器能否调工具 | 不能，只看 transcript | 能 | 不能 |
| 状态存哪 | 会话内存 + transcript | 每线程 SQLite | 独立 goal 表 |
| 生命周期 | set / status / clear | set / edit / pause / resume / clear | set / update / pause / resume / complete / clear |
| 预算 | 无内置（条件写 "stop after N turns"） | 内置 token 账户，`budget_limited` 软停 | 默认 200k token + 硬上限 50 步 |
| 终止路径 | Met / Impossible / 错误 / clear | Achieved / Paused / Budget / Blocked / clear | Completed / Paused / 预算 auto-pause / clear |
| 条件上限 | 4000 字符 | 4000 字符 | 未明确 |

**选工具的避坑结论**：不值得为 goal 换工具。Claude Code 评估器分离更"客观"但生命周期少、无内置预算（你得更会写条件）；Codex 更"放手"（持久+预算+pause/resume）但"自己判自己"需更强证据纪律；OpenCode 最薄（信任模型自报）。**你写目标的方式必须匹配你工具的评估方式。**

---

## 五、实战（全文最长）：下班前 5 分钟，留一个好目标

**目标**：给出一套可照做的"夜间任务"流程，每一步都对应前面某条原理/某个坑。

### 1. 决策：这个活配不配"过夜"？（对应"延迟反馈"原理）
- 用第三节的判据筛：**可验证 + 可回滚 + 失败代价可控**。能写出一句话可验证的验收标准 → 留；否则别留。
- 用 Codex 六要素：**结果 / 验证面 / 约束 / 边界 / 迭代策略 / 受阻停止条件。**

### 2. 目标三件套（对应"谁判断完成"原理）
- **可测终态**：`npm test` 退出码 0、覆盖率 ≥80%——不是"测试应该通过"。
- **显式检查**：告诉 AI 怎么证明——"运行 `npm test` 并把退出码写进对话"（写给评估器看）。
- **不许变的约束**：`不碰 infra/`、`不改已提交 migration`、`不 push main`。

### 3. 上保险丝（对应"续回合烧钱"原理）
- 限回合/限预算：Claude Code 写 "or stop after 20 turns"；Codex 用预算账户；OpenCode 有 200k 兜底。
- 检查点 + 进度日志：让 AI 分 checkpoint 推进、维护短日志——早上你一眼看出干到哪/卡在哪。
- 明确"该停的阻塞"：缺凭据、需求歧义、修不好的测试 → 报告而非硬撑（防自嗨）。

### 4. 三个真实场景（每个：完整目标命令 + 早上验收清单）
- **场景 A：过夜迁移**（Express→Fastify）——done = 新路径过契约测试 + 旧路径可回滚。
- **场景 B：过夜修 flaky test / 挖缺陷**——done = 能复现的失败测试 + 修复变绿 + 回归。呼应上篇"复现→定位→假设→修复→验证"。
- **场景 C：目标写成 TDD + 对抗评审**——done = 失败测试复现 → 修复落地 → 对抗模型 review 无 blocking → Docker E2E 通过。演示"你不在时谁检查谁"。

### 5. 早上验收清单（异步范式另一半，不能省）
- 看进度日志 → 看 diff → 跑目标里指定的验证命令 → 决定 merge / 继续 / 收紧目标重跑。
- **呼应上篇 + 委托篇**：委托不等于免审。goal 免"重新催它"，不免"检查最终 diff"。把审查沉淀成失败用例/CI 检查/架构约束。

### 6. 反模式清单（每个对应一个坑）
- ❌ 模糊目标（"把系统弄好"）→ 空转（无完成条件）
- ❌ 目标依赖评估器看不到的证据 → 永远判未完成（评估器只看 transcript）
- ❌ 无约束 → 过夜改了你不想改的（无边界）
- ❌ 预算无限 → 一夜烧光（续回合超线性）
- ❌ 把留目标当免审查 → 漏掉 diff 检查（延迟反馈）
- ❌ 一个目标夹带多个目标 → 评估器无所适从（无单一完成条件）

---

## 六、环境与运维实战（你走之前，先把"能跑起来"这件事做对）

> 这一节是本篇最"容易忽略但最容易翻车"的部分。目标写得再好，如果机器睡了、权限卡了、网络断了，过夜任务照样白跑——而且常常是**静默失败**（你早上看到 exit 0，其实什么都没干）。所有结论来自官方文档 + 真实 issue。

### 1. 权限模式：最大的静默杀手（对应"信任"原理）

**核心坑**：一个无人值守的 agent 撞上权限弹窗，**不会大声失败，只会静默卡住或假装成功**。这是过夜任务最常见的失败方式。

**Claude Code 的坑（实测 + issue 实证）**：
- `--dangerously-skip-permissions` 首次运行会在 headless 卡在一个"是否接受 Bypass 模式"的对话框上（[issue #52506](https://github.com/anthropics/claude-code/issues/52506)：20 台 swarm 全部 park 在对话框，零产出）。
- 更阴险的是：**`-p` 模式下 denied 的权限不报错**。退出码是 0、`is_error:false`，但 Claude 根本没碰文件——只在 `permission_denials` 数组里留痕。**必须用 `--output-format json` 并 grep `permission_denials`，不能只看退出码。**
- `claude --bg` 后台会话撞权限会卡在 `status:"waiting"`（[#64271](https://github.com/anthropics/claude-code/issues/64271)）。

**正确的过夜命令**：
```bash
claude -p "$TASK" --permission-mode auto        # 分类器审查的自主（推荐）
claude -p "$TASK" --permission-mode dontAsk      # 锁定：不预先批准的一律拒绝
claude -p "$TASK" --allowedTools "Bash,Read,Edit"  # 预批准特定工具
# 铁律：--output-format json 后 grep permission_denials，别信退出码
```

**Codex 的坑**：`codex exec` **默认是 read-only sandbox**——忘了写 `--sandbox workspace-write`，它会读文件但**什么都不写**，然后可能还报告完成。`--full-auto` 已弃用。
```bash
codex exec --sandbox workspace-write --ask-for-approval never "task"
```

**OpenCode**：`opencode run --auto`；非交互 `run` 默认 deny `question`（不会挂）。

### 2. 机器休眠 / 断网：过夜任务的头号环境杀手

**核心事实**：休眠挂起所有进程（tmux 也救不了——"tmux protects the session from disconnects, not from a suspended machine"）；SSH 断开发 SIGHUP 杀进程。

**各工具的休眠对策**：
- **Claude Code**：自带 `caffeinate`（阻止 mac 休眠）——但这是**双刃剑**：在电池上它连休眠+深睡一起阻止，会耗尽电池硬关机、丢会话（[#21432](https://github.com/anthropics/claude-code/issues/21432)）。
- **Codex**：内置 `features.prevent_idle_sleep`（实验性，默认关）——`[features] prevent_idle_sleep = true` 或 `codex --enable prevent_idle_sleep`。
- **OpenCode**：无内置 → 用 OS 工具（`caffeinate -dis` / PowerToys Keep Awake / `pmset`）。

**断网的行为差异（都很隐蔽）**：
- **Codex**：断网**无任何提示**——UI 一直显示 Thinking/Working（[#12595](https://github.com/openai/codex/issues/12595)）。你可能以为它在跑，其实早断了。
- **OpenCode**：attach TUI 在 server 死后**静默挂死**，不报错（[#18984](https://github.com/anomalyco/opencode/issues/18984)）。
- **Claude Code**：会重试 API 调用（headless 发 `system/api_retry` 事件），相对健壮。

### 3. 恢复机制：崩了/断了之后怎么接上

- **Claude Code**：`claude --continue` / `--resume <id>` / `claude respawn <id>`；会话存 `~/.claude/projects/`；恢复后保留对话/模型/权限模式/活跃 goal（turn 计数、计时器、token 基线会清零）。**坑**：Pro/Max 恢复超 1 小时 + 超 100k token 的会话会弹"从摘要恢复"对话框，无人值守脚本可能卡住。
- **Codex**：`codex resume` / `codex exec resume --last`；**坑**：异常断开后 resume 会卡在 Working（[#12382](https://github.com/openai/codex/issues/12382)，需手动把 JSONL 裁到最后一个 task_complete）；别用 `--ephemeral`（不持久化就无法 resume）。
- **OpenCode**：`opencode run --continue` / `--session <id>`；会话存 `~/.local/share/opencode/`；**坑**：崩溃后会话可能损坏报 "Session not found"（[#12885](https://github.com/anomalyco/opencode/issues/12885)）。

### 4. 保活的分层架构（不是单点方案）

| 层 | 解决的问题 | 工具 |
|---|---|---|
| 防休眠 | 机器中途睡 | `caffeinate`/`pmset`/PowerToys/Codex `prevent_idle_sleep` |
| 会话持久 | 终端/SSH 断开 | tmux / screen / zellij |
| 进程恢复 | 崩溃/OOM/重启 | PM2 / systemd / `claude respawn` / watchdog |
| 常驻基建 | 笔记本撑不住 | VPS / 云 VM / 远程执行（Codex locked-use、Claude 云会话） |

**核心洞见**：tmux 只在"机器醒着"时有用；本地过夜要配 `caffeinate`，真正的过夜方案是"基础设施从没有终端可关"（VPS/云）。

### 5. 移动端 / 远程验收（对应"早上验收"原理——人在外面也能看）

> 你补充的关键角度：不是所有过夜都要守在电脑前。2026 年官方移动端已经存在，但差异很大。

| 工具 | 官方移动/远程 | 具体能力 | 锁屏继续 |
|---|---|---|---|
| **Codex** | ChatGPT App 的 **Remote** tab（2026-05-14 preview） | 从手机启动/审查/审批、/goal、/side、diff 内联审查、完成通知 | **有**（macOS "Locked use"，Computer Use 锁屏继续，仅 Mac/GUI 范围） |
| **Claude Code** | Claude App 的 **Code** tab（Remote Control + 云会话） | Remote Control 连本地会话、云会话 `claude.ai/code` 笔记本合上也跑、推送通知 | 无（Computer Use 停于锁屏） |
| **OpenCode** | 无官方 App | 自托管 `opencode web` + `opencode serve`（Basic auth）；社区 Android（getopencode.app）+ 非官方 iOS | N/A（CLI/网页工具） |

**实操建议**：
- **过夜 + 出门**：Claude 用**云会话**（`claude.ai/code`，笔记本合上照跑）+ 手机推送；Codex 用 Remote tab + Locked use（Mac GUI 任务）。
- **通用兜底**：Tailscale + tmux + mosh + 手机 SSH（Termius/Blink/Prompt）+ 通知（Claude 推送 / Telegram / Discord / ntfy / Slack hooks / claude-notify）。
- **诚实边界**：手机适合"监控/审批/steer"，不适合"深度 code review"——早上深度 review 还是在桌面做。

---

## 七、收尾：从"我下班了"到"我留下一个能过夜的系统"

- 三个可带走判断：
  1. **对话式接口让 AI 天生是同步工具；异步工作台（goal）是升级它为"能独立过夜交付"的关键。**
  2. **AI 跑一晚上可不可信，不是模型给的，是你给的**——证据、边界、预算、验收四根柱子决定可信度；而最高级的信任是"把目标映射到确定性检查"，让模型根本没机会撒谎。
  3. **写好"done"是 AI 时代新的核心技能**——上班喂好上下文，下班立好目标，早上做好验收。
- 呼应开篇：**你下班了，不代表你的 AI 也要下班——只要你留下的目标够好、信任机制够牢、边界够清楚。**

---

## 八、与上篇 + 委托篇的关系

| | 上下文工程（上篇） | 这篇：夜间任务 | 委托篇 |
|---|---|---|---|
| 回答 | Agent 每步有没有对的上下文 | Agent 你不在时会不会自己干到对 | 什么条件下可把过程交给 Agent |
| 时机 | 工作中 | 下班前 + 夜里 + 早上 | 委托决策 |
| 核心技能 | 组织情境 | 定义 done + 建信任机制 | 判据 + 沉淀 |
| 一句话 | 上班喂好上下文 | 下班立好目标、早上验收 | 放心要有依据 |

三篇 = 完整运行范式：给对上下文 + 立好目标 + 建立可信委托。

---

## 九、写作风格与格式要求（沿用现有文章）

1. **开篇立论**：抛反直觉痛点（"你下班，AI 也下班，但这不是它懒，是对话式接口的结构"），亮论点，一句话钉死。
2. **证据扎实**：官方文档、源码、版本号、真实数字（"三个月 session 从 25 分钟翻倍到 45 分钟"）。注明来源。
3. **反复强对比**：同步 vs 异步、声称 vs 证明、人在环 vs 无人环、自评 vs 确定性检查、即时反馈 vs 延迟验收。
4. **每个原理都落到"坑 → 避法"**——这是本篇区别于泛泛而谈的写作纪律。
5. **加粗关键句**；结构 `##`/`###`/`####`；表格对比；代码块放真实命令/目标模板/源码。

---

## 十、事实核查清单（写作时逐一核对）

- [ ] Claude Code `/goal`：v2.1.139，2026-05-11；`/goal <condition>`、`/goal`（状态）、`/goal clear`（别名 stop/off/reset/none/cancel）；条件 4000 字符；无原生 pause/resume、无内置预算；评估器默认 Haiku；`--resume` 恢复但计数清零；终止 Met/Impossible/不可恢复错误/clear；8 次连续 block 上限；`CLAUDE_CODE_GOAL_CHECKIN_MINUTES`（v2.1.234+）。
- [ ] Codex `/goal`：v0.128.0（04-30）首发；v0.129.0 实验性；v0.133.0（05-21）默认启用 + 专用 DB；命令 `/goal <objective>`、`/goal`、`/goal edit`、`/goal pause`、`/goal resume`、`/goal clear`；条件 4000 字符；`[features] goals = true`；SQLite `thread_goals`（状态 Active/Paused/Blocked/UsageLimited/BudgetLimited/Complete）；工具 create_goal/get_goal/update_goal（update 只能 complete/blocked）。
- [ ] Codex `--goal` exec 标志被官方拒绝（issue #26966，not_planned）。
- [ ] OpenCode：上游 sst/opencode 主分支无 goal；fork PR #32743 提供原生实现（引用时注明）。
- [ ] 范式佐证：Anthropic 2026 Trends（session 翻倍）；两家厂商数月内各自发布；secemp9/goal 移植到 OpenCode。
- [ ] 权限坑：Claude `--dangerously-skip-permissions` headless 卡对话框(#52506)；`-p` 模式 denied 权限 exit 0 不报错（grep `permission_denials`）；`--bg` 卡 waiting(#64271)；`--permission-mode auto/dontAsk/--allowedTools`。Codex `exec` 默认 read-only sandbox（要 `--sandbox workspace-write --ask-for-approval never`）；`--full-auto` 已弃用。OpenCode `run --auto`，非交互默认 deny question。
- [ ] 休眠坑：Claude 自带 caffeinate 会耗尽电池硬关机(#21432)；Codex `features.prevent_idle_sleep`（实验性默认关）；OpenCode 无内置→OS 工具。断网：Codex 无提示(#12595 UI 一直 Thinking)；OpenCode attach 静默挂死(#18984)；Claude 重试 api_retry。
- [ ] 恢复坑：Claude `--continue/--resume/--respawn`（恢复超 1h+100k 会弹摘要对话框）；Codex `codex resume`（异常断开卡 Working 需修 JSONL #12382，别用 `--ephemeral`）；OpenCode `--continue/--session`（崩溃可能损坏 #12885）。
- [ ] 移动端：Codex = ChatGPT App Remote tab（2026-05-14 preview）+ mac Locked use（Computer Use 锁屏，仅 Mac/GUI）；Claude = Claude App Code tab（Remote Control + 云会话 claude.ai/code + 推送）/config "Push when Claude decides"；OpenCode 无官方 App（自托管 `opencode web` + 社区 Android）。
- [ ] 续回合 token：Claude 官方 docs "sends your full conversation with every request"；token 数二次方增长，缓存读 0.1x 让成本近似线性；缓存 TTL 5 分钟→过夜回合间隔>5min=缓存失效=全价重处理。三工具默认自动压缩（Codex 默认=上下文 90%）。

---

## 十一、研究来源（写作时参考锚点）

**官方文档**
- Claude Code goal docs：https://code.claude.com/docs/en/goal
- Claude Code commands：https://code.claude.com/docs/en/commands
- Claude Code hooks（Stop 机制）：https://code.claude.com/docs/en/hooks
- Claude Code What's New W20：https://code.claude.com/docs/en/whats-new/2026-w20
- Codex cookbook：https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex
- Codex follow-a-goal：https://developers.openai.com/codex/use-cases/follow-goals
- Codex slash-commands：https://developers.openai.com/codex/reference/slash-commands
- Codex long-running-work：https://developers.openai.com/codex/long-running-work

**源码**
- Claude Code：`anthropics/claude-code` CHANGELOG（v2.1.139 条目）；tag v2.1.139
- Codex：`openai/codex`（SHA 9bf6737）——`goal_display.rs`、`ext/goal/src/spec.rs`、`steering.rs`、`state/goals_migrations/0001_thread_goals.sql`、`templates/goals/continuation.md`
- OpenCode：`anomalyco/opencode` PR #32743（SHA 43d29156）——`session/goal-command.ts`、`goal.ts`、`sql.ts`、`tool/goal.ts`、`session/prompt.ts`（pursue 循环）

**深度分析**
- Magutti "From Ralph to /goal"：https://www.magutti.com/blog/from-ralph-to-goal-how-codex-and-claude-code-handle-autonomous-work
- Pinggy：https://pinggy.io/blog/claude_code_loop_codex_goal_long_horizon_tasks/
- Daniel Vaughan：https://codex.danielvaughan.com/2026/05/01/codex-cli-goal-workflows-persistent-long-horizon-task-execution/
- Jakub Kontra：https://jakubkontra.com/en/blog/goal-vs-loop-vs-stop-hook-claude-code
- augusteo：https://www.augusteo.com/blog/claude-code-codex-goal/

**第三方生态**：secemp9/goal、kingbootoshi/goal-ledger、tolibear/goalbuddy、pyyush/goal、chrischabot/claude-code-goal、balakumardev/claude-code-goal、xihuai18/claude-goal、jthack/claude-goal、bullish0x/goal-cc、KingGyuSuh/codex-goal-in-cc

---

## 十二、篇幅与节奏

- 目标：10000–14000 字（新增环境与运维实战，比上版更长）。
- 比例：原理（对话式接口 + 信任梯度 + 延迟反馈）40% / 三工具分野 8% / 实战（写目标 + 验收）25% / **环境与运维实战（权限/休眠/断网/移动端）20%** / 选工具 + 收尾 7%。
- 每个原理小节都以"坑 → 避法"收尾，确保"理解原理"直接转化为"会避坑"。
- 可选配实验：`experiments/` 实测——同一 refactor 分别跑 Claude Code / Codex goal，对比收敛/停止/预算，作"实测"章。可选，先写主体。
