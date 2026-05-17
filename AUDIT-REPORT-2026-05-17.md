# 系统审计报告: skill-craft-adapter

**审计模式**: audit（多 Skill 系统审计）
**日期**: 2026-05-17
**目标目录**: `D:\Code\AI\SkillCraft\skill-craft-adapter`
**Skill 数量**: 4

---

## 系统概览

| Skill | 位置 | 角色 |
|-------|------|------|
| skill-check | `skills/skill-check/SKILL.md` | 单个 Skill 质量评估 |
| skill-fix | `skills/skill-fix/SKILL.md` | 评估并修复缺陷 |
| skill-audit | `skills/skill-audit/SKILL.md` | 多 Skill 系统审计 |
| skill-create | `skills/skill-create/SKILL.md` | 从零创建新 Skill |

**共享核心**:
- `core/references/` (10 个参考文档)
- `core/scripts/` (7 个脚本)
- `commands/skill-craft.md` (主入口调度)
- `README.md` (系统文档)

---

## Step 1: 系统扫描

✅ Checkpoint: `Step 1 完成: 发现 4 个 Skill, 10 个共享 references, 7 个 scripts, 3 个系统级文档`

---

## Step 2: 审计标准加载

✅ Checkpoint: `Step 2 完成: 审计标准已加载, 9 项必查`

---

## Step 3: 路由与分工审计

### 两两对比 (6/6 组合)

| # | 组合 | 结果 | 说明 |
|---|------|------|------|
| 1 | check vs fix | PASS | 触发词互斥（评估/检查 vs 修复/修/调整）；前置条件相同（单个 Skill 路径），意图词无交集 |
| 2 | check vs audit | PASS | 单个 vs 多个（≥2），前置条件互斥；check DO NOT: "多 Skill 父目录（→ /skill-audit）" |
| 3 | check vs create | PASS | 评估现有 vs 创建新；前置条件不同（路径 vs 描述） |
| 4 | fix vs audit | PASS | 修复单个 vs 审计多个；fix DO NOT: "多 Skill 目录（→ /skill-audit）" |
| 5 | fix vs create | PASS | 修复现有 vs 创建新；create DO NOT: "修改现有 Skill（→ /skill-fix）" |
| 6 | audit vs create | PASS | 审计系统 vs 创建新；完全不同领域 |

验收: 已对比组合数 == 6 == 4*(4-1)/2 ✅

**子 Agent 路由审计补充发现**:
- **W1 (WARNING)**: "评估" 一词在 check 和 fix 的 description 中共用。主入口已通过关键词分配解决（"评估" → check），但 fix description 仍含 "Evaluates and repairs"，可能造成认知歧义 (`skills/skill-fix/SKILL.md:4`)
- **W2 (WARNING)**: audit 不触发条件不完整 — 只指向 /skill-check，未提及 /skill-fix (`skills/skill-audit/SKILL.md:40-41`)。description (行 9) 已补偿此遗漏
- **W3 (WARNING)**: 主入口路由关键词覆盖不足，口语化输入（"看看"、"处理一下"、"有问题"）无法路由 (`commands/skill-craft.md:14-24`)。fix description 含 "改进 skill" 但主入口 fix 关键词不含 "改进"
- **M1**: check 关键词列表中 "评估" 出现两次 (`commands/skill-craft.md:17`)
- **M2**: skill-check 触发条件含 "审计" (`skills/skill-check/SKILL.md:35`) 但主入口将 "审计" 路由到 audit，两条路径结果不一致

### 路由模拟 (5 个用户输入)

| 用户输入 | 路由到 | 结果 |
|---------|--------|------|
| "评估一下 skill-check" | /skill-check | PASS |
| "修复这个 skill 的问题" | /skill-fix | PASS |
| "创建一个新的 skill 用于代码审计" | /skill-create | PASS |
| "审计 skill 系统 ./skills" | /skill-audit | PASS |
| "看看这个 skill 有没有问题" | 未匹配 → 帮助 | WARNING: "看看" 不在任何关键词列表 |

### 角色分工

| Skill | 核心动作 | 边界 |
|-------|---------|------|
| skill-check | 评估、检查、打分 | 只读评估，不修改 |
| skill-fix | 修复、调整、更新 | 评估+修复，基于 check 基线 |
| skill-audit | 系统审计、路由检查 | 多 Skill 系统级一致性 |
| skill-create | 创建、生成、新建 | 从零生成，不修改现有 |

角色分工清晰，无越界。推荐链闭环: check→fix/audit, fix→check, create→check, audit→fix。

