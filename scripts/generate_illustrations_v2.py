#!/usr/bin/env python3
"""
配置驱动的配图生成脚本

工作流：
1. Claude分析文章内容，生成visual_config.json
2. 脚本读取配置，批量生成《纽约客》风格配图
3. 自动插入到markdown中

优势：
- 分析（Claude）和执行（脚本）清晰分离
- 配置可保存、修改、重用
- 支持单独重新生成某张图
"""
import json
import re
import sys
from pathlib import Path

# 添加共享库路径
shared_lib_path = str(Path.home() / '.claude' / 'skills' / 'shared-lib')
sys.path.insert(0, shared_lib_path)

from image_api import ImageGenerator


def parse_h2_sections(markdown_path):
    """解析markdown中的所有H2标题"""
    with open(markdown_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    sections = []
    current_h2 = None
    current_line_num = 0

    for i, line in enumerate(lines, 1):
        h2_match = re.match(r'^##\s+(.+)$', line.strip())
        if h2_match:
            if current_h2:
                sections.append((current_h2, current_line_num))
            current_h2 = h2_match.group(1)
            current_line_num = i

    if current_h2:
        sections.append((current_h2, current_line_num))

    return sections


def create_visual_config_template(markdown_path, output_path="visual_config.json"):
    """
    创建视觉配置模板，供Claude填写

    输出JSON格式：
    {
        "sections": [
            {
                "h2_title": "深度的悖论",
                "visual_description": "两座积木塔对比，大塔摇摇欲坠，小塔稳固..."
            },
            ...
        ]
    }
    """
    markdown_path = Path(markdown_path)
    sections = parse_h2_sections(str(markdown_path))

    config = {
        "article_title": markdown_path.stem,
        "sections": [
            {
                "h2_title": title,
                "visual_description": "待Claude分析填写..."
            }
            for title, _ in sections
        ]
    }

    output_path = markdown_path.parent / output_path
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"✅ 配置模板已创建: {output_path}")
    print(f"📝 请Claude分析文章并填写每个section的visual_description")
    return str(output_path)


def insert_image_into_markdown(markdown_path, h2_title, image_path):
    """在H2标题后插入图片引用"""
    with open(markdown_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 找到H2标题
    for i, line in enumerate(lines):
        if re.match(rf'^##\s+{re.escape(h2_title)}\s*$', line.strip()):
            # 检查下一行是否已有图片
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('!['):
                print(f"   ⚠️  图片已存在，跳过插入")
                return

            # 插入图片
            image_md = f"\n![{h2_title}]({image_path})\n\n"
            lines.insert(i + 1, image_md)

            # 写回文件
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return

    print(f"   ⚠️  未找到H2标题: {h2_title}")


def generate_from_config(
    markdown_path,
    config_path="visual_config.json",
    output_dir="images/illustrations",
    provider='auto',
    skip_existing=True
):
    """
    根据配置文件生成所有配图

    Args:
        markdown_path: markdown文件路径
        config_path: 配置文件路径（JSON）
        output_dir: 图片输出目录
        provider: API选择 ('jimeng', 'gemini', 'auto')
        skip_existing: 是否跳过已存在的图片
    """
    markdown_path = Path(markdown_path)
    config_path = markdown_path.parent / config_path

    # 1. 读取配置
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        print(f"💡 请先运行: python generate_illustrations_v2.py --create-template {markdown_path}")
        return 0

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    sections = config['sections']
    print(f"\n📋 读取配置: {len(sections)} 个章节")

    # 2. 创建输出目录
    abs_output_dir = markdown_path.parent / output_dir
    abs_output_dir.mkdir(parents=True, exist_ok=True)

    # 3. 初始化图片生成器
    generator = ImageGenerator(provider=provider)

    # 4. 批量生成
    success_count = 0

    for idx, section in enumerate(sections, 1):
        h2_title = section['h2_title']
        visual_desc = section['visual_description']
        caption = section.get('caption', '')  # 获取底部标题

        print(f"\n[{idx}/{len(sections)}] 正在为「{h2_title}」生成配图...")
        if caption:
            print(f"   📝 底部标题: {caption}")

        # 检查是否需要分析
        if visual_desc == "待Claude分析填写..." or not visual_desc.strip():
            print(f"   ⚠️  跳过：未填写visual_description")
            continue

        # 图片路径
        image_filename = f"illustration_{idx}.png"
        image_output_path = abs_output_dir / image_filename
        image_rel_path = f"{output_dir}/{image_filename}"

        # 跳过已存在
        if skip_existing and image_output_path.exists():
            print(f"   ⏭️  图片已存在，跳过")
            insert_image_into_markdown(markdown_path, h2_title, image_rel_path)
            success_count += 1
            continue

        try:
            # 生成图片（16:9横幅 + 底部标题）
            print(f"   🎨 视觉描述: {visual_desc[:60]}...")
            image_url, used_provider = generator.generate_newyorker_style(
                visual_strategy=visual_desc,
                caption=caption,  # 传递底部标题
                aspect_ratio='16:9',  # 16:9横幅，更适合文章配图
                max_retries=3
            )

            # 保存图片
            generator.save_image(image_url, str(image_output_path))
            print(f"   ✅ 图片已保存: {image_filename} (使用 {used_provider})")

            # 插入到markdown
            insert_image_into_markdown(markdown_path, h2_title, image_rel_path)
            print(f"   ✅ 已插入到markdown")

            success_count += 1

        except Exception as e:
            print(f"   ❌ 生成失败: {e}")

    # 5. 总结
    print("\n" + "="*60)
    print(f"✨ 完成！成功生成 {success_count}/{len(sections)} 张配图")
    print(f"\n📁 图片保存在: {output_dir}")
    print(f"📄 Markdown已更新: {markdown_path.name}")

    return success_count


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='配置驱动的纽约客风格配图生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：

  1. 创建配置模板：
     python generate_illustrations_v2.py --create-template article.md

  2. Claude分析文章并填写visual_config.json

  3. 根据配置批量生图：
     python generate_illustrations_v2.py article.md

  4. 重新生成第3张图（修改配置后）：
     python generate_illustrations_v2.py article.md --no-skip
        """
    )

    parser.add_argument('markdown', nargs='?', help='Markdown文件路径')
    parser.add_argument('--create-template', metavar='FILE',
                       help='创建配置模板（无需先分析文章）')
    parser.add_argument('--config', default='visual_config.json',
                       help='配置文件路径（默认: visual_config.json）')
    parser.add_argument('--output-dir', default='images/illustrations',
                       help='图片输出目录（默认: images/illustrations）')
    parser.add_argument('--provider', choices=['jimeng', 'gemini', 'auto'],
                       default='auto', help='图片生成API（默认: auto）')
    parser.add_argument('--no-skip', action='store_true',
                       help='重新生成已存在的图片')

    args = parser.parse_args()

    # 创建模板模式
    if args.create_template:
        create_visual_config_template(args.create_template, args.config)
        return

    # 生成模式
    if not args.markdown:
        parser.print_help()
        return

    generate_from_config(
        markdown_path=args.markdown,
        config_path=args.config,
        output_dir=args.output_dir,
        provider=args.provider,
        skip_existing=not args.no_skip
    )


if __name__ == '__main__':
    main()
