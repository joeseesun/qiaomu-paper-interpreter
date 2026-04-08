# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

#### 1. Table截图只包含标题不包含表格数据

- **[Critical] Table截图只包含标题不包含表格数据**
  - **问题**：`extract_all_figures.py` 对Table的截图区域计算错误
  - **根因**：代码假设Table标题在表格上方，实际PDF中Table标题通常在表格下方
  - **Bug代码**：
    ```python
    # 旧逻辑（错误）
    y0 = max(0, inst.y0 - 20)   # 只往上偏移20pt
    y1 = min(page_height, inst.y1 + 400)  # 往下400pt找表格
    ```
  - **表现**：截图只包含"Table X: ..."标题文字和下方说明，表格主体在上方被漏掉
  - **修复**：
    ```python
    # 新逻辑（正确）
    y0 = max(0, inst.y0 - 400)  # 往上400pt包含表格主体
    y1 = min(page_height, inst.y1 + 100)  # 往下100pt包含说明文字
    ```
  - **验证**：T5论文的Table 1/2/3现在都包含完整表格数据
  - **影响**：`scripts/extract_all_figures.py:102-106`
  - **Linus品味**：注释说"标题在上方"但代码按"标题在下方"写，注释和实现不一致是Bug的温床

#### 2. 重复提取图表导致文件覆盖

- **[Critical] 跨页图表重复提取，后者覆盖前者**
  - **问题**：同一个图表被提取多次，后面的覆盖前面的，导致文件名与内容不匹配
  - **表现**：
    - T5论文提取33次，实际只有22个独立图表
    - `table3.png`实际内容是Table 5（被第22页的Table 5覆盖）
    - 11个图表重复提取：Figure 1/3/4/6, Table 2/3/4/8/11/12/14
  - **根因1 - 无法区分定义和引用**：
    ```python
    # 旧正则（错误）- 匹配所有"Table X:"和"Table X."
    r'(Table)\s+(\d+)\s*[:\.]'
    ```
    - 问题：既匹配定义（"Table 3: Examples..."）也匹配引用（"shown in Table 3."）
    - 结果：同一页多次出现同一个Table编号，全部被提取
  - **根因2 - 去重只在单页内有效**：
    ```python
    # 旧逻辑（错误）- 每页重新初始化seen字典
    for page_num, page in enumerate(doc, 1):
        seen = {}  # 页面级去重，跨页失效
    ```
    - 问题：跨页图表在第一页提取一次，第二页又提取一次
    - 结果：文件被覆盖，`table3.png`变成最后一次保存的内容
  - **修复方案**：
    ```python
    # 1. 只匹配定义（冒号），忽略引用（句号）
    patterns = [
        r'(Figure)\s+(\d+)\s*:',  # 只匹配"Figure X:"
        r'(Table)\s+(\d+)\s*:',   # 只匹配"Table X:"
    ]

    # 2. 全局去重，跨页面维护
    global_seen = {}  # 移到循环外
    for page_num, page in enumerate(doc, 1):
        # 页面内去重
        page_seen = {...}
        # 全局去重检查
        for key in page_seen:
            if key not in global_seen:
                global_seen[key] = page_num
                # 只提取首次出现的
    ```
  - **效果对比**：
    | 指标 | 修复前 | 修复后 |
    |------|--------|--------|
    | 提取次数 | 33 | 22 |
    | 重复次数 | 11 | 0 |
    | Figure 1 | 2次（第3/9页） | 1次（第3页） |
    | Table 3 | 2次（第21/22页，被覆盖） | 1次（第21页，正确） |
    | table3.png内容 | Table 5（错误） | Table 3（正确） |
  - **影响文件**：`scripts/extract_all_figures.py:39-83`
  - **Linus品味**：
    - 去重是消除特殊情况的经典案例
    - 全局状态（global_seen）比局部状态（seen per page）更简单
    - 冒号vs句号的区分让模式匹配更精确，减少if/else分支

---

## [2.0.0] - 2026-01-02

### Changed - 架构升级
- **[Breaking] PDF处理引擎替换**：从 pdfplumber 迁移到 Markitdown
  - 原因：pdfplumber 是低级字节流解析，输出混乱（空格丢失、公式错乱、表格无法识别）
  - 新方案：Markitdown 理解文档结构，输出标准Markdown（格式完整、表格清晰、公式保留）
  - 文件格式：`extracted_text.txt` → `extracted_text.md`
  - 架构哲学：消除"格式后处理"这个特殊情况，直接获得结构化数据
  - 性能对比：
    - pdfplumber: 51,630字符，空格丢失，需大量后处理
    - Markitdown: 57,968字符，保留完整格式，开箱即用
  - Linus品味原则：不要为每种特殊情况写if/else，选择让特殊情况消失的设计