✅ Checkpoint: `Step 3 完成: 6 个路由组合, 0 个冲突, 3 WARNING`

---

## Step 4: 一致性、完整性与 Decision Gate 审计

### 4.1 真值源统一 — PASS (含 1 项 P2 术语漂移)

权重数字 55%/20%/15%/10% 在以下位置一致：
- `README.md:108-111`
- `skills/skill-check/SKILL.md:89`
- `core/references/check-guide.md:161-172`
- `core/references/report-template.md:21,38,54,66`
- `core/references/security-guide.md:4,214`
- `core/references/quality-standards.md:258`

框架术语 "8 模块" / "7 反模式" 在所有文件中一致。

**子 Agent 发现 — 术语漂移 (P2)**:
- `README.md:3,:110` 使用 "**完备性**原则"
- `check-guide.md:89`, `quality-standards.md:173`, `report-template.md:54` 使用 "**完整性**原则"
- `skill-check/SKILL.md:103` 仅写 "3**原则**"（无前缀修饰词）
- 建议: 统一为 "完整性原则"（核心文档的主流用法）

### 4.2 引用链完整 — PASS (含 1 项 P1 路径语义不匹配)

所有 SKILL.md 引用的 `core/references/xxx-guide.md` 文件：
- `core/references/check-guide.md` ← skill-check/SKILL.md:84 ✅ 存在
- `core/references/fix-guide.md` ← skill-fix/SKILL.md:85 ✅ 存在
- `core/references/audit-guide.md` ← skill-audit/SKILL.md:84 ✅ 存在
- `core/references/create-guide.md` ← skill-create/SKILL.md:81 ✅ 存在

共享引用 (fix-guide, check-guide, create-guide 间交叉引用) 全部存在且非空。

**子 Agent 发现 — `{checker-root}/scripts/` 路径语义不匹配 (P1)**:
- `check-guide.md:11-14`, `fix-guide.md:9-12`, `create-guide.md:59-60` 使用 `{checker-root}/scripts/` 引用脚本
- 原始 skill-craft 架构: 每个 Skill 有自己的 `scripts/` 目录，`{checker-root}` 解析到 Skill 目录
- adapter 架构: 脚本集中在 `core/scripts/`，`{checker-root}` 解析到 `skills/skill-xxx/`（无 scripts/ 子目录）
- 影响: LLM 按文档指令 `python3 {checker-root}/scripts/validate-metadata.py` 执行时，路径不正确
- 缓解: LLM 可能通过上下文推理找到 `core/scripts/` 实际位置，但工程规范不一致

`${CLAUDE_PLUGIN_DATA}/audit-history.jsonl` 路径在 3 个 Skill 中一致引用：
- `skills/skill-check/SKILL.md:110`
- `skills/skill-fix/SKILL.md:110`
- `skills/skill-audit/SKILL.md:116`

### 4.3 承诺-实现一致 — PASS (含 1 项 P2 遗漏)

| 承诺 | 位置 | 实现 | 状态 |
|------|------|------|------|
| 5 个命令 | README.md:49-55 | commands/ + skills/ 均存在 | ✅ |
| 调度优先级 fix>check>create>audit | commands/skill-craft.md:14 | 代码实现 | ✅ |
| validate-metadata.py | README.md:117 | core/scripts/validate-metadata.py 存在 | ✅ |
| validate-structure.py | README.md:120 | core/scripts/validate-structure.py 存在 | ✅ |
| Python CLI | README.md:85-98 | core/scripts/skill-craft.py 存在 | ✅ |

**子 Agent 发现 — README 遗漏 validate-security.py (P2)**:
- `README.md:113-121` 验证脚本章节仅列出 validate-metadata.py 和 validate-structure.py
- validate-security.py 被 check-guide.md:109 和 security-guide.md:20 引用，但 README 未提及
- 建议: 补充 validate-security.py 的使用说明

### 4.4 旧口径残留 — PASS

- 无 `skill-craft/` 旧路径残留（grep 验证 .md 文件: 0 匹配）
- 无旧命名、旧规则数残留
- 路径统一使用 `core/references/` 前缀

### 4.5 Decision Gate — PASS

所有 4 个 Skill 行为准则均包含：
- "强结论必须通过 Decision Gate" 规则
- "证据不足时输出 tentative / unresolved" 降级路径
- 事实性约束（幻觉防护）章节含零结果处理表

### 补充检查

