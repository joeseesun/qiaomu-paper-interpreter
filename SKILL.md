---
name: qiaomu-paper-interpreter
description: Transform academic papers into conversational Chinese articles in Qiaomu's style. Use when user provides arXiv URL/ID with keywords "解读论文", "论文解读", "理解paper", "读paper", or "乔木风格". Runs fully automatically.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, TodoWrite
---

# 乔木论文解读

## 概述

<<<<<<< HEAD
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
=======
将学术论文自动转化为乔木风格的深度解读文章。**全自动执行**，无需用户中途确认。

**核心特点**：
- 对话式语言，像和朋友聊天
- 关键术语用引用块（>）解释，每出现新术语立刻加
- 生活化类比帮助理解，每个核心方法后必须紧跟一个类比
- 真实论文图表嵌入文章（从 LaTeX 源码精确提取）
- AI 生成纸雕水彩封面 + 《纽约客》风格配图（需配置图片生成服务）
- 写作风格规范已内嵌，无需外部依赖

---

## 配置（首次使用必读）

### 配置方式：.env 文件

在 skill 目录下创建 `.env` 文件（已加入 `.gitignore`，不会被发布）：

```bash
# ~/.claude/skills/qiaomu-paper-interpreter/.env

PAPER_OUTPUT_DIR=~/Papers/papers
PAPER_READING_DIR=~/Papers/reading
OBSIDIAN_VAULT=
IMAGE_PROVIDER=skip
IMAGE_GENERATOR_SCRIPT=
```

**参考模板**：skill 目录下的 `.env.example` 包含所有可用变量及说明。

**变量说明**：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PAPER_OUTPUT_DIR` | `~/Papers/papers` | 论文工作目录根路径 |
| `PAPER_READING_DIR` | `~/Papers/reading` | 最终文章存放目录 |
| `OBSIDIAN_VAULT` | 空 | Obsidian vault 名称，空则跳过自动打开 |
| `IMAGE_PROVIDER` | `skip` | `skip`（跳过配图）/ `jimeng` / `openai` |
| `IMAGE_GENERATOR_SCRIPT` | 空 | 图片生成脚本路径，空则用内置默认 |

系统环境变量优先级高于 `.env` 文件，适合 CI/CD 或多项目场景。

### 配置读取逻辑（每次执行时运行）

```python
import os
from pathlib import Path

SKILL_DIR = Path("~/.agents/skills/qiaomu-paper-interpreter").expanduser()

# 1. 读取 .env 文件（如果存在）
env_file = SKILL_DIR / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            # 系统环境变量优先，.env 不覆盖已设置的值
            os.environ.setdefault(k.strip(), v.strip())

# 2. 读取最终配置（含默认值兜底）
OUTPUT_DIR    = Path(os.environ.get("PAPER_OUTPUT_DIR",    "~/Papers/papers")).expanduser()
READING_DIR   = Path(os.environ.get("PAPER_READING_DIR",   "~/Papers/reading")).expanduser()
OBSIDIAN_VAULT = os.environ.get("OBSIDIAN_VAULT", "")
IMAGE_PROVIDER = os.environ.get("IMAGE_PROVIDER", "skip")   # skip | jimeng | openai
IMAGE_GENERATOR_SCRIPT = os.environ.get("IMAGE_GENERATOR_SCRIPT", "")

# 图片生成脚本默认路径
if not IMAGE_GENERATOR_SCRIPT and IMAGE_PROVIDER != "skip":
    IMAGE_GENERATOR_SCRIPT = str(
        Path("~/.agents/skills/qiaomu-image-generator/scripts/generate.py").expanduser()
    )
```

---

## 执行流程（4步）

**顺序**：步骤A → 步骤B → 步骤C → 步骤D

**执行原则**：全程自动，用 TodoWrite 显示进度，静默修复质量问题。

### 初始化 Todo

```python
TodoWrite([
    {"content": "A. 提取论文内容 + 并发转换图片", "status": "in_progress"},
    {"content": "B. 生成乔木风格解读文章", "status": "pending"},
    {"content": "C. 生成 AI 配图（封面 + 纽约客）", "status": "pending"},
    {"content": "D. 保存发布", "status": "pending"},
>>>>>>> 3f6d27c (Initial release: qiaomu-paper-interpreter v1.2.1)
])
```

---

<<<<<<< HEAD
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

=======
## 步骤A：提取论文内容 + 并发转换图片

**目标**：一次完成 LaTeX 提取、元数据解析、图片并发转换、图表清单生成。

### A1. 确定 arxiv_id

支持输入格式：

| 输入 | 处理方式 |
|------|---------|
| `https://arxiv.org/abs/2605.03269` | 直接提取 ID |
| `https://arxiv.org/pdf/2605.03269` | 直接提取 ID（和 abs 等价） |
| `https://arxiv.org/pdf/2605.03269v2` | 提取 ID，保留版本号 |
| `https://huggingface.co/papers/2605.03269` | 先 WebFetch 页面找 arXiv 链接，再提取 ID |
| `2605.03269` | 直接作为 ID 使用 |

**内部流程**：extract_tex.py 拿到 ID 后，从 `https://arxiv.org/e-print/{id}` 下载 LaTeX 源码 tar.gz，自动解压，找 main.tex，提取结构化内容和图片。

