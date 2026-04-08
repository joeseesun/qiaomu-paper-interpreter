# 乔木论文解读 Skill

学术论文自动转化为乔木风格通俗易懂解读文章的Claude Code skill。

## 特性

- ✅ **全自动workflow**：从PDF下载到最终发布，一气呵成
- ✅ **智能PDF管理**：自动提取元数据，生成有意义的文件名和目录
- ✅ **对话式语言**：像朋友聊天一样讲解复杂概念
- ✅ **术语解释**：每个专业术语都有引用块说明
- ✅ **生活化类比**：用日常例子帮助理解
- ✅ **论文原图提取**：自动提取所有Figure和Table
- ✅ **《纽约客》风格配图**：16:9横幅，黑白线条+朱红色点缀，底部中文标题
- ✅ **免费配图选项**：支持免费模型（jimeng-image-4.1）和付费模型（4.5）选择

## 快速开始

```bash
# 在Claude Code中使用（默认付费配图）
解读 https://arxiv.org/pdf/1706.03762

# 使用免费配图
解读这篇论文，免费配图 https://arxiv.org/pdf/1706.03762
```

自动执行：
1. 下载PDF并提取元数据
2. 提取完整文本内容
3. 自动提取所有论文图表（Figure/Table）
4. 撰写乔木风格解读文章
5. 生成《纽约客》风格配图（每个H2章节）
   - 默认：付费模型（jimeng-image-4.5），质量更高
   - 免费：免费模型（jimeng-image-4.1），质量略低但完全免费
6. 保存最终文件到根目录（用H1标题命名）

## 目录结构

```
qiaomu-paper-interpreter/
├── README.md                           # 本文件
├── SKILL.md                           # 详细的workflow说明
├── CHANGELOG.md                       # 版本变更记录
├── visual_description_guide.md        # 配图设计编写指南
├── .gitignore                         # Git忽略规则
├── scripts/                           # 工具脚本
│   ├── extract_pdf_metadata.py        # PDF元数据提取
│   ├── extract_all_figures.py         # 批量提取论文图表
│   ├── generate_illustrations_v2.py   # 《纽约客》配图生成
│   └── finalize_markdown.py           # 最终化处理（提取H1）
└── references/                        # 参考文档
    └── style-guide.md                 # 乔木写作风格指南
```

## 依赖

- `pdfplumber` - PDF文本提取
- `PyMuPDF` (fitz) - PDF图表提取
- `requests` - HTTP请求
- `shared-lib/image_api.py` - 图片生成API（即梦/Gemini）

## 配置

### 图片生成API

需要配置环境变量：

```bash
# 即梦API（优先）
export JIMENG_SESSION_ID="your_session_id"
export JIMENG_API_URL="http://localhost:8000"

# Gemini API（备用，自动fallback）
# API key已内置，无需额外配置
```

## 核心改进

### 2025-12-23: 配图生成prompt修复

**问题**：英文prompt被AI误读为要画的文字内容

**修复**：使用中文描述风格特征
- ✅ "钢笔墨水速写"代替"pen and ink drawing"
- ✅ "朱红色点缀"代替"#E34334"
- ✅ 风格与内容清晰分离

详见 `SKILL.md` 最近更新章节。

## 使用示例

### 输入

```
解读 https://arxiv.org/pdf/1706.03762
```

### 输出

```
papers/Transformer_2017/
├── Transformer_2017.pdf           # 原始PDF
├── metadata.json                  # 元数据
├── extracted_text.md              # 提取的文本（Markdown格式）
├── Transformer论文_解读.md         # 工作副本
└── images/
    ├── Transformer_2017_figure1.png    # 论文原图
    ├── Transformer_2017_table1.png
    └── illustrations/                  # 《纽约客》配图
        ├── Transformer_2017_illustration_1.png
        └── ...

./注意力即一切：AI架构的范式革命.md  # 最终发布文件（用H1标题命名）
```

## 贡献

欢迎提issue和PR！

## 许可

MIT License
