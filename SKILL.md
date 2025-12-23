---
name: qiaomu-paper-interpreter
description: Academic paper interpretation and rewriting in Qiaomu's conversational Chinese style. Use when user provides a PDF paper URL and requests paper interpretation, analysis, or rewriting. Triggers include "解读这篇论文", "帮我理解这篇paper", "用乔木风格写这篇论文", or when user provides a PDF URL asking for paper summary or explanation. This skill runs automatically from start to finish without asking user for confirmation.
---

# 乔木论文解读

## 最近更新

### 2025-12-23: 配图生成prompt重大修复

**问题**：使用英文prompt导致AI将指令误读为要画的文字
- ❌ "The New Yorker" → 被画成标题文字
- ❌ "#E34334" → 被画成颜色代码
- ❌ "Query-Key" → 从描述中提取并画出

**修复**：改回中文prompt描述风格特征
```python
# ✅ 修复后的prompt（中文描述，AI不会误读）
prompt = f"""钢笔墨水速写，单线条手绘漫画风格，
黑白线条为主，朱红色点缀，
简洁留白背景，松弛的线条艺术，带幽默感，

{visual_strategy}

风格要求：
简约优雅的线条，手绘松弛质感，
横向宽幅构图16:9，大量留白和呼吸感，
墨水渲染增加层次，精致细节，底部用优雅的衬线字体写上：{caption}"""
```

**改进**：
- ✅ 支持16:9横幅比例（更适合文章配图）
- ✅ 支持底部中文标题（《纽约客》经典元素）
- ✅ 准确提炼文章核心要点设计视觉隐喻
- ✅ 创建visual_description编写指南

**相关文件**：
- `shared-lib/image_api.py` - 修复后的图片生成API
- `visual_description_guide.md` - 配图设计编写指南

---

## 概述

这个skill将学术论文自动转化为乔木风格的通俗易懂解读文章。**整个流程全自动执行**，从PDF读取到文件保存一气呵成。

核心特点：
- **全自动workflow**：无需用户中途确认，直接生成最终文档
- **对话式语言**：像和朋友聊天一样讲解复杂概念
- **术语解释**：每个专业术语都有引用块说明
- **生活化类比**：用日常例子帮助理解
- **深度思考**：不满足于表面，挖掘背后的洞察
- **配图标注**：标注论文中重要图表的位置

## 自动化工作流程

**关键原则**：此workflow必须自动执行完所有步骤，不要在中途询问用户意见或等待确认。直接生成完整的最终版本。

**推荐执行顺序**：

**方式A（推荐）**：先提取图表，再写作
```
步骤0 → 步骤1 → 步骤5（提取所有图表）→ 步骤2（参考figure_list.md写作）→ 步骤3-7
```
优势：写作时能看到所有可用图表，可以更充分地引用数据图表

**方式B**：边写边标注
```
步骤0 → 步骤1 → 步骤2（用占位符标注）→ 步骤5（提取并替换）→ 步骤3-7
```
优势：写作流畅不被打断，后续自动提取替换

### 步骤0：智能PDF管理与目录创建

**核心改进**：从PDF自动提取元数据，生成有意义的文件名和目录结构！

使用 `scripts/extract_pdf_metadata.py` 自动处理：

```python
from scripts.extract_pdf_metadata import organize_paper_directory

# 1. 下载PDF（临时文件）
temp_pdf = download_pdf(url)  # 例如：/tmp/1910.10683.pdf

# 2. 提取元数据并组织目录（自动提取标题、年份、作者）
paper_dir, paper_id, metadata = organize_paper_directory(
    pdf_path=temp_pdf,
    output_base="papers",
    url=url,
    user_hint=None  # 可选：用户提供的简短标识（如"T5"）
)

# 自动执行：
# - 提取完整标题："Exploring the Limits of Transfer Learning..."
# - 提取年份：2019 (从arxiv URL或PDF metadata)
# - 生成paper_id："T5_2019" 或 "Transfer_Learning_2019"
# - 创建目录：papers/T5_2019/
# - 重命名PDF：papers/T5_2019/T5_2019.pdf
# - 保存元数据：papers/T5_2019/metadata.json

# 最终目录结构：
# papers/
#   └── T5_2019/                      ← 论文标识_年份
#       ├── T5_2019.pdf               ← 有意义的PDF名
#       ├── metadata.json             ← 完整元数据
#       ├── extracted_text.txt        ← 后续生成
#       ├── T5论文_解读.md             ← 后续生成
#       └── images/
#           ├── T5_2019_figure1.png   ← 图片前缀匹配
#           └── T5_2019_table15.png
```

