# 故障排查指南

## 常见问题

### 1. PDF下载失败

**症状**：
```
错误：无法下载PDF
```

**可能原因**：
- arXiv服务器暂时不可用
- 网络连接问题
- URL格式错误

**解决方案**：
1. 检查URL格式是否正确（应为`https://arxiv.org/pdf/xxxx.xxxxx`）
2. 尝试在浏览器中打开URL，确认PDF可访问
3. 等待几分钟后重试
4. 如果仍失败，手动下载PDF并提供本地路径

---

### 2. 文本提取失败

**症状**：
```
错误：PDF文本提取失败
extracted_text.md 为空或乱码
```

**可能原因**：
- PDF是扫描版（纯图片）
- PDF有加密保护
- PDF格式损坏

**解决方案**：
1. 检查PDF是否可复制文本（在PDF阅读器中测试）
2. 如果是扫描版，Markitdown 支持 OCR（需要安装 tesseract）
3. 尝试手动转换：
   ```bash
   pip install pypdf
   # 修改scripts/extract_pdf_metadata.py使用pypdf
   ```

---

### 3. 图表提取失败

**症状**：
```
✗ 未找到 Figure X 在第 Y 页
图表截图不完整
```

**可能原因**：
- 论文中Figure标记格式不标准（如"Fig."、"FIGURE"）
- 图表位置计算错误
- 图表跨页

**解决方案**：

#### 问题A："未找到 Figure X"

检查PDF中的标题格式：
```python
# 常见变体
"Figure 1"   ✓ 支持
"Fig. 1"     ✓ 支持
"FIGURE 1"   ✗ 需要修改脚本
"Figure 1:"  ✗ 需要修改脚本
```

修改`scripts/extract_all_figures.py`：
```python
# 找到这行
pattern = r'(Figure|Fig\.)\s*(\d+)'

# 改为（添加更多变体）
pattern = r'(Figure|Fig\.|FIGURE|FIG\.)\s*(\d+):?'
```

#### 问题B：Table只截到文字没有表格

检查表格列标题关键词：
```python
# 默认关键词
table_keywords = ["Model", "Method", "Dataset", "Task", "Architecture"]

# 如果失败，检查PDF中表格第一行，添加到关键词
table_keywords.append("YourTableHeader")
```

#### 问题C：截图区域不完整

调整截取范围：
```python
# 在 scripts/extract_all_figures.py 中找到
y0 = caption_top - 500  # Figure向上500pt

# 改为更大的值
y0 = caption_top - 700  # 增加到700pt
```

---

### 4. 配图生成失败

**症状**：
```
⚠️ 即梦API失败
⚠️ Gemini API失败
❌ 生成失败: 所有API均失败
```

**可能原因**：
- 即梦API积分耗尽
- Gemini API服务暂时不可用
- 网络问题
- visual_description不够具体

**解决方案**：

#### 方案1：检查API配置
```bash
# 检查即梦API配置
echo $JIMENG_SESSION_ID

# 如果为空，配置它
export JIMENG_SESSION_ID="your_session_id"
```

#### 方案2：检查API状态
```bash
# 测试Gemini API
curl -X POST https://api.tu-zi.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemini-3-pro-image-preview","messages":[{"role":"user","content":"test"}]}'
```

#### 方案3：优化visual_description

❌ **太抽象**（生成失败）：
```json
{
  "visual_description": "用隐喻手法表现核心主题"
}
```

✅ **具体场景**（生成成功）：
```json
{
  "visual_description": "一座桥梁的横截面图，多层钢架结构相互支撑，信息像车流一样在桥面和下方钢架间流动，用黑白线条绘制主体结构，朱红色标注关键连接点"
}
```

#### 方案4：跳过配图生成

如果API持续失败，可以跳过此步骤：
- 文章解读仍然完整
- 只是缺少《纽约客》风格配图
- 论文原图（Figure/Table）仍会正常提取

