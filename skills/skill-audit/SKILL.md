---
name: skill-audit
description: |
  Audits multiple Claude Code Skills in a directory for system-level consistency, route conflicts,
  and cross-Skill quality alignment using the 8-module quality framework.
  Performs system scanning, route auditing, consistency checking, and verification closure.
  Use when auditing multi-Skill systems ("审计 skill", "系统审计", "audit skill system",
  "全局检查", "路由冲突检查", "route conflict", "multi-skill audit").
  Do not use for evaluating a single Skill (use /skill-check), fixing defects (use /skill-fix),
  or creating new Skills (use /skill-create).
tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
  - Write
---

# Skill Audit — 多 Skill 系统审计

> 按用户语言响应

## 前置条件

- 路径不存在 → 输出"路径不存在：`<path>`"，停止
- 路径存在但 <2 个 SKILL.md → 按数量输出引导：
  - 0 个 SKILL.md → 输出"目录下无 Skill，审计需要 ≥2 个。请先运行 /skill-create 创建 Skill"，停止
  - 1 个 SKILL.md → 输出"目录下仅 1 个 Skill，审计需要 ≥2 个。如需评估该 Skill 请运行 /skill-check；如需创建更多 Skill 请运行 /skill-create"，停止
- ≥2 个 SKILL.md → 通过，继续执行

---

## 触发条件

**同时满足**:
- 用户提供了包含**多个** Skill 的父目录路径
- 或用户明确要求"系统级审计""全局检查""路由冲突检查"
- 目录下存在 ≥2 个 SKILL.md

**不触发**:
- 讨论 Skill 设计概念但无具体目标
- 单个 Skill 评估（→ /skill-check）
- 单个 Skill 修复（→ /skill-fix）

**歧义处理**: 询问 "您是要 audit（多 Skill 系统审计）、check（单个评估）、fix（评估+修复）、还是 create（从零创建）？"

---

## 行为准则

以下规则在全部执行阶段持续有效，不因步骤推进而衰减：

1. ❗ **每个发现必须引用来源**（文件路径 + 章节/行号）— 每次输出前自检此条
2. ❗ **强结论必须通过 Decision Gate** — 证据不足时输出 `tentative` / `unresolved` — 每次输出前自检此条

其他: 评估的是 Skill 本身的结构质量和系统一致性，不是 Skill 所服务领域的专业深度

---

## 工具优先级（不可自行降级）

| 操作 | 首选工具 | 降级条件 | 降级工具 |
|------|---------|---------|---------|
| 读取文件 | Read | Read 返回错误 | Bash cat |
| 查找文件 | Glob | Glob 返回 0 且路径确认存在 | Bash ls -R |
| 搜索关键词 | Grep | Grep 连续 2 次失败 | Bash grep |
| 修改已有文件 | Edit | Edit 失败 | 调整 old_string 后重试 Edit |
| 创建新文件 | Write | — | — |

- 单次超时 ≠ 工具不可用，必须重试 1 次
- 降级必须标注: "⚠️ 降级: [原因]"
- 不可用 Bash sed/awk 替代 Edit

---

## 输出约束

禁止输出:
- "让我来分析一下..." / "首先我们需要..." 等开场白
- 工具调用前后的重复描述
- 已知信息的复述
- 对 Skill 所服务领域的专业评论

---

## 执行流程 → Read `core/references/audit-guide.md`

- 7 步: 系统扫描 → 加载标准 → 路由审计 → 一致性审计 → **安全扫描** → 验证闭环 → 系统报告
- 多 Skill 专属: 路由边界、角色分工、旧口径残留、外围文档传播
- **安全扫描**: 对每个被审计的 Skill 运行 `core/scripts/validate-security.py`，Critical 级发现纳入 P0 行动项
- 每步有 ✅ Checkpoint（含通过标准: 已对比组合数 == N*(N-1)/2 / 已检查项数 == 5 / 发现总数 == 各步问题数之和(含安全问题)）
- Skill 数量 > 15 时必须分批（每批 ≤8 个），按子目录分组或字母序

---

## 依赖链

系统扫描 → 覆盖所有 Skill → 路由/一致性/安全扫描/Decision Gate → 发现总数 == 各步问题数之和(含安全问题)

- 后续步骤必须引用前序步骤的实际产出（禁止重新扫描已覆盖的 Skill）
- 交叉验证: 写入报告前发现总数 == Step 3 问题数 + Step 4 问题数 + Step 5 问题数 + Step 6 问题数

---

## 子 Agent 委派

路由审计 + 一致性审计 可并行 2 个子 agent，各收到目标 Skill 列表 + 检查标准（复制不转述），边界明确

合并检查:
- 去重: 两个子 agent 发现的同一问题只计一次
- 一致性: 路由审计与一致性审计的结论不矛盾
- 计数验证: 合并后发现总数 == 路由审计发现数 + 一致性审计发现数 + 安全扫描发现数 + 验证闭环发现数

---

## 审计历史

系统报告末尾附"评分趋势"表（仅有历史的 Skill）：
1. `${CLAUDE_PLUGIN_DATA}/audit-history.jsonl`（优先）
2. `~/.claude/skill-craft-data/audit-history.jsonl`（fallback）

无历史 → 不提及，不编造。

---

## Gotchas

1. **大量 Skill 时超上下文**：目录下 Skill > 15 时必须分批 audit，每批 ≤8 个
2. **评分不可跨 Skill 横向比较**：分数只适合同一 Skill 的纵向趋势
3. **路由冲突基于实际 description 对比**：旧口径通过 grep 验证

---

## 事实性约束（幻觉防护）

结论必须引用来源（文件路径+行号），无来源 = 不输出。

| 场景 | 正确输出 | 禁止输出 |
|------|---------|---------|
| 模块缺失 | "ABSENT: 模块 N 不存在" | "模块 N 较弱" |
| 反模式无风险 | "PASS: 未发现漏洞指标" | 编造风险 |
| 无法判断 | "UNABLE TO ASSESS: [原因]" | 猜测评分 |

标注: 工具确认→无标注 / 降级推测→"⚠️ 降级分析" / 领域建议→"💡 通用建议"

**audit 特有**: 路由冲突基于实际 description 对比；旧口径通过 grep 验证

---

## 完成后推荐

→ 建议下一步: `/skill-fix <path>`（修复具体 Skill 问题）