**如果论文没有 LaTeX 源码（PDF-only）**：
`e-print` 返回 PDF 而不是 tar.gz，extract_tex.py 会返回 `has_source: false`。此时自动切换到 markitdown fallback：
```bash
markitdown "https://arxiv.org/pdf/{arxiv_id}" -o "{paper_dir}/extracted_text.md"
```
fallback 情况下无法提取真实图表，figure_list.md 标注"LaTeX 源码不可用"，文章中用文字描述代替图片引用。

### A2. 并发启动：extract_tex.py + arXiv API（含断点续跑）

**断点续跑**：如果 `extract_result.json` 已存在且有效，直接跳过下载，从 A3 继续。适用于崩溃重试场景。

```python
import subprocess, threading, urllib.request, re, time, json
from pathlib import Path

# ── 断点续跑检测 ──
# 检查是否有已完成的 paper_id 目录（paper_id 此时尚未确定，用 arxiv_id 查找）
existing = list(OUTPUT_DIR.glob(f"*{arxiv_id.replace('.', '_')}*"))
_resume_dir = next((d for d in existing
                    if (d / "extract_result.json").exists()
                    and (d / "extract_result.json").stat().st_size > 100), None)

if _resume_dir:
    paper_dir = _resume_dir
    result_file = paper_dir / "extract_result.json"
    print(f"⚡ 断点续跑：跳过下载，使用 {paper_dir.name}")
    arxiv_meta = {}   # 仍需 API 获取日期，下面会并发请求
    _skip_extract = True
else:
    paper_dir = OUTPUT_DIR / f"tmp_{int(time.time())}"
    paper_dir.mkdir(parents=True, exist_ok=True)
    result_file = paper_dir / "extract_result.json"
    _skip_extract = False

# ── 线程1：并发请求 arXiv API（⚠️ 发布日期严禁猜测，只用此处返回值）──
arxiv_meta = {}
def fetch_arxiv_meta():
    try:
        xml = urllib.request.urlopen(
            f"http://export.arxiv.org/api/query?id_list={arxiv_id}", timeout=10
        ).read().decode()
        m = re.search(r'<published>(.*?)</published>', xml)
        arxiv_meta["published_date"] = m.group(1)[:10] if m else ""
        # ⚠️ 必须从 <entry> 内提取，xml 第一个 <title> 是 feed 标题，不是论文标题
        entries = re.findall(r'<entry>(.*?)</entry>', xml, re.DOTALL)
        entry = entries[0] if entries else ""
        t = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
        arxiv_meta["title"] = t.group(1).strip().replace('\n', ' ') if t else ""
        arxiv_meta["authors"] = re.findall(r'<name>(.*?)</name>', entry)
    except Exception:
        arxiv_meta["published_date"] = ""

meta_thread = threading.Thread(target=fetch_arxiv_meta, daemon=True)
meta_thread.start()

# ── 线程2（主线程）：运行 extract_tex.py，120s 超时 ──
if not _skip_extract:
    try:
        proc = subprocess.run(
            ["python3",
             str(Path("~/.agents/skills/qiaomu-markdown-proxy/scripts/extract_tex.py").expanduser()),
             arxiv_url_or_id, "--json", "--output-dir", str(paper_dir / "latex_source")],
            capture_output=True, text=True, timeout=120
        )
        result_file.write_text(proc.stdout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        print("⚠️ extract_tex.py 超时（>120s），切换 markitdown fallback")
        proc = None

meta_thread.join(timeout=5)
```

> 依赖 `qiaomu-markdown-proxy` skill 中的 `extract_tex.py`。如未安装，见常见问题处理。

### A3. 解析 JSON，失败检测 + 合并 arXiv 元数据

```python
import os

# ── 失败检测：空输出或无 JSON → 切 markitdown fallback ──
raw = result_file.read_text(encoding="utf-8") if result_file.exists() else ""
json_start = raw.find('{')

if json_start == -1 or len(raw.strip()) < 50:
    print("⚠️ extract_tex.py 输出无效，切换 markitdown fallback")
    import subprocess as _sp
    _sp.run(["markitdown", f"https://arxiv.org/pdf/{arxiv_id}",
             "-o", str(paper_dir / "extracted_text.md")], check=False)
    data = {}
    figures = []
else:
    try:
        data = json.loads(raw[json_start:])
    except json.JSONDecodeError:
        print("⚠️ JSON 解析失败，切换 markitdown fallback")
        import subprocess as _sp
        _sp.run(["markitdown", f"https://arxiv.org/pdf/{arxiv_id}",
                 "-o", str(paper_dir / "extracted_text.md")], check=False)
        data = {}
        figures = []

title    = data.get("title", "") or arxiv_meta.get("title", "")
authors  = data.get("authors", []) or arxiv_meta.get("authors", [])
arxiv_id = data.get("arxiv_id", arxiv_id)
markdown = data.get("markdown", "")
figures  = data.get("media", {}).get("figures", figures if 'figures' in dir() else [])
published_date = arxiv_meta.get("published_date", "")
```

