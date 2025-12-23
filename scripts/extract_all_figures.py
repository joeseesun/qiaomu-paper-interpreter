#!/usr/bin/env python3
"""
自动从PDF中提取所有Figure和Table
不依赖markdown标注，直接扫描整个PDF
"""
import fitz  # PyMuPDF
import re
from pathlib import Path
import sys


def extract_all_figures(pdf_path, output_dir="images", prefix=""):
    """
    自动扫描PDF中的所有Figure和Table，批量截图保存

    Args:
        pdf_path: PDF文件路径
        output_dir: 输出目录
        prefix: 文件名前缀（如"ResNet_2015"）

    Returns:
        提取成功的图表列表
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not pdf_path.exists():
        print(f"❌ PDF文件不存在: {pdf_path}")
        return []

    doc = fitz.open(str(pdf_path))

    print(f"📄 正在扫描PDF: {pdf_path.name}")
    print(f"📄 总页数: {len(doc)}")
    print(f"📁 输出目录: {output_dir}\n")

    extracted = []

    # 扫描每一页
    for page_num, page in enumerate(doc, 1):
        text = page.get_text()

        # 查找Figure和Table标记（支持多种格式）
        # 匹配: "Figure 4:", "Fig. 4.", "Table 7:"等
        patterns = [
            r'(Figure)\s+(\d+)\s*[:\.]',
            r'(Fig\.)\s+(\d+)\s*[:\.]',
            r'(Table)\s+(\d+)\s*[:\.]',
        ]

        found_items = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                item_type = match.group(1).lower()
                item_num = match.group(2)
                position = match.span()[0]

                # 规范化类型
                if item_type.startswith('fig'):
                    item_type = 'figure'

                found_items.append((item_type, item_num, position, match))

        if not found_items:
            continue

        # 去重（同一个图表可能有多个引用）
        seen = {}
        for item_type, item_num, position, match in found_items:
            key = (item_type, item_num)
            if key not in seen or position < seen[key][0]:
                seen[key] = (position, match)

        # 对每个图表截图
        for (item_type, item_num), (position, match) in seen.items():
            print(f"[第{page_num}页] 发现 {item_type.capitalize()} {item_num}...")

            # 查找标题位置
            text_instances = page.search_for(match.group(0))

            if not text_instances:
                print(f"  ⚠️  找不到标题位置，跳过")
                continue

            # 使用第一个匹配位置
            inst = text_instances[0]

            # 计算截图区域
            page_width = page.rect.width
            page_height = page.rect.height

            x0 = page_width * 0.08  # 左边距8%
            x1 = page_width * 0.92  # 右边距8%

            if item_type == 'figure':
                # Figure: 标题通常在图片下方
                # 向上找图片（400-600pt），向下包含标题
                y0 = max(0, inst.y0 - 500)
                y1 = min(page_height, inst.y1 + 30)
            else:  # table
                # Table: 标题在表格上方
                # 向下找表格内容（300-500pt）
                y0 = max(0, inst.y0 - 20)
                y1 = min(page_height, inst.y1 + 400)

            # 截图
            clip_rect = fitz.Rect(x0, y0, x1, y1)
            pix = page.get_pixmap(clip=clip_rect, matrix=fitz.Matrix(2, 2))  # 2x分辨率

            # 生成文件名
            if prefix:
                filename = f"{prefix}_{item_type}{item_num}.png"
            else:
                filename = f"{item_type}{item_num}.png"

            output_path = output_dir / filename

            # 保存
            pix.save(str(output_path))

            print(f"  ✅ 已保存: {filename}")

            extracted.append({
                'type': item_type,
                'number': item_num,
                'page': page_num,
                'filename': filename,
                'path': str(output_path)
            })

    doc.close()

    print(f"\n{'='*60}")
    print(f"✨ 完成！成功提取 {len(extracted)} 个图表")
    print(f"📁 保存位置: {output_dir.absolute()}")

    return extracted


def generate_markdown_references(extracted, output_file="figure_list.md"):
    """
    生成markdown引用列表，方便复制粘贴到文章中
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 提取的图表列表\n\n")
        f.write("复制下面的引用到你的文章中：\n\n")

        for item in extracted:
            item_type = item['type'].capitalize()
            item_num = item['number']
            filename = item['filename']
            page = item['page']

            f.write(f"## {item_type} {item_num} (第{page}页)\n\n")
            f.write(f"```markdown\n")
            f.write(f"![{item_type} {item_num}](images/{filename})\n")
            f.write(f"```\n\n")

    print(f"📝 引用列表已保存: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("用法: python extract_all_figures.py <PDF文件> [输出目录] [前缀]")
        print("\n示例:")
        print("  python extract_all_figures.py paper.pdf")
        print("  python extract_all_figures.py ResNet_2015.pdf images ResNet_2015")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "images"
    prefix = sys.argv[3] if len(sys.argv) > 3 else ""

    extracted = extract_all_figures(pdf_path, output_dir, prefix)

    if extracted:
        # 生成引用列表
        list_file = Path(output_dir) / "figure_list.md"
        generate_markdown_references(extracted, list_file)


if __name__ == '__main__':
    main()
