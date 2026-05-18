# qiaomu-paper-interpreter

将 arXiv 论文自动转化为乔木风格中文解读文章的 Claude Code Skill。

**全程自动，无需中途确认。**

## 功能

- **arXiv 原生支持**：输入论文链接或 ID，自动获取 LaTeX 源码提取图表（比 PDF 边界框检测更准确）
- **乔木风格写作**：8000-10000 字深度解读，对话式语言 + 术语引用块 + 生活化类比
- **双层配图**：纸雕水彩封面 + 《纽约客》风格章节插图（黑白线条 + 朱红色点缀）
- **论文原图提取**：从 LaTeX 源码精准提取所有 Figure / Table
- **智能文件管理**：工作目录保留完整档案，阅读目录存放纯净文章
- **即梦 API 集成**：支持免费模型（4.1）和付费模型（4.5）

## 快速开始

在 Claude Code 中直接说：

```
解读论文 https://arxiv.org/abs/1706.03762
```

```
读paper 2501.00001
```

```
帮我理解这篇paper https://arxiv.org/abs/2312.00001，乔木风格
```

## 输出

**工作目录**（`25 论文库/21.01 papers/{paper_id}/`）：

```
Transformer_2017/
├── Transformer_2017.pdf
├── metadata.json
├── extracted_text.md
├── images/              # 论文原图（Figure / Table）
├── illustrations/       # AI 生成配图
│   ├── cover.png        # 纸雕水彩封面
│   └── 01-*.png         # 纽约客风格章节插图
└── 注意力即一切：AI架构的范式革命_解读.md
```

**阅读目录**（`25 论文库/21.02 论文解读/`）：

```
注意力即一切：AI架构的范式革命.md   # 纯净版，直接阅读
```

## 配置

复制 `.env.example` 为 `.env` 并按需修改：

```bash
cp .env.example .env
```

| 变量 | 说明 | 示例 |
|------|------|------|
| `PAPER_OUTPUT_DIR` | 论文工作目录 | `~/Papers/papers` |
| `PAPER_READING_DIR` | 解读文章目录 | `~/Papers/reading` |
| `OBSIDIAN_VAULT` | Obsidian Vault 名称，完成后自动打开 | `MyVault` |
| `IMAGE_PROVIDER` | 配图方案：`skip` / `jimeng` | `jimeng` |

## 依赖

```bash
pip install pdfplumber pymupdf requests
```

图片生成需要安装 [qiaomu-image-generator](https://github.com/joeseesun/qiaomu-image-generator) skill 并配置即梦 API。

## 安装

```bash
claude skill install https://github.com/joeseesun/qiaomu-paper-interpreter
```

## 目录结构

```
qiaomu-paper-interpreter/
├── SKILL.md                      # Skill 定义与完整工作流
├── scripts/
│   ├── extract_figures.py        # LaTeX 源码图表提取（主力）
│   ├── extract_all_figures.py    # PDF 图表提取（备用）
│   ├── extract_pdf_metadata.py   # PDF 元数据提取
│   ├── generate_illustrations_v2.py  # 配图生成
│   ├── finalize_markdown.py      # 文章最终化处理
│   └── load_env.py               # 环境变量加载
├── references/
│   ├── style-guide.md            # 乔木写作风格指南
│   └── workflow.md               # 工作流参考
├── visual_description_guide.md   # 配图描述编写指南
├── .env.example                  # 配置模板
└── .gitignore
```

## 📱 关注作者

如果这个项目对你有帮助，欢迎关注我获取更多技术分享：

- **X (Twitter)**: [@vista8](https://x.com/vista8)
- **微信公众号「向阳乔木推荐看」**:

<p align="center">
  <img src="https://github.com/joeseesun/terminal-boost/raw/main/assets/wechat-qr.jpg" alt="向阳乔木推荐看公众号二维码" width="300">
</p>

## License

MIT
