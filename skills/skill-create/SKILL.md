---
name: skill-create
description: |
  Creates a new Claude Code Skill from scratch based on user requirements, following the 8-module quality framework.
  Generates SKILL.md, references, and validation scripts with proper structure and completeness.
  Use when creating new Skills ("创建 skill", "新建 skill", "generate skill", "create a skill",
  "build a skill", "scaffold skill").
  Do not use for evaluating existing Skills, fixing Skill defects, or general code scaffolding.
argument-hint: <desc>
tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
  - Write
---

# Skill Create — 从零创建 Skill

> 按用户语言响应

## 前置条件

- 无参数 → 输出"请描述要创建的 Skill 的用途（如：代码安全审计、API 文档生成）"，等待用户输入
- desc 非空 → 通过，继续执行

---

## 参数解析

$ARGUMENTS 解析规则：
- `--ref <value>`: 可重复，提供参考文献（URL/本地文件/spec 引用）
- `<desc>`: 最后一个非 flag 参数，Skill 用途描述
- 示例: `/skill-create --ref https://skill-template.md "创建一个代码审查 Skill"`

---

## 参考加载

当用户通过 `--ref` 提供参考文献时：

1. 解析参数列表，提取所有 `--ref` 值
2. 按类型识别规则加载：
   - `spec:<name>` → 映射为 `openspec/specs/<name>.md` 并读取
   - `https?://...` → WebFetch 抓取
   - 其他 → 本地文件路径，Read 读取
3. 检查内容大小限制（单参考 ≤10000 字符，总量 ≤30000 字符）
4. 将成功加载的参考注入生成上下文
5. 失败时警告 + 跳过，不阻断生成

✅ Checkpoint: `参考加载完成: 成功 N 个, 跳过 M 个, 共 P 个 --ref 参数`

**参考用户规范原则**: 当用户参考包含 Skill 结构规范时，生成内容遵循用户规范。

---

## 触发条件

**同时满足**:
- 用户要求创建/生成/新建一个 Skill
- 用户描述了 Skill 的用途或领域

**不触发**:
- 讨论 Skill 设计概念但无创建意图（"Skill 应该怎么写？"）
- 修改现有 Skill（→ /skill-fix）

**歧义处理**: 询问 "您是要 create（从零创建）、fix（修复现有）、check（评估）、还是 audit（系统审计）？"

---

## 行为准则

以下规则在全部执行阶段持续有效，不因步骤推进而衰减：

1. ❗ **强结论必须通过 Decision Gate** — 证据不足时输出 `tentative` / `unresolved` — 每次输出前自检此条
2. ❗ **生成内容基于用户需求描述**，不可添加用户未要求的领域知识 — 每次输出前自检此条

其他: create 模式遵循 Skill Craft 的评分框架标准，确保生成的 Skill 从一开始就符合质量要求

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
- **create 模式：禁止生成与现有 Skill 路由冲突的触发条件**

---

## 执行流程 → Read `core/references/create-guide.md`

- 6 步: 明确需求 → 规模判断 → 生成文件 → 自检清单 → **自动化验证**(validate-metadata + validate-structure + validate-security) → 创建报告
- 规模适配:
  - 轻量(模块1+2+4+8)
  - 中等(1-5+8)
  - 重型(全部8个)
- 每步有 ✅ Checkpoint

失败降级:
- 需求不明确 → 提出具体问题引导，不自行假设
- 参考文档不可读 → 使用内置规模适配表和模块模板
- 验证脚本不可用 → 手动检查 name/description/结构，标注 "⚠️ 降级: 自动化验证不可用"

---

## 依赖链

需求 → 规模判断(基于需求) → 必需模块(全部填充) → Decision Gate 模板 → 自检(逐项核对) → 已填充数 == 必需模块数

- Step 3 生成内容必须基于 Step 1 需求 + Step 2 规模判断（禁止重新搜索需求）
- 交叉验证: 写入文件前已填充模块数 == Step 2 确定的必需模块数

---

## 子 Agent 委派

通常不需要子 agent。仅在重型 Skill 的多 references 文件生成时可考虑并行创建独立文件。

---

## Gotchas

1. **触发条件冲突**：创建前必须扫描现有 Skill 的触发条件，避免路由冲突
2. **规模判断影响模块数**：轻量 Skill 不需要全部 8 个模块，过度设计会降低可用性
3. **自动化验证是强制步骤**：生成后必须运行 validate-metadata.py、validate-structure.py 和 validate-security.py

---

## 事实性约束（幻觉防护）

结论必须引用来源，无来源 = 不输出。生成内容基于用户需求描述，不添加用户未要求的领域知识。

| 场景 | 正确输出 | 禁止输出 |
|------|---------|---------|
| 模块缺失 | "ABSENT: 模块 N 不存在" | "模块 N 较弱" |
| 无法判断 | "UNABLE TO ASSESS: [原因]" | 猜测 |

标注: 工具确认→无标注 / 降级推测→"⚠️ 降级分析" / 领域建议→"💡 通用建议"

**create 特有**: 触发条件基于用户描述，不添加用户未要求的领域知识

---

## 完成后推荐

→ 建议下一步: `/skill-check <path>`（评估新 Skill 质量）
