# Vocabulary Mining

一个用于从论文中提取英语单词和短语，并进行去重管理的工具集。

## 快速开始（脚本一键生成）

### 1. 复制并填写配置文件

```bash
cp /Users/lilin/develop/workspace/cursor/vocabulary_mining/EnLearning/config.env.example /Users/lilin/develop/workspace/cursor/vocabulary_mining/EnLearning/config.env
```

在 `EnLearning/config.env` 中填写：
- `INPUT_FILE` 或 `INPUT_URL`
- `OUTPUT_DIR`
- `DASHSCOPE_API_KEY`
说明：
- `INPUT_URL` 会交给百炼网页检索/阅读工具处理（非本地抓取），通过 Responses API 调用 `web_search` / `web_extractor` 工具。citeturn0search1turn0search8
- 网页工具在 Responses API 中仅支持中国内地地域，请在配置中设置 `REGION=CN`。citeturn0search1
- 若使用 `qwen3-max-2026-01-23`，需要开启 `ENABLE_THINKING=1`；官方示例也推荐启用 `web_search`/`web_extractor`/`code_interpreter` 组合。citeturn0search1turn0search8

### 2. 一键运行

```bash
chmod +x /Users/lilin/develop/workspace/cursor/vocabulary_mining/EnLearning/run_generate.sh
/Users/lilin/develop/workspace/cursor/vocabulary_mining/EnLearning/run_generate.sh
```

脚本会自动创建虚拟环境、安装依赖，生成 `words.md` / `phrases.md`，并自动去重。

---

## 旧版 UI（可选）

### 1. 安装依赖

```bash
cd /Users/lilin/develop/workspace/cursor/vocabulary_mining/EnLearning
pip install -r requirements.txt
```

### 2. 设置百炼 API Key

```bash
export DASHSCOPE_API_KEY="你的Key"
```

### 3. 启动 UI

```bash
python /Users/lilin/develop/workspace/cursor/vocabulary_mining/EnLearning/ui/app.py
```

打开浏览器访问：

```
http://127.0.0.1:7860
```

在页面中粘贴原材料或输入 URL，编辑 prompt，点击生成即可自动写入 `EnLearning/YYYYMMDD/words.md` 和 `phrases.md`，并自动去重合并。

---

## 传统流程（CLI）

### 第一步：使用 Prompt 生成 Markdown 表格

在 `EnLearning/prompts/prompt.py` 中有两个 prompt 模板，用于从论文中提取单词和短语：

- `english_word_extraction`: 提取单词的 prompt
- `english_phrases_extraction`: 提取短语的 prompt

#### 使用示例

EnLearning/prompts/prompt.py 其中有两个prompt用来生成markdown编码格式的表格。
请用其中的两个prompt，分别帮我生成基于论文https://arxiv.org/pdf/2505.20416 的70个单词和50个短语，并用一个readmd.txt来简述论文的内容

### 第二步：运行去重和合并脚本

生成 markdown 文件后，使用脚本进行去重和合并处理。

## 项目结构

```
vocabulary_mining/
├── EnLearning/
│   ├── deduplicate_and_append.py  # 去重和合并脚本
│   ├── prompts/
│   │   └── prompt.py               # Prompt 模板
│   ├── duplicate/
│   │   ├── words.txt              # 单词库（去重后的所有单词）
│   │   └── phrases.txt             # 短语库（去重后的所有短语）
│   └── YYYYMMDD/                  # 按日期组织的 markdown 文件目录
│       ├── words.md                # 从论文提取的单词（markdown 表格格式）
│       └── phrases.md              # 从论文提取的短语（markdown 表格格式）
└── README.md
```

## 功能说明

### 1. Prompt 模板 (`prompts/prompt.py`)

包含两个 prompt 模板，用于从论文中提取单词和短语：

### 2. 去重和合并脚本 (`deduplicate_and_append.py`)

主要功能：

1. **从 markdown 文件提取单词/短语**
   - 读取指定目录下的 `words.md` 和 `phrases.md`
   - 从 markdown 表格中提取第一列（英文单词/短语）

