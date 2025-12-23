#!/usr/bin/env python3
"""
从PDF中提取指定的Figure和Table，并保存为图片
"""
import re
import os
from pathlib import Path

def extract_figure_annotations(markdown_path):
    """
    从markdown文件中提取所有配图标注

    返回: [(页码, 类型, 编号, 描述, 原始标注文本), ...]
    例如: [(3, 'Figure', '1', '展示T5的text-to-text统一框架', '**【配图建议：...】**')]
    """
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'\*\*【配图建议：第(\d+)页，(Figure|Table)\s*([0-9]+|[IVX]+)\s*-\s*([^】]+)】\*\*'
    matches = re.finditer(pattern, content)

    annotations = []
    for match in matches:
        page_num = int(match.group(1))
        fig_type = match.group(2)
        fig_num = match.group(3)
        description = match.group(4).strip()
        original_text = match.group(0)

        annotations.append((page_num, fig_type, fig_num, description, original_text))

    return annotations


def extract_figures_from_pdf_pymupdf(pdf_path, annotations, output_dir="images", prefix=""):
    """
    使用PyMuPDF从PDF中提取指定的图表

    参数:
        pdf_path: PDF文件路径
        annotations: 配图标注列表
        output_dir: 输出目录
        prefix: 图片文件名前缀（如"T5"）

    返回: {原始标注: 图片路径} 的字典
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("需要安装PyMuPDF: pip install pymupdf")
        return {}

    # 创建输出目录
    Path(output_dir).mkdir(exist_ok=True)

    doc = fitz.open(pdf_path)
    screenshot_map = {}

    for page_num, fig_type, fig_num, description, original_text in annotations:
        # 页码从0开始
        page_idx = page_num - 1

        if page_idx >= len(doc):
            print(f"警告：页码 {page_num} 超出范围")
            continue

        page = doc[page_idx]

        # 搜索图表标题
        search_terms = [
            f"{fig_type} {fig_num}",
            f"{fig_type} {fig_num}:",
            f"{fig_type} {fig_num}.",
        ]

        found = False
        for term in search_terms:
            text_instances = page.search_for(term)

            if text_instances:
                # 找到第一个匹配
                inst = text_instances[0]

                # 扩展边界框以包含整个图表
                # Figure的caption在图片下方，Table的caption在表格上方
                x0 = page.rect.width * 0.05  # 左边距5%
                x1 = page.rect.width * 0.95  # 右边距5%

                if fig_type == "Figure":
                    # Figure: caption在图片下方，所以向上找图片
                    # inst.y0是标题顶部，inst.y1是标题底部
                    y0 = max(0, inst.y0 - 500)  # 标题上方500pt（图片区域）
                    y1 = inst.y1 + 20  # 包含标题，下方留20pt
                else:  # Table
                    # Table: 表格数据在caption上方！
                    # 先搜索caption上方是否有"Model"、"Method"等表格列标题关键词
                    # 如果找不到就使用默认范围
                    table_keywords = ["Model", "Method", "Task", "Dataset"]
                    table_top = inst.y0 - 300  # 默认向上300pt

                    for keyword in table_keywords:
                        keyword_instances = page.search_for(keyword)
                        for kw_inst in keyword_instances:
                            # 找caption上方100-500pt范围内的关键词
                            if (inst.y0 - 500) < kw_inst.y0 < inst.y0:
                                table_top = min(table_top, kw_inst.y0 - 20)
                                break

                    y0 = max(0, table_top)  # 表格顶部
                    y1 = inst.y1 + 20  # 包含caption，下方留20pt

                clip_rect = fitz.Rect(x0, y0, x1, y1)

                # 截图
                pix = page.get_pixmap(clip=clip_rect, matrix=fitz.Matrix(2, 2))  # 2x分辨率

                # 保存（带前缀避免冲突）
                if prefix:
                    img_filename = f"{prefix}_{fig_type.lower()}{fig_num}.png"
                else:
                    img_filename = f"{fig_type.lower()}{fig_num}.png"
                img_path = os.path.join(output_dir, img_filename)
                pix.save(img_path)

                screenshot_map[original_text] = img_path
                print(f"✓ 提取 {fig_type} {fig_num} -> {img_path}")
                found = True
                break

        if not found:
            print(f"✗ 未找到 {fig_type} {fig_num} 在第 {page_num} 页")

    doc.close()
    return screenshot_map


def extract_figures_from_pdf_pdfplumber(pdf_path, annotations, output_dir="images", prefix=""):
    """
    使用pdfplumber从PDF中提取图表（备选方案）

    参数:
        pdf_path: PDF文件路径
        annotations: 配图标注列表
        output_dir: 输出目录
        prefix: 图片文件名前缀（如"T5"）
    """
    try:
        import pdfplumber
        from PIL import Image
    except ImportError:
        print("需要安装: pip install pdfplumber pillow")
        return {}

    Path(output_dir).mkdir(exist_ok=True)

    screenshot_map = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, fig_type, fig_num, description, original_text in annotations:
            page_idx = page_num - 1

            if page_idx >= len(pdf.pages):
                continue

            page = pdf.pages[page_idx]

            # 获取页面图片
            img = page.to_image(resolution=150)

            # 搜索文本位置
            words = page.extract_words()
            search_text = f"{fig_type} {fig_num}"

            for word in words:
                if search_text in word['text']:
                    # 找到了，截取区域
                    x0 = page.width * 0.05
                    x1 = page.width * 0.95

                    if fig_type == "Figure":
                        # Figure: caption在图片下方，向上找
                        y0 = max(0, word['top'] - 500)
                        y1 = min(word['bottom'] + 20, page.height)
                    else:  # Table
                        # Table: 表格在caption上方，向上找
                        # 搜索caption上方的表格列标题
                        table_top = word['top'] - 300  # 默认值
                        table_keywords = ["Model", "Method", "Task", "Dataset"]

                        for kw in table_keywords:
                            for w in words:
                                if kw in w['text'] and (word['top'] - 500) < w['top'] < word['top']:
                                    table_top = min(table_top, w['top'] - 20)
                                    break

                        y0 = max(0, table_top)
                        y1 = min(word['bottom'] + 20, page.height)

                    # 裁剪
                    cropped = img.original.crop((x0, y0, x1, y1))

                    # 保存（带前缀避免冲突）
                    if prefix:
                        img_filename = f"{prefix}_{fig_type.lower()}{fig_num}.png"
                    else:
                        img_filename = f"{fig_type.lower()}{fig_num}.png"
                    img_path = os.path.join(output_dir, img_filename)
                    cropped.save(img_path)

                    screenshot_map[original_text] = img_path
                    print(f"✓ 提取 {fig_type} {fig_num} -> {img_path}")
                    break

    return screenshot_map


def replace_annotations_with_images(markdown_path, screenshot_map, output_path=None):
    """
    将markdown中的配图标注替换为实际图片

    参数:
        markdown_path: 原始markdown文件
        screenshot_map: {原始标注: 图片路径} 字典
        output_path: 输出文件路径（如果为None，则覆盖原文件）
    """
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for annotation, img_path in screenshot_map.items():
        # 提取描述
        desc_match = re.search(r'-\s*([^】]+)', annotation)
        description = desc_match.group(1).strip() if desc_match else ""

        # 替换为markdown图片语法
        replacement = f"![{description}]({img_path})\n\n*{description}*"
        content = content.replace(annotation, replacement)

    # 保存
    if output_path is None:
        output_path = markdown_path

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✅ 已更新 {output_path}")
    print(f"   替换了 {len(screenshot_map)} 处配图标注")


def main():
    """主函数：从命令行调用"""
    import sys

    if len(sys.argv) < 3:
        print("用法: python extract_figures.py <PDF文件> <Markdown文件> [输出目录] [图片前缀]")
        print("示例: python extract_figures.py paper.pdf T5论文_解读.md images T5")
        print("      如果不指定前缀，会从markdown文件名自动提取")
        sys.exit(1)

    pdf_path = sys.argv[1]
    markdown_path = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "images"

    # 图片前缀：优先使用命令行参数，其次从文件名提取
    if len(sys.argv) > 4:
        prefix = sys.argv[4]
    else:
        # 从markdown文件名提取前缀
        # 例如："T5论文_解读.md" -> "T5"
        # 或 "BERT_Pretraining_解读.md" -> "BERT_Pretraining"
        md_basename = os.path.basename(markdown_path)
        md_name = os.path.splitext(md_basename)[0]
        # 提取第一个下划线或"论文"、"解读"之前的部分
        for sep in ['_解读', '_论文', '论文', '解读', '_']:
            if sep in md_name:
                prefix = md_name.split(sep)[0]
                break
        else:
            prefix = md_name[:20]  # 如果没有分隔符，取前20个字符

        # 清理前缀中的特殊字符
        prefix = re.sub(r'[^\w\-]', '_', prefix)

    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        print(f"错误：PDF文件不存在: {pdf_path}")
        sys.exit(1)

    if not os.path.exists(markdown_path):
        print(f"错误：Markdown文件不存在: {markdown_path}")
        sys.exit(1)

    # 提取标注
    print("正在解析markdown中的配图标注...")
    annotations = extract_figure_annotations(markdown_path)
    print(f"找到 {len(annotations)} 处配图标注")
    print(f"图片前缀: {prefix}\n")

    if not annotations:
        print("没有找到任何配图标注，退出")
        sys.exit(0)

    # 提取图表
    print("正在从PDF中提取图表...")

    # 优先使用PyMuPDF，失败则使用pdfplumber
    screenshot_map = extract_figures_from_pdf_pymupdf(pdf_path, annotations, output_dir, prefix)

    if not screenshot_map:
        print("\nPyMuPDF提取失败，尝试使用pdfplumber...")
        screenshot_map = extract_figures_from_pdf_pdfplumber(pdf_path, annotations, output_dir, prefix)

    if not screenshot_map:
        print("\n所有提取方法都失败了")
        sys.exit(1)

    # 更新markdown
    print("\n正在更新markdown文件...")
    replace_annotations_with_images(markdown_path, screenshot_map)

    print("\n✨ 完成！")


if __name__ == "__main__":
    main()
