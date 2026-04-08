# 乔木论文解读 - 架构文档

## 核心设计原则

**关注点分离**：
- Claude 负责内容理解和视觉策略生成
- Python 脚本负责图片生成和文档更新
- 共享库提供统一的 API 接口

**单一真相源**：
- 所有图片生成逻辑集中在 `~/.claude/skills/shared-lib/image_api.py`
- 避免功能重复，确保一致性

## 目录结构

```
~/.claude/skills/qiaomu-paper-interpreter/
├── SKILL.md                          # Skill 定义和使用指南
├── ARCHITECTURE.md                   # 本文件 - 架构说明
├── README.md                         # 功能说明和快速开始
├── scripts/
│   ├── generate_illustrations_v2.py  # ✅ 主力脚本：并发生成配图
│   ├── generate_illustrations.py     # 单线程版本（保留用于调试）
│   ├── finalize_markdown.py          # Markdown 最终处理
│   ├── extract_pdf_metadata.py       # PDF 元数据提取
│   ├── load_env.py                   # 环境变量加载器
│   │
│   ├── image_api.py.deprecated       # ❌ 已废弃：使用 shared-lib 替代
│   └── image_api.py.deprecated.txt   # 废弃说明
│
└── references/
    ├── workflow.md                   # 工作流程详解
    └── style-guide.md                # 视觉风格指南
```

## 依赖关系

### 外部服务

```
本地 Docker 容器
├── 镜像: ghcr.io/zhizinan1997/jimeng-free-api-all:latest
├── 端口: 8000
└── 环境变量: JIMENG_SESSION_ID
    ↓
即梦官方 API
├── 认证: Bearer Token (session_id)
├── 模型: jimeng-image-4.5 (付费) / jimeng-image-4.1 (免费)
└── 限额: 66积分/天 (免费版)
```

### 代码依赖

```
scripts/generate_illustrations_v2.py
    ↓
    导入优先级设置
    sys.path.insert(0, '~/.claude/skills/shared-lib')
    ↓
~/.claude/skills/shared-lib/image_api.py
    ├── ImageGenerator.generate_newyorker_style()
    │   ├── 构建统一提示词模板
    │   ├── 调用 _generate_jimeng()
    │   └── Fallback: _generate_gemini()
    │
    ├── _generate_jimeng()
    │   └── POST http://localhost:8000/v1/images/generations
    │
    └── save_image()
        └── 下载并保存 PNG
```

## 核心工作流

### 1. 配图生成流程

```
用户触发 Skill
    ↓
Claude 分析文章内容
    ↓
生成 visual_config.json
    ├── h2_title: "章节标题"
    ├── visual_description: "具体视觉描述"
    └── caption: "底部标题"
    ↓
调用 generate_illustrations_v2.py
    ├── 封面生成 (关键词 → 视觉策略)
    ├── 章节配图并发生成 (3线程池)
    │   ├── ImageGenerator.generate_newyorker_style()
    │   ├── 重试机制 (最多3次)
    │   └── 文件命名: {paper_slug}-{idx:02d}.png
    │
    └── 自动插入 Markdown
        ├── 线程安全 (markdown_lock)
        ├── 防重复检查
        └── Obsidian 兼容路径处理
    ↓
输出: 带配图的完整文章
```

### 2. 图片生成技术细节

**提示词架构** (已优化，零文字干扰):

```python
prompt = f"""纽约客杂志插图风格：钢笔线条速写，黑白为主，朱红色点缀，简约留白。

{visual_strategy}  # ← 唯一动态内容

16:9横幅构图，手绘松弛质感{caption_instruction}"""
```

**关键优化点**：
- ✅ 只包含抽象的 `visual_strategy` 参数
- ✅ 移除所有结构化标记 (`主题:`, `核心观点:`)
- ✅ 移除所有具体内容变量 (避免渲染成文字)
- ✅ 自然语言描述比例 ("横向宽幅构图16:9")
- ✅ 明确禁止文字 ("画面中不要任何文字")

## 环境配置

### 必需环境变量