# 生成 paper_id（代码化，避免每次结果不一致导致重名）
def make_paper_id(title: str, pub_date: str) -> str:
    year = pub_date[:4] if pub_date else "0000"
    # 提取全大写缩写词（长度 2-6），如 BERT、MACE、VL
    abbrevs = re.findall(r'\b[A-Z]{2,6}\b', title)
    if abbrevs:
        return f"{'_'.join(abbrevs[:2])}_{year}"
    # 否则取前 3 个英文关键词（跳过冠词介词）
    skip = {'a','an','the','of','for','on','in','to','and','or','with','via'}
    words = [w for w in re.findall(r'[a-zA-Z]+', title) if w.lower() not in skip]
    slug = "_".join(w.capitalize() for w in words[:3])
    return f"{slug}_{year}"

paper_id = make_paper_id(title, published_date)

# 重命名临时目录（如已存在则加后缀避免冲突）
new_dir = OUTPUT_DIR / paper_id
if new_dir.exists():
    new_dir = OUTPUT_DIR / f"{paper_id}_2"
os.rename(paper_dir, new_dir)
paper_dir = new_dir

# 保存文本和元数据
(paper_dir / "extracted_text.md").write_text(markdown, encoding="utf-8")
(paper_dir / "metadata.json").write_text(
    json.dumps({
        "paper_id": paper_id, "title": title, "authors": authors,
        "arxiv_id": arxiv_id,
        "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
        "published_date": published_date,
    }, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
```

### A4. 并发转换图片

**过滤规则**：跳过 >20MB 的图（多页定性对比图，不适合放博客）；其余全部转换。

```python
import concurrent.futures, subprocess, shutil

(paper_dir / "images").mkdir(exist_ok=True)

def convert_figure(fig):
    idx   = fig["index"]
    raw_src = fig["local_files"][0] if fig.get("local_files") else None
    if not raw_src:
        return None

    # local_files 可能是相对路径或绝对路径，逐级尝试
    latex_dir = paper_dir / "latex_source"
    candidates = [
        Path(raw_src),                              # 原始路径（绝对）
        latex_dir / raw_src,                        # 相对于 latex_source/
        latex_dir / Path(raw_src).name,             # 只取文件名，在 latex_source/ 下找
    ] + list(latex_dir.glob(f"**/{Path(raw_src).name}"))  # 递归搜索

    src = next((p for p in candidates if p.exists()), None)
    if not src:
        return None

    caption = fig.get("caption", "")
    words   = re.findall(r'[a-zA-Z]+', caption)[:3]
    slug    = "_".join(w.lower() for w in words) or "fig"
    dst     = paper_dir / "images" / f"figure{idx}_{slug}.png"

    ext = Path(src).suffix.lower()
    size_mb = Path(src).stat().st_size / 1024 / 1024

    if ext == ".pdf":
        if size_mb > 20:
            return {"index": idx, "skipped": True,
                    "reason": f"超大图({size_mb:.0f}MB)", "caption": caption}
        r = subprocess.run(
            ["pdftoppm", "-r", "150", "-png", "-singlefile", src, str(dst)[:-4]],
            capture_output=True
        )
        if r.returncode != 0 or not dst.exists():
            subprocess.run(["convert", "-density", "150", f"{src}[0]", str(dst)])
    elif ext in (".eps", ".ps"):
        subprocess.run(["convert", "-density", "150", src, str(dst)])
    elif ext in (".png", ".jpg", ".jpeg", ".gif"):
        shutil.copy2(src, dst)

    if not dst.exists():
        return {"index": idx, "skipped": True, "reason": "转换失败", "caption": caption}

    return {"index": idx, "file": str(dst),
            "filename": dst.name, "caption": caption,
            "size_kb": dst.stat().st_size // 1024}

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(convert_figure, figures))

converted = [r for r in results if r and not r.get("skipped")]
skipped   = [r for r in results if r and r.get("skipped")]
```

### A5. 生成 figure_list.md

```markdown
# 论文图表清单

## 可用图表（建议全部引用）

| 编号 | 文件 | 大小 | Caption 摘要 | 建议章节 |
|------|------|------|-------------|---------|
| Figure 1 | figure1_teaser.png | 2.1MB | 整体效果展示 | 开头引入 |
| Figure 2 | figure2_overview.png | 746KB | 系统架构图 | 方法解读 |
| ...

## 跳过的图

| 编号 | 原因 | Caption 摘要 |
|------|------|-------------|
| Figure 3 | 超大图(84MB) | 定性对比图 |
```

**完成后**：更新 Todo A 为 completed，B 为 in_progress。

---

## 步骤B：生成乔木风格解读文章

### B0. 写作前准备（必须完整执行）

**第一步：读取完整论文内容 + 当前日期**

```python
import datetime

# 读取 A 步骤提取的完整正文（不能只靠记忆，必须重新读取）
paper_text = (paper_dir / "extracted_text.md").read_text(encoding="utf-8")
figure_list = (paper_dir / "figure_list.md").read_text(encoding="utf-8")
metadata = json.loads((paper_dir / "metadata.json").read_text(encoding="utf-8"))

# 读取当前日期，用于计算论文发布至今的时间跨度
today = datetime.date.today()   # e.g. 2026-05-12
pub_date = metadata.get("published_date", "")
years_since = (today.year - int(pub_date[:4])) if pub_date else 0
print(f"论文发布于 {pub_date}，距今 {years_since} 年（{today}）")
```

**当前日期的用途**：
- 在"写在后面"中具体说出"这篇论文发表于 X 年，距今 Y 年"，不用模糊说"几年前"
- 主动调用训练知识，找出这篇论文**发布后出现的重要后继工作**：哪些论文直接引用并发展了它的思路？哪些产品落地了它的方法？
- 如果论文发布时间超过 2 年，必须在"写在后面"或相关章节自然提到后续影响（不是列表，而是融入正文），例如"2 年后 Stable Diffusion 用的正是 CLIP 做图文对齐"这样的具体陈述
- 知识截止日期内未发生的事不要猜测，只写确实知道的

**第二步：自动判断是否为里程碑论文（决定字数下限）**

```python
LANDMARK_KEYWORDS = {
    # NLP / LLM
    "transformer", "attention is all you need",
    "bert", "gpt", "gpt-2", "gpt-3", "gpt-4",
    "rlhf", "reinforcement learning from human feedback",
    "instruct", "instructgpt",
    "chain-of-thought", "chain of thought",
    "in-context learning", "scaling laws",
    "codex", "alphacode", "word2vec", "seq2seq",
    # 多模态 / 生成
    "clip", "dall-e", "imagen", "stable diffusion",
    "diffusion", "ddpm", "gan", "generative adversarial",
    "vae", "variational autoencoder",
    # CV 骨干网络
    "resnet", "vit", "vision transformer",
    "alexnet", "vgg", "googlenet", "inception",
    "densenet", "efficientnet", "mobilenet",
    "batch normalization",
    # 视频理解
    "two-stream", "two stream", "i3d", "slowfast",
    "optical flow", "action recognition",
    # 检测 / 分割
    "faster rcnn", "yolo", "mask rcnn", "detr",
    "feature pyramid", "fpn",
    # 优化 / 训练技巧
    "lora", "dropout", "adam optimizer",
    "knowledge distillation",
    # 强化学习
    "dqn", "alphago", "ppo", "proximal policy",
}
title_lower = metadata.get("title", "").lower()
is_landmark = any(kw in title_lower for kw in LANDMARK_KEYWORDS)
min_words = 8000 if is_landmark else 5000
print(f"{'⭐ 里程碑论文' if is_landmark else '普通论文'}，字数下限：{min_words} 字")
```

**第三步：阅读写作规范**（见下方 B0 写作风格）

---

### B0. 乔木写作风格（内嵌，无需读取外部文件）

#### 语言特质
- 口语化、对话感强，像和读者面对面聊天
- 用"你"直接称呼读者
- **生活化类比触发规则**：每讲完一个核心方法/设计决策的技术解释后，**必须**紧跟一个类比段落，用日常生活中的场景说明"这就像……"。全文 ≥ 3 处，分散在不同章节
- 在专业性和可读性之间自然平衡

#### 表达习惯
- 短段落，多留白，视觉舒适
- 重要观点用 **加粗**，加粗句必须单独成段，不和其他句子同处一段
- 加粗句之前和之后都留空行
- **引用块触发规则**：每当文章中出现一个新的专有名词、技术术语、缩写时，**立刻**在其后加引用块解释，不要等写完再补。格式：`> **术语**：一句话解释`。全文累计 ≥ 10 处
- 冒号后接长内容，冒号后另起段落
- 三条以上并列经验，用列表

#### 内容层次
- 不满足于表面解释，延伸到更深的思考
- 善于在不同领域间建立联系（技术→生活→认知）
- 既讲"是什么"，也讲"为什么重要"
- 每段通过「增量信息测试」：这段提供了前面没有的新信息吗？

#### 风格调性
- 真诚、不装、承认自己的困惑
- 专业但不掉书袋，数据和案例支撑观点
- 批判性反思融入正文流，不辟独立章节

#### 让文章"生动有趣"的具体技法（每篇至少用 3 种）

1. **开头用悬念或反直觉事实**：不是"本文提出了X方法"，而是"2014 年，有一件让所有人困惑的事……"或"你可能不知道，深度学习曾经有整整两年打不过一个叫做'密集轨迹'的老方法"

2. **写研究者的困境和直觉**：不只说方法，要写"为什么他们会想到这个"。如果能推测研究者当时的思路（有据可查），大胆写出来

3. **反事实推理**：在讲完一个设计决策后，追问"如果不这样做会怎样"。例如"如果只用空间流，会发生什么？实验数据告诉我们：准确率从 88% 掉到 72.6%，整整少了 15 个点"

4. **具体化数字场景**：把抽象数字变成可感受的场景。"20 个百分点的差距，意味着什么？意味着每 5 个动作里，深度学习就要比手工方法多认错 1 个"

5. **图片叙事**：不只是插图，要描述图里能看到什么、这说明了什么。"看这张第一层卷积核的图，你会发现它们大多是方向性的滤波器……这不是巧合，这是网络自己学出来的，它发现光流场里最重要的信息就是方向"

6. **人物和机构背景**（仅限有公开信息的内容）：Simonyan 和 Zisserman 是同一个 VGG 组的，他们几个月后发表了 VGGNet——两篇论文是同期的工作。这个细节本身就是故事

7. **历史节点感**：点明这篇论文发表的时刻在历史上的意义。"这是深度学习在视频动作识别上第一次赢过手工特征——在 2014 年，这句话的分量不亚于 AlexNet 横空出世"

---

### B1. 硬性禁止清单（写完必须逐条自检）

| 禁止项 | 上限 | 替换方式 |
|--------|------|---------|
| 破折号（——） | **0 个** | 逗号、句号、冒号 |
| 总之 / 综上所述 / 综上 | **0 个** | 直接写结论 |
| 让我们 / 让我们来拆解 | **0 个** | 直接陈述 |
| 关键在于 / 关键来了 | **0 个** | 直接说关键点 |
| 想象一个世界 | **0 个** | — |
| 不是X而是Y | 最多 1 次 | — |
| 值得注意的是 / 重要的是 / 有趣的是 | **0 个** | 删掉，直接说 |
| delve / landscape / tapestry / robust / leverage | **0 个** | 用简单词 |
| 结尾写"总结" / 总结一下 | **0 个** | 画面或问题收尾 |
| 每个列表项都粗体开头 | **禁止** | 粗体只用于真正重点 |
| 碎片式短句独立成段制造假强调 | **禁止** | 合并为一句 |
| 预告式渲染："最震撼的部分"/"一针见血" | **禁止** | 删掉，直接呈现内容 |

### B2. 文章结构

文章由两部分组成：**正文**（主体解读）+ **写在后面**（意义总结）。

#### 正文结构

```
1. 开头场景引入（不直接说"这篇论文..."，用具体场景）
2. 核心问题（这件事难在哪？）
3. 方法解读（每个核心贡献一个 H2 节）
   - 是什么 → 为什么这么设计 → 生活化类比（必须有）
   - 新术语出现立刻加引用块
   - 插入对应论文原图
4. 数据表格（核心实验结果，加粗最佳值）
```

**字数要求**：
- 普通方法论论文：≥ 5000 汉字
- 里程碑论文：≥ 8000 汉字
- **由 B0 第二步的 `is_landmark` 自动判断**，覆盖关键词见上方列表
- **写完必须自检**：`grep -oP '[\x{4e00}-\x{9fff}]' article.md | wc -l`，低于 `min_words` 则继续扩充，不得以"文章完成"为由停笔

**每个 H2 节必须包含的四要素（缺一不可）**：
1. **技术解释**：这个设计是什么，为什么这样设计（不只是"是什么"）
2. **生活化类比**：用日常场景说明这个技术决策，每节 ≥ 1 个，全文 ≥ 3 个
3. **论文原图**：插入对应 figure，并用 1-2 句话解释图里能看到什么
4. **意义追问**：这个设计决策解决了什么根本矛盾？如果不这样做会怎样？

**历史现场要求**（论文发表 > 2 年时强制）**：
- 在"核心问题"节或第一个 H2 节中，必须描述该论文发表时领域的具体状态：当时最强的方法是什么、准确率是多少、为什么大家认为这是极限
- 用具体数字说话，不说"当时方法不好"，要说"当时最好的方法只有 X%，而手工特征达到 Y%，差了 Z 个百分点"
- 至少提及 1 个这篇论文发表前的代表性工作作为对照基准

**影响链要求**（写在后面）**：
- 必须追溯 ≥ 2 篇直接建立在本论文基础上的后续工作，用具体年份和改进点说明
- 格式参考："3 年后，X 团队的 Y 论文把这个思路扩展到……，准确率提升到……"
- 禁止只说"影响了后来的研究"，必须说出具体是哪篇论文、做了什么改变

#### 写在后面（必须包含，放文章末尾正文之前）

这一节用来帮读者建立全局视角，回答三个问题：

1. **这篇论文在历史上的位置**：它出现之前，领域是什么状态？它改变了什么？有没有引发范式转变？
2. **为什么今天还值得读**：三五年后的今天，它的影响落地在哪里？读者每天接触的哪些产品或工具源于此？
3. **给读者的一条启示**：不是鸡汤，而是从这篇论文的思路中提炼出的一个可迁移的思维方式或方法论。

**格式规范**：
- 用 `## 写在后面` 作为节标题
- 300-500 字，不要超过 500 字
- 语气比正文更私人，更像作者自己的感受
- 结尾用一个具体的画面或开放性问题收尾，不用"总结"句式
- 禁止破折号、禁止"总之"、禁止列清单

**示例框架**（不要照抄，按实际论文情况写）**：
```
2021年这篇论文发表时，大多数人还在用…（具体场景）。

Codex 的出现改变了一件事：…（核心改变，具体说）。

但更有意思的是…（从论文思路提炼的方法论洞察）。

现在回头看，…（今天的影响落点）。

（结尾画面或问题）
```

#### 结尾升华（紧接"写在后面"之后）

用一个让读者脑子停不下来的画面、故事或问题作为最后一段，不归纳、不总结。

**完整顺序**：
```
论文信息引用块（开头）→ 正文主体 → ## 写在后面 → 结尾升华段落 → 论文信息引用块（末尾）
```

#### 论文信息引用块（**开头和末尾各放一次**，固定格式）

- **开头**：紧跟在 H1 标题之后，正文第一段之前。让读者一眼看到论文出处。
- **末尾**：文章最后，分隔线之后。方便从中间读进来的读者溯源。

所有字段均来自 `metadata.json`，**禁止凭记忆填写**。

⚠️ **换行规则**：每行之间必须加空的 `>` 行，否则 Markdown 渲染器会把所有行合并成一段：

```markdown
> **论文原文**：{完整英文标题}
>
> **arXiv**：https://arxiv.org/abs/{arxiv_id}
>
> **发布日期**：{published_date}
>
> **作者**：{前三位作者} et al.（{机构}）
```

末尾版本前加一条分隔线 `---`。

注意：
- 不要在发布日期后加任何括号注释（如"来自 arXiv API，非推测"），直接写日期即可
- 如果 `published_date` 为空，写 `未能获取` 即可，不要猜测

### B3. 图片引用策略

**原则：所有已成功转换的图，都应在文章中找到对应位置引用。**

1. 读取 `figure_list.md`，了解所有可用图及其建议章节
2. 写每个章节时，主动匹配并插入对应图片
3. 不要集中堆放，每张图紧跟在最相关的段落之后

**引用格式（相对路径，方便本地预览）**：
```markdown
![图2：系统架构](images/figure2_overview.png)
```

**图片-章节映射参考**：
- teaser / result 展示图 → 开头引入或结尾
- overview / architecture 图 → 方法总览节
- 模块细节图 → 对应具体方法节
- comparison / ablation 图 → 实验数据节
- user study / visualization → 数据分析节

### B4. 写作后自检（必须执行，不合格必须修改后才能保存）

```python
import re

text = open(article_path, encoding="utf-8").read()
chinese_count = len(re.findall(r'[\u4e00-\u9fff]', text))

checks = [
    (len(re.findall(r'——', text)) == 0,         f"破折号: {len(re.findall(r'——', text))} 个（必须为0）"),
    (len(re.findall(r'总之|综上|让我们|关键在于|值得注意', text)) == 0,
                                                 "禁用词检查（必须为0）"),
    (len(re.findall(r'> \*\*', text)) >= 10,    f"术语引用块: {len(re.findall(r'> \*\*', text))} 个（≥10）"),
    (len(re.findall(r'!\[', text)) >= 3,        f"图片引用: {len(re.findall(r'!\[', text))} 张（≥3）"),
    ('## 写在后面' in text,                      "写在后面节（必须有）"),
    (text.count('> **论文原文**') >= 2,          "论文信息引用块（开头+末尾各一次，共2次）"),
    (chinese_count >= min_words,                 f"汉字数: {chinese_count}（要求 ≥ {min_words}）"),
]

all_pass = True
for ok, msg in checks:
    status = "✅" if ok else "❌"
    print(f"{status} {msg}")
    if not ok:
        all_pass = False

if not all_pass:
    print("\n⚠️ 自检未通过，继续补充修改，不得保存！")
    # 字数不足时：继续写，展开已有章节，或新增"背景"/"技术细节"/"消融实验"节
else:
    print(f"\n✅ 自检通过，汉字数 {chinese_count}，保存文章")
```

**保存到** `{paper_dir}/{中文标题}_解读.md`

**完成后**：更新 Todo B 为 completed，C 为 in_progress。

---

## 步骤C：生成 AI 配图

**前提**：`IMAGE_PROVIDER != "skip"`，否则跳过本步骤，直接进入步骤D。

### C1. 封面图

提炼 1-3 个核心关键词（如 `MACE 音乐驱动舞蹈 级联专家`）：

```bash
mkdir -p "{paper_dir}/illustrations"

# 生成封面配置
cat > "{paper_dir}/illustrations/visual_config_cover.json" << EOF
{
  "task_id": "cover_{paper_id}",
>>>>>>> 3f6d27c (Initial release: qiaomu-paper-interpreter v1.2.1)
  "cover": {
    "enabled": true,
    "filename": "cover.png",
    "style": "paper-watercolor-cover",
    "aspect_ratio": "16:9",
<<<<<<< HEAD
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
=======
    "description": "{关键词1} {关键词2} {关键词3}"
  },
  "illustrations": [],
  "defaults": {
    "style": "paper-watercolor-cover",
    "provider": "{IMAGE_PROVIDER}",
    "retry_count": 2
  }
}
EOF

python "{IMAGE_GENERATOR_SCRIPT}" \
  "{paper_dir}/illustrations/visual_config_cover.json" --workers 1

# 插入文章开头
python3 -c "
content = open('{article_path}').read()
open('{article_path}', 'w').write('![封面](illustrations/cover.png)\n\n' + content)
"
```

### C2. 纽约客配图（3线程并发）

为每个主要 H2 节设计 visual_description（50-80字中文，具象场景隐喻抽象概念，不写风格指令）：
>>>>>>> 3f6d27c (Initial release: qiaomu-paper-interpreter v1.2.1)

```json
{
  "task_id": "illustrations_{paper_id}",
<<<<<<< HEAD
  "template": "paper",
  "source": "{paper_dir}/{标题}_解读.md",
  "output_dir": "{paper_dir}/illustrations",
=======
>>>>>>> 3f6d27c (Initial release: qiaomu-paper-interpreter v1.2.1)
  "cover": { "enabled": false },
  "illustrations": [
    {
      "id": "01",
<<<<<<< HEAD
      "h2_title": "H2标题",
      "visual_description": "50-80字中文具体场景描述",
      "filename": "01-slug.png"
    },
    {
      "id": "02",
      "h2_title": "H2标题",
      "visual_description": "50-80字中文具体场景描述",
      "filename": "02-slug.png"
=======
      "h2_title": "对应H2标题",
      "visual_description": "50-80字具象场景描述",
      "filename": "01-slug.png"
>>>>>>> 3f6d27c (Initial release: qiaomu-paper-interpreter v1.2.1)
    }
  ],
  "defaults": {
    "style": "newyorker",
<<<<<<< HEAD
    "provider": "jimeng",
=======
    "provider": "{IMAGE_PROVIDER}",
>>>>>>> 3f6d27c (Initial release: qiaomu-paper-interpreter v1.2.1)
    "retry_count": 2
  }
}
```

<<<<<<< HEAD
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
=======
```bash
python "{IMAGE_GENERATOR_SCRIPT}" \
  "{paper_dir}/illustrations/visual_config.json" --workers 3
```

**完成后**：更新 Todo C 为 completed，D 为 in_progress。

---

## 步骤D：保存 + 打开

### D1. 复制到阅读目录

```python
import shutil
from pathlib import Path

article_path = paper_dir / f"{chinese_title}_解读.md"
images_dir   = paper_dir / "images"
dest_dir     = READING_DIR
dest_images  = dest_dir / f"{paper_id}_images"

dest_dir.mkdir(parents=True, exist_ok=True)
dest_images.mkdir(parents=True, exist_ok=True)

# 复制文章，更新图片路径为新的相对路径
content = article_path.read_text(encoding="utf-8")
content = content.replace("images/", f"{paper_id}_images/")
(dest_dir / article_path.name).write_text(content, encoding="utf-8")

# 复制图片
if images_dir.exists():
    for img in images_dir.glob("*.png"):
        shutil.copy2(img, dest_images / img.name)

print(f"已复制到: {dest_dir / article_path.name}")
```

### D2. 在 Obsidian 中打开（仅当 OBSIDIAN_VAULT 非空）

```python
import os, urllib.parse
from pathlib import Path

vault = os.environ.get("OBSIDIAN_VAULT", "")
if vault:
    reading_dir = Path(os.environ.get("PAPER_READING_DIR", "~/Papers/reading")).expanduser()
    dest_file = reading_dir / article_path.name
    # 计算相对于 vault 根目录的路径（Obsidian URI 需要 vault 内相对路径）
    vault_root = None
    for parent in dest_file.parents:
        if parent.name == vault:
            vault_root = parent
            break
    if vault_root:
        rel = dest_file.relative_to(vault_root)
        encoded = urllib.parse.quote(str(rel).replace(".md", ""), safe="/")
    else:
        # fallback: 只用文件名（去掉 .md）
        encoded = urllib.parse.quote(article_path.stem, safe="")
    uri = f"obsidian://open?vault={urllib.parse.quote(vault)}&file={encoded}"
    os.system(f'open "{uri}"')
```

### D3. 发布到博客

**触发条件**：用户输入包含"发布"/"博客"/"blog"/"post"时，本步骤必须自动执行，不询问用户。

上传本地图片并替换路径，然后发布（status 固定为 draft）：
```python
import json, re, subprocess
from pathlib import Path

TOKEN = open(Path("~/.claude/skills/qiaomu-blog-publish/config.json").expanduser()).read()
TOKEN = json.loads(TOKEN)["token"]

content = article_path.read_text(encoding="utf-8")
title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
title = title_match.group(1).strip()
body  = content[title_match.end():].lstrip('\n')

# 上传单张图片，带 retry（最多 2 次）
def upload_image(abs_path):
    # timeout=60 防止大图超时（870KB 图曾在 30s 内超时）
    for _ in range(2):
        r = subprocess.run(["curl", "-s", "-X", "POST",
            "https://blog.qiaomu.ai/api/uploads",
            "-H", f"Authorization: Bearer {TOKEN}",
            "-F", f"file=@{abs_path}"], capture_output=True, text=True, timeout=60)
        try:
            resp = json.loads(r.stdout)
            if resp.get("success") and resp.get("url"):
                return resp["url"]
        except Exception:
            pass
    return None  # 两次都失败，保留原路径

# 并发上传所有图片（最多 5 线程）
import concurrent.futures
local_images = [
    (m[0], m[1], article_path.parent / m[1])
    for m in re.findall(r'!\[([^\]]*)\]\((images/[^)]+)\)', body)
]
local_images = [(alt, img_path, abs_path)
                for alt, img_path, abs_path in local_images if abs_path.exists()]

def upload_one(item):
    alt, img_path, abs_path = item
    url = upload_image(abs_path)
    return img_path, url

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
    for img_path, url in pool.map(upload_one, local_images):
        if url:
            body = body.replace(f"({img_path})", f"({url})")

# 生成 SEO slug：论文英文缩写/代号 + 1-2 个领域词，不含日期
# 规则：全小写、连字符分隔、≤50字符
# 例："two-stream-video-action-recognition", "bert-masked-language-model"
# 提取英文大写词（模型名/方法名）
_model_words = re.findall(r'\b([A-Z][A-Z0-9\-]{1,})\b', title)  # e.g. BERT, CLIP, GPT
_model_slug = "-".join(w.lower() for w in _model_words[:2]) if _model_words else ""
# 补充领域关键词（取自 paper_id 中的小写词，去掉年份和泛词）
_domain_words = [w for w in paper_id.lower().replace("_", "-").split("-")
                 if len(w) > 3 and w not in ("paper","2014","2015","2016","2017","2018","2019","2020","2021","2022","2023","2024","2025","2026")]
_domain_slug = "-".join(_domain_words[:3])
if _model_slug:
    seo_slug = f"{_model_slug}-{_domain_slug}"[:60]
else:
    seo_slug = _domain_slug[:60]
seo_slug = re.sub(r'-+', '-', seo_slug).strip('-')

# 去掉正文里的 H1 标题（博客已有单独标题字段，避免重复显示）
_lines = body.split('\n')
for _i, _line in enumerate(_lines):
    if _line.startswith('# '):
        del _lines[_i]
        while _i < len(_lines) and _lines[_i].strip() == '':
            del _lines[_i]
        break
body = '\n'.join(_lines)

payload = json.dumps({
    "title": title, "content": body,
    "slug": seo_slug,
    "category": "paper", "status": "draft"
}, ensure_ascii=False)
r = subprocess.run(["curl", "-s", "-X", "POST",
    "https://blog.qiaomu.ai/api/posts",
    "-H", f"Authorization: Bearer {TOKEN}",
    "-H", "Content-Type: application/json",
    "-d", payload], capture_output=True, text=True)
resp = json.loads(r.stdout)
slug = resp.get("slug", "")
if slug:
    print(f"✅ 博客草稿已创建")
    print(f"   Slug: {slug}")
    print(f"   编辑: https://blog.qiaomu.ai/editor?slug={slug}")
    print(f"   预览: https://blog.qiaomu.ai/posts/{slug}")
else:
    print(f"⚠️ 发布响应异常: {r.stdout[:200]}")
```

### D4. 完成报告
>>>>>>> 3f6d27c (Initial release: qiaomu-paper-interpreter v1.2.1)

```
✅ 论文解读完成！

<<<<<<< HEAD
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
=======
📄 标题：{h1_title}
📝 字数：约 X 字
🖼️ 原文图表：N 张引用 / M 张转换（K 张超大跳过）
🎨 封面：已生成 / 已跳过（IMAGE_PROVIDER=skip）
🎭 配图：N 张 / 已跳过

📁 {paper_dir}/
📖 已在 Obsidian 中打开 / Obsidian 未配置，请手动打开
🌐 博客草稿：https://blog.qiaomu.ai/editor?slug={slug}（如触发了发布）
>>>>>>> 3f6d27c (Initial release: qiaomu-paper-interpreter v1.2.1)
```

---

<<<<<<< HEAD
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
=======
## 常见问题处理

### arXiv 来源为 HuggingFace 链接

先 WebFetch 页面，找到 `arxiv.org` 链接，再传入 `extract_tex.py`。

### LaTeX 源码不可用（论文未上传 arXiv）

```bash
markitdown <pdf_url_or_path> -o {paper_dir}/extracted_text.md
```

此情况下无法提取真实图表，`figure_list.md` 标注"不可用"，文章中用文字描述代替图片引用。

### extract_tex.py 不存在

该脚本来自 `qiaomu-markdown-proxy` skill。安装方式：
```bash
# 克隆 skill
git clone https://github.com/joeseesun/qiaomu-skills ~/.agents/skills/qiaomu-markdown-proxy
ln -s ../../.agents/skills/qiaomu-markdown-proxy ~/.claude/skills/qiaomu-markdown-proxy
```

或直接使用 markitdown fallback。

### 超大图（>20MB）需要强制转换

调低分辨率：
```bash
pdftoppm -r 72 -png -singlefile src.pdf dst
```

### 图片生成失败

如果 `IMAGE_PROVIDER` 配置了但生成失败，跳过配图步骤，保存纯文章版本，在报告中说明。

---

## 质量检查清单（保存前强制）

- [ ] `grep -c '——'` = 0
- [ ] `grep -c '总之\|综上\|让我们'` = 0
- [ ] 术语引用块 ≥ 10 处
- [ ] 生活化类比 ≥ 3 处
- [ ] 数据表格 ≥ 1 个（加粗最佳值）
- [ ] 图片引用数 ≈ 已转换图总数（不漏图）
- [ ] 包含 `## 写在后面` 节（300-500字，回答历史位置/当下意义/可迁移启示）
- [ ] **开头**（H1 之后）有论文信息引用块
- [ ] **末尾**（分隔线之后）有论文信息引用块
- [ ] 结尾以画面/问题收尾，无"总结"段落
- [ ] 逐段增量信息测试（每段提供新信息？）
>>>>>>> 3f6d27c (Initial release: qiaomu-paper-interpreter v1.2.1)

---

## 参考文档

<<<<<<< HEAD
- **风格指南**：`references/style-guide.md`
- **使用示例**：`examples.md`
- **故障排查**：`TROUBLESHOOTING.md`
- **配图设计**：`visual_description_guide.md`
- **版本历史**：`CHANGELOG.md`
=======
- **LaTeX 提取**：`~/.agents/skills/qiaomu-markdown-proxy/scripts/extract_tex.py`（依赖 `qiaomu-markdown-proxy` skill）
- **图片生成**：`~/.agents/skills/qiaomu-image-generator/scripts/generate.py`（可替换为自己的生图脚本，需配置 `IMAGE_GENERATOR_SCRIPT`）
- **博客发布 token**：`~/.claude/skills/qiaomu-blog-publish/config.json`（`{"token":"qm_xxx"}`）
- **写作风格**：已内联到本 skill（步骤 B0），无需外部依赖
>>>>>>> 3f6d27c (Initial release: qiaomu-paper-interpreter v1.2.1)