2. **与现有内容去重**
   - 读取 `duplicate/words.txt` 和 `duplicate/phrases.txt`
   - 与 markdown 中的内容进行去重

3. **重新写入 txt 文件**
   - 将合并后的所有单词/短语按行写入对应的 txt 文件（覆盖模式）
   - 保留原有内容的顺序，新内容追加在末尾

4. **从 markdown 文件删除重复行**
   - 删除 markdown 文件中已在 txt 文件中存在的单词/短语行
   - 保留表头和未重复的内容

## 使用方法

### 方式1：处理单个目录

处理指定目录下的 markdown 文件：

```bash
cd /Users/lilin/develop/workspace/cursor/vocabulary_mining/EnLearning
python deduplicate_and_append.py 20251215
```

**工作流程**：
1. 从 `20251215/words.md` 和 `20251215/phrases.md` 提取内容
2. 与 `duplicate/words.txt` 和 `duplicate/phrases.txt` 去重
3. 将合并后的内容写入 txt 文件
4. 从 markdown 文件中删除重复的行

### 方式2：批量处理所有目录

不指定目录名时，脚本会：

1. **清空 duplicate 目录**：删除 `duplicate/words.txt` 和 `duplicate/phrases.txt`
2. **查找所有八位数字目录**：自动找到所有符合 `YYYYMMDD` 格式的目录（如 `20251209`, `20251215`）
3. **按顺序处理**：按目录名排序后依次处理每个目录
4. **累积结果**：每个目录的处理结果会累积到 duplicate 目录下的文件中

```bash
cd /Users/lilin/develop/workspace/cursor/vocabulary_mining/EnLearning
python deduplicate_and_append.py
```

**注意事项**：
- 批量处理模式会先清空 duplicate 目录，请确保重要数据已备份
- 目录会按名称排序处理（如先处理 20251209，再处理 20251215）

## Markdown 文件格式

markdown 文件应为表格格式，例如：

```markdown
### 📘 词汇表（Words）

| 英文 | 美式音标 | 中文含义 | 示例 |
|------|----------|--------|------|
| synthetic | /sɪnˈθɛtɪk/ | 合成的；人工生成的 | GraphGen generates synthetic QA pairs. |
| calibration | /ˌkælɪˈbreɪʃn/ | 校准 | Expected calibration error identifies knowledge blind spots. |
```

脚本会提取第一列（英文）的内容进行去重处理。

## 完整工作流程示例

假设你要处理一篇新论文：

1. **准备论文内容**
   - 获取论文 PDF 或文本内容
   - 例如：https://arxiv.org/pdf/2505.20416

2. **使用 Prompt 生成表格**
   - 使用 `english_word_extraction` prompt，要求生成 ？ 个单词
   - 使用 `english_phrases_extraction` prompt，要求生成 ？个短语
   - 将 LLM 生成的 markdown 表格保存到 `EnLearning/20251215/words.md` 和 `EnLearning/20251215/phrases.md`

3. **运行脚本处理**
   ```bash
   cd /Users/lilin/develop/workspace/cursor/vocabulary_mining/EnLearning
   python deduplicate_and_append.py 20251215
   ```

4. **查看结果**
   - 合并后的单词会写入 `duplicate/words.txt`
   - 合并后的短语会写入 `duplicate/phrases.txt`
   - markdown 文件中的重复行会被删除

## 注意事项

1. **目录名格式**：建议使用 `YYYYMMDD` 格式（如 `20251215`）
2. **文件命名**：markdown 文件必须命名为 `words.md` 和 `phrases.md`
3. **txt 文件格式**：每行一个单词或短语，脚本会自动忽略注释行（以 `#` 开头）
4. **覆盖写入**：txt 文件会被完全覆盖，请确保重要数据已备份
5. **批量处理**：批量处理模式会先清空 duplicate 目录，请谨慎使用

## 依赖

- Python 3.x
- 标准库：`pathlib`, `sys`, `re`

无需安装额外的第三方库。
