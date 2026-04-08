#!/usr/bin/env python3
"""
自动从PDF中提取所有Figure和Table - v2.0 全面优化版

改进点：
1. 通用分隔符模式：支持 : | . — - 等各种学术论文格式
2. 更智能的引用过滤：基于上下文判断是标题还是引用
3. 双向搜索：Figure 标题可能在图片上方或下方
4. 调试模式：--debug 参数输出详细匹配信息
5. 更好的边界检测：处理矢量图和复杂布局
"""
import fitz  # PyMuPDF
import re
from pathlib import Path
import sys
import argparse


# ============ 配置常量 ============

# 通用分隔符模式（覆盖主流学术论文格式）
# 支持: Figure 1: / Figure 1. / Figure 1 | / Figure 1 — / Figure 1 - / Figure 1 Description
SEPARATORS = r'[:：\.\|—\-]'

# 引用动词（用于过滤正文中的引用，如 "Figure 1 shows..."）
REFERENCE_VERBS = {
    'shows', 'show', 'showing', 'shown',
    'illustrates', 'illustrate', 'illustrating', 'illustrated',
    'demonstrates', 'demonstrate', 'demonstrating', 'demonstrated',
    'presents', 'present', 'presenting', 'presented',
    'depicts', 'depict', 'depicting', 'depicted',
    'displays', 'display', 'displaying', 'displayed',
    'summarizes', 'summarize', 'summarizing', 'summarized',
    'compares', 'compare', 'comparing', 'compared',
    'lists', 'list', 'listing', 'listed',
    'reports', 'report', 'reporting', 'reported',
    'provides', 'provide', 'providing', 'provided',
    'contains', 'contain', 'containing', 'contained',
    'includes', 'include', 'including', 'included',
    'describes', 'describe', 'describing', 'described',
    'outlines', 'outline', 'outlining', 'outlined',
}

# 引用介词（用于过滤正文中的引用，如 "as shown in Figure 1"）
REFERENCE_PREPOSITIONS = {'in', 'of', 'from', 'see', 'cf', 'refer', 'to'}


def is_likely_caption(text_before: str, text_after: str, match_text: str) -> bool:
    """
    判断匹配到的 Figure/Table 是标题还是引用

    标题特征：
    - 在行首或段落开头
    - 后面跟着分隔符或描述性名词
    - 不是 "as shown in Figure 1" 这样的句式

    引用特征：
    - 前面有介词（in, of, from, see）
    - 后面跟着动词（shows, illustrates）
    - 在句子中间
    """
    # 检查前文：如果前面紧跟介词，很可能是引用
    before_words = text_before.strip().split()[-3:] if text_before.strip() else []
    for word in before_words:
        if word.lower().rstrip('.,;:') in REFERENCE_PREPOSITIONS:
            return False

    # 检查后文：如果后面紧跟动词，很可能是引用
    after_words = text_after.strip().split()[:2] if text_after.strip() else []
    for word in after_words:
        if word.lower().rstrip('.,;:') in REFERENCE_VERBS:
            return False

    # 检查是否在行首（标题的典型位置）
    # 前文为空，或者前文以换行结束
    if not text_before.strip() or text_before.rstrip().endswith('\n'):
        return True

    # 检查后面是否有分隔符（标题的典型格式）
    if text_after and re.match(r'\s*' + SEPARATORS, text_after):
        return True

    # 检查后面是否跟着大写字母开头的描述（如 "Figure 1 The Architecture"）
    if text_after and re.match(r'\s+[A-Z][a-z]', text_after):
        # 但要排除动词
        first_word = text_after.strip().split()[0] if text_after.strip() else ''
        if first_word.lower() not in REFERENCE_VERBS:
            return True

    return False


def find_figure_captions(page, page_num: int, debug: bool = False) -> list:
    """
    在页面中查找所有 Figure/Table 标题

    返回: [(item_type, item_num, title_rect, full_title_text), ...]
    """
    text = page.get_text()
    found_items = []

    # 统一的匹配模式：Figure/Fig./Table + 数字
    # 捕获组1: 类型（Figure/Fig./Table）
    # 捕获组2: 编号
    pattern = r'(Figure|Fig\.?|TABLE|Table)\s+(\d+)'

    for match in re.finditer(pattern, text, re.IGNORECASE):
        item_type = match.group(1).lower()
        item_num = match.group(2)
        position = match.start()

        # 标准化类型名
        if item_type.startswith('fig'):
            item_type = 'figure'
        elif item_type == 'table':
            item_type = 'table'

        # 获取上下文
        context_before = text[max(0, position-50):position]
        context_after = text[match.end():match.end()+100]

        # 判断是标题还是引用
        if not is_likely_caption(context_before, context_after, match.group(0)):
            if debug:
                print(f"    [跳过引用] {match.group(0)} (上文: ...{context_before[-20:]})")
            continue

        # 提取完整标题（包括分隔符和描述）
        # 尝试匹配到行尾或句号
        title_pattern = re.escape(match.group(0)) + r'[^\.]*\.?'
        title_match = re.search(title_pattern, text[position:position+300])
        if title_match:
            full_title = title_match.group(0).strip()
        else:
            full_title = match.group(0)

        # 在页面上定位标题
        search_text = match.group(0)
        text_instances = page.search_for(search_text)

        if not text_instances:
            if debug:
                print(f"    [找不到位置] {search_text}")
            continue

        # 使用第一个匹配（通常是页面上最靠上的）
        title_rect = text_instances[0]

        if debug:
            print(f"    [找到标题] {item_type.capitalize()} {item_num} @ y={title_rect.y0:.0f}")

        found_items.append({
            'type': item_type,
            'number': item_num,
            'rect': title_rect,
            'full_title': full_title,
            'page_num': page_num
        })

    return found_items


