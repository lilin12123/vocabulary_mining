# -*- coding: utf-8 -*-
"""
脚本功能：
1. 读取 phrases.txt 和 words.txt 的所有行（每行代表一个单词或短语）
2. 从 markdown 文件中提取单词/短语，与现有内容去重
3. 将合并后的所有单词/短语重新按行写入对应的 txt 文件中
4. 从 markdown 文件中删除重复的行（已在 txt 文件中存在的）
"""

import re
import sys
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


def extract_items_from_markdown(markdown_file):
    """
    从 markdown 表格中提取第一列（英文单词/短语）。
    支持文件中存在多段表格；会跳过表头和分隔线。
    
    Args:
        markdown_file: markdown 文件路径
        
    Returns:
        list: 提取出的单词/短语列表
    """
    items = []
    
    with open(markdown_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        word_or_phrase = _parse_first_column_from_md_table_row(line)
        if word_or_phrase:
            items.append(word_or_phrase)
    
    return items


def read_markdown_lines(markdown_file):
    """
    读取 markdown 文件的所有行，并标记表格数据行（用于后续删除重复项）。
    支持文件中存在多段表格；会跳过表头和分隔线。
    
    Args:
        markdown_file: markdown 文件路径
        
    Returns:
        list: 行列表；表格数据行以 (word_or_phrase, original_line) 表示，其它行保持 original_line 字符串
    """
    with open(markdown_file, 'r', encoding='utf-8') as f:
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


def read_existing_items(txt_file):
    """
    读取现有 txt 文件中的所有单词/短语（忽略注释行和批次标记）
    
    Args:
        txt_file: txt 文件路径
        
    Returns:
        list: 现有单词/短语的列表（保持顺序）
    """
    existing = []
    
    if not Path(txt_file).exists():
        return existing
    
    with open(txt_file, 'r', encoding='utf-8') as f:
        for line in f:
            item = line.strip()
            # 忽略空行和注释行（包括批次标记）
            if item and not item.startswith('#'):
                existing.append(item)
    
    return existing


def write_all_items(txt_file, all_items):
    """
    将所有单词/短语重新写入 txt 文件中（覆盖模式）
    
    Args:
        txt_file: txt 文件路径
        all_items: 所有单词/短语列表（已去重）
    """
    # 确保目录存在
    Path(txt_file).parent.mkdir(parents=True, exist_ok=True)
    
    # 覆盖模式写入
    with open(txt_file, 'w', encoding='utf-8') as f:
        for item in all_items:
            f.write(f"{item}\n")
    
    print(f"已重新写入 {len(all_items)} 个项目到 {txt_file}")


def remove_duplicates_from_markdown(markdown_file, existing_items_set, item_type="单词"):
    """
    从 markdown 文件中删除重复的行（已在 txt 文件中存在的单词/短语）
    
    Args:
        markdown_file: markdown 文件路径
        existing_items_set: 现有单词/短语的集合
        item_type: 类型描述（用于日志输出）
    """
    data_lines = read_markdown_lines(markdown_file)
    
    # 统计重复的行
    duplicate_count = 0
    new_lines = []
    
    # 处理所有行（含多段表格）
    for line_data in data_lines:
        if isinstance(line_data, tuple):
            # 这是一个数据行
            word_or_phrase, original_line = line_data
            if word_or_phrase in existing_items_set:
                # 这是重复的，跳过
                duplicate_count += 1
            else:
                # 保留这一行
                new_lines.append(original_line)
        else:
            # 这是其他行（空行等），保留
            new_lines.append(line_data)
    
    # 重新写入 markdown 文件
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"从 markdown 文件中删除了 {duplicate_count} 个重复的{item_type}行")


def find_date_directories(base_dir):
    """
    查找所有符合要求的目录（八位数字）
    
    Args:
        base_dir: 基础目录路径
        
    Returns:
        list: 符合条件的目录名列表（按名称排序）
    """
    date_dirs = []
    pattern = re.compile(r'^\d{8}$')  # 八位数字
    
    for item in base_dir.iterdir():
        if item.is_dir() and pattern.match(item.name):
            date_dirs.append(item.name)
    
    return sorted(date_dirs)


def clear_duplicate_files(duplicate_dir):
    """
    删除 duplicate 目录下的所有文件
    
    Args:
        duplicate_dir: duplicate 目录路径
    """
    if not duplicate_dir.exists():
        return
    
    for file in duplicate_dir.iterdir():
        if file.is_file():
            file.unlink()
            print(f"已删除: {file.name}")


