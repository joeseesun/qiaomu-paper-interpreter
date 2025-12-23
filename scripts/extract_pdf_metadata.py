#!/usr/bin/env python3
"""
从PDF中提取元数据（标题、作者、年份）并生成合理的文件名
"""
import re
import json
import os
from pathlib import Path
from datetime import datetime


def extract_title_from_pdf(pdf_path):
    """
    从PDF提取标题（优先从第一页文本，备选从metadata）

    返回: 完整标题字符串
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("需要安装PyMuPDF: pip install pymupdf")
        return None

    doc = fitz.open(pdf_path)

    # 方法1：尝试从PDF metadata读取
    metadata = doc.metadata
    if metadata and metadata.get('title') and len(metadata.get('title', '')) > 5:
        title = metadata['title']
        doc.close()
        return title.strip()

    # 方法2：从第一页提取（通常标题是第一页最大字号的文本）
    if len(doc) > 0:
        first_page = doc[0]
        blocks = first_page.get_text("dict")["blocks"]

        # 找到字号最大的文本块（通常是标题）
        max_size = 0
        title_text = ""

        for block in blocks:
            if block.get("type") == 0:  # 文本块
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        size = span.get("size", 0)
                        text = span.get("text", "").strip()

                        # 标题特征：字号大、位于页面上半部分、不是单个词
                        if size > max_size and len(text) > 10 and line.get("bbox", [0,0,0,0])[1] < 200:
                            max_size = size
                            title_text = text

        if title_text:
            doc.close()
            return title_text

    doc.close()
    return None


def extract_year_from_pdf(pdf_path, url=None):
    """
    提取论文年份

    优先级：
    1. arxiv URL (如 https://arxiv.org/pdf/1910.10683 → 2019)
    2. PDF metadata
    3. 文件创建时间

    返回: 年份字符串 (如 "2019")
    """
    # 方法1：从arxiv URL提取
    if url and 'arxiv.org' in url:
        # arxiv编号格式：YYMM.NNNNN 或 arch-ive/YYMMNNN
        match = re.search(r'/(\d{4})\.', url)
        if match:
            yymm = match.group(1)
            year = int(yymm[:2])
            # 2007年后arxiv用4位年份，之前用2位
            if year > 90:
                return f"19{year}"
            else:
                return f"20{year}"

    # 方法2：从PDF metadata
    try:
        import fitz
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        doc.close()

        if metadata and metadata.get('creationDate'):
            # 格式通常是 "D:20191023..." 或 "D:2019..."
            date_str = metadata['creationDate']
            match = re.search(r'(\d{4})', date_str)
            if match:
                return match.group(1)
    except:
        pass

    # 方法3：文件创建时间
    stat = os.stat(pdf_path)
    year = datetime.fromtimestamp(stat.st_ctime).year
    return str(year)


def simplify_title(title, max_length=30):
    """
    简化标题为短标识

    策略：
    1. 提取首字母缩写（如 BERT, GPT, T5）
    2. 提取关键词（Transfer Learning, Attention）
    3. 翻译为中文关键词

    参数:
        title: 完整标题
        max_length: 最大长度

    返回: 简化后的标识（英文，适合做文件名）
    """
    # 常见缩写模式
    acronyms = re.findall(r'\b[A-Z][A-Z0-9]+\b', title)
    if acronyms:
        # 使用第一个缩写
        return acronyms[0]

    # 提取关键词（大写开头的词）
    keywords = re.findall(r'\b[A-Z][a-z]+\b', title)
    if len(keywords) >= 2:
        # 组合前2-3个关键词
        combined = '_'.join(keywords[:3])
        if len(combined) <= max_length:
            return combined

    # 如果没有合适的关键词，使用前N个单词
    words = title.split()[:3]
    simplified = '_'.join(w for w in words if len(w) > 3)

    # 清理特殊字符
    simplified = re.sub(r'[^\w\-]', '_', simplified)
    simplified = re.sub(r'_+', '_', simplified)

    return simplified[:max_length]


def generate_paper_id(title, year, user_hint=None):
    """
    生成论文标识

    优先级：
    1. 用户提示（如果提供）
    2. 标题简化 + 年份

    参数:
        title: 完整标题
        year: 年份
        user_hint: 用户提供的简短标识（可选）

    返回: paper_id (如 "T5_2019", "BERT_2018")
    """
    if user_hint:
        # 清理用户输入
        clean_hint = re.sub(r'[^\w\-]', '_', user_hint)
        return f"{clean_hint}_{year}"

    # 自动生成
    simplified = simplify_title(title)
    return f"{simplified}_{year}"


def extract_authors_from_pdf(pdf_path):
    """
    提取作者列表

    返回: 作者列表
    """
    try:
        import fitz
        doc = fitz.open(pdf_path)

        # 从metadata提取
        metadata = doc.metadata
        if metadata and metadata.get('author'):
            authors = metadata['author']
            doc.close()
            return [a.strip() for a in authors.split(',')]

        # 从第一页文本提取（标题下方通常是作者）
        # 这个较复杂，暂时跳过
        doc.close()
    except:
        pass

    return []


def create_metadata_json(pdf_path, url=None, user_hint=None):
    """
    创建完整的元数据JSON

    参数:
        pdf_path: PDF文件路径
        url: 原始URL（可选）
        user_hint: 用户提供的简短标识（可选）

    返回: (paper_id, metadata_dict)
    """
    # 提取信息
    title = extract_title_from_pdf(pdf_path)
    year = extract_year_from_pdf(pdf_path, url)
    authors = extract_authors_from_pdf(pdf_path)
    paper_id = generate_paper_id(title or "Unknown", year, user_hint)

    # 构建元数据
    metadata = {
        "paper_id": paper_id,
        "title": title or "Unknown",
        "year": year,
        "authors": authors,
        "source_url": url or "",
        "extracted_at": datetime.now().isoformat(),
        "original_filename": os.path.basename(pdf_path)
    }

    return paper_id, metadata


def organize_paper_directory(pdf_path, output_base="papers", url=None, user_hint=None):
    """
    组织论文目录结构

    参数:
        pdf_path: 原始PDF路径
        output_base: 输出基础目录
        url: 原始URL
        user_hint: 用户标识提示

    返回: (paper_dir, paper_id, metadata)
    """
    # 创建元数据
    paper_id, metadata = create_metadata_json(pdf_path, url, user_hint)

    # 创建目录
    paper_dir = os.path.join(output_base, paper_id)
    os.makedirs(paper_dir, exist_ok=True)
    os.makedirs(os.path.join(paper_dir, "images"), exist_ok=True)

    # 复制并重命名PDF
    new_pdf_path = os.path.join(paper_dir, f"{paper_id}.pdf")
    if pdf_path != new_pdf_path:
        import shutil
        shutil.copy2(pdf_path, new_pdf_path)

    # 保存元数据
    metadata_path = os.path.join(paper_dir, "metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ 论文目录已创建：{paper_dir}")
    print(f"   标题：{metadata['title'][:60]}...")
    print(f"   年份：{metadata['year']}")
    print(f"   PDF：{paper_id}.pdf")
    print(f"   元数据：metadata.json")

    return paper_dir, paper_id, metadata


def main():
    """命令行工具"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python extract_pdf_metadata.py <PDF文件> [URL] [用户标识]")
        print("示例: python extract_pdf_metadata.py paper.pdf https://arxiv.org/pdf/1910.10683 T5")
        print("      python extract_pdf_metadata.py bert.pdf \"\" BERT")
        sys.exit(1)

    pdf_path = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None
    user_hint = sys.argv[3] if len(sys.argv) > 3 else None

    if not os.path.exists(pdf_path):
        print(f"错误：文件不存在: {pdf_path}")
        sys.exit(1)

    # 组织目录
    paper_dir, paper_id, metadata = organize_paper_directory(
        pdf_path,
        output_base="papers",
        url=url,
        user_hint=user_hint
    )

    print(f"\n📁 目录结构：")
    print(f"papers/")
    print(f"└── {paper_id}/")
    print(f"    ├── {paper_id}.pdf")
    print(f"    ├── metadata.json")
    print(f"    └── images/")


if __name__ == "__main__":
    main()
