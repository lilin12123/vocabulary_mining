# -*- coding: utf-8 -*-
"""
脚本功能：
1. 读取 phrases.txt 和 words.txt 的所有行（每行代表一个单词或短语）
2. 从 markdown 文件中提取单词/短语，与现有内容去重
3. 将合并后的所有单词/短语重新按行写入对应的 txt 文件中
4. 从 markdown 文件中删除重复的行（已在 txt 文件中存在的）
"""

import sys
from pathlib import Path

# Ensure package import works when running from EnLearning directory
sys.path.append(str(Path(__file__).resolve().parents[1]))

from EnLearning.lib import deduper


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
        
        stats = deduper.process_directory(dir_name, base_dir, duplicate_dir)
        if "error" in stats:
            print(f"警告：{stats['error']}，跳过")
        else:
            print(f"目录 {dir_name} 处理完成！")
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
        deduper.clear_duplicate_files(duplicate_dir)
        print("清理完成\n")
        
        # 查找所有符合条件的目录
        date_dirs = deduper.find_date_directories(base_dir)
        
        if not date_dirs:
            print("未找到符合条件的目录（八位数字）")
            sys.exit(0)
        
        print(f"找到 {len(date_dirs)} 个符合条件的目录: {', '.join(date_dirs)}")
        print()
        
        # 依次处理每个目录
        for dir_name in date_dirs:
            stats = deduper.process_directory(dir_name, base_dir, duplicate_dir)
            if "error" in stats:
                print(f"警告：{stats['error']}，跳过")
            else:
                print(f"目录 {dir_name} 处理完成！")
        
        print("\n" + "=" * 60)
        print("所有目录处理完成！")
        print("=" * 60)


if __name__ == "__main__":
    main()
