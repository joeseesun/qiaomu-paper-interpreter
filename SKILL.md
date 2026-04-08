---
name: qiaomu-paper-interpreter
description: Transform academic papers into conversational Chinese articles in Qiaomu's style. Use when user provides PDF URL with keywords "解读论文", "理解paper", or "乔木风格". Runs fully automatically.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, TodoWrite
---

# 乔木论文解读

## 概述

将学术论文自动转化为乔木风格的通俗易懂解读文章。**全自动执行**，无需用户中途确认。

**核心特点**：
- 对话式语言，像和朋友聊天
- 每个术语都有引用块解释
- 生活化类比帮助理解
- 自动提取论文图表
- 生成纸雕水彩封面
- 生成《纽约客》风格配图

**输出**：
- 8000-10000字深度解读文章
- 纸雕水彩风格封面图
- 完整论文档案（PDF + 图表 + 元数据）
- 发布就绪的markdown文件


---

## 📁 文件管理规范

**核心原则**：所有过程文件在工作目录，最终文章复制到阅读目录

### 工作目录：`20-29 学习/25 论文库/21.01 papers/{paper_id}/`

```
20-29 学习/25 论文库/21.01 papers/LLM_Agents_2023/
├── {paper_id}.pdf
├── metadata.json
├── extracted_text.md
├── images/              # 原文图表（Figure/Table）
├── illustrations/       # AI生成配图（封面+纽约客）
│   ├── cover.png        # 封面图（纸雕水彩风格）
│   ├── 01-*.png         # 纽约客风格配图
│   └── visual_config*.json  # 配图配置
└── {标题}_解读.md       # 最终文章（工作副本）
```

### 阅读目录：`20-29 学习/25 论文库/21.02 论文解读/`

最终文章自动复制到此目录，方便统一阅读。

**优势**：
- ✅ 工作目录保留完整档案（PDF + 图表 + 配图）
- ✅ 阅读目录只有纯净文章
- ✅ 双份保留，互不干扰

详见：`FILE_MANAGEMENT.md` 和 `FILE_LOCATIONS.md`

---

## 自动化工作流程

**执行原则**：
1. ✅ 全程自动，不询问用户
2. ✅ 使用TodoWrite显示进度
3. ✅ 静默修复质量问题
4. ✅ 生成完整最终版本

**推荐顺序**：步骤0 → 1 → 5 → 2 → 4 → 5.5 → 6 → 7

---

### 初始化：创建进度追踪

**第一步**：创建todo list，让用户看到进度

```python
TodoWrite([
    {"content": "下载PDF并创建论文目录", "status": "in_progress", "activeForm": "下载PDF并创建论文目录"},
    {"content": "提取PDF文本内容", "status": "pending", "activeForm": "提取PDF文本内容"},
    {"content": "生成乔木风格解读文章", "status": "pending", "activeForm": "生成乔木风格解读文章"},
    {"content": "提取论文图表", "status": "pending", "activeForm": "提取论文图表"},
    {"content": "生成纽约客风格配图", "status": "pending", "activeForm": "生成纽约客风格配图"},
    {"content": "保存最终文件", "status": "pending", "activeForm": "保存最终文件"}
])
```

**每完成一步**，立即更新状态为`completed`，下一步为`in_progress`

**标准 Todo 列表**：
```python
TodoWrite([
    {"content": "下载PDF并创建论文目录", "status": "in_progress", "activeForm": "下载PDF并创建论文目录"},
    {"content": "提取PDF文本内容", "status": "pending", "activeForm": "提取PDF文本内容"},
    {"content": "提取论文图表", "status": "pending", "activeForm": "提取论文图表"},
    {"content": "生成乔木风格解读文章", "status": "pending", "activeForm": "生成乔木风格解读文章"},
    {"content": "生成封面图（提炼关键词）", "status": "pending", "activeForm": "生成封面图（提炼关键词）"},
    {"content": "生成《纽约客》风格配图", "status": "pending", "activeForm": "生成《纽约客》风格配图"},
    {"content": "保存最终文件", "status": "pending", "activeForm": "保存最终文件"}
])
```

---

### 步骤0：智能PDF管理

**目标**：下载PDF，创建规范化目录结构

