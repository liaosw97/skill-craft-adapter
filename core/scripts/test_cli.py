#!/usr/bin/env python3
"""T6.5 Python CLI 功能验证测试 — 完整场景覆盖 (CLI-01~CLI-06)."""

import ast
import os
import subprocess
import sys
import tempfile

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skill-craft.py")
SCRIPT_DIR = os.path.dirname(SCRIPT)
SKILL_TARGET = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "..", "skill-craft"))

passed = 0
failed = 0
skipped = 0


def run_cli(args):
    """Run the CLI and return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [sys.executable, SCRIPT] + args,
        capture_output=True, text=True,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


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


def make_fixture(structure):
    """Create temp dir with given structure. structure = dict of {path: content}."""
    tmpdir = tempfile.mkdtemp(prefix="sdd-test-")
    for relpath, content in structure.items():
        fpath = os.path.join(tmpdir, relpath)
        os.makedirs(os.path.dirname(fpath), exist_ok=True)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
    return tmpdir


# ============================================================
# 场景 1: check 单步执行 (CLI-01-a, CLI-01-b, CLI-03-a, CLI-04-a, CLI-04-b)
# ============================================================
print("=" * 60)
print("场景 1: check 单步执行 (CLI-01, CLI-03, CLI-04)")
print("=" * 60)

stdout, stderr, rc = run_cli(["check", "--path", SKILL_TARGET])
check("[CLI-01-a] check 退出码 0", rc == 0, f"实际退出码: {rc}")
check("[CLI-01-b] 结构化输出含 [编排] 模式: check", "[编排] 模式: check" in stdout)
check("[CLI-01-b] 含 [前置条件] ✅", "[前置条件] ✅" in stdout)
check("[CLI-03-a] 含 validate-metadata.py 输出", "validate-metadata.py" in stdout)
check("[CLI-03-a] 含 validate-structure.py 输出", "validate-structure.py" in stdout)
check("[CLI-04-a] 含建议下一步", "建议下一步" in stdout)
check("[CLI-04-b] 建议指向 /skill-fix", "/skill-fix" in stdout)

# ============================================================
# 场景 2: fix 模式 (CLI-01-a 补全)
# ============================================================
print()
print("=" * 60)
print("场景 2: fix 单步执行 (CLI-01-a 补全)")
print("=" * 60)

stdout, stderr, rc = run_cli(["fix", "--path", SKILL_TARGET])
check("[CLI-01-a] fix 退出码 0", rc == 0, f"实际退出码: {rc}")
check("[CLI-01-a] fix 含 [编排] 模式: fix", "[编排] 模式: fix" in stdout)
check("[CLI-03-a] fix 调用验证脚本", "validate-metadata.py" in stdout)

# ============================================================
# 场景 3: create 模式 (CLI-03-b)
# ============================================================
print()
print("=" * 60)
print("场景 3: create 模式 (CLI-03-b)")
print("=" * 60)

stdout, stderr, rc = run_cli(["create", "--path", SKILL_TARGET])
check("[CLI-01-a] create 退出码 0", rc == 0, f"实际退出码: {rc}")
check("[CLI-03-b] create 输出创建清单", "创建检查清单" in stdout or "checklist" in stdout.lower(),
      f"stdout[:200]={stdout[:200]}")
check("[CLI-03-b] create 无 validate 脚本执行头",
      not any(f"validate-{v}.py" in line and line.strip().startswith("---")
              for line in stdout.split("\n") for v in ["metadata", "structure"]))
check("[CLI-04-b] create 建议指向 /skill-check", "/skill-check" in stdout)

# ============================================================
# 场景 4: audit 模式 (CLI-03-c, CLI-03-d)
# ============================================================
print()
print("=" * 60)
print("场景 4: audit 模式 (CLI-03-c, CLI-03-d)")
print("=" * 60)

# 4a: audit 前置条件 — ≥2 个 Skill
multi_skill = make_fixture({
    "a/SKILL.md": "---\nname: skill-a\n---\n# A",
    "b/SKILL.md": "---\nname: skill-b\n---\n# B",
})
stdout, stderr, rc = run_cli(["audit", "--path", multi_skill])
check("[CLI-03-d] audit ≥2 Skill 通过前置", rc == 0, f"退出码: {rc}")
check("[CLI-03-d] 发现 2 个 Skill", "2 个 Skill" in stdout, stdout[:200])
check("[CLI-03-c] audit 遍历子目录", "skill-a" in stdout or "skill-b" in stdout or "a)" in stdout,
      stdout[:300])

# 4b: audit 前置条件 — <2 个 Skill
single_skill = make_fixture({
    "only/SKILL.md": "---\nname: only-one\n---\n# Only",
})
stdout, stderr, rc = run_cli(["audit", "--path", single_skill])
check("[CLI-03-d] audit <2 Skill 阻断", rc == 0)
check("[CLI-03-d] 含前置条件 ❌", "[前置条件] ❌" in stdout)
check("[CLI-03-d] 提示需要 ≥2", "≥2" in stdout, stdout[:200])

# ============================================================
# 场景 5: 前置阻断 — 路径不存在 (CLI-02-a)
# ============================================================
print()
print("=" * 60)
print("场景 5: 前置阻断 — 路径不存在 (CLI-02-a)")
print("=" * 60)

stdout, stderr, rc = run_cli(["check", "--path", "/nonexistent/path/xyz"])
check("[CLI-02-a] 退出码 0", rc == 0, f"实际退出码: {rc}")
check("[CLI-02-a] 含 [前置条件] ❌", "[前置条件] ❌" in stdout)
check("[CLI-02-a] 含 路径不存在", "路径不存在" in stdout)
check("[CLI-02-a] 含引导信息", "引导" in stdout or "请检查" in stdout or "/skill-create" in stdout)

# ============================================================
# 场景 6: 前置阻断 — SKILL.md 缺失 (CLI-02-b)
# ============================================================
print()
print("=" * 60)
print("场景 6: 前置阻断 — SKILL.md 缺失 (CLI-02-b)")
print("=" * 60)

no_skill_dir = tempfile.mkdtemp(prefix="sdd-no-skill-")
stdout, stderr, rc = run_cli(["check", "--path", no_skill_dir])
check("[CLI-02-b] 退出码 0", rc == 0, f"实际退出码: {rc}")
check("[CLI-02-b] 含 [前置条件] ❌", "[前置条件] ❌" in stdout)
check("[CLI-02-b] 提示不含 SKILL.md", "SKILL.md" in stdout, stdout[:200])
check("[CLI-02-b] 引导 /skill-create", "/skill-create" in stdout, stdout[:200])

# ============================================================
# 场景 7: 无效模式 (CLI-01-c)
# ============================================================
print()
print("=" * 60)
print("场景 7: 无效模式 (CLI-01-c)")
print("=" * 60)

stdout, stderr, rc = run_cli(["invalid", "--path", SKILL_TARGET])
check("[CLI-01-c] 退出码非 0", rc != 0, f"实际退出码: {rc}")
# 注：argparse choices 机制返回退出码 2 + 英文错误，与 spec 有偏差
# 此处验证当前实现行为，偏差已在 spec-compliance-batch6.md 记录
check("[CLI-01-c] 含错误信息 (argparse 格式)",
      "invalid choice" in stderr.lower() or "error" in stderr.lower(),
      f"stderr={stderr[:100]}")

# ============================================================
# 场景 8: 串联执行成功路径 (CLI-05-a, CLI-05-b)
# ============================================================
print()
print("=" * 60)
print("场景 8: 串联执行 — 成功路径 (CLI-05-a, CLI-05-b)")
print("=" * 60)

stdout, stderr, rc = run_cli(["check", "--path", SKILL_TARGET, "--flow", "check,fix"])
check("[CLI-05-a] 退出码 0", rc == 0, f"实际退出码: {rc}")
check("[CLI-05-a] 含流水线标记", "流水线" in stdout)
check("[CLI-05-a] 按序执行含 [1/2] 和 [2/2]", "[1/2]" in stdout and "[2/2]" in stdout,
      stdout[:300])

# ============================================================
# 场景 9: 串联执行失败路径 (CLI-05-c)
# ============================================================
print()
print("=" * 60)
print("场景 9: 串联执行 — 失败跳过 (CLI-05-c)")
print("=" * 60)

stdout, stderr, rc = run_cli(["check", "--path", "/nonexistent/xyz", "--flow", "check,fix"])
check("[CLI-05-c] 退出码 0", rc == 0, f"实际退出码: {rc}")
check("[CLI-05-c] 含 SKIPPED 标记", "SKIPPED" in stdout, stdout[:300])
check("[CLI-05-c] 前置条件未满足", "前置条件未满足" in stdout, stdout[:300])
check("[CLI-05-c] 两步均被跳过", stdout.count("SKIPPED") >= 2, f"SKIPPED 出现 {stdout.count('SKIPPED')} 次")

# ============================================================
# 场景 10: 标准库约束 (CLI-06-a)
# ============================================================
print()
print("=" * 60)
print("场景 10: 标准库约束 (CLI-06-a)")
print("=" * 60)

STDLIB_MODULES = {
    'os', 're', 'sys', 'argparse', 'subprocess', 'json', 'pathlib',
    '__future__', 'io', 'textwrap', 'shutil', 'glob', 'fnmatch',
    'collections', 'datetime', 'math', 'time', 'tempfile', 'ast',
}
non_stdlib = []
with open(SCRIPT, encoding="utf-8") as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            mod = alias.name.split(".")[0]
            if mod not in STDLIB_MODULES:
                non_stdlib.append(alias.name)
check("[CLI-06-a] 仅使用标准库 import", len(non_stdlib) == 0,
      f"非标准库: {non_stdlib}" if non_stdlib else "")

# ============================================================
# 汇总
# ============================================================
print()
print("=" * 60)
print(f"汇总: {passed} 通过, {failed} 失败, {skipped} 跳过")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