def process_directory(dir_name, base_dir, duplicate_dir):
    """
    处理指定目录的单词和短语
    
    Args:
        dir_name: 目录名
        base_dir: 基础目录路径
        duplicate_dir: duplicate 目录路径
    """
    # Markdown 文件路径
    markdown_dir = base_dir / dir_name
    words_md = markdown_dir / "words.md"
    phrases_md = markdown_dir / "phrases.md"
    
    # 检查目录和文件是否存在
    if not markdown_dir.exists():
        print(f"警告：目录 {markdown_dir} 不存在，跳过")
        return
    
    if not words_md.exists():
        print(f"警告：文件 {words_md} 不存在，跳过")
        return
    
    if not phrases_md.exists():
        print(f"警告：文件 {phrases_md} 不存在，跳过")
        return
    
    # TXT 文件路径
    words_txt = duplicate_dir / "words.txt"
    phrases_txt = duplicate_dir / "phrases.txt"
    
    print(f"\n{'=' * 60}")
    print(f"处理目录: {dir_name}")
    print(f"{'=' * 60}")
    
    # 处理单词
    print("\n处理单词...")
    
    # 从 markdown 提取单词
    words_from_md = extract_items_from_markdown(words_md)
    print(f"从 markdown 中提取了 {len(words_from_md)} 个单词")
    
    # 读取现有单词
    existing_words = read_existing_items(words_txt)
    print(f"现有 txt 文件中有 {len(existing_words)} 个单词")
    
    # 合并并去重：现有单词 + markdown 中的新单词
    existing_words_set = set(existing_words)
    new_words = [w for w in words_from_md if w not in existing_words_set]
    print(f"去重后，有 {len(new_words)} 个新单词需要添加")
    
    # 合并所有单词（先保留现有的，再添加新的）
    all_words = existing_words + new_words
    
    if new_words:
        print(f"新单词列表: {new_words[:10]}{'...' if len(new_words) > 10 else ''}")
    
    # 重新写入所有单词
    write_all_items(words_txt, all_words)
    
    # 从 markdown 文件中删除重复的单词行（只删除运行脚本前就存在于 txt 中的）
    remove_duplicates_from_markdown(words_md, existing_words_set, "单词")
    
    # 处理短语
    print("\n处理短语...")
    
    # 从 markdown 提取短语
    phrases_from_md = extract_items_from_markdown(phrases_md)
    print(f"从 markdown 中提取了 {len(phrases_from_md)} 个短语")
    
    # 读取现有短语
    existing_phrases = read_existing_items(phrases_txt)
    print(f"现有 txt 文件中有 {len(existing_phrases)} 个短语")
    
    # 合并并去重：现有短语 + markdown 中的新短语
    existing_phrases_set = set(existing_phrases)
    new_phrases = [p for p in phrases_from_md if p not in existing_phrases_set]
    print(f"去重后，有 {len(new_phrases)} 个新短语需要添加")
    
    # 合并所有短语（先保留现有的，再添加新的）
    all_phrases = existing_phrases + new_phrases
    
    if new_phrases:
        print(f"新短语列表: {new_phrases[:10]}{'...' if len(new_phrases) > 10 else ''}")
    
    # 重新写入所有短语
    write_all_items(phrases_txt, all_phrases)
    
    # 从 markdown 文件中删除重复的短语行（只删除运行脚本前就存在于 txt 中的）
    remove_duplicates_from_markdown(phrases_md, existing_phrases_set, "短语")
    
    print(f"\n目录 {dir_name} 处理完成！")


def main():
    # 文件路径配置
    base_dir = Path(__file__).parent
    duplicate_dir = base_dir / "duplicate"
    
    # 获取目录名（从命令行参数）
    if len(sys.argv) >= 2:
        # 指定了目录名，处理单个目录
        dir_name = sys.argv[1].strip()
        
        if not dir_name:
            print("错误：目录名不能为空")
            sys.exit(1)
        
        process_directory(dir_name, base_dir, duplicate_dir)
        print("\n" + "=" * 60)
        print("处理完成！")
        print("=" * 60)
    else:
        # 没有指定目录名，处理所有符合条件的目录
        print("=" * 60)
        print("批量处理模式：处理所有八位数字目录")
        print("=" * 60)
        
        # 删除 duplicate 目录下的文件
        print("\n清理 duplicate 目录...")
        clear_duplicate_files(duplicate_dir)
        print("清理完成\n")
        
        # 查找所有符合条件的目录
        date_dirs = find_date_directories(base_dir)
        
        if not date_dirs:
            print("未找到符合条件的目录（八位数字）")
            sys.exit(0)
        
        print(f"找到 {len(date_dirs)} 个符合条件的目录: {', '.join(date_dirs)}")
        print()
        
        # 依次处理每个目录
        for dir_name in date_dirs:
            process_directory(dir_name, base_dir, duplicate_dir)
        
        print("\n" + "=" * 60)
        print("所有目录处理完成！")
        print("=" * 60)


if __name__ == "__main__":
    main()

