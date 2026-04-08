# 使用示例

## 完整工作流示例

### 示例1：解读Transformer论文

**用户输入**：
```
解读 https://arxiv.org/pdf/1706.03762
```

**执行流程**：

```
0. 智能PDF管理：
   ✓ 下载PDF（临时）
   ✓ 提取标题："Attention Is All You Need"
   ✓ 提取年份：2017 (从URL)
   ✓ 生成paper_id：Transformer_2017
   ✓ 创建目录：papers/Transformer_2017/
   ✓ 重命名PDF：papers/Transformer_2017/Transformer_2017.pdf
   ✓ 保存元数据：papers/Transformer_2017/metadata.json

1. 提取文本 → papers/Transformer_2017/extracted_text.md（Markitdown格式化）

2. 自动生成完整解读（包含：
   - 故事化引入
   - 15+个术语解释（引用块）
   - 5处生活化类比
   - 3个数据对比表格
   - 4处配图标注
   - 方法论思考）

3. 保存到工作目录 → papers/Transformer_2017/Transformer论文_解读.md

4. 执行图表提取（带前缀 Transformer_2017）：
   ✓ 提取 Figure 1 -> papers/Transformer_2017/images/Transformer_2017_figure1.png
   ✓ 提取 Figure 2 -> papers/Transformer_2017/images/Transformer_2017_figure2.png
   ✓ 提取 Table 1 -> papers/Transformer_2017/images/Transformer_2017_table1.png
   ✓ 提取 Table 2 -> papers/Transformer_2017/images/Transformer_2017_table2.png

5. 生成《纽约客》风格配图（带前缀 Transformer_2017）：
   [1/10] 正在为「旧世界的问题」生成配图...
   ✓ 图片已保存: papers/Transformer_2017/images/illustrations/illustration_1.png
   ✓ 已插入到markdown

   [2/10] 正在为「注意力的魔法」生成配图...
   ✓ 图片已保存: papers/Transformer_2017/images/illustrations/illustration_2.png
   ✓ 已插入到markdown

   ... (共10张配图)

   ✅ 完成！成功生成 10/10 张配图

6. 提取H1标题并保存最终文件：
   ✓ 提取H1标题："注意力即一切：AI架构的范式革命"
   ✓ 删除文章中的H1行
   ✓ 保存到根目录 → ./注意力即一切：AI架构的范式革命.md

7. 报告完成

总耗时：约4-6分钟（含配图生成）
```

**最终文件结构**：

```
./
├── 注意力即一切：AI架构的范式革命.md  ← 最终文件（用H1标题命名，无H1）
└── papers/                              ← 统一管理所有论文
    └── Transformer_2017/                ← 论文标识_年份
        ├── Transformer_2017.pdf         ← 原始PDF（已重命名）
        ├── metadata.json                ← 元数据（标题、作者、年份等）
        ├── extracted_text.md            ← 提取的完整文本（Markdown格式）
        ├── Transformer论文_解读.md       ← 工作副本（保留H1标题）
        └── images/
            ├── Transformer_2017_figure1.png        ← 论文原图（带前缀）
            ├── Transformer_2017_figure2.png
            ├── Transformer_2017_table1.png
            ├── Transformer_2017_table2.png
            └── illustrations/                      ← 《纽约客》风格配图
                ├── illustration_1.png
                ├── illustration_2.png
                ├── illustration_3.png
                └── ... (共10张)
```

**生成的文章特点**：
- 字数：约9000字
- 术语解释：15+处引用块
- 生活化类比：5+处
- 数据表格：3个
- 论文原图：5张（Figure）+ 4张（Table）
- 纽约客配图：10张

---

### 示例2：解读T5论文

**用户输入**：
```
用乔木风格解读这篇paper: https://arxiv.org/pdf/1910.10683
```

**执行流程**：

```
0. 智能PDF管理：
   ✓ 下载PDF
   ✓ 提取标题："Exploring the Limits of Transfer Learning..."
   ✓ 生成paper_id：T5_2019
   ✓ 创建目录：papers/T5_2019/

1-6. [执行完整workflow...]

7. 最终输出：
   📄 AI模型的统一范式：T5的突破.md
   📁 papers/T5_2019/ (完整档案)
```