**元数据示例** (metadata.json)：
```json
{
  "paper_id": "T5_2019",
  "title": "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer",
  "year": "2019",
  "authors": ["Colin Raffel", "Noam Shazeer", ...],
  "source_url": "https://arxiv.org/pdf/1910.10683",
  "extracted_at": "2024-01-15T10:30:00",
  "original_filename": "1910.10683.pdf"
}
```

**命名规则**：
- `paper_id`：自动从标题提取首字母缩写或关键词（如 "T5", "BERT", "GPT"）+ 年份
- PDF文件名：`{paper_id}.pdf`
- 图片前缀：`{paper_id}_`
- 解读文件名：`{中文标题}_解读.md`（如 "T5论文_解读.md"）

### 步骤1：读取PDF内容

PDF已在步骤0中下载并重命名为 `{paper_dir}/{paper_id}.pdf`。

使用pdfplumber提取完整文本，保存到 `{paper_dir}/extracted_text.txt`：

```python
import pdfplumber

pdf_path = f"{paper_dir}/{paper_id}.pdf"
with pdfplumber.open(pdf_path) as pdf:
    full_text = ""
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            full_text += f"\n--- Page {i+1} ---\n{text}"

# 保存提取的文本
with open(f"{paper_dir}/extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(full_text)
```

**重点关注**：
- 标题、作者、摘要
- 所有章节内容
- 图表标题（Figure X, Table X）
- 实验结果数据
- 结论部分

### 步骤2：一次性生成完整解读

**不要分初稿和完善版**，直接生成最终完整版本。必须包含：

#### 内容结构

1. **引入部分**（用故事/场景引入，不直接讲技术）
2. **核心概念**（每个术语用 > 引用块解释 + 生活化类比）
3. **技术细节**（分层：是什么→为什么→怎么做）
4. **实验数据**（表格展示，加粗重点数字）
5. **深度洞察**（方法论启发、历史意义）
6. **结尾升华**（延伸到认知层面）

#### 术语解释格式

```markdown
> **Transformer**：一种神经网络架构，核心是"自注意力机制"。可以想象成你在读一句话时，会自动关注句子中最重要的几个词，而不是平均分配注意力。
```

#### 论文图表引用

**核心原则**：步骤5会自动提取所有论文图表，为你提供丰富的素材库。**根据内容需要自然引用，不刻意堆砌**。

**图表信息来源**：
步骤5会生成 `images/figure_list.md`，列出所有可用图表：
- 哪些Figure和Table已提取
- 每个图表在论文第几页
- 如何引用（markdown格式）

**写作时如何决定是否引用**：

✅ **建议引用的场景**：
- 解释核心架构时，有对应的结构图
- 讨论实验结果时，有对比曲线或数据表
- 分析模型效果时，有可视化图（注意力、特征分布等）
- 说明方法细节时，有示意图能辅助理解

❌ **不必引用的场景**：
- 纯概念讲解，图表帮助不大
- 论文中的公式推导图（公众号读者看不懂）
- 重复的实验对比（只选最有代表性的）

**引用格式**：
```markdown
![描述性标题](papers/{paper_id}/images/{paper_id}_figure1.png)

*配图说明*
```

**如果步骤5还未执行**，可以先用占位符：
```markdown
**【配图：Figure 1 - 架构示意图】**
```

#### 风格要求（严格遵守）

详见 references/style-guide.md，核心要点：
- 短段落，多留白
- 用"就像""比如""试想一下"引导
- **绝对不用破折号**
- **使用中文标点符号**（，。：！？）
- 重要观点**加粗**
- 不用"首先""其次""值得注意的是"

### 步骤3：内部质量检查（不输出给用户）

生成后内部检查（不要向用户报告这些检查）：

