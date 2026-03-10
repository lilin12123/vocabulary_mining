# Vocab RPG Web Game

本目录提供背单词 Web Game 的可运行版本（FastAPI + 原生前端）。

## 启动

```bash
cd /Users/lilin/develop/workspace/cursor/vocabulary_mining/EnLearning/web_game
python app.py
```

浏览器访问：

```
http://127.0.0.1:7870
```

## LLM 配置
- 默认读取环境变量 `DASHSCOPE_API_KEY`（或 `OPENAI_API_KEY`）。
- 可选覆盖：
  - `LLM_MODEL`（默认 `qwen-plus`）
  - `LLM_BASE_URL`（默认 DashScope compatible endpoint）

## 缓存
- 预生成内容保存在 `cache/questions.json`。
- 缓存键：`word + model + prompt_hash`。

## 账号与记录
- 最多 100 个本地账号，存储在 `data/users.json`。
- 个人历史记录存储在 `data/records.json`，登录后可查看。
