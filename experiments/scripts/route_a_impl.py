"""
路线 A（知识库/RAG）：基于检索片段实现 {time:u} token。

从检索片段获得的信息：
1. _internal_config.py 存在，有 TIMESTAMP_PRECISION，可选值 micro/milli/sec（片段 1，664 字符）
2. register_time_token(name, specifier, formatter) 是注册方式（片段 1/3）
3. _register_default_tokens() 用 register_time_token 注册各 token（片段 2，2403 字符）
4. _unix_epoch_micros 处理微秒+精度，但片段 5 只有 694 字符、被截断（看不到完整实现）
5. tokens 正则（片段 4 提到 registry 但没给出正则内容）

未知信息（片段没覆盖的）：
- tokens 正则是否要加 "u"？（片段 2 的 2403 字符被截断在 "Q","%d"... 看不到正则定义）
- _unix_epoch_micros 的完整实现（截断在 epoch 计算处）
- 测试组织
"""