```
- 核心贡献是否都覆盖？→ 如否，补充
- 实验结果是否充分？→ 如否，补充数据表格
- 术语解释是否完整？→ 如否，添加引用块
- 生活化类比是否足够？→ 至少3处
- 配图标注是否完整？→ 至少2-3处
- 破折号检查？→ 必须为0
- 中文标点检查？→ 全部替换
```

如发现问题，**静默修复**后继续。

### 步骤4：保存markdown到工作目录

保存到工作目录（包含配图标注）：

```python
# 文件名：使用中文关键词 + "_解读.md"
# 例如："T5论文_解读.md"、"BERT预训练_解读.md"
# 可以从metadata.json中的标题翻译提取，或让用户指定
filename = f"{chinese_title}_解读.md"  # 如："T5论文_解读.md"
md_path = os.path.join(paper_dir, filename)

with open(md_path, "w", encoding="utf-8") as f:
    f.write(final_content)
```

### 步骤5：全自动提取所有论文图表

**重要改进**：不再依赖markdown标注，直接扫描PDF自动提取所有图表！

使用 `scripts/extract_all_figures.py` 全自动批量提取：

```bash
# 一键提取PDF中的所有Figure和Table
cd {paper_dir}
python ~/.claude/skills/qiaomu-paper-interpreter/scripts/extract_all_figures.py \
  {paper_id}.pdf \
  images \
  {paper_id}

# 示例（以T5论文为例）：
# python extract_all_figures.py T5_2019.pdf images T5_2019
#                               ↑            ↑      ↑
#                               PDF文件      输出目录  图片前缀

# 脚本会自动：
# 1. 扫描PDF所有页面，查找"Figure X"、"Fig. X"、"Table X"标记
# 2. 智能定位图表边界，精确截图
# 3. 批量保存：{paper_id}_figure1.png, {paper_id}_table1.png...
# 4. 生成引用列表：images/figure_list.md（供写作时参考）
```

**提取特性**：
- ✅ 全自动：无需手动标注页码和位置
- ✅ 高成功率：支持多种标记格式（Figure 4, Fig. 4, Table 7）
- ✅ 零成本：约10秒提取完整个论文
- ✅ 智能截图：自动判断Figure/Table边界，2x高清分辨率

**输出结构**：
```
papers/{paper_id}/images/
├── {paper_id}_figure1.png    ← 论文中的第1个图
├── {paper_id}_figure2.png
├── {paper_id}_table1.png      ← 论文中的第1个表
├── {paper_id}_table2.png
└── figure_list.md             ← 自动生成的引用列表（重要！）
```

**figure_list.md 内容示例**：
```markdown
## Figure 1 (第3页)
![Figure 1](images/{paper_id}_figure1.png)

## Table 2 (第7页)
![Table 2](images/{paper_id}_table2.png)
```

**如何使用图表信息**：

1. **写作前浏览**：打开 `figure_list.md`，快速了解论文有哪些图表
2. **按需引用**：写到相关内容时，参考列表选择合适的图表插入
3. **自然融入**：图表应该辅助理解，而非堆砌装饰

**图表搭配策略**：

**论文原图** + **纽约客配图** = 完整体验

- **论文原图**：数据、架构、实验结果（专业、准确）
- **纽约客配图**：概念隐喻、抽象可视化（趣味、理解）

示例组合：
- H2「核心架构」：纽约客配图（隐喻）+ 论文架构图（细节）
- H2「实验结果」：论文数据表（数据）+ 纽约客配图（含义）
- H2「方法创新」：仅纽约客配图（纯概念，无需数据图）

### 步骤5.5：生成《纽约客》风格配图

**重要**：为公众号文章的每个二级标题生成《纽约客》专栏漫画风格的插画！

**新架构：配置驱动工作流**

为了生成高质量的插画，我们采用**分析与执行分离**的架构：

**工作流**：
1. **Claude分析内容** → 为每个H2章节生成具体的视觉描述
2. **脚本批量生图** → 根据配置调用图片生成API

**步骤A：创建配置模板**

```bash
cd {paper_dir}
python ~/.claude/skills/qiaomu-paper-interpreter/scripts/generate_illustrations_v2.py \
  --create-template {filename}

# 自动生成 visual_config.json：
# {
#   "sections": [
#     {"h2_title": "深度的悖论", "visual_description": "待Claude分析填写..."},
#     ...
#   ]
# }
```

