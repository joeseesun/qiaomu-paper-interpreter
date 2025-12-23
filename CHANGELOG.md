# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2025-12-23

### Fixed
- **[Critical] 配图生成prompt修复**：使用中文描述风格特征，避免AI将英文指令误读为要画的文字
  - 修复：`shared-lib/image_api.py`
  - 问题：英文"The New Yorker"、"#E34334"等被画成文字内容
  - 解决：改用"钢笔墨水速写"、"朱红色点缀"等中文描述

### Added
- **16:9横幅比例支持**：更适合文章配图的宽屏比例
- **底部中文标题**：《纽约客》经典元素，一句话点题
- **visual_description编写指南**：详细的配图设计规范和检查清单
- **配图改进对比文档**：展示优化前后的具体差异

### Changed
- `generate_newyorker_style()` 增加 `caption` 参数支持底部标题
- 默认aspect_ratio从4:3改为16:9
- visual_config.json格式更新，增加`caption`和`core_point`字段

### Documentation
- 新增 `visual_description_guide.md` - 配图设计编写指南
- 新增 `README.md` - 项目概述和快速开始
- 新增 `CHANGELOG.md` - 版本变更记录
- 更新 `SKILL.md` - 添加"最近更新"章节

## [1.0.0] - 2025-12-22

### Added
- 初始版本
- 智能PDF管理：自动提取元数据，生成有意义的文件名
- 论文图表自动提取：批量提取所有Figure和Table
- 乔木风格文章生成：对话式语言，术语解释，生活化类比
- 《纽约客》风格配图生成：配置驱动workflow
- 最终化处理：提取H1标题作为文件名

### Technical
- `scripts/extract_pdf_metadata.py` - PDF元数据提取
- `scripts/extract_all_figures.py` - 批量图表提取
- `scripts/generate_illustrations_v2.py` - 配图生成
- `scripts/finalize_markdown.py` - 最终化处理
- `shared-lib/image_api.py` - 统一图片生成API

[Unreleased]: https://github.com/yourusername/qiaomu-paper-interpreter/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/yourusername/qiaomu-paper-interpreter/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/yourusername/qiaomu-paper-interpreter/releases/tag/v1.0.0
