---
name: skill-check
description: |
  Evaluates a single Claude Code Skill using 8-module quality framework with weighted scoring.
  Performs structural scanning, anti-pattern detection, completeness verification, and decision-gate checks.
  Use when checking Skill quality ("check skill", "skill 质量", "评估这个 skill", "review skill",
  "skill 好不好", "skill 总是不触发", "skill 输出不稳定", "evaluate skill", "skill quality report",
  "grade this skill").
  Do not use for general code review, non-Skill documentation, or Skill design concept discussions without a concrete target.
tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
  - Write
---

# Skill Check — 单个 Skill 质量评估

> 按用户语言响应

## 前置条件

- 路径不存在 → 输出"路径不存在：`<path>`"，停止
- 路径存在但不含 SKILL.md → 输出"目标目录不含 SKILL.md，不是有效的 Skill 目录。如需创建新 Skill，请运行 /skill-create"，停止
- 路径存在且有 SKILL.md → 通过，继续执行

---

## 参数解析

$ARGUMENTS 解析规则：
- `--ref <value>`: 可重复，提供参考文献（URL/本地文件/spec 引用）
- `<path>`: 最后一个非 flag 参数，目标 Skill 路径
- 示例: `/skill-check --ref https://standard.md --ref ./local-guide.md ./my-skill`

---

## 参考加载

当用户通过 `--ref` 提供参考文献时：

1. 解析参数列表，提取所有 `--ref` 值
2. 按类型识别规则加载：
   - `spec:<name>` → 映射为 `openspec/specs/<name>.md` 并读取
   - `https?://...` → WebFetch 抓取
   - 其他 → 本地文件路径，Read 读取
3. 检查内容大小限制（单参考 ≤10000 字符，总量 ≤30000 字符）
4. 将成功加载的参考注入评估上下文
5. 失败时警告 + 跳过，不阻断评估

✅ Checkpoint: `参考加载完成: 成功 N 个, 跳过 M 个, 共 P 个 --ref 参数`

---

## 触发条件

**同时满足**:
- 用户提供了现有**单个** Skill 目录路径（含 SKILL.md）
- 用户意图是评估/检查/审计单个/打分/review
- 问题现象信号（优先匹配）: "skill 总是不触发" "skill 输出不稳定" "skill 质量怎么样"

**不触发**:
- 讨论 Skill 设计概念但无具体目标（"Skill 应该怎么写？"）
- 非 Skill 类文件的代码审计（用 code-audit）
- 多 Skill 父目录（→ /skill-audit）

**歧义处理**: 询问 "您是要 check（单个评估）、fix（评估+修复）、create（从零创建）、还是 audit（多 Skill 系统审计）？"

---

## 行为准则

以下规则在全部执行阶段持续有效，不因步骤推进而衰减：

1. ❗ **每个发现必须引用来源**（文件路径 + 章节/行号）— 每次输出前自检此条
2. ❗ **评分基于检查清单客观打分**（0/1/2 或 Pass/Partial/Fail），不凭印象 — 每次输出前自检此条
3. ❗ **强结论必须通过 Decision Gate** — 证据不足时输出 `tentative` / `unresolved` — 每次输出前自检此条

其他: 评估的是 Skill 本身的结构质量，不是 Skill 所服务领域的专业深度

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
- 8 模块 / 7 反模式本身的定义解释
- 对 Skill 所服务领域的专业评论

---

## 执行流程 → Read `core/references/check-guide.md`

- 快速检查: 3 步（结构扫描 → 模块存在性 → 快速报告），每步有 ✅ Checkpoint
- 深度检查: 先 quick check 识别问题区域，再**按需加载**对应 reference
- 安全扫描: 运行 validate-security.py 进行 Critical 级静态模式检测，深度检查时加载 security-guide.md
- 评分: 模块(55%) + 反模式(20%) + 完整性(15%) + Decision Gate(10%)
- 上下文保护: quick check 不加载完整标准；deep check 才加载 quality-standards.md 与 decision-gates.md
- **默认用深度检查**，仅在用户明确说"快速看一下"时才用快速模式

---

## 依赖链

检查清单 → 评估步骤(不自创标准) → 安全扫描(validate-security.py) → Decision Gate 检查 → 报告引用评分(不重估) → 行动项总数 == 各步问题数之和(含安全问题)

---

## 子 Agent 委派

8模块/7反模式/3原则 可并行 3 个子 agent，各收到目标内容 + 检查清单原文（复制不转述），边界明确，合并时去重+一致性+计数验证

---

## 审计历史

每次 check 完成后追加结果到审计历史文件（一行一条 JSON）：
1. `${CLAUDE_PLUGIN_DATA}/audit-history.jsonl`（优先）
2. `~/.claude/skill-craft-data/audit-history.jsonl`（fallback）

执行前先查历史，同一 Skill 有历史记录时输出对比（`上次 → 本次`）。无历史 → 不提及，不编造。
报告输出后先展示待写入记录，用户确认后写入。

---

## Gotchas

1. **check 快速模式漏检**：快速检查（3 步）只查模块存在性，不查反模式和完整性。结构完整但质量差只有深度检查能发现
2. **评分不可跨 Skill 横向比较**：分数只适合同一 Skill 的纵向趋势对比
3. **权重改版后分数不可跨版本比较**：读取 audit-history.jsonl 时按 `weights_version` 字段区分

---

## 事实性约束（幻觉防护）

结论必须引用来源（文件路径+行号），无来源 = 不输出。

| 场景 | 正确输出 | 禁止输出 |
|------|---------|---------|
| 模块缺失 | "ABSENT: 模块 N 不存在" | "模块 N 较弱" |
| 反模式无风险 | "PASS: 未发现漏洞指标" | 编造风险 |
| 无法判断 | "UNABLE TO ASSESS: [原因]" | 猜测评分 |

标注: 工具确认→无标注 / 降级推测→"⚠️ 降级分析" / 领域建议→"💡 通用建议"

---

## 完成后推荐

→ 建议下一步: `/skill-fix <path>`（修复发现的问题）或 `/skill-audit <path>`（系统级审计）