**步骤B：Claude分析并填写配置**

你（Claude）需要：
1. 读取文章内容，理解每个H2章节的核心观点
2. 为每个章节设计具体的视觉场景描述（50-80字）
3. 用具象的物体、场景来隐喻抽象概念

**视觉描述示例**（正确）：

示例1 - 架构类：
```json
{
  "h2_title": "模型架构",
  "visual_description": "一座桥梁的横截面图，多层钢架结构相互支撑，信息像车流一样在桥面和下方钢架间流动，用黑白线条绘制主体结构，朱红色标注关键连接点"
}
```

示例2 - 对比类：
```json
{
  "h2_title": "实验结果",
  "visual_description": "两个天平，左侧天平倾斜不平衡，右侧天平完美平衡，天平两侧分别放着不同的模型方块，用黑白线条绘制天平，朱红色点缀平衡的那一侧"
}
```

**❌ 错误示例**（太抽象）：
```json
{
  "visual_description": "用隐喻手法表现核心主题"  // 太抽象，生图API无法理解
}
```

**步骤C：根据配置批量生图**

```bash
cd {paper_dir}
python ~/.claude/skills/qiaomu-paper-interpreter/scripts/generate_illustrations_v2.py {filename}

# 脚本会：
# 1. 读取 visual_config.json
# 2. 为每个H2标题生成《纽约客》风格配图
# 3. 自动调用 即梦API（优先）或 Gemini API（备用）
# 4. 保存到 images/illustrations/
# 5. 自动插入到markdown中H2标题后
```

**《纽约客》配图风格要求**：

```
统一视觉风格：
✓ 1K清晰度，16:9比例（不要用4K）
✓ 钢笔墨水速写/手绘线条，简洁留白背景
✓ 隐喻式表达：用视觉语言传达深层含义
✓ 精致细节：松弛的线条艺术，耐看
✓ 高级配色：黑白为主（不要出现其他颜色），单色点缀（朱红 #E34234）
✓ 墨水渲染/点缀：增强层次感
✓ 底部标题：衬线字体，简洁有力，中文

设计哲学：
• 用视觉隐喻讲故事
• 简约而不简单，幽默而不肤浅
• 每页都是艺术品，值得细品
• 所有页面保持统一的风格、配色、质感
```

**配图示例**：
```
papers/T5_2019/images/
├── T5_2019_figure1.png           ← 论文原图
├── T5_2019_table15.png
└── illustrations/                ← 新生成的配图
    ├── T5_2019_illustration_1.png   ← H2「什么是T5」配图
    ├── T5_2019_illustration_2.png   ← H2「核心创新」配图
    └── T5_2019_illustration_3.png   ← H2「实验结果」配图
```

**插入效果**：
```markdown
## 什么是T5

![什么是T5](images/illustrations/T5_2019_illustration_1.png)

T5的全称是"Text-to-Text Transfer Transformer"...
```

**API配置（自动Fallback）**：

脚本使用共享库的 `ImageGenerator` 类，支持多API自动切换：
- **即梦API**（优先）：需要配置 `JIMENG_SESSION_ID` 环境变量
  - 速度快（10-20秒/张）
  - 中文理解好，纽约客风格稳定
  - 限制：每日66积分（约66张图）
- **Gemini API**（备用）：自动fallback
  - API地址：`https://api.tu-zi.com/v1/chat/completions`
  - 模型：`gemini-3-pro-image-preview`
  - 无额度限制，稳定性高
- **自动重试**：每张图最多重试3次

**生成时间**：
- 单张图（即梦）：约10-20秒
- 单张图（Gemini）：约30-60秒
- 14个H2标题：总计约3-8分钟（取决于API选择）

**容错处理**：
- 即梦失败自动切换Gemini
- SSL错误、网络超时自动重试
- 配置未填写的section自动跳过

### 步骤6：提取H1标题并保存最终文件到根目录

**关键改进**：使用H1标题作为最终文件名，并删除文章中的H1标题！

使用 `scripts/finalize_markdown.py` 自动处理：