def analyze_figure_boundaries(page, title_rect, item_type: str, debug: bool = False):
    """
    分析Figure/Table的精确边界

    改进策略：
    1. 双向搜索：图片可能在标题上方或下方
    2. 更大的搜索范围
    3. 更好的矢量图检测
    """
    page_width = page.rect.width
    page_height = page.rect.height

    # 获取页面所有元素
    text_blocks = page.get_text("dict")["blocks"]
    images = page.get_images(full=True)
    drawings = page.get_drawings()

    # 初始边界从标题开始
    y0, y1 = title_rect.y0, title_rect.y1
    x0, x1 = title_rect.x0, title_rect.x1

    if item_type == 'figure':
        # === 搜索图片内容（上方和下方都找）===
        image_found = False
        best_image_rect = None

        # 1. 尝试找位图图片
        for img_info in images:
            try:
                img_rect = page.get_image_bbox(img_info)

                # 图片在标题上方（常见情况）
                if img_rect.y1 < title_rect.y0 and (title_rect.y0 - img_rect.y1) < 100:
                    if not best_image_rect or img_rect.y0 < best_image_rect.y0:
                        best_image_rect = img_rect
                        image_found = True

                # 图片在标题下方（某些论文格式）
                elif img_rect.y0 > title_rect.y1 and (img_rect.y0 - title_rect.y1) < 50:
                    if not best_image_rect or img_rect.y1 > best_image_rect.y1:
                        best_image_rect = img_rect
                        image_found = True
            except:
                continue

        if best_image_rect:
            y0 = min(y0, best_image_rect.y0)
            y1 = max(y1, best_image_rect.y1)
            x0 = min(x0, best_image_rect.x0)
            x1 = max(x1, best_image_rect.x1)

        # 2. 如果没找到位图，尝试找矢量绘图
        if not image_found and drawings:
            # 收集标题上方300pt范围内的所有绘图（扩大搜索范围）
            drawing_rects = []
            for drawing in drawings:
                draw_rect = drawing.get('rect')
                if draw_rect:
                    # 上方
                    if draw_rect.y1 < title_rect.y0 and (title_rect.y0 - draw_rect.y0) < 400:
                        drawing_rects.append(draw_rect)
                    # 下方
                    elif draw_rect.y0 > title_rect.y1 and (draw_rect.y0 - title_rect.y1) < 100:
                        drawing_rects.append(draw_rect)

            if drawing_rects:
                y0 = min(y0, min(r.y0 for r in drawing_rects))
                y1 = max(y1, max(r.y1 for r in drawing_rects))
                x0 = min(x0, min(r.x0 for r in drawing_rects))
                x1 = max(x1, max(r.x1 for r in drawing_rects))
                image_found = True

        # 3. 如果还没找到，扩大搜索范围到标题上方400pt
        if not image_found:
            # 可能是纯文本构成的图表或者复杂布局
            for block in text_blocks:
                if block.get('type') == 0:  # 文本块
                    block_rect = fitz.Rect(block['bbox'])
                    # 在标题上方，但不太远
                    if block_rect.y1 < title_rect.y0 and (title_rect.y0 - block_rect.y0) < 400:
                        y0 = min(y0, block_rect.y0)

        # === 向下找说明文字 ===
        caption_end = title_rect.y1
        for block in text_blocks:
            if block.get('type') == 0:
                block_rect = fitz.Rect(block['bbox'])
                # 紧接着标题下方的文本
                if block_rect.y0 >= title_rect.y1 and (block_rect.y0 - title_rect.y1) < 50:
                    # 说明文字通常较短
                    text_content = ""
                    for line in block.get('lines', []):
                        for span in line.get('spans', []):
                            text_content += span.get('text', '')

                    if len(text_content.strip()) < 500:  # 说明文字不会太长
                        caption_end = max(caption_end, block_rect.y1)
                        x0 = min(x0, block_rect.x0)
                        x1 = max(x1, block_rect.x1)

        y1 = max(y1, caption_end)

    else:  # table
        # Table 的标题通常在表格上方
        # 向下找表格主体
        table_found = False

        # 1. 查找标题下方的表格线
        table_drawings = []
        for drawing in drawings:
            draw_rect = drawing.get('rect')
            if draw_rect and draw_rect.y0 >= title_rect.y1:
                if (draw_rect.y0 - title_rect.y1) < 500:
                    width = draw_rect.x1 - draw_rect.x0
                    height = draw_rect.y1 - draw_rect.y0
                    # 表格线特征：水平细线
                    if height < 5 or width > 100:
                        table_drawings.append(draw_rect)

        if table_drawings:
            y1 = max(r.y1 for r in table_drawings)
            x0 = min(x0, min(r.x0 for r in table_drawings))
            x1 = max(x1, max(r.x1 for r in table_drawings))
            table_found = True

        # 2. 如果没找到绘图，查找密集的文本块
        if not table_found:
            table_blocks = []
            last_y = title_rect.y1

            for block in text_blocks:
                if block.get('type') == 0:
                    block_rect = fitz.Rect(block['bbox'])
                    if block_rect.y0 >= title_rect.y1 and (block_rect.y0 - title_rect.y1) < 500:
                        gap = block_rect.y0 - last_y
                        if len(table_blocks) > 0 and gap > 50:
                            break
                        table_blocks.append(block_rect)
                        last_y = block_rect.y1

            if len(table_blocks) >= 2:
                y1 = max(r.y1 for r in table_blocks)
                x0 = min(x0, min(r.x0 for r in table_blocks))
                x1 = max(x1, max(r.x1 for r in table_blocks))

    # 添加边距
    margin = 15
    x0 = max(0, x0 - margin)
    x1 = min(page_width, x1 + margin)
    y0 = max(0, y0 - margin)
    y1 = min(page_height, y1 + margin)

    # 确保最小尺寸（避免只截取标题）
    min_height = 100
    if y1 - y0 < min_height:
        # 如果太小，向上扩展
        y0 = max(0, title_rect.y0 - 300)

    return fitz.Rect(x0, y0, x1, y1)


