# 📁 文件位置规范

## 核心原则

**所有过程文件统一在工作目录，最终文章复制到阅读目录**

---

## 目录结构

### 工作目录：`20-29 学习/25 论文库/21.01 papers/{paper_id}/`

所有过程文件都在这里，完整保留论文档案：

```
20-29 学习/25 论文库/21.01 papers/LLM_Agents_2023/
├── source/
│   ├── LLM_Agents_2023.pdf          # 原始PDF
│   ├── metadata.json                 # 元数据
│   └── extracted_text.md             # 提取文本
│
├── images/                           # 原文图表
│   ├── LLM_Agents_2023_figure1.png
│   ├── LLM_Agents_2023_figure2.png
│   └── figure_list.md
│
├── illustrations/                    # AI生成配图
│   ├── 三个魔法组件.png
│   ├── 规划_会拆解任务的大脑.png
│   └── ...
│
├── work/                             # 临时文件
│   └── visual_config.json
│
└── 让AI像人一样思考_解读.md          # 最终文章（工作副本）
```

### 阅读目录：`20-29 学习/25 论文库/21.02 论文解读/`

最终文章复制到这里，方便阅读：

```
20-29 学习/25 论文库/21.02 论文解读/
├── 让AI像人一样思考_解读.md
├── 深度学习的本质_解读.md
└── ...
```

---

## 为什么这样设计？

✅ **工作目录保留完整档案**
- 原始PDF + 图表 + 配图全在一起
- 方便后续引用、修改、备份

✅ **阅读目录简洁清晰**
- 只有最终文章，无杂乱文件
- 统一位置，方便浏览和搜索

✅ **双份保留，互不干扰**
- 工作目录：完整资料，供深度使用
- 阅读目录：纯净文章，供快速阅读

---

## 脚本修改要点

所有涉及路径的脚本需要修改：

1. **extract_pdf_metadata.py**
   ```python
   BASE_DIR = "20-29 学习/25 论文库/21.01 papers"  # 固定
   ```

2. **generate_illustrations_v2.py**
   ```python
   # 输出到论文目录下的 illustrations/
   output_dir = f"{paper_dir}/illustrations"
   ```

3. **finalize_markdown.py**
   ```python
   # 最终文章复制到两个位置
   work_copy = f"{paper_dir}/{title}_解读.md"
   reading_copy = f"20-29 学习/25 论文库/21.02 论文解读/{title}_解读.md"
   ```

4. **visual_config.json**
   ```python
   # 生成在 work/ 子目录
   config_path = f"{paper_dir}/work/visual_config.json"
   ```

---

## 迁移清单

- [x] 创建 `20-29 学习/25 论文库/21.02 论文解读/` 目录
- [x] 移动现有文章到新位置
- [x] 清理根目录临时文件
- [ ] 修改脚本路径配置
- [ ] 更新 SKILL.md 说明
- [ ] 测试完整流程

---

详见：`FILE_MANAGEMENT.md` 完整设计文档
