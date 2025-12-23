#!/usr/bin/env python3
"""
提取markdown的H1标题作为文件名，并删除文章中的H1标题
"""
import re
import os
import sys


def extract_h1_and_remove(markdown_path):
    """
    读取markdown文件，提取H1标题，删除H1行，返回新内容和标题

    参数:
        markdown_path: markdown文件路径

    返回: (h1_title, new_content)
        h1_title: 提取的H1标题（不含#符号），如果没有H1则返回None
        new_content: 删除H1后的内容
    """
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配H1标题（行首的 # 标题）
    h1_pattern = r'^#\s+(.+)$'
    lines = content.split('\n')

    h1_title = None
    new_lines = []
    h1_found = False

    for line in lines:
        match = re.match(h1_pattern, line)
        if match and not h1_found:
            # 找到第一个H1标题
            h1_title = match.group(1).strip()
            h1_found = True
            # 跳过这一行（删除H1）
            continue
        else:
            new_lines.append(line)

    # 删除开头的空行
    while new_lines and new_lines[0].strip() == '':
        new_lines.pop(0)

    new_content = '\n'.join(new_lines)

    return h1_title, new_content


def save_with_h1_title(markdown_path, output_dir="."):
    """
    使用H1标题作为文件名保存markdown文件

    参数:
        markdown_path: 输入markdown文件路径
        output_dir: 输出目录（默认当前目录）

    返回: (success, output_path, h1_title)
        success: 是否成功
        output_path: 输出文件路径
        h1_title: 提取的H1标题
    """
    h1_title, new_content = extract_h1_and_remove(markdown_path)

    if not h1_title:
        return False, None, "未找到H1标题"

    # 生成新文件名：H1标题.md
    # 清理文件名中的非法字符
    safe_filename = h1_title
    # 移除Windows/Mac非法字符: / \ : * ? " < > |
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        safe_filename = safe_filename.replace(char, '')

    output_filename = f"{safe_filename}.md"
    output_path = os.path.join(output_dir, output_filename)

    # 保存文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True, output_path, h1_title


def main():
    """命令行工具"""
    if len(sys.argv) < 2:
        print("用法: python finalize_markdown.py <输入markdown> [输出目录]")
        print("示例: python finalize_markdown.py papers/T5_2019/T5论文_解读.md .")
        print()
        print("功能:")
        print("  1. 提取markdown中的H1标题")
        print("  2. 删除文章中的H1行")
        print("  3. 用H1标题作为文件名保存到输出目录")
        sys.exit(1)

    markdown_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    if not os.path.exists(markdown_path):
        print(f"错误：文件不存在: {markdown_path}")
        sys.exit(1)

    # 执行处理
    success, output_path, h1_title = save_with_h1_title(markdown_path, output_dir)

    if success:
        print(f"✅ 成功！")
        print(f"   H1标题: {h1_title}")
        print(f"   最终文件: {output_path}")
    else:
        print(f"❌ 失败: {h1_title}")
        sys.exit(1)


if __name__ == "__main__":
    main()
