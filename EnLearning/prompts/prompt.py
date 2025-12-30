# -*- coding: utf-8 -*-
from pathlib import Path
import yaml
import logging

_log = logging.getLogger(__name__)


class DPOGenerationPrompts:
    def __init__(self) -> None:
        super().__init__()
        
        self.english_word_extraction = """
我的目的是，通过这篇论文，学习一下在人工智能的研究和商务工作中会用到的英语。
论文: $1
任务：请帮我总结此论文的正文中，出现的$2个单词。不要包括简短的常用词汇。
格式要求：
   - 给出markdown编码格式的表格，包括英文、美式音标、中文含义、示例这4列。词性相同的单词放在一起。
   - 将生成的单词表格保存为 `EnLearning/YYYYMMDD/words.md`
   - 其中 `YYYYMMDD` 是日期，例如 `20251215`
"""
        self.english_phrases_extraction = """
我的目的是，通过这篇论文，学习一下在人工智能的研究和商务工作中会用到的英语。
论文: $1
任务：请帮我总结此论文的正文中，出现的$2个短语。尽量给出专业短语，不要包括简短的常用短语和生活化短语。
格式要求：
   - 给出markdown编码格式的表格，包括英文、美式音标、中文含义、示例这4列。语义有关联的放在一起。
   - 将生成的短语表格保存为 `EnLearning/YYYYMMDD/phrases.md`
   - 其中 `YYYYMMDD` 是日期，例如 `20251215`
"""