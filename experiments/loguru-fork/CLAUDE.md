# ACME fork 操作规程（CLAUDE.md）

## 这是什么
ACME 公司的 loguru 私有 fork。行为与上游 loguru 一致，但内部实现有 fork 特有的重构。

## 快速开始
- 测试：`/tmp/opencode/venv/bin/python -m pytest tests/ -q`（基线：1598 passed, 47 skipped）
- 单测文件：`/tmp/opencode/venv/bin/python -m pytest tests/test_datetime.py -q`
- 包导入：`sys.path.insert(0, '.')` 后 `import loguru`

## 代码结构约定
- 时间格式化核心在 `loguru/_datetime.py`——token 通过 `register_time_token(name, specifier, formatter)` 注册（fork 特有，不是上游的扁平 dict）
- fork 特有的构建配置在 `loguru/_internal_config.py`——含 `TIMESTAMP_PRECISION` 精度开关（micro/milli/sec），渲染时惰性读取
- 注意 `_compile_format` 有 `lru_cache`：改精度/加 token 后需要 `_compile_format.cache_clear()` 才能生效

## 新增功能时的步骤
1. 读 `loguru/_datetime.py` 理解现有 token 的注册模式（如 `x` token 如何读取精度配置）
2. 在 `_register_default_tokens()` 注册新 token
3. 检查 `tokens` 正则是否要扩展
4. 写测试（参考 `tests/test_datetime.py` 的既有写法）
5. 跑全量测试确认无回归