```bash
# 执行最终化处理
cd {project_root}
python ~/.claude/skills/qiaomu-paper-interpreter/scripts/finalize_markdown.py \
  {paper_dir}/{filename} \
  .

# 示例：
# python finalize_markdown.py papers/T5_2019/T5论文_解读.md .
#                             ↑                              ↑
#                             输入markdown文件               输出目录（根目录）

# 脚本会：
# 1. 读取markdown文件
# 2. 提取H1标题（如 "# AI的"增长密码"：当模型遇上数学定律"）
# 3. 删除文章中的H1行
# 4. 用H1标题作为文件名保存到根目录（如 "AI的"增长密码"：当模型遇上数学定律.md"）
```

**Python实现示例**：

```python
from scripts.finalize_markdown import save_with_h1_title

# 处理最终markdown文件
final_md = os.path.join(paper_dir, filename)  # 如 papers/T5_2019/T5论文_解读.md
success, output_path, h1_title = save_with_h1_title(final_md, ".")

if success:
    print(f"✅ 最终文件: {h1_title}.md")
else:
    print(f"❌ 处理失败: {h1_title}")
```

**效果对比**：

```markdown
# 处理前（papers/T5_2019/T5论文_解读.md）：
# AI模型的统一范式：T5的突破

想象一下，你有一个万能工具...

## 什么是T5
...

# 处理后（根目录/AI模型的统一范式：T5的突破.md）：
想象一下，你有一个万能工具...

## 什么是T5
...
```

**文件结构**：

```
./
├── AI模型的统一范式：T5的突破.md    ← 最终文件（用H1标题命名，无H1）
├── AI的"增长密码"：当模型遇上数学定律.md  ← 另一篇论文
└── papers/                          ← 统一管理所有论文
    ├── T5_2019/
    │   ├── T5_2019.pdf              ← 重命名后的原始PDF
    │   ├── metadata.json            ← 元数据
    │   ├── extracted_text.txt       ← 提取的文本
    │   ├── T5论文_解读.md            ← 工作副本（保留H1）
    │   └── images/
    │       ├── T5_2019_figure1.png
    │       └── T5_2019_table15.png
    │
    └── Scaling_Laws_Neural_2020/
        ├── Scaling_Laws_Neural_2020.pdf
        ├── metadata.json
        └── images/
```

**优点**：
- ✅ 文件名直接显示文章标题，一目了然
- ✅ 文章内容更简洁，开篇直接进入正文
- ✅ 工作目录保留完整版本（含H1），便于后续修改
- ✅ 根目录只有最终发布版本

### 步骤7：完成报告

简短告知用户：
```
✅ 论文解读完成！

📄 最终文件：{h1_title}.md（已保存到当前目录）
   例如：AI模型的统一范式：T5的突破.md
📝 字数：约X字
🖼️ 图表：已自动提取X张（Figure Y张，Table Z张）
🎨 配图：已生成X张《纽约客》风格插画

📁 论文档案：papers/{paper_id}/
   ├── {paper_id}.pdf（原始论文，已重命名）
   ├── metadata.json（标题、作者、年份等元数据）
   ├── extracted_text.txt（提取的完整文本）
   ├── {filename}（工作副本，保留H1标题）
   └── images/
       ├── {paper_id}_figure1.png（论文原图）
       ├── {paper_id}_table15.png
       └── illustrations/
           ├── {paper_id}_illustration_1.png（H2配图）
           ├── {paper_id}_illustration_2.png
           └── {paper_id}_illustration_3.png

风格特点：
- 所有术语已用引用块解释
- 包含X处生活化类比
- 重点数据已制表展示
- 论文图表已精确截取并插入
- 每个H2标题都有《纽约客》风格配图

✨ 最终优化：
  • 文件名使用H1标题，一目了然
  • 文章开篇直接进入正文，无H1标题
  • 工作副本保留完整结构，便于后续修改

💡 提示：
  • 所有论文的原始PDF和资料都保存在 papers/ 目录中
  • 配图使用《纽约客》专栏漫画风格，适合公众号发布
  • 所有图片带{paper_id}_前缀，永不冲突
```

## 完整示例工作流