---

### 示例3：快速触发方式

**方式1：直接提供URL**
```
https://arxiv.org/pdf/1706.03762
```

**方式2：明确指令**
```
解读这篇论文 https://arxiv.org/pdf/1706.03762
```

**方式3：使用skill命令**
```
/qiaomu-paper-interpreter https://arxiv.org/pdf/1706.03762
```

---

## 输出示例

### 元数据文件（metadata.json）

```json
{
  "paper_id": "Transformer_2017",
  "title": "Attention Is All You Need",
  "year": "2017",
  "authors": [
    "Ashish Vaswani",
    "Noam Shazeer",
    "Niki Parmar",
    "Jakob Uszkoreit",
    "Llion Jones",
    "Aidan N. Gomez",
    "Lukasz Kaiser",
    "Illia Polosukhin"
  ],
  "source_url": "https://arxiv.org/pdf/1706.03762",
  "extracted_at": "2025-12-23T17:05:00",
  "original_filename": "1706.03762.pdf"
}
```

### 图表列表（figure_list.md）

```markdown
## Figure 1 (第3页)
![Figure 1](images/Transformer_2017_figure1.png)

## Figure 2 (第4页)
![Figure 2](images/Transformer_2017_figure2.png)

## Table 1 (第6页)
![Table 1](images/Transformer_2017_table1.png)

## Table 2 (第8页)
![Table 2](images/Transformer_2017_table2.png)
```

### 配图配置（visual_config.json）

```json
{
  "article_title": "Transformer论文_解读",
  "sections": [
    {
      "h2_title": "旧世界的问题",
      "visual_description": "工厂流水线场景，8个工人站成一排，只有第一个工人在忙碌工作，其余7人无所事事地等待，用黑白线条绘制，朱红色标注第一个工人",
      "caption": "七个GPU在等待",
      "core_point": "RNN必须串行处理，8个GPU只能排队等待"
    },
    {
      "h2_title": "注意力的魔法",
      "visual_description": "图书馆场景，中央有一个目录检索台，多条虚线连接到不同书架上亮起的书本，展示Query-Key-Value匹配机制",
      "caption": "查询、匹配、获取",
      "core_point": "Query-Key-Value机制：查询匹配，直接定位相关信息"
    }
  ]
}
```

---

## 常见使用场景

### 场景1：学习新论文
**需求**：快速理解一篇复杂的学术论文
**操作**：提供PDF URL
**输出**：通俗易懂的解读文章 + 完整档案

### 场景2：准备分享内容
**需求**：把论文改写成公众号文章
**操作**：指定"用乔木风格解读"
**输出**：带配图的完整文章，可直接发布

### 场景3：建立论文库
**需求**：系统化管理多篇论文
**操作**：依次解读多篇论文
**输出**：
```
papers/
├── Transformer_2017/
├── BERT_2018/
├── GPT3_2020/
└── T5_2019/
```

每篇论文都有完整的元数据、原图、解读

### 场景4：深度研究
**需求**：详细分析论文的实验数据
**操作**：解读后，查看`images/`目录的所有图表
**输出**：所有Figure和Table的高清截图

---

## 性能指标

| 指标 | 数值 |
|------|------|
| 平均执行时间 | 4-6分钟 |
| 文章字数 | 8000-10000字 |
| 术语解释 | 15+处 |
| 生活化类比 | 5+处 |
| 论文图表提取 | 自动识别全部 |
| 纽约客配图 | 每个H2标题1张 |
| PDF文本提取准确率 | >95% |
| 图表提取成功率 | >90% |

---

## 优势总结

✅ **全自动**：无需手动干预，一键生成
✅ **高质量**：专业内容 + 通俗语言
✅ **完整归档**：PDF + 图表 + 元数据 + 解读
✅ **可复用**：所有资料规范化保存
✅ **可发布**：带配图，适合公众号
✅ **可扩展**：轻松建立论文知识库