**执行**：
```bash
cd ~/乔木新知识库
python ~/.claude/skills/qiaomu-paper-interpreter/scripts/extract_pdf_metadata.py \
  <temp_pdf> "20-29 学习/25 论文库/21.01 papers" <url>

# 参数说明：
# 1. <temp_pdf>: 临时下载的PDF路径（如 /tmp/paper.pdf）
# 2. "20-29 学习/25 论文库/21.01 papers": 输出基础目录
# 3. <url>: 原始PDF的URL（可选，用于提取年份等信息）
```

**输出**：
- `20-29 学习/25 论文库/21.01 papers/{paper_id}/` 目录（如 `21.01 papers/SAM_2025/`）
- `{paper_id}.pdf` 重命名的PDF
- `metadata.json` 元数据文件

**paper_id生成规则**：
- 提取论文标题中的缩写词（如 SAM, BERT, GPT）
- 如无缩写，提取前2-3个关键词
- 加上年份，生成简洁标识（如 `SAM_2025`, `BERT_2018`）

**元数据包含**：
- paper_id（如 "SAM_2025"）
- title（完整标题）
- year（发表年份）
- authors（作者列表）
- source_url（来源URL）

**完成后**：更新todo状态

---

### 步骤1：提取PDF文本

**目标**：提取完整文本内容，保留格式和结构

**执行**：使用 Markitdown 将 PDF 转换为 Markdown

```bash
markitdown {paper_dir}/{paper_id}.pdf -o {paper_dir}/extracted_text.md
```

**输出**：`{paper_dir}/extracted_text.md`

**架构优势**（相比 pdfplumber）：
- ✅ 保留完整格式（空格、标点、换行）
- ✅ 数学公式结构完整
- ✅ 表格自动转换为 Markdown 表格
- ✅ 图表描述清晰可读
- ✅ 文档结构语义化（标题、引用、列表）

**重点关注**：
- 摘要和结论
- 方法描述
- 实验结果
- 图表标题（Figure X, Table X）

**完成后**：更新todo状态

---

### 步骤5：提前提取图表

**目标**：提取所有Figure和Table，供写作时引用

**执行**：
```bash
cd {paper_dir}
python ~/.claude/skills/qiaomu-paper-interpreter/scripts/extract_all_figures.py \
  {paper_id}.pdf images {paper_id}
```

**输出**：
- `images/{paper_id}_figure1.png`
- `images/{paper_id}_table1.png`
- `images/figure_list.md`（引用清单）

**特性**：
- 全自动识别Figure/Table标记
- 智能定位边界
- 2x高清分辨率

**完成后**：更新todo状态

---

### 步骤2：生成完整解读

**目标**：一次性生成最终完整版本（不要分初稿和完善版）

#### 内容结构（必须包含）

1. **引入**：用故事/场景引入，不直接讲技术
2. **核心概念**：术语解释（引用块） + 生活化类比
3. **技术细节**：是什么 → 为什么 → 怎么做
4. **实验数据**：表格展示，加粗重点
5. **深度洞察**：方法论启发、历史意义
6. **结尾升华**：延伸到认知层面

#### 术语解释格式（强制）

```markdown
> **Transformer**：一种神经网络架构，核心是"自注意力机制"。可以想象成你在读一句话时，会自动关注句子中最重要的几个词，而不是平均分配注意力。
```

#### 图表引用策略

- 查看`images/figure_list.md`，了解可用图表
- **自然引用**，不刻意堆砌
- 引用格式：`![描述](20-29 学习/25 论文库/21.01 papers/{paper_id}/images/{paper_id}_figure1.png)`
- 建议：核心架构图、关键实验数据、可视化分析

#### 风格要求（严格遵守）

详见`references/style-guide.md`，核心：
- ✅ 短段落，多留白
- ✅ "就像""比如""试想一下"
- ✅ 中文标点（，。：！？）
- ✅ 重要观点加粗
- ❌ 绝对不用破折号
- ❌ 不用"首先""其次""值得注意的是"

#### 内部质量检查（静默执行）

生成后自检：
- 核心贡献覆盖？
- 术语解释完整？（至少15处）
- 生活化类比？（至少3处）
- 数据表格？（至少1个）
- 图表引用？（至少2处）
- 破折号？（必须0个）
- 中文标点？（100%）

发现问题→静默修复→继续

**完成后**：
- 保存到`{paper_dir}/{中文标题}_解读.md`
- 更新todo状态

