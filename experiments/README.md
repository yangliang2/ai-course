# 实战实验：知识库路线 vs 上下文工程路线

《别建知识库了，做上下文工程》一文的配套实验。同一任务、同一模型，仅上下文配置不同，对比两条路线的表现。

## 实验结论（一句话）

知识库路线交付"无法验证的猜测"，上下文工程路线 2 轮迭代完成且全量测试通过——**知识库能给你"最相关的片段"，给不了"验证自己有没有做对的能力"**。

## 实验素材

- **`loguru-fork/`**：loguru（Python 日志库）的私有化改造副本（"ACME fork"），3 处与上游不同：
  1. token 注册机制从扁平 dict 改为注册表 + `register_time_token()`（`loguru/_datetime.py`）；
  2. 新增上游没有的 `loguru/_internal_config.py`（`TIMESTAMP_PRECISION` 精度开关 micro/milli/sec）；
  3. `x` token 用精确整数运算并读取精度配置（含 `_compile_format` 的 lru_cache 缓存坑）。
  - 改造后全量测试 **1598 passed, 47 skipped**（与改造前一致）——改造不是"故意弄坏"。
  - `CLAUDE.md` 是上下文工程路线的操作规程（只写怎么跑测试/代码结构/注意事项，不写实现细节）。

## 任务

在 fork 上实现新功能：新增 `{time:u}` token（输出"当日已过秒数 + 微秒"，微秒位数遵守 `TIMESTAMP_PRECISION`）。
成功标准：功能正确 + 现有测试全过 + 新增回归测试（`tests/test_datetime_u_token.py`，5 个）。

## 两条路线

### 路线 A（知识库/RAG）
1. `python scripts/build_rag_index.py loguru-fork rag_index.pkl` —— README + docs + 源码切片（1091+ 片），TF-IDF 向量化；
2. `python scripts/route_a_search.py rag_index.pkl "<任务描述>"` —— 检索 top-k 片段注入上下文；
3. 模型只能靠检索片段完成任务，无运行验证能力。
- **结果**：检索命中部分线索（如 `register_time_token` 函数开头），但切片截断关键实现；模型**不知道 tokens 正则需要加 `u`**（决定成败的细节），且无法运行验证——最终交付"无法验证的猜测"。

### 路线 B（上下文工程）
- 给模型：`CLAUDE.md`（操作规程）+ 工具（grep/read/pytest）。
- **过程**：grep 定位注册机制 → 读 `_unix_epoch_micros` 完整实现 → 发现正则缺 `u` → 实现 token → 写测试 → **首跑 5 失败** → 迭代修复（闭包作用域 bug + 测试断言精度未显式控制）→ 全量 **1603 passed**（1598 原有 + 5 新增，0 回归）。

## 复现步骤

```bash
# 需要 Python 3.10+，依赖：pytest、freezegun、scikit-learn
python -m venv venv && source venv/bin/activate
pip install pytest freezegun scikit-learn

# 路线 B（上下文工程）
cd loguru-fork
python -m pytest tests/ -q          # 期望 1603 passed, 47 skipped

# 路线 A（知识库）
cd ..
python scripts/build_rag_index.py loguru-fork rag_index.pkl
python scripts/route_a_search.py rag_index.pkl "How to add a new time format token to the {time:...} format"
```

## 对比表

| 维度 | 路线 A（知识库） | 路线 B（上下文工程） |
|---|---|---|
| 完成任务 | ❌ 交付无法验证的猜测 | ✅ 完成 |
| 全量测试 | 无法运行 | 1603 passed（+5，0 回归） |
| 定位关键信息 | 部分命中但切片截断 | 完整读取 |
| 发现"正则缺 u" | 不知道 | ✅ 发现并处理 |
| 迭代修复 | 无此能力 | 2 轮修复 |
| 运行验证 | 结构性缺失 | 核心闭环 |

## 公平性说明

- 两条路线使用同一个仓库、同一个任务、同一个成功标准、同一个模型；
- 路线 A 允许换词重试（模拟真实用户反复检索）；
- 改造 3 处后全量测试仍通过（不是"故意弄坏"）；
- 过程全部记录（检索结果、修复日志见各脚本与文章正文），可复现。

## 相关文件

- `loguru-fork/` —— 实验仓库（含 CLAUDE.md、改造后的 `_datetime.py`、新增测试）
- `scripts/build_rag_index.py` —— 知识库索引构建
- `scripts/route_a_search.py` —— 知识库检索
- `scripts/route_a_attempt.patch` / `route_a_impl.py` / `route_a_patch.py` —— 路线 A 的尝试记录
