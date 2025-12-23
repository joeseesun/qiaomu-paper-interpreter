# Visual Description 编写指南

## 核心原则

为《纽约客》风格配图编写visual_description时，务必遵循以下原则：

### ✅ 正确示例

```json
{
  "h2_title": "注意力的魔法",
  "visual_description": "A busy cafe from bird's eye view, multiple conversations creating sound waves, one spotlight beam illuminating a single table of two people talking, showing selective attention"
}
```

**特点**：
- ✅ 使用英文（AI图片生成模型对英文理解更准确）
- ✅ 描述具体的视觉场景和物体
- ✅ 用隐喻手法表达抽象概念
- ✅ **不包含任何文字指令**（如"底部标题"、"标注"等）

### ❌ 错误示例

```json
{
  "h2_title": "注意力的魔法",
  "visual_description": "嘈杂咖啡馆的鸟瞰图，多个人在交谈，声波以同心圆扩散，一束聚光灯从天花板投下照亮一桌对话的两人，用黑白墨水绘制场景，朱红色标注聚光灯，底部标题：专注的力量"
}
```

**问题**：
- ❌ 使用中文（AI理解不如英文准确）
- ❌ 包含风格指令（"用黑白墨水绘制"、"朱红色标注"）→ 这些由系统统一控制，不需要重复
- ❌ **包含文字指令**（"底部标题：专注的力量"）→ 会导致AI在图中画文字，违背纽约客风格

## 编写模板

```
[主体物体/场景] + [动作/状态] + [隐喻含义]
```

### 示例1：对比类

```
Two-road comparison: upper shows single-lane with cars queuing slowly, lower shows multi-lane highway with cars speeding in parallel, illustrating parallelization advantage
```

### 示例2：隐喻类

```
A razor blade close-up with sharp clean edge, scattered complex parts and gears beside it being shaved off, sharp contrast, illustrating Occam's Razor principle
```

### 示例3：关系网络类

```
A page with text, multiple dotted lines connecting different words to each other, forming a spider-web relationship network, some lines thick and some thin
```

## 风格控制

**不要**在visual_description中描述风格细节，这些已由系统统一控制：

系统自动添加的风格prompt：
```
The New Yorker magazine editorial cartoon style,
single-line pen and ink drawing, minimalist line art,
black and white sketch with subtle red accent (#E34234),
clean white background, sophisticated humor,
NO text, NO labels, NO words in the image
```

你只需要描述：**画什么内容**，而不是**怎么画**。

## 常见错误

| 错误 | 原因 | 修正 |
|------|------|------|
| "底部标题：XXX" | 会导致AI画文字 | 删除所有文字指令 |
| "用黑白线条绘制" | 风格已统一控制 | 只描述内容，不描述风格 |
| "朱红色标注XX" | 颜色使用已统一 | 只说"标注XX"即可 |
| 使用中文描述 | AI理解不准确 | 改用英文 |
| 描述过于抽象 | AI无法可视化 | 使用具体物体和场景 |

## 质量检查清单

写完visual_description后，检查：

- [ ] 使用英文
- [ ] 描述了具体的物体/场景
- [ ] 没有包含"底部标题"、"标注文字"等文字指令
- [ ] 没有重复描述风格（黑白、线条、朱红色等）
- [ ] 长度在30-80词之间（太短概念不清，太长AI抓不住重点）
- [ ] 有明确的视觉隐喻，能表达H2章节的核心观点

## 改进对比

### 改进前（会产生问题）

```json
{
  "visual_description": "一条蜿蜒的单行道路，汽车排成长队缓慢前行，最前面的车已模糊不清，用黑白钢笔线条绘制道路和车辆，朱红色标注堵塞的队列，底部标题：记忆的拥堵"
}
```

问题：中文、风格重复、包含文字指令

### 改进后（正确）

```json
{
  "visual_description": "A winding single-lane road with cars queuing slowly, the front cars fading into distance, conveying the limitation of sequential processing"
}
```

改进：英文、只描述内容、无文字指令、清晰的隐喻