```
用户输入：https://arxiv.org/pdf/1910.10683

执行流程：
0. 智能PDF管理：
   ✓ 下载PDF（临时）
   ✓ 提取标题："Exploring the Limits of Transfer Learning..."
   ✓ 提取年份：2019 (从URL)
   ✓ 生成paper_id：T5_2019
   ✓ 创建目录：papers/T5_2019/
   ✓ 重命名PDF：papers/T5_2019/T5_2019.pdf
   ✓ 保存元数据：papers/T5_2019/metadata.json

1. 提取文本 → papers/T5_2019/extracted_text.txt

2. 自动生成完整解读（包含：
   - 故事化引入
   - 15+个术语解释（引用块）
   - 5处生活化类比
   - 3个数据对比表格
   - 4处配图标注
   - 方法论思考）

3. 保存到工作目录 → papers/T5_2019/T5论文_解读.md

4. 执行图表提取（带前缀 T5_2019）：
   ✓ 提取 Figure 1 -> papers/T5_2019/images/T5_2019_figure1.png
   ✓ 提取 Table 13 -> papers/T5_2019/images/T5_2019_table13.png
   ✓ 提取 Table 14 -> papers/T5_2019/images/T5_2019_table14.png
   ✓ 提取 Table 15 -> papers/T5_2019/images/T5_2019_table15.png
   ✓ 替换标注为实际图片

5. 生成《纽约客》风格配图（带前缀 T5_2019，自动重试3次）：
   [1/5] 正在为「什么是T5」生成配图...
   ✓ 图片已保存: papers/T5_2019/images/illustrations/T5_2019_illustration_1.png
   ✓ 已插入到markdown

   [2/5] 正在为「核心创新」生成配图...
   ✗ 失败: API请求失败: SSLEOFError
   等待5秒后重试...
   第2次尝试（共3次）...
   ✓ 重试成功！
   ✓ 图片已保存: papers/T5_2019/images/illustrations/T5_2019_illustration_2.png
   ✓ 已插入到markdown

   [3/5] 正在为「实验结果」生成配图...
   ✓ 图片已保存: papers/T5_2019/images/illustrations/T5_2019_illustration_3.png
   ✓ 已插入到markdown

   ... (共5张配图)

   ✅ 完成！成功生成 5/5 张配图（含1次重试成功）

6. 提取H1标题并保存最终文件：
   ✓ 提取H1标题："AI模型的统一范式：T5的突破"
   ✓ 删除文章中的H1行
   ✓ 保存到根目录 → ./AI模型的统一范式：T5的突破.md

7. 报告完成

总耗时：约4-6分钟（含配图生成）

最终文件结构：
./
├── AI模型的统一范式：T5的突破.md  ← 最终文件（用H1标题命名，无H1）
└── papers/                        ← 统一管理所有论文
    └── T5_2019/                   ← 论文标识_年份
        ├── T5_2019.pdf            ← 原始PDF（已重命名）
        ├── metadata.json          ← 元数据（标题、作者、年份等）
        ├── extracted_text.txt     ← 提取的完整文本
        ├── T5论文_解读.md          ← 工作副本（保留H1标题）
        └── images/
            ├── T5_2019_figure1.png        ← 论文原图（带前缀）
            ├── T5_2019_table13.png
            ├── T5_2019_table14.png
            ├── T5_2019_table15.png
            └── illustrations/             ← 《纽约客》风格配图
                ├── T5_2019_illustration_1.png
                ├── T5_2019_illustration_2.png
                ├── T5_2019_illustration_3.png
                ├── T5_2019_illustration_4.png
                └── T5_2019_illustration_5.png

优点：
✓ PDF有意义的名字（T5_2019.pdf，一目了然）
✓ 根目录整洁（只有最终md文件）
✓ 最终文件名直接显示文章标题，一目了然
✓ 文章开篇直接进入正文，无H1标题
✓ papers/目录统一管理所有论文原始资料
✓ 每篇论文独立子目录，易于查找
✓ 图片带paper_id前缀，永不冲突
✓ 元数据JSON记录完整信息（标题、作者、年份、来源URL）
✓ 工作副本保留完整结构（含H1），便于后续修改
✓ 《纽约客》风格配图，适合公众号发布
✓ 论文原图和生成配图分开存放，易于管理
```

## 质量保证

生成的文档必须通过：
- [x] 所有专业术语有引用块解释
- [x] 至少3处生活化类比
- [x] 语言口语化
- [x] 0个破折号
- [x] 100%中文标点
- [x] 重要观点加粗
- [x] 至少2处配图标注
- [x] 包含实验数据表格
- [x] 结尾有升华

