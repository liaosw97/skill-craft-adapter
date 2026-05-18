#!/usr/bin/env python3
"""T6.1~T6.4, T6.6 运行时验证 — 文件级自动化测试.

验证 plugin 结构、SKILL.md 内容、调度逻辑、前置条件、推荐链的文件级正确性。
Claude Code 运行时行为需要手动验证（见末尾清单）。
"""

import json
import os
import re
import subprocess
import sys

BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SKILLS_DIR = os.path.join(BASE_DIR, "skills")
COMMANDS_DIR = os.path.join(BASE_DIR, "commands")
PLUGIN_JSON = os.path.join(BASE_DIR, ".claude-plugin", "plugin.json")
CLI_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skill-craft.py")
SKILL_TARGET = os.environ.get("SKILL_TARGET", os.path.join(BASE_DIR, "skills", "skill-check"))

passed = 0
failed = 0


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}")
        if detail:
            print(f"     {detail}")
        failed += 1


def read_file(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_skill(skill_name):
    return read_file(os.path.join(SKILLS_DIR, skill_name, "SKILL.md"))


# ============================================================
# T6.1: 插件注册验证 [spec:plugin-structure#SC-02]
# ============================================================
print("=" * 60)
print("T6.1: 插件注册验证 (SC-02)")
print("=" * 60)

# plugin.json
check("[T6.1] plugin.json 存在", os.path.isfile(PLUGIN_JSON))
pj = json.loads(read_file(PLUGIN_JSON))
check("[T6.1] name = skill-craft-adapter", pj.get("name") == "skill-craft-adapter")
check("[T6.1] description ≥ 50 字符", len(pj.get("description", "")) >= 50,
      f"实际 {len(pj.get('description', ''))} 字符")
check("[T6.1] description 含负向触发", "Do not use" in pj.get("description", ""))
check("[T6.1] version 存在", "version" in pj)
check("[T6.1] author 存在", "author" in pj)
check("[T6.1] license 存在", "license" in pj)
check("[T6.1] repository 存在", "repository" in pj)

# 4 skills + 1 command
EXPECTED_SKILLS = ["skill-check", "skill-fix", "skill-create", "skill-audit"]
for s in EXPECTED_SKILLS:
    skill_path = os.path.join(SKILLS_DIR, s, "SKILL.md")
    check(f"[T6.1] skill {s}/SKILL.md 存在", os.path.isfile(skill_path))

check("[T6.1] commands/skill-craft.md 存在",
      os.path.isfile(os.path.join(COMMANDS_DIR, "skill-craft.md")))

# SKILL.md frontmatter name 一致性
for s in EXPECTED_SKILLS:
    content = read_skill(s)
    match = re.search(r'^name:\s*(\S+)', content, re.MULTILINE)
    if match:
        check(f"[T6.1] {s} frontmatter name = {s}",
              match.group(1) == s, f"实际: {match.group(1)}")
    else:
        check(f"[T6.1] {s} frontmatter name = {s}", False, "未找到 name 字段")

# ============================================================
# T6.2: 主入口调度功能验证 [spec:plugin-structure#SC-03]
# ============================================================
print()
print("=" * 60)
print("T6.2: 主入口调度功能验证 (SC-03)")
print("=" * 60)

cmd_content = read_file(os.path.join(COMMANDS_DIR, "skill-craft.md"))
check("[T6.2] 含调度逻辑标题", "调度逻辑" in cmd_content)
check("[T6.2] 含 fix 模式关键词", "修复" in cmd_content and "fix" in cmd_content.lower())
check("[T6.2] 含 check 模式关键词", "评估" in cmd_content or "检查" in cmd_content)
check("[T6.2] 含 create 模式关键词", "创建" in cmd_content or "新建" in cmd_content)
check("[T6.2] 含 audit 模式关键词", "审计" in cmd_content or "audit" in cmd_content.lower())
check("[T6.2] 含优先级说明", "优先级" in cmd_content or "fix > check" in cmd_content)
check("[T6.2] 含空参数处理", "$ARGUMENTS" in cmd_content and "空" in cmd_content)
check("[T6.2] 调度指向 /skill-fix", "/skill-fix" in cmd_content)
check("[T6.2] 调度指向 /skill-check", "/skill-check" in cmd_content)
check("[T6.2] 调度指向 /skill-create", "/skill-create" in cmd_content)
check("[T6.2] 调度指向 /skill-audit", "/skill-audit" in cmd_content)

# ============================================================
# T6.3: 前置条件阻断验证 [spec:prerequisite-guidance#PG-01~PG-04]
# ============================================================
print()
print("=" * 60)
print("T6.3: 前置条件阻断验证 (PG-01~PG-04)")
print("=" * 60)

# skill-check 前置条件 (PG-01)
check_md = read_skill("skill-check")
check("[T6.3/PG-01] skill-check 含前置条件节", "前置条件" in check_md)
check("[T6.3/PG-01] 路径不存在引导", "路径不存在" in check_md)
check("[T6.3/PG-01] 无 SKILL.md 引导", "SKILL.md" in check_md and "/skill-create" in check_md)

# skill-fix 前置条件 (PG-02)
fix_md = read_skill("skill-fix")
check("[T6.3/PG-02] skill-fix 含前置条件节", "前置条件" in fix_md)
check("[T6.3/PG-02] 路径不存在引导", "路径不存在" in fix_md)
check("[T6.3/PG-02] 含建议先 check 提示",
      "建议先" in fix_md or "/skill-check" in fix_md)

# skill-create 前置条件 (PG-03)
create_md = read_skill("skill-create")
check("[T6.3/PG-03] skill-create 含前置条件节", "前置条件" in create_md)
check("[T6.3/PG-03] 无参数引导", "无参数" in create_md or "请描述" in create_md)

# skill-audit 前置条件 (PG-04)
audit_md = read_skill("skill-audit")
check("[T6.3/PG-04] skill-audit 含前置条件节", "前置条件" in audit_md)
check("[T6.3/PG-04] ≥2 Skill 要求", "≥2" in audit_md)
check("[T6.3/PG-04] 不足引导", "/skill-create" in audit_md)

# ============================================================
# T6.4: 评估流程端到端 (Python CLI 代理验证)
# ============================================================
print()
print("=" * 60)
print("T6.4: 评估流程端到端 (CMD-01, Python CLI 代理)")
print("=" * 60)

result = subprocess.run(
    [sys.executable, CLI_SCRIPT, "check", "--path", SKILL_TARGET],
    capture_output=True, text=True,
)
stdout = result.stdout.strip()
check("[T6.4] check 模式退出码 0", result.returncode == 0)
check("[T6.4] 输出含评分结果",
      "PASS" in stdout or "FAIL" in stdout or "validate" in stdout.lower())
check("[T6.4] 输出含建议下一步", "建议下一步" in stdout)

# ============================================================
# T6.6: 推荐链端到端验证 [spec:prerequisite-guidance#PG-05]
# ============================================================
print()
print("=" * 60)
print("T6.6: 推荐链端到端验证 (PG-05)")
print("=" * 60)

# SKILL.md 推荐链
RECOMMENDATIONS_SKILL = {
    "skill-check": ["/skill-fix", "/skill-audit"],
    "skill-fix": ["/skill-check"],
    "skill-create": ["/skill-check"],
    "skill-audit": ["/skill-fix"],
}

for skill, expected_cmds in RECOMMENDATIONS_SKILL.items():
    content = read_skill(skill)
    has_section = "完成后推荐" in content or "建议下一步" in content
    check(f"[T6.6] {skill} 含推荐节", has_section)
    for cmd in expected_cmds:
        check(f"[T6.6] {skill} 推荐 {cmd}", cmd in content)

# CLI 推荐一致性
CLI_RECS = {
    "check": ["/skill-fix", "/skill-audit"],
    "fix": ["/skill-check"],
    "create": ["/skill-check"],
    "audit": ["/skill-fix"],
}

cli_script_content = read_file(CLI_SCRIPT)
for mode, expected_cmds in CLI_RECS.items():
    for cmd in expected_cmds:
        check(f"[T6.6] CLI {mode} 推荐 {cmd}",
              cmd in cli_script_content,
              f"CLI RECOMMENDATIONS[{mode}] 中未找到 {cmd}")

# ============================================================
# T6.7: 跨模式功能覆盖矩阵 [spec:test-coverage#SC-01~SC-06]
# ============================================================
print()
print("=" * 60)
print("T6.7: 跨模式功能覆盖矩阵")
print("=" * 60)

GUIDES_DIR = os.path.join(BASE_DIR, "core", "references")
GUIDES = {
    "check": os.path.join(GUIDES_DIR, "check-guide.md"),
    "fix": os.path.join(GUIDES_DIR, "fix-guide.md"),
    "audit": os.path.join(GUIDES_DIR, "audit-guide.md"),
    "create": os.path.join(GUIDES_DIR, "create-guide.md"),
}

# 功能 1: 安全扫描 (validate-security) — 4 个模式均应覆盖 [spec:test-coverage#SC-02]
for mode, path in GUIDES.items():
    content = read_file(path)
    check(f"[T6.7/SC-02] {mode} guide 含 validate-security",
          "validate-security" in content)

# 功能 2+3: 结构验证 + 元数据验证 [spec:test-coverage#SC-03]
# audit 模式豁免: 不涉及结构/元数据验证，这是 check/fix/create 的职责
for mode, path in GUIDES.items():
    if mode == "audit":
        # audit 模式不涉及结构/元数据验证，这是 check/fix/create 的职责
        continue
    content = read_file(path)
    check(f"[T6.7/SC-03] {mode} guide 含 validate-structure",
          "validate-structure" in content)
    check(f"[T6.7/SC-03] {mode} guide 含 validate-metadata",
          "validate-metadata" in content)

# 功能 4: 审计历史 [spec:test-coverage#SC-04]
# create 模式豁免: 不需要审计历史因为不涉及评估分数
for mode in EXPECTED_SKILLS:
    content = read_skill(mode)
    if mode == "skill-create":
        # create 模式不需要审计历史因为不涉及评估分数
        continue
    check(f"[T6.7/SC-04] {mode} SKILL.md 含审计历史",
          "审计历史" in content or "audit-history" in content)

# 功能 5: Decision Gate [spec:test-coverage#SC-05]
for mode in EXPECTED_SKILLS:
    content = read_skill(mode)
    check(f"[T6.7/SC-05] {mode} SKILL.md 含 Decision Gate",
          "Decision Gate" in content)

# 功能 6: 推荐链 (完成后推荐) [spec:test-coverage#SC-06]
for mode in EXPECTED_SKILLS:
    content = read_skill(mode)
    check(f"[T6.7/SC-06] {mode} SKILL.md 含完成后推荐",
          "完成后推荐" in content)

# ============================================================
# 汇总
# ============================================================
print()
print("=" * 60)
print(f"汇总: {passed} 通过, {failed} 失败")
print("=" * 60)

# ============================================================
# Claude Code 手动验证清单
# ============================================================
MANUAL_CHECKLIST = """
═══════════════════════════════════════════════════════════
Claude Code 手动验证清单 (需在安装插件后执行)
═══════════════════════════════════════════════════════════

T6.1 插件注册:
  [ ] /skill-craft 命令可见
  [ ] /skill-check 命令可见
  [ ] /skill-fix 命令可见
  [ ] /skill-create 命令可见
  [ ] /skill-audit 命令可见

T6.2 主入口调度:
  [ ] /skill-craft 评估这个 skill → 调度到 check
  [ ] /skill-craft 修复这个 skill → 调度到 fix
  [ ] /skill-craft 创建一个新 skill → 调度到 create
  [ ] /skill-craft 审计这个目录 → 调度到 audit
  [ ] /skill-craft 评估并修复 → 按 fix > check 优先级
  [ ] /skill-craft (无参数) → 输出可用模式列表

T6.3 前置条件阻断:
  [ ] /skill-check /tmp/empty-dir → 输出"不含 SKILL.md"引导，不继续
  [ ] /skill-check /tmp/nonexistent → 输出"路径不存在"，停止
  [ ] /skill-audit /tmp/single-skill → 输出"仅 1 个"引导，停止
  [ ] /skill-create (无参数) → 输出"请描述"，等待输入

T6.4 评估流程端到端:
  [ ] /skill-check skill-craft/ → 输出含评分、行动项、推荐链

T6.6 推荐链端到端:
  [ ] check 完成 → 推荐 /skill-fix 或 /skill-audit
  [ ] fix 完成 → 推荐 /skill-check
  [ ] create 完成 → 推荐 /skill-check
  [ ] audit 完成 → 推荐 /skill-fix
═══════════════════════════════════════════════════════════
"""
print(MANUAL_CHECKLIST)

sys.exit(0 if failed == 0 else 1)
