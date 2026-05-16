---
description: Skill Craft 主入口 — 评估、修复、创建或审计 Claude Code Skills
argument-hint: <mode> <path>
---

# /skill-craft — 主入口命令

解析 `$ARGUMENTS`，关键词匹配调度到对应子命令。

## 调度逻辑

按优先级匹配（fix > check > create > audit）：

1. **fix 模式** — 匹配关键词: "修复"、"fix"、"修"、"调整"、"更新"、"repair"
   → 输出: "请运行 `/skill-fix <path>` 进行评估并修复"

2. **check 模式** — 匹配关键词: "评估"、"检查"、"check"、"审计单个"、"review"、"打分"、"评估"、"好不好"、"质量"
   → 输出: "请运行 `/skill-check <path>` 进行质量评估"

3. **create 模式** — 匹配关键词: "创建"、"新建"、"create"、"生成"、"generate"
   → 输出: "请运行 `/skill-create <desc>` 创建新 Skill"

4. **audit 模式** — 匹配关键词: "审计"、"audit"、"系统审计"、"全局检查"、"路由冲突"
   → 输出: "请运行 `/skill-audit <path>` 进行系统级审计"

## 特殊情况

- **$ARGUMENTS 为空**: 输出:
  ```
  Skill Craft — Skill 质量工程工具

  请指定模式:
    /skill-check <path>   — 评估单个 Skill 质量
    /skill-fix <path>     — 评估并修复 Skill 缺陷
    /skill-create <desc>  — 创建新 Skill
    /skill-audit <path>   — 多 Skill 系统审计

  示例: /skill-craft 评估这个 skill → /skill-check ./my-skill
  ```

- **多模式匹配**: 按优先级取第一个匹配，额外输出:
  "检测到复合意图，优先执行 [匹配的模式]。如需其他模式请直接运行对应命令。"

- **未匹配任何关键词**: 输出可用模式列表（同空参数输出）