```bash
# .env 文件或 shell 配置
export JIMENG_SESSION_ID="your_session_id_here"  # 必需
export JIMENG_API_URL="http://localhost:8000"    # 可选，默认值
```

### 获取 Session ID

1. 访问 https://jimeng.jianying.com/
2. 开发者工具 (F12) → Application → Cookies
3. 复制 `sessionid` 值

### 启动 Docker 服务

```bash
# 检查服务状态
docker ps | grep jimeng-free-api

# 如未运行，启动服务
docker run -it -d \
  --init \
  --name jimeng-free-api \
  -p 8000:8000 \
  -e TZ=Asia/Shanghai \
  ghcr.io/zhizinan1997/jimeng-free-api-all:latest
```

## 性能优化

### 并发策略

- **线程池大小**: 3 (平衡速度与限流)
- **理论加速比**: 3× (实测接近)
- **单张耗时**: 10-30秒 (jimeng-image-4.1)

**示例**:
- 12张图串行: 348秒 (约6分钟)
- 12张图并发: 116秒 (约2分钟)

### 容错机制

1. **重试策略**: 每个 API 调用最多重试 3 次
2. **Fallback**: jimeng 失败自动切换到 gemini
3. **线程安全**: `markdown_lock` 保护文件写入
4. **防重复**: 检查现有图片引用，避免重复插入

## 测试验证

### 快速测试

```bash
cd /tmp && python3 << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / '.claude' / 'skills' / 'shared-lib'))

from image_api import ImageGenerator

gen = ImageGenerator(provider='jimeng', jimeng_model='jimeng-image-4.1')
url, provider = gen.generate_newyorker_style(
    visual_strategy="一只橘色短毛猫坐在窗台上，背景是城市夜景",
    aspect_ratio='16:9'
)
gen.save_image(url, "/tmp/test.png")
print(f"✅ 测试成功: {provider}, /tmp/test.png")
EOF
```

### 预期输出

```
✅ 测试成功: jimeng, /tmp/test.png
```

验证图片:
```bash
file /tmp/test.png
# 输出: PNG image data, 2560 x 1440, 8-bit/color RGB
```

## 故障排查

### 问题 1: API 连接失败

**症状**: `Connection refused` 或 `timeout`

**解决**:
```bash
# 检查 Docker 状态
docker ps | grep jimeng-free-api

# 重启服务
docker restart jimeng-free-api

# 查看日志
docker logs jimeng-free-api
```

### 问题 2: 认证失败

**症状**: `401 Unauthorized`

**解决**:
```bash
# 检查环境变量
echo $JIMENG_SESSION_ID

# Session ID 过期，重新获取
# 1. 访问 https://jimeng.jianying.com/
# 2. 开发者工具获取新 sessionid
# 3. 更新环境变量
export JIMENG_SESSION_ID="new_session_id"
```

### 问题 3: 积分不足

**症状**: 提示积分用尽

**解决**:
- 等待第二天 0 点自动刷新 (66积分)
- 或使用付费模型 `jimeng-image-4.5`

### 问题 4: 图片有文字干扰

**症状**: 生成图片包含不需要的文字

**诊断**:
```python
# 检查 visual_strategy 是否包含具体内容
# ❌ 错误: "主题：残差学习，核心观点：解决退化问题"
# ✅ 正确: "用隐喻手法表现深度学习中的残差连接"
```

**解决**: 使用抽象的视觉描述，避免具体术语

## 版本历史

### v2.0.0 (Current)
- ✅ 迁移到 shared-lib 统一接口
- ✅ 废弃本地 image_api.py
- ✅ 优化提示词模板 (零文字干扰)
- ✅ 添加架构文档

### v1.0.0
- 初始实现
- 本地 image_api.py (已废弃)
- 存在文字干扰问题

## 相关资源

- **共享库**: `~/.claude/skills/shared-lib/image_api.py`
- **即梦官网**: https://jimeng.jianying.com/
- **Docker 镜像**: ghcr.io/zhizinan1997/jimeng-free-api-all
- **相关 Skills**:
  - article-illustrator (文章配图)
  - jimeng-image-generator (单图生成)
