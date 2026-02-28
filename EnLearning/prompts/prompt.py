# -*- coding: utf-8 -*-
from pathlib import Path
import logging

_log = logging.getLogger(__name__)


class DPOGenerationPrompts:
    def __init__(self) -> None:
        super().__init__()
        
        self.english_word_extraction = """
我的目的是，通过这篇论文，学习一下在人工智能的研究和商务工作中会用到的英语。
论文: $1
如果输入内容是 URL，请你自行访问并读取正文后再完成任务。
任务：请帮我总结此论文的正文中，出现的$2个单词。不要包括简短的常用词汇。
格式要求：
   - 给出markdown编码格式的表格，包括英文、美式音标、中文含义、近义词、示例这5列。词性相同的单词放在一起。
   - 将生成的单词表格保存为 `EnLearning/YYYYMMDD/words.md`
   - 其中 `YYYYMMDD` 是今天的日期`
"""
        self.english_phrases_extraction = """
我的目的是，通过这篇论文，学习一下在人工智能的研究和商务工作中会用到的英语。
论文: $1
如果输入内容是 URL，请你自行访问并读取正文后再完成任务。
任务：请帮我总结此论文的正文中，出现的$2个短语。尽量给出专业短语，不要包括简短的常用短语和生活化短语。
格式要求：
   - 给出markdown编码格式的表格，包括英文、中文含义、近义词、示例这4列。语义有关联的放在一起。
   - 将生成的短语表格保存为 `EnLearning/YYYYMMDD/phrases.md`
   - 其中 `YYYYMMDD` 是今天的日期`
"""

# 我的目的是，通过这个transcript，学习商务和专业英语。

# 网址：https://lexfridman.com/keyu-jin-transcript

# 任务：请帮我总结此transcript中，出现的70个单词和50个短语。不要包括简短的常用词汇。

# 格式要求：
# - 每个单词或短语，包括英文、美式音标、中文含义、近义词、示例这5列。
# - 给出markdown编码格式的表格。
# - 词性相同的单词放在一起。
