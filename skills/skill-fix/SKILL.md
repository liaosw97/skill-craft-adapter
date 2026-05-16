---
name: skill-fix
description: |
  Evaluates and repairs a single Claude Code Skill by identifying defects and applying targeted fixes.
  Performs assessment, problem listing, prioritized repair, and regression verification.
  Use when fixing Skill defects ("fix skill", "修复 skill", "skill 有问题", "调整 skill",
  "update skill", "repair skill", "改进 skill").
  Do not use for creating new Skills from scratch, general code review, or Skill design concept discussions.
tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
  - Write
---

# Skill Fix — 评估并修复

> 按用户语言响应

## 前置条件

- 路径不存在 → 输出"路径不存在：`<path>`"，停止
- 路径存在但不含 SKILL.md → 输出"目标目录不含 SKILL.md，不是有效的 Skill 目录。如需创建新 Skill，请运行 /skill-create"，停止
- 路径存在 + SKILL.md 存在 + 审计历史中无 check 记录 → 通过，额外提示"建议先运行 /skill-check 建立基线分数"

---

## 触发条件

**同时满足**:
- 用户提供了现有 Skill 目录路径（含 SKILL.md）
- 用户意图是修复/修/调整/更新/fix/repair

**不触发**:
- 讨论 Skill 设计概念但无具体目标
- 非 Skill 类文件的代码修复
- 多 Skill 目录（→ /skill-audit）

**歧义处理**: 询问 "您是要 fix（评估+修复）、check（仅评估）、create（从零创建）、还是 audit（多 Skill 系统审计）？"

---

## 行为准则

1. ❗ **每个发现/修改必须引用来源**（文件路径 + 章节/行号）— 每次输出前自检此条
2. ❗ **禁止单边修复** — 改文档必须同步改实现，改实现必须同步改文档。每次修改前自检此条
3. ❗ **强结论必须通过 Decision Gate** — 证据不足时输出 `tentative` / `unresolved` — 每次输出前自检此条

其他:
- fix 模式：修复范围仅限审计发现，不可"顺便优化"审计未提及的内容
- 评估的是 Skill 本身的结构质量，不是 Skill 所服务领域的专业深度

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
- **fix 模式：禁止只说"已修复"而不展示验证方法和结果**

---

## 执行流程 → Read `core/references/fix-guide.md`

- 8 步: 结构扫描 → 加载清单+约束 → 深度评估 → 问题清单 → P0修复 → P1修复 → P2修复 → 全局验证+**回归评估**
- 每项修复强制: 修改 → 读回验证 → 变更影响扫描(4种关联：引用方/对称文件/下游消费者/同层文件) → 关联同步
- 审计结果先输出，再改文件。每步有 ✅ Checkpoint

---

## 依赖链

评估结果 → 问题清单(不遗漏) → 逐项修复 → 回归 Decision Gate → 修复数 + 未修复数 == 问题总数

---

## 子 Agent 委派

- **评估可并行**：问题扫描阶段可 dispatch 多个子 agent
- **修复不可并行**：修复间有依赖，必须串行执行

---

## 审计历史

每次 fix 完成后追加修复后结果到审计历史文件：
1. `${CLAUDE_PLUGIN_DATA}/audit-history.jsonl`（优先）
2. `~/.claude/skill-craft-data/audit-history.jsonl`（fallback）

执行前先查历史，有 check 记录时输出基线对比。fix 写入修复后的分数。

---

## Gotchas

1. **fix 前必须 check**：直接 fix 缺少基线分数，无法量化改进效果。fix 流程已内置评估步骤
2. **"顺便优化"陷阱**：修复过程中发现审计未提及的问题，禁止"顺便改掉"。记录到"后续建议"即可
3. **评分不可跨 Skill 横向比较**：分数只适合同一 Skill 的纵向趋势对比
4. **权重改版后分数不可跨版本比较**：按 `weights_version` 字段区分

---

## 事实性约束（幻觉防护）

结论必须引用来源（文件路径+行号），无来源 = 不输出。

| 场景 | 正确输出 | 禁止输出 |
|------|---------|---------|
| 模块缺失 | "ABSENT: 模块 N 不存在" | "模块 N 较弱" |
| 反模式无风险 | "PASS: 未发现漏洞指标" | 编造风险 |
| 无法判断 | "UNABLE TO ASSESS: [原因]" | 猜测评分 |

标注: 工具确认→无标注 / 降级推测→"⚠️ 降级分析" / 领域建议→"💡 通用建议"

**fix 特有**: 修复仅限审计发现；每项修复须说明出处+内容+验证结果

---

## 完成后推荐

→ 建议下一步: `/skill-check <path>`（验证修复效果）
