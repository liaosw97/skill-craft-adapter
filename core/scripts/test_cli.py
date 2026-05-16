#!/usr/bin/env python3
"""T6.5 Python CLI 功能验证测试 — 4 个场景."""

import subprocess
import sys
import os

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skill-craft.py")
# 使用 skill-craft 上级目录作为有效 Skill 目标
SCRIPT_DIR = os.path.dirname(SCRIPT)
SKILL_TARGET = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "..", "skill-craft"))

passed = 0
failed = 0


def run_cli(args, expect_exit_0=True):
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


print("=" * 60)
print("场景 1: 单步执行 (CLI-01, CLI-03, CLI-04)")
print("=" * 60)

stdout, stderr, rc = run_cli(["check", "--path", SKILL_TARGET])
check("退出码为 0", rc == 0, f"实际退出码: {rc}")
check("包含 [编排] 模式: check", "[编排] 模式: check" in stdout, stdout[:200])
check("包含 [前置条件] ✅", "[前置条件] ✅" in stdout)
check("包含 validate-metadata.py 输出", "validate-metadata.py" in stdout)
check("包含 validate-structure.py 输出", "validate-structure.py" in stdout)
check("包含建议下一步", "建议下一步" in stdout)

print()
print("=" * 60)
print("场景 2: 前置阻断 (CLI-02)")
print("=" * 60)

stdout, stderr, rc = run_cli(["check", "--path", "/nonexistent/path/xyz"])
check("退出码为 0 (条件不满足非脚本故障)", rc == 0, f"实际退出码: {rc}")
check("包含 [前置条件] ❌", "[前置条件] ❌" in stdout)
check("包含 路径不存在", "路径不存在" in stdout)
check("包含引导信息", "引导" in stdout or "请检查" in stdout)

print()
print("=" * 60)
print("场景 3: 无效模式 (CLI-01)")
print("=" * 60)

stdout, stderr, rc = run_cli(["invalid", "--path", SKILL_TARGET])
check("退出码非 0", rc != 0, f"实际退出码: {rc}")
check("包含错误信息", stderr != "" or stdout != "", f"stdout={stdout[:100]}, stderr={stderr[:100]}")

print()
print("=" * 60)
print("场景 4: 串联执行 (CLI-05)")
print("=" * 60)

stdout, stderr, rc = run_cli(["check", "--path", SKILL_TARGET, "--flow", "check,fix"])
check("退出码为 0", rc == 0, f"实际退出码: {rc}")
check("包含流水线标记", "流水线" in stdout or "[编排] 流水线" in stdout, stdout[:200])
check("包含多步执行", "1/2" in stdout or "[1/2]" in stdout)

print()
print("=" * 60)
print(f"汇总: {passed} 通过, {failed} 失败")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