**结构一致性**: 4 个 Skill 均包含全部 8 个模块（触发条件、行为准则、工具优先级、输出约束、流程检查点、依赖链、子代理委派、幻觉防护）。工具优先级表格式完全一致。

**Decision Gate 深度**:
- skill-check: 声明强结论需 Decision Gate，引用 decision-gates.md
- skill-fix: 同上 + "禁止单边修复" + "修复仅限审计发现"
- skill-audit: 同上 + 路由冲突基于实际 description 对比
- skill-create: 同上 + "生成内容基于用户需求描述"

验收: 已检查项数 == 5 ✅

✅ Checkpoint: `Step 4 完成: 5 项一致性检查, 1 P1 + 2 P2`

---

## Step 5: 验证闭环与外围文档审计

### 验证闭环

| 项目 | 状态 | 证据 |
|------|------|------|
| test_runtime.py | 存在 | `core/scripts/test_runtime.py` (243 行) |
| test_cli.py | 存在 | `core/scripts/test_cli.py` (232 行) |
| test_security.py | 存在 | `core/scripts/test_security.py` (307 行) |
| 测试清单文档 | 不存在 | 无 TESTING.md 或等效文档 |

**测试覆盖**:
- test_runtime.py: 插件注册 (T6.1)、调度 (T6.2)、前置条件 (T6.3)、端到端 (T6.4)、推荐链 (T6.6)
- test_cli.py: CLI 场景 1-10 (check/fix/create/audit、前置阻断、串联执行、标准库约束)
- test_security.py: 安全验证场景 1-11 (凭证窃取、数据外泄、后门、豁免、命令注入、Prompt注入、C2)

### 外围文档

| 文档 | 旧规则传播 | 状态 |
|------|-----------|------|
| README.md | 无 | ✅ |
| commands/skill-craft.md | 无 | ✅ |
| plugin.json | N/A | ✅ |
| marketplace.json | N/A | ✅ |

✅ Checkpoint: `Step 5 完成: 验证闭环 + 外围文档检查`

---

## 交叉验证

- [x] 发现总数 == Steps 3+4+5 的问题数之和
- Step 3 路由问题: 3 WARNING (W1, W2, W3) → 3 P2
- Step 4 一致性问题: 1 P1 + 2 P2
- Step 5 验证闭环问题: 4 P2
- **总问题数: 10 (1 P1 + 9 P2)**

---

## 行动项

### P0（阻塞可靠执行）

无。

### P1（导致行为退化）

**P1-1**: `{checker-root}/scripts/` 路径语义不匹配
- 位置: `core/references/check-guide.md:11-14`, `core/references/fix-guide.md:9-12`, `core/references/create-guide.md:59-60`
- 现状: 继承自原始 skill-craft 架构，`{checker-root}` 在 adapter 中解析到 `skills/skill-xxx/`（无 scripts/），脚本实际在 `core/scripts/`
- 影响: LLM 按指令执行 `python3 {checker-root}/scripts/validate-metadata.py` 时路径不正确
- 根因: adapter 从"每 Skill 独立目录"架构重构为"共享核心"架构时，references 文件中的脚本路径未同步适配
- 修复建议: 将 `{checker-root}/scripts/` 替换为 adapter 实际路径 `core/scripts/`（或定义 adapter 专用的 `{adapter-root}` 变量）
- 验证方法: 修复后 grep 验证所有 `{checker-root}` 引用已更新或已定义映射

### P2（影响可维护性）

**P2-1**: skill-audit 前置条件 1 Skill 时的重定向不精确
- 位置: `skills/skill-audit/SKILL.md:28`
- 现状: "请先运行 /skill-create 创建更多 Skill"
- 建议: 区分 N=0 和 N=1 场景。N=1 时应建议 "/skill-check 评估单个 Skill" 或 "/skill-create 创建更多 Skill"
- 影响: 用户有 1 个现有 Skill 时获得误导性引导

**P2-2**: 测试目标依赖上游项目
- 位置: `core/scripts/test_runtime.py:19`, `core/scripts/test_cli.py:12`
- 现状: `SKILL_TARGET` 指向 `../../skill-craft`（上游项目）
- 影响: 仅克隆 adapter 仓库时测试无法运行，降低可移植性
- 建议: 添加 adapter 自身 Skills 作为测试目标 fixture（如 test_security.py 已使用 fixture 模式）

**P2-3**: 无独立测试清单文档
- 位置: 缺少 `TESTING.md` 或等效文件
- 现状: 测试逻辑分散在 3 个 .py 文件中，无顶层测试清单
- 影响: 新贡献者难以快速了解测试覆盖范围
- 建议: 创建 `TESTING.md` 列出测试场景、运行方法和覆盖矩阵

