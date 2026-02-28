# -*- coding: utf-8 -*-
"""
Deduplication utilities for EnLearning.
"""

from __future__ import annotations

import re
from pathlib import Path

_MD_TABLE_SEPARATOR_CELL_RE = re.compile(r"^:?-{3,}:?$")


def _parse_first_column_from_md_table_row(line: str) -> str | None:
    """
    Parse the first column from a markdown table row.

    Returns None when the line is not a data row, e.g.:
    - not a table row (doesn't start with '|')
    - header row (first cell is '英文' / 'English')
    - separator/alignment row (cells are '---', ':---:', etc.)
    """
    s = line.strip()
    if not s.startswith("|"):
        return None

    # Split row cells. Example:
    # | word | phonetics | meaning | synonyms | example |
    cells = [c.strip() for c in s.strip("|").split("|")]
    if len(cells) < 2:
        return None

    first = cells[0].strip()
    if not first:
        return None

    # Skip header rows
    if first in {"英文", "English", "Word", "Phrase"}:
        return None

    # Skip separator/alignment rows
    # e.g. |------|----| or |:----:|:---|
    if all((_MD_TABLE_SEPARATOR_CELL_RE.fullmatch(c) is not None) for c in cells if c):
        return None

    # Sometimes the first cell itself is a separator
    if _MD_TABLE_SEPARATOR_CELL_RE.fullmatch(first) is not None:
        return None

    return first


def extract_items_from_markdown(markdown_file: Path) -> list[str]:
    """
    从 markdown 表格中提取第一列（英文单词/短语）。
    支持文件中存在多段表格；会跳过表头和分隔线。
    """
    items: list[str] = []
    with markdown_file.open("r", encoding="utf-8") as f:
        for line in f:
            word_or_phrase = _parse_first_column_from_md_table_row(line)
            if word_or_phrase:
                items.append(word_or_phrase)
    return items


def read_markdown_lines(markdown_file: Path):
    """
    读取 markdown 文件的所有行，并标记表格数据行（用于后续删除重复项）。
    支持文件中存在多段表格；会跳过表头和分隔线。

    Returns:
        list: 行列表；表格数据行以 (word_or_phrase, original_line) 表示，其它行保持 original_line 字符串
    """
    with markdown_file.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    data_lines = []
    for line in lines:
        original_line = line
        word_or_phrase = _parse_first_column_from_md_table_row(original_line)
        if word_or_phrase:
            data_lines.append((word_or_phrase, original_line))
        else:
            data_lines.append(original_line)
    return data_lines


def read_existing_items(txt_file: Path) -> list[str]:
    """
    读取现有 txt 文件中的所有单词/短语（忽略注释行和批次标记）
    """
    existing: list[str] = []
    if not txt_file.exists():
        return existing

    with txt_file.open("r", encoding="utf-8") as f:
        for line in f:
            item = line.strip()
            # 忽略空行和注释行（包括批次标记）
            if item and not item.startswith("#"):
                existing.append(item)
    return existing


def write_all_items(txt_file: Path, all_items: list[str]) -> None:
    """
    将所有单词/短语重新写入 txt 文件中（覆盖模式）
    """
    txt_file.parent.mkdir(parents=True, exist_ok=True)
    with txt_file.open("w", encoding="utf-8") as f:
        for item in all_items:
            f.write(f"{item}\n")


def remove_duplicates_from_markdown(
    markdown_file: Path, existing_items_set: set[str]
) -> int:
    """
    从 markdown 文件中删除重复的行（已在 txt 文件中存在的单词/短语）
    Returns:
        int: 删除的重复行数
    """
    data_lines = read_markdown_lines(markdown_file)
    duplicate_count = 0
    new_lines = []

    for line_data in data_lines:
        if isinstance(line_data, tuple):
            word_or_phrase, original_line = line_data
            if word_or_phrase in existing_items_set:
                duplicate_count += 1
            else:
                new_lines.append(original_line)
        else:
            new_lines.append(line_data)

    with markdown_file.open("w", encoding="utf-8") as f:
        f.writelines(new_lines)

    return duplicate_count


def find_date_directories(base_dir: Path) -> list[str]:
    """
    查找所有符合要求的目录（八位数字）
    """
    date_dirs: list[str] = []
    pattern = re.compile(r"^\d{8}$")
    for item in base_dir.iterdir():
        if item.is_dir() and pattern.match(item.name):
            date_dirs.append(item.name)
    return sorted(date_dirs)


def clear_duplicate_files(duplicate_dir: Path) -> None:
    """
    删除 duplicate 目录下的所有文件
    """
    if not duplicate_dir.exists():
        return
    for file in duplicate_dir.iterdir():
        if file.is_file():
            file.unlink()


def process_directory(dir_name: str, base_dir: Path, duplicate_dir: Path) -> dict:
    """
    处理指定目录的单词和短语。
    Returns:
        dict: 处理统计信息
    """
    markdown_dir = base_dir / dir_name
    words_md = markdown_dir / "words.md"
    phrases_md = markdown_dir / "phrases.md"

    if not markdown_dir.exists():
        return {"error": f"目录 {markdown_dir} 不存在"}
    if not words_md.exists():
        return {"error": f"文件 {words_md} 不存在"}
    if not phrases_md.exists():
        return {"error": f"文件 {phrases_md} 不存在"}

    words_txt = duplicate_dir / "words.txt"
    phrases_txt = duplicate_dir / "phrases.txt"

    words_from_md = extract_items_from_markdown(words_md)
    existing_words = read_existing_items(words_txt)
    existing_words_set = set(existing_words)
    new_words = [w for w in words_from_md if w not in existing_words_set]
    all_words = existing_words + new_words
    write_all_items(words_txt, all_words)
    removed_words = remove_duplicates_from_markdown(words_md, existing_words_set)

    phrases_from_md = extract_items_from_markdown(phrases_md)
    existing_phrases = read_existing_items(phrases_txt)
    existing_phrases_set = set(existing_phrases)
    new_phrases = [p for p in phrases_from_md if p not in existing_phrases_set]
    all_phrases = existing_phrases + new_phrases
    write_all_items(phrases_txt, all_phrases)
    removed_phrases = remove_duplicates_from_markdown(
        phrases_md, existing_phrases_set
    )

    return {
        "words": {
            "extracted": len(words_from_md),
            "existing": len(existing_words),
            "new": len(new_words),
            "removed_from_md": removed_words,
        },
        "phrases": {
            "extracted": len(phrases_from_md),
            "existing": len(existing_phrases),
            "new": len(new_phrases),
            "removed_from_md": removed_phrases,
        },
    }


def process_all(base_dir: Path, duplicate_dir: Path) -> list[dict]:
    """
    批量处理所有符合条件的日期目录。
    """
    clear_duplicate_files(duplicate_dir)
    stats: list[dict] = []
    for dir_name in find_date_directories(base_dir):
        stats.append(process_directory(dir_name, base_dir, duplicate_dir))
    return stats