### Added
- Markitdown 支持：
  - ✅ 完整空格和标点保留
  - ✅ 数学公式格式完整（`x𝑙+1 = x𝑙 + F (x𝑙, W𝑙)`）
  - ✅ 表格自动转换为Markdown表格（管道符分隔）
  - ✅ 图表描述清晰可读
  - ✅ 文档结构语义化（标题、引用、列表）
  - ✅ 可选OCR支持（需要tesseract）

### Fixed
- 文本提取质量问题：
  - 空格丢失：`ZhendaXie` → `Zhenda Xie`
  - 公式格式：`=x𝑙` → `= x𝑙`
  - 表格混乱：原始文本流 → 结构化Markdown表格

### Documentation
- 更新所有文档中的 `extracted_text.txt` → `extracted_text.md`
- 更新 SKILL.md 步骤1：详细说明Markitdown架构优势
- 更新 TROUBLESHOOTING.md：Markitdown内置OCR支持

### Migration Guide
无需用户操作，skill自动使用新方式。旧的 `extracted_text.txt` 仍可读但不再生成。

## [1.2.2] - 2025-12-31

### Fixed
- **[Critical] Obsidian 图片索引冲突**：文件名全局唯一化
  - 问题：不同论文都使用 `illustration_1.png` 等通用名称，Obsidian 索引冲突导致图片预览/链接混乱
  - 解决：文件名包含论文标识符 `{paper_slug}-{idx:02d}.png`
  - 示例：`Deep_Residual_Learning_2015-01.png`, `BERT_2018-01.png`
  - 优势：文件名自描述、全局唯一、不依赖目录隔离
  - 影响：修复 `generate_illustrations_v2.py` Line 143-146

### Changed
- 文件命名策略：从 `illustration_{idx}.png` 改为 `{paper_slug}-{idx:02d}.png`
- 路径生成逻辑：保持相对路径不变，只改文件名

## [1.2.1] - 2025-12-23

### Fixed
- **[Critical] 图片路径错误**：修复finalize后图片路径失效的问题
  - 问题：生成配图时使用相对路径 `images/illustrations/`，文章移动到根目录后路径错误
  - 解决：生成时直接使用完整相对路径 `papers/{paper_id}/images/illustrations/`
  - 影响：防止不同论文的配图互相干扰
- **图片路径验证**：finalize_markdown.py新增图片路径自动验证
  - 在保存最终文章时，自动检查所有图片路径是否存在
  - 显示无效路径的详细列表，便于排查问题

### Documentation
- 新增 `STRUCTURE_OPTIMIZATION_PLAN.md` - 文件组织结构优化方案
  - 诊断当前问题：路径混乱、命名不规范、中间产物混杂
  - 提出优化方案：分离式结构（source/workspace/assets）
  - 制定实施步骤：P0立即修复，P1短期优化，P2长期完善

## [1.2.0] - 2025-12-23

### Performance
- **⚡ 并发生成配图**：3线程并发，性能提升3倍（12张图从6分钟降至2分钟）
  - 新增：`generate_illustrations_parallel.py` 并发版本脚本
  - 线程安全：使用锁保护markdown文件读写
  - 智能调度：ThreadPoolExecutor实现任务并发
  - 可配置：`--workers N` 参数控制并发数

### Fixed
- **[Critical] image_api.py返回值bug**：修复provider模式下返回tuple类型不匹配
  - 问题：`generate_newyorker_style()` 在jimeng/gemini模式返回str，auto模式返回tuple
  - 解决：统一返回 `(image_url, provider_used)` tuple
- **防重复插入配图**：增强检测逻辑避免并发时重复插入
  - 检查相同图片路径
  - 检查是否已有其他illustration图片
  - 线程安全的文件读写

### Improved
- **友好的错误提示**：区分超时、服务不可用等不同错误类型
- **更好的进度显示**：实时显示每张图的生成状态和耗时
- **性能统计**：显示总耗时、平均耗时、加速比等指标

### Documentation
- 更新 `SKILL.md` 配图生成章节，增加性能优化说明
- 记录API性能：即梦约29秒/张，Gemini当前不可用(503)

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