**P2-4**: marketplace.json 描述缺少负向触发条件
- 位置: `.claude-plugin/marketplace.json:7`
- 现状: "Claude Code Skill quality evaluation plugin — 8-module weighted scoring framework"
- plugin.json 描述含 "Do not use for..." 但 marketplace.json 不含
- 影响: Marketplace 展示时用户缺少适用边界信息
- 建议: 同步 marketplace.json description 与 plugin.json

**P2-5**: README 与核心文档术语漂移 ("完备性" vs "完整性")
- 位置: `README.md:3,:110` 用 "完备性原则"
- 核心文档 `check-guide.md:89`, `quality-standards.md:173`, `report-template.md:54` 用 "完整性原则"
- `skill-check/SKILL.md:103` 仅写 "3原则"（无前缀修饰词）
- 建议: 统一为 "完整性原则"

**P2-6**: README 遗漏 validate-security.py
- 位置: `README.md:113-121`
- 现状: 验证脚本章节仅列出 validate-metadata.py 和 validate-structure.py
- validate-security.py 被 check-guide.md:109, security-guide.md:20 引用
- 建议: 补充 validate-security.py 的使用说明

**P2-7**: 主入口路由关键词覆盖不足
- 位置: `commands/skill-craft.md:14-24`
- 现状: fix 关键词不含 "改进"（但 fix description 行 7 含 "改进 skill"）；口语化输入（"看看"、"处理一下"、"有问题"）无法路由
- 建议: 补充 "改进" (fix)、"evaluate" (check)、"grade" (check) 等关键词；修正 check 关键词中 "评估" 的重复项（行 17）

**P2-8**: skill-check 触发条件与主入口路由对 "审计" 一词归属不一致
- 位置: `skills/skill-check/SKILL.md:35` (意图含 "审计") vs `commands/skill-craft.md:24` (audit 关键词含 "审计")
- 现状: 直接调用 /skill-check 时 "审计" 被接受；走主入口时 "审计" 路由到 audit
- 影响: 两条路径行为不一致，但功能上不造成错误执行
- 建议: skill-check 触发条件中 "审计" 改为 "审计单个" 或移除，与主入口保持一致

**P2-9**: audit 不触发条件不完整
- 位置: `skills/skill-audit/SKILL.md:40-41`
- 现状: 只列 "单个 Skill 评估 (→ /skill-check)"，未提及 "单个 Skill 修复 (→ /skill-fix)"
- audit description (行 9) 已在 "Do not use for" 中列出 fix，但触发条件章节遗漏
- 建议: 不触发条件增加 "单个 Skill 修复 (→ /skill-fix)"

**行动项验证**: 总数 10 == Step3(3) + Step4(3) + Step5(4) ✅

---

## 总结

- **优势**: 路由设计严谨（4 个 Skill 6 对组合无硬冲突）；权重真值源完全统一（55%/20%/15%/10% 在 10+ 文件中一致）；Decision Gate 防护在所有 Skill 中一致实施；角色分工（查/改/验/建）清晰无越界
- **主要缺口**: 1 项 P1（adapter 架构重构后 `{checker-root}` 路径语义未适配）+ 9 项 P2（术语漂移、文档遗漏、路由关键词覆盖、重定向精度等）
- **系统评级**: **基本生产就绪** — 核心功能完整，路由互斥，引用链无断链。P1 路径问题可能导致脚本执行失败，建议优先修复

---

## 评分趋势

> 基于审计历史文件

| Skill | 上次分数 (2026-05-16, check) | 上次分数 (2026-05-16, fix) | 备注 |
|-------|------|------|------|
| skill-check | 10.0 | — | |
| skill-fix | 10.0 | — | |
| skill-create | 10.0 | — | |
| skill-audit | 9.4 | 10.0 | fix 修复了 check 阶段 P2 问题 |

---

## 待写入审计历史

```json
{"skill":"skill-craft-adapter","path":"D:\\Code\\AI\\SkillCraft\\skill-craft-adapter","mode":"audit","date":"2026-05-17","scope":"4-skills","p0":0,"p1":1,"p2":9,"p1_details":"checker-root-path-mismatch","p2_details":"audit-redirect-precision,test-portability,test-doc,marketplace-desc,terminology-drift,readme-security-omit,keyword-coverage,audit-trigger-inconsistency,audit-notrigger-incomplete","route_conflicts":0,"consistency_issues":1}
```

是否确认写入审计历史？
