# 文件组织结构优化方案

## 当前问题诊断

### 问题1：图片路径混乱

**现状**：
```
AI不插电/
├── AI训练的自动挡：Adam优化器的故事.md  # 最终文章
├── images/illustrations/                  # Adam的配图
├── papers/
│   └── LSTM_1997/
│       ├── AI的长期记忆突破_解读.md      # 工作副本
│       └── images/illustrations/          # LSTM的配图
```

**问题**：
- 生成配图时使用相对路径 `images/illustrations/`
- finalize时移动文章到根目录，但没有同步更新图片路径
- 导致LSTM文章可能引用到Adam的配图

**根本原因**：
- `generate_illustrations_v2.py` 生成相对路径
- `finalize_markdown.py` 只移动文章，不处理图片路径

---

### 问题2：paper_id命名过长

**现状**：
```
papers/https___deeplearning_cs_cmu_edu_S23_document_readings_LSTM_pdf_1997/
```

**问题**：
- URL转换的ID太长，不易读
- 不符合人类直觉
- 路径引用复杂

---

### 问题3：中间产物和最终产物混杂

**现状**：
```
papers/LSTM_1997/
├── LSTM_1997.pdf                    # 原始PDF
├── extracted_text.md               # 中间产物
├── metadata.json                    # 元数据
├── visual_config.json               # 中间产物
├── 解读.md                          # 工作副本
└── images/
    ├── LSTM_1997_figure1.png       # 论文原图
    └── illustrations/
        └── illustration_1.png       # AI配图
```

**问题**：
- 中间产物（extracted_text.md, visual_config.json）和资源文件混在一起
- 图片分散在两个目录
- 不清楚哪些是交付物，哪些是临时文件

---

## 优化方案

### 方案A：完全分离式（推荐）

```
AI不插电/
├── 📄 最终文章（根目录）
│   ├── AI的长期记忆突破：LSTM如何让神经网络记住过去.md
│   └── AI训练的自动挡：Adam优化器的故事.md
│
└── 📁 papers/
    ├── LSTM_1997/                          # 简化paper_id
    │   ├── 📦 source/                      # 源文件
    │   │   ├── paper.pdf                   # 原始PDF（固定名）
    │   │   ├── metadata.json               # 元数据
    │   │   └── extracted_text.md          # 提取的文本
    │   │
    │   ├── 🔨 workspace/                   # 工作区（中间产物）
    │   │   ├── draft.md                    # 工作副本
    │   │   └── visual_config.json          # 配图配置
    │   │
    │   └── 🖼️  assets/                     # 资源文件
    │       ├── paper_figures/              # 论文原图
    │       │   ├── figure_1.png
    │       │   ├── figure_2.png
    │       │   └── table_1.png
    │       └── illustrations/              # AI生成配图
    │           ├── illustration_1.png
    │           └── illustration_2.png
    │
    └── Adam_2014/
        └── ...
```

**路径规则**：
- 最终文章中的图片路径：`papers/{paper_id}/assets/illustrations/illustration_1.png`
- 论文原图路径：`papers/{paper_id}/assets/paper_figures/figure_1.png`
- 所有路径都是从**根目录**开始的相对路径

**优点**：
- ✅ 结构清晰：source / workspace / assets 三层分离
- ✅ 路径可预测：统一的命名规则
- ✅ 完全隔离：不同论文之间零干扰
- ✅ 易于清理：中间产物在workspace，可随时删除

---

### 方案B：扁平式（简化版）

```
AI不插电/
├── AI的长期记忆突破：LSTM如何让神经网络记住过去.md
└── papers/
    └── LSTM_1997/
        ├── paper.pdf
        ├── metadata.json
        ├── _workspace/                 # 下划线开头表示临时
        │   ├── extracted_text.md
        │   ├── draft.md
        │   └── visual_config.json
        └── assets/
            ├── figures/                # 所有图片统一
            └── illustrations/
```

**优点**：
- ✅ 更扁平，层级少
- ✅ workspace用下划线标识，易识别
- ✅ 图片统一在assets下

**缺点**：
- ⚠️ 论文原图和AI配图不够分离

---

## 实施步骤

### 步骤1：优化 `extract_pdf_metadata.py`

**当前**：生成超长paper_id（URL式）