def scan_and_extract_figures(pdf_path, output_dir="images", prefix="", debug=False):
    """
    两阶段提取：
    1. 扫描阶段：找到所有Figure/Table标题
    2. 提取阶段：分析边界并截取
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
    print(f"📁 输出目录: {output_dir}")
    if debug:
        print(f"🔧 调试模式: 开启")
    print()

    # ============ 阶段1: 扫描并标记 ============
    print("🔍 阶段1: 扫描所有图表标题...")
    all_items = []
    global_seen = {}

    for page_num, page in enumerate(doc, 1):
        if debug:
            print(f"\n  === 第 {page_num} 页 ===")

        items = find_figure_captions(page, page_num, debug=debug)

        # 全局去重（同一个 Figure/Table 只处理一次）
        for item in items:
            key = (item['type'], item['number'])
            if key not in global_seen:
                global_seen[key] = page_num
                item['page'] = page
                all_items.append(item)
                if not debug:
                    print(f"  [第{page_num}页] {item['type'].capitalize()} {item['number']}")

    print(f"\n✅ 阶段1完成: 找到 {len(all_items)} 个图表\n")

    if not all_items:
        print("⚠️  未找到任何图表。可能的原因：")
        print("   1. PDF中没有标准格式的Figure/Table标题")
        print("   2. 使用 --debug 参数查看详细匹配信息")
        doc.close()
        return []

    # ============ 阶段2: 分析边界并截取 ============
    print("✂️  阶段2: 分析边界并截取...")
    extracted = []

    for item in all_items:
        item_type = item['type']
        item_num = item['number']
        page_num = item['page_num']
        page = item['page']
        title_rect = item['rect']

        print(f"  [第{page_num}页] {item_type.capitalize()} {item_num} - 分析边界...", end='')

        # 分析精确边界
        precise_rect = analyze_figure_boundaries(page, title_rect, item_type, debug=debug)

        width = precise_rect.x1 - precise_rect.x0
        height = precise_rect.y1 - precise_rect.y0
        print(f" ({int(width)}x{int(height)}) ", end='')

        # 截取图片
        pix = page.get_pixmap(clip=precise_rect, matrix=fitz.Matrix(2, 2))  # 2x分辨率

        # 生成文件名
        if prefix:
            filename = f"{prefix}_{item_type}{item_num}.png"
        else:
            filename = f"{item_type}{item_num}.png"

        output_path = output_dir / filename
        pix.save(str(output_path))

        print(f"✅ 已保存")

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
    """生成markdown引用列表"""
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
    parser = argparse.ArgumentParser(
        description='从PDF中自动提取Figure和Table',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python extract_all_figures.py paper.pdf
  python extract_all_figures.py paper.pdf images paper_prefix
  python extract_all_figures.py paper.pdf --debug  # 调试模式
        """
    )
    parser.add_argument('pdf', help='PDF文件路径')
    parser.add_argument('output_dir', nargs='?', default='images', help='输出目录 (默认: images)')
    parser.add_argument('prefix', nargs='?', default='', help='文件名前缀')
    parser.add_argument('--debug', '-d', action='store_true', help='开启调试模式，输出详细匹配信息')

    args = parser.parse_args()

    extracted = scan_and_extract_figures(
        args.pdf,
        args.output_dir,
        args.prefix,
        debug=args.debug
    )

    if extracted:
        list_file = Path(args.output_dir) / "figure_list.md"
        generate_markdown_references(extracted, list_file)


if __name__ == '__main__':
    main()