## 图表提取详解

### 工作原理

`scripts/extract_figures.py` 的执行流程：

1. **解析标注**：
   ```python
   # 从markdown提取：**【配图建议：第3页，Figure 1 - 描述】**
   pattern = r'\*\*【配图建议：第(\d+)页，(Figure|Table)\s*([0-9]+)\s*-\s*([^】]+)】\*\*'
   ```

2. **定位图表**：
   - 打开PDF第X页
   - 搜索"Figure Y"或"Table Y"文本
   - 获取文本位置的边界框(bbox)

3. **扩展截取范围**（关键！）：

   **Figure和Table布局完全不同**：
   - Figure: 图片在上，caption在下 → 从caption**向上**截取
   - Table: 表格在上，caption在下 → 从caption**向上**截取

   ```python
   x0 = 页面宽度 * 0.05  （左边距5%）
   x1 = 页面宽度 * 0.95  （右边距5%）

   if Figure:
       y0 = caption_top - 500pt   （向上500pt找图片）
       y1 = caption_bottom + 20pt （包含caption）

   if Table:
       # 搜索caption上方的"Model"/"Method"等列标题
       table_top = 搜索关键词位置 - 20pt
       y0 = table_top              （表格顶部）
       y1 = caption_bottom + 20pt  （包含caption）
   ```

4. **高清截图**：
   ```python
   pix = page.get_pixmap(clip=clip_rect, matrix=fitz.Matrix(2, 2))
   # 2x分辨率，确保清晰度
   ```

5. **替换标注**：
   ```markdown
   # 原标注
   **【配图建议：第3页，Figure 1 - 展示T5的text-to-text统一框架】**

   # 替换为
   ![展示T5的text-to-text统一框架](images/figure1.png)

   *展示T5的text-to-text统一框架*
   ```

### 手动调用（可选）

如果自动提取失败，可以手动调用：

```bash
cd /path/to/paper/directory

# 安装依赖
pip install pymupdf pillow pdfplumber

# 执行提取
python ~/.claude/skills/qiaomu-paper-interpreter/scripts/extract_figures.py \
  paper.pdf \
  T5论文_解读.md \
  images

# 输出示例：
# 正在解析markdown中的配图标注...
# 找到 4 处配图标注
#
# 正在从PDF中提取图表...
# ✓ 提取 Figure 1 -> images/figure1.png
# ✓ 提取 Table 13 -> images/table13.png
# ✗ 未找到 Table 99 在第 100 页
#
# 正在更新markdown文件...
# ✅ 已更新 T5论文_解读.md
#    替换了 3 处配图标注
```

### 提取失败排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| "未找到 Figure X" | PDF中的标题格式不匹配 | 检查PDF中是否为"Fig. X"或"FIGURE X"，手动调整搜索词 |
| Table只截到文字没有表格 | 搜索关键词失败 | 检查表格列标题，在脚本中添加更多关键词（如"Type", "Name"等） |
| 截图区域不完整 | 图表比默认范围更大 | 对Figure增大500→700，对Table增大300→500 |
| 图表太小看不清 | 分辨率不够 | 修改Matrix参数从(2,2)到(3,3)或(4,4) |
| 截到了页眉页脚 | 边界框超出图表范围 | 减小y0向上的距离，或增加关键词搜索精度 |
| PyMuPDF安装失败 | 缺少依赖 | 使用备选：`pip install pdfplumber pillow` |

## 故障处理

| 问题 | 解决方案 |
|------|----------|
| PDF无法下载 | 用WebFetch获取内容 |
| 文本提取失败 | 尝试pypdf作为备选 |
| 论文超长（>50页） | 重点读摘要、方法、实验、结论 |
| 非英文论文 | 中文直接解读，其他语言建议用户提供英文版 |
| 图表提取失败 | 手动调用脚本，根据输出调整参数 |
| 图表截取不完整 | 在脚本中增大y1参数（默认400→600） |

## 参考资源

- 乔木风格详细指南：[references/style-guide.md](references/style-guide.md)
- 原始workflow参考：[references/workflow.md](references/workflow.md)