**改进**：
```python
def generate_paper_id(pdf_path, url=None):
    """
    智能生成简短、可读的paper_id

    规则：
    1. 从PDF元数据提取：{FirstAuthorLastName}_{Title关键词}_{Year}
    2. 如果失败，从文件名提取
    3. 确保唯一性（如果冲突，添加后缀_v2）

    示例：
    - Hochreiter_LSTM_1997
    - Kingma_Adam_2014
    - Vaswani_Transformer_2017
    """
    pass
```

### 步骤2：优化 `generate_illustrations_v2.py`

**当前**：生成相对路径 `images/illustrations/illustration_1.png`

**改进**：
```python
def generate_from_config_parallel(...):
    # 获取paper_id
    paper_id = markdown_path.parent.name

    # 生成完整相对路径（从根目录开始）
    image_rel_path = f"papers/{paper_id}/assets/illustrations/{image_filename}"

    # 插入到markdown
    insert_image_into_markdown(markdown_path, h2_title, image_rel_path)
```

### 步骤3：优化 `finalize_markdown.py`

**当前**：
- 只移动文章
- 删除H1

**改进**：
```python
def finalize_markdown(source_md, output_dir):
    """
    最终化markdown文件

    操作：
    1. 提取H1作为文件名
    2. 删除文章中的H1
    3. 确保所有图片路径正确（已经是完整相对路径）
    4. 保存到根目录
    5. 保留工作副本在workspace/
    """
    # 验证图片路径
    for img_path in extract_image_paths(content):
        if not Path(output_dir) / img_path).exists():
            print(f"⚠️  警告：图片不存在 {img_path}")

    # 保存最终版本
    ...
```

### 步骤4：优化 `extract_all_figures.py`

**改进**：
```python
def extract_all_figures(pdf_path, output_dir, prefix):
    """
    输出到统一的assets结构：

    assets/
    ├── paper_figures/
    │   ├── figure_1.png
    │   └── table_1.png
    └── illustrations/
        └── (稍后生成)
    """
    # 保存到 assets/paper_figures/
    output_path = output_dir / "paper_figures" / f"figure_{num}.png"
```

---

## 迁移现有文件

创建迁移脚本 `scripts/migrate_to_new_structure.py`：

```python
"""
将现有论文迁移到新结构

使用：
python migrate_to_new_structure.py papers/旧目录/ papers/新目录/
"""
```

---

## 配置文件

添加 `config.json` 到skill根目录：

```json
{
  "output_structure": "separated",  // "separated" or "flat"
  "paper_id_format": "short",       // "short" or "full"
  "asset_organization": "categorized",  // "categorized" or "unified"
  "paths": {
    "root": ".",
    "papers": "papers",
    "workspace_dir": "workspace",
    "assets_dir": "assets",
    "paper_figures": "paper_figures",
    "illustrations": "illustrations"
  }
}
```

---

## 质量检查清单

### 生成后自动检查

```bash
# 在finalize后执行
check_paper_output() {
  paper_id=$1

  # 1. 检查目录结构
  [ -d "papers/$paper_id/source" ] || echo "❌ source目录缺失"
  [ -d "papers/$paper_id/assets" ] || echo "❌ assets目录缺失"

  # 2. 检查必需文件
  [ -f "papers/$paper_id/source/paper.pdf" ] || echo "❌ PDF缺失"
  [ -f "papers/$paper_id/source/metadata.json" ] || echo "❌ 元数据缺失"

  # 3. 检查图片路径
  final_md=$(find . -maxdepth 1 -name "*$paper_id*.md")
  grep -o 'papers/[^)]*\.png' "$final_md" | while read path; do
    [ -f "$path" ] || echo "❌ 图片不存在: $path"
  done

  echo "✅ 结构检查完成"
}
```

---

## 优先级

### P0（立即实施）
- [ ] 修复 `generate_illustrations_v2.py` 的路径生成逻辑
- [ ] 修复 `finalize_markdown.py` 的路径验证

### P1（短期）
- [ ] 实现新的目录结构（方案A）
- [ ] 优化 paper_id 生成
- [ ] 添加结构验证脚本

### P2（长期）
- [ ] 迁移现有论文
- [ ] 添加配置文件支持
- [ ] 完善文档

---

**预期效果**：

✅ **确定性**：每个论文的路径完全可预测
✅ **隔离性**：不同论文零干扰
✅ **可维护性**：清晰的结构，易于理解和修改
✅ **健壮性**：自动验证，防止路径错误