---

### 步骤4：生成封面图（提炼关键词）

**目标**：从文章中提炼1-3个核心关键词，生成封面图并插入文章开头

**工作流程**：
1. 提炼关键词
2. 生成封面配置
3. 调用配图生成器
4. 插入文章开头

#### 1. 提炼关键词

从文章标题和核心内容中提取：
- 论文名称/缩写（如 Qwen3-TTS、SAM）
- 核心技术概念（如 语音合成、分割模型）
- 关键特性（如 3秒克隆、多语言）

**原则**：
- 控制在20字以内
- 1-3个核心概念
- 避免过长描述

**示例**：
- Qwen3-TTS → `Qwen3-TTS 语音合成 3秒克隆`
- Segment Anything → `SAM 图像分割 零样本泛化`

#### 2. 生成封面配置

在 `illustrations/` 目录下创建 `visual_config_cover.json`：

```json
{
  "task_id": "cover_{paper_id}",
  "template": "paper",
  "source": "{article_path}",
  "output_dir": "{illustrations_dir}",

  "cover": {
    "enabled": true,
    "filename": "cover.png",
    "style": "paper-watercolor-cover",
    "aspect_ratio": "16:9",
    "description": "{关键词1} {关键词2} {关键词3}",
    "retry_count": 2
  },

  "illustrations": [],

  "defaults": {
    "style": "paper-watercolor-cover",
    "provider": "jimeng",
    "retry_count": 2
  }
}
```

**字段说明**：
| 字段 | 值 | 说明 |
|------|-----|------|
| template | `paper` | 论文解读场景 |
| style | `paper-watercolor-cover` | 纸雕水彩封面风格 |
| aspect_ratio | `16:9` | 横向宽屏 |
| description | 关键词字符串 | 空格分隔的核心概念 |

#### 3. 调用配图生成器

```bash
cd {illustrations_dir}
python ~/.claude/skills/qiaomu-image-generator/scripts/generate.py \
  visual_config_cover.json --workers 1
```

**输出**：
- `illustrations/cover.png` - 封面图片（约5MB）

#### 4. 插入文章开头

在Markdown文件最前面添加：

```markdown
![封面](illustrations/cover.png)
```

**执行方式**：
```bash
# 方式1：使用 sed 在文件开头插入
sed -i '1i ![封面](illustrations/cover.png)\n' {article}

# 方式2：使用 Python 脚本
python -c "
content = open('{article}').read()
with open('{article}', 'w') as f:
    f.write('![封面](illustrations/cover.png)\n\n' + content)
"
```

**完成后**：更新todo状态

---

### 步骤5.5：生成《纽约客》配图

**目标**：为每个H2标题生成配图（**并发加速，3倍性能提升**）

**工作流**：
1. Claude读取文章，理解每个H2核心观点，创建`visual_config.json`
2. 调用 `qiaomu-image-generator/scripts/generate.py` 批量并发生成

#### 1. Claude创建 visual_config.json

在 `{paper_dir}/illustrations/` 目录下创建 `visual_config.json`：

```json
{
  "task_id": "illustrations_{paper_id}",
  "template": "paper",
  "source": "{paper_dir}/{标题}_解读.md",
  "output_dir": "{paper_dir}/illustrations",
  "cover": { "enabled": false },
  "illustrations": [
    {
      "id": "01",
      "h2_title": "H2标题",
      "visual_description": "50-80字中文具体场景描述",
      "filename": "01-slug.png"
    },
    {
      "id": "02",
      "h2_title": "H2标题",
      "visual_description": "50-80字中文具体场景描述",
      "filename": "02-slug.png"
    }
  ],
  "defaults": {
    "style": "newyorker",
    "provider": "jimeng",
    "retry_count": 2
  }
}
```

#### 2. visual_description 编写规范

**必须用中文**（即梦API是国产模型，中文描述更准确）

**编写要求**：
- 必须基于 H2 **段落内容** 设计（不是仅看标题）
- 用具象物体/场景隐喻抽象概念
- 50-80字
- 不包含风格指令（如"黑白线条"、"朱红色"）
- 不包含文字指令（如"底部标题"、"标注文字"）

**编写流程**（每个H2都要执行）：

1. **定位章节内容**：找到H2标题，读取该H2下的所有段落
2. **提炼核心观点**：这个章节的中心思想、关键对比、具体例子
3. **设计视觉隐喻**：用具象场景表达抽象概念