---

### 5. 依赖安装问题

**症状**：
```
ModuleNotFoundError: No module named 'pdfplumber'
ModuleNotFoundError: No module named 'fitz'
```

**解决方案**：

#### 完整依赖安装
```bash
# 核心依赖
pip install pdfplumber pymupdf pillow requests

# 如果pymupdf安装失败
pip install --upgrade pip
pip install pymupdf --no-cache-dir

# 如果仍失败，使用conda
conda install -c conda-forge pymupdf
```

#### 依赖版本要求
```
pdfplumber >= 0.7.0
pymupdf >= 1.20.0
pillow >= 9.0.0
requests >= 2.28.0
```

---

### 6. 权限问题

**症状**：
```
Permission denied: papers/xxx/xxx.pdf
```

**解决方案**：
```bash
# 检查目录权限
ls -la papers/

# 修复权限
chmod -R 755 papers/
```

---

### 7. 磁盘空间不足

**症状**：
```
OSError: [Errno 28] No space left on device
```

**解决方案**：
```bash
# 检查磁盘空间
df -h

# 清理旧论文（如果不需要）
rm -rf papers/old_paper_*/

# 或者清理临时文件
rm -rf /tmp/*.pdf
```

---

## 图表提取详细排查

### Figure提取失败排查表

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| "未找到 Figure X" | PDF中的标题格式不匹配 | 检查PDF中是否为"Fig. X"或"FIGURE X"，修改脚本正则表达式 |
| 截图区域不完整 | 图表比默认范围更大 | 增大y0参数：500→700pt |
| 图表太小看不清 | 分辨率不够 | 修改Matrix参数：(2,2)→(3,3) |
| 截到了页眉页脚 | 边界框超出图表范围 | 减小y0向上的距离，增加精度 |
| Figure跨页 | 图表分布在两页 | 手动分别提取两部分 |

### Table提取失败排查表

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 只截到文字没有表格 | 搜索关键词失败 | 检查表格列标题，添加到关键词列表 |
| 表格不完整 | 表格较大 | 增大截取范围：300→500pt |
| 表格跨页 | 长表格分页显示 | 分别提取各页部分 |

---

## 性能优化建议

### 问题：执行时间过长

**优化方案**：

1. **跳过配图生成**（节省3-5分钟）
   - 如果只需要文字解读，可手动删除步骤5.5

2. **减少图表提取**（节省10-30秒）
   - 只提取关键图表
   - 在生成文章时减少图表引用

3. **使用更快的API**
   - 即梦API（10-20秒/张）优于Gemini（30-60秒/张）
   - 配置`JIMENG_SESSION_ID`环境变量

---

## 数据恢复

### 意外中断后的恢复

如果执行过程中中断（网络、断电等），可以从中间步骤继续：

```bash
# 检查已完成的步骤
ls papers/YourPaper_2024/

# 如果有extracted_text.md，跳过步骤0-1
# 如果有xxx_解读.md，跳过步骤0-2
# 如果有images/，跳过步骤0-5

# 手动执行剩余步骤
cd papers/YourPaper_2024
python ~/.claude/skills/qiaomu-paper-interpreter/scripts/finalize_markdown.py xxx_解读.md ../..
```

---

## 联系支持

如果以上方案都无法解决问题：

1. 查看详细日志（如果有）
2. 检查`CHANGELOG.md`确认版本
3. 查看`README.md`的已知问题列表
4. 提交Issue（如果skill在GitHub上）

---

## 调试模式

开启详细日志：
```bash
# 在脚本中添加调试输出
export DEBUG=1

# 运行skill
# 会显示详细的执行过程
```

查看中间文件：
```bash
# 检查提取的文本
cat papers/YourPaper_2024/extracted_text.md | head -100

# 检查图表列表
cat papers/YourPaper_2024/images/figure_list.md

# 检查配图配置
cat papers/YourPaper_2024/visual_config.json
```