**示例**：

```
H2标题："注意力机制的突破"

Step 1 - 读取段落内容：
"传统的序列模型像流水线工人，只能按顺序处理...
注意力机制让模型可以同时关注所有位置..."

Step 2 - 提炼核心观点：
- 核心：从顺序处理到并行关注
- 对比：流水线 vs 全局视角

Step 3 - 设计视觉隐喻：
"一个指挥家站在舞台中央，双手张开同时指向乐团的不同声部，每个乐手上方浮现不同亮度的光圈，表示被关注的程度不同，而不是按座位顺序逐个演奏"
```

#### 3. 批量并发生成

```bash
cd ~/乔木新知识库
python ~/.claude/skills/qiaomu-image-generator/scripts/generate.py \
  {paper_dir}/illustrations/visual_config.json --workers 3
```

**性能优化**：
- ⚡ 并发生成：3线程并发，12张图约2分钟（vs 串行6分钟）
- 🛡️ 防重复：自动检测并跳过已插入的配图
- 🎯 智能重试：2次重试，友好错误提示

**配图要求**（系统自动控制，无需在visual_description中描述）：
- 钢笔墨水速写，16:9比例
- 黑白线条 + 朱红色点缀
- 简洁留白，松弛线条
- 底部中文标题

**完成后**：更新todo状态

---

### 步骤6：保存最终文件

**目标**：用H1标题作为文件名，保存到论文解读目录

**执行**：
```bash
python ~/.claude/skills/qiaomu-paper-interpreter/scripts/finalize_markdown.py \
  {paper_dir}/{filename} "20-29 学习/25 论文库/21.02 论文解读"
```

**处理**：
- 提取H1标题
- 删除文章中的H1行
- 用H1标题命名保存到论文解读目录

**效果**：
- 论文解读目录：`20-29 学习/25 论文库/21.02 论文解读/AI的突破.md`（最终版，无H1）
- 工作目录：`20-29 学习/25 论文库/21.01 papers/{paper_id}/{标题}_解读.md`（保留H1）

**完成后**：更新todo状态为completed

---

### 步骤7：完成报告并打开文章

**目标**：告知用户完成情况，并自动在Obsidian中打开文章

**执行**：
```bash
# 自动在Obsidian中打开生成的文章
# 注意：file参数不需要.md后缀，路径相对于vault根目录
open "obsidian://open?vault=乔木新知识库&file=20-29 学习/25 论文库/21.01 papers/{paper_id}/{filename_without_extension}"
```

**路径说明**：
- `vault`：知识库名称（乔木新知识库）
- `file`：相对于vault根目录的路径，不含.md后缀
- 示例：`20-29 学习/25 论文库/21.01 papers/Agentic_Reasoning_Large_2026/乔木解读_Agentic_Reasoning`

简短告知用户：

```
✅ 论文解读完成！

📄 最终文件：{h1_title}.md
📝 字数：约X字
🎨 封面：已生成（纸雕水彩风格）
🖼️ 图表：已提取X张（Figure Y张，Table Z张）
📊 配图：已生成X张

📁 论文档案：20-29 学习/25 论文库/21.01 papers/{paper_id}/
   ├── {paper_id}.pdf
   ├── metadata.json
   ├── extracted_text.md
   ├── {filename}（工作副本）
   ├── illustrations/cover.png（封面图）
   ├── illustrations/（纽约客配图）
   └── images/（原文图表）

风格特点：
- 术语解释：X处
- 生活化类比：X处
- 数据表格：X个

📖 已在Obsidian中打开文章
```

---

## 质量检查清单

生成的文档必须通过：

- [x] 所有术语有引用块解释（≥15处）
- [x] 生活化类比（≥3处）
- [x] 语言口语化
- [x] 破折号（=0个）
- [x] 中文标点（100%）
- [x] 重要观点加粗
- [x] 图表引用（≥2处）
- [x] 数据表格（≥1个）
- [x] 结尾有升华

---

## 参考文档

- **风格指南**：`references/style-guide.md`
- **使用示例**：`examples.md`
- **故障排查**：`TROUBLESHOOTING.md`
- **配图设计**：`visual_description_guide.md`
- **版本历史**：`CHANGELOG.md`
