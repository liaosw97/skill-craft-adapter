#!/usr/bin/env python3
"""Skill Craft Adapter CLI — 编排 Skill 质量检测流程.

Usage:
    python skill-craft.py check --path <target>
    python skill-craft.py fix --path <target>
    python skill-craft.py create --path <target>
    python skill-craft.py audit --path <target>
    python skill-craft.py check --path <target> --flow check,fix
"""
import argparse
import os
import subprocess
import sys

MODES = ["check", "fix", "create", "audit"]

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def check_prerequisites(mode, path):
    """Check prerequisites for the given mode. Returns (passed, message)."""
    if mode in ("check", "fix"):
        if not os.path.exists(path):
            msg = f"路径不存在：{path}"
            return False, msg, f"请检查路径是否正确。如需创建新 Skill，请运行 /skill-create"
        skill_md = os.path.join(path, "SKILL.md")
        if not os.path.isfile(skill_md):
            msg = f"目标目录不含 SKILL.md，不是有效的 Skill 目录"
            return False, msg, "如需创建新 Skill，请运行 /skill-create"
        if mode == "fix":
            return True, "前置条件通过", None
        return True, "前置条件通过", None

    elif mode == "create":
        return True, "前置条件通过（create 模式无路径前置）", None

    elif mode == "audit":
        if not os.path.exists(path):
            msg = f"路径不存在：{path}"
            return False, msg, "请检查路径是否正确"
        skill_count = 0
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)
            if os.path.isfile(os.path.join(entry_path, "SKILL.md")):
                skill_count += 1
            elif os.path.isfile(entry_path) and entry == "SKILL.md":
                skill_count += 1
        if skill_count < 2:
            msg = f"目录下仅 {skill_count} 个 Skill，审计需要 ≥2 个"
            return False, msg, "请先运行 /skill-create 创建更多 Skill"
        return True, f"前置条件通过（发现 {skill_count} 个 Skill）", None

    return True, "前置条件通过", None


def run_validation(path):
    """Run validate-metadata.py, validate-structure.py, and validate-security.py on the target path."""
    results = []
    scripts = ["validate-metadata.py", "validate-structure.py", "validate-security.py"]
    for script in scripts:
        script_path = os.path.join(SCRIPTS_DIR, script)
        if not os.path.isfile(script_path):
            # Graceful degradation for security script, hard fail for others
            if script == "validate-security.py":
                results.append({
                    "script": script,
                    "stdout": "⚠️ 降级: validate-security.py 未找到，安全扫描跳过",
                    "stderr": "",
                    "returncode": 0,
                })
            else:
                results.append({
                    "script": script,
                    "stdout": "",
                    "stderr": f"[编排] 脚本未找到: {script_path}",
                    "returncode": -1,
                })
            continue
        result = subprocess.run(
            [sys.executable, script_path, "--path", path],
            capture_output=True, text=True,
        )
        results.append({
            "script": script,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        })
    return results


def find_skill_dirs(path):
    """Find subdirectories containing SKILL.md under the given path."""
    dirs = []
    for entry in sorted(os.listdir(path)):
        entry_path = os.path.join(path, entry)
        if os.path.isdir(entry_path) and os.path.isfile(os.path.join(entry_path, "SKILL.md")):
            dirs.append(entry_path)
    return dirs


RECOMMENDATIONS = {
    "check": "→ 建议下一步: /skill-fix <path>（修复发现的问题）或 /skill-audit <path>（系统级审计）",
    "fix": "→ 建议下一步: /skill-check <path>（验证修复效果）",
    "create": "→ 建议下一步: /skill-check <path>（评估新 Skill 质量）",
    "audit": "→ 建议下一步: /skill-fix <path>（修复具体 Skill 问题）",
}


def print_report(mode, path, prereq_result, validation_results=None):
    """Print the final structured report with guidance."""
    passed, prereq_msg, guidance = prereq_result

    print(f"\n{'='*50}")
    print(f"[编排] 模式: {mode}")
    print(f"[编排] 目标: {path}")
    print(f"{'='*50}")

    if not passed:
        print(f"\n[前置条件] ❌ {prereq_msg}")
        if guidance:
            print(f"→ 引导: {guidance}")
        print(f"\n{RECOMMENDATIONS.get(mode, '')}")
        return

    print(f"\n[前置条件] ✅ {prereq_msg}")

    if validation_results:
        for i, vr in enumerate(validation_results, 1):
            print(f"\n--- [{i}/{len(validation_results)}] {vr['script']} ---")
            if vr["stdout"]:
                print(vr["stdout"])
            if vr["stderr"]:
                print(vr["stderr"], file=sys.stderr)

    print(f"\n{RECOMMENDATIONS.get(mode, '')}")


def run_single(mode, path):
    """Execute a single mode on the target path."""
    prereq = check_prerequisites(mode, path)
    passed = prereq[0]

    if not passed:
        print_report(mode, path, prereq)
        return False

    validation_results = None

    if mode in ("check", "fix"):
        validation_results = run_validation(path)

    elif mode == "audit":
        skill_dirs = find_skill_dirs(path)
        validation_results = []
        for sd in skill_dirs:
            dir_results = run_validation(sd)
            for vr in dir_results:
                vr["script"] = f"{vr['script']} ({os.path.basename(sd)})"
            validation_results.extend(dir_results)

    elif mode == "create":
        validation_results = [{
            "script": "create-checklist",
            "stdout": "Skill 创建检查清单:\n"
                      "  1. 确定用途描述和触发条件\n"
                      "  2. 选择规模（轻量/中等/重型）\n"
                      "  3. 创建 SKILL.md（含 frontmatter）\n"
                      "  4. 创建 references/ 目录和参考文档\n"
                      "  5. 运行 validate-metadata.py 和 validate-structure.py 验证",
            "stderr": "",
            "returncode": 0,
        }]

    print_report(mode, path, prereq, validation_results)
    return True


def run_flow(modes, path):
    """Execute multiple modes in sequence, continuing even if one fails."""
    total = len(modes)
    for i, mode in enumerate(modes, 1):
        print(f"\n{'#'*50}")
        print(f"[编排] 流水线 [{i}/{total}]: {mode}")
        print(f"{'#'*50}")
        prereq = check_prerequisites(mode, path)
        if not prereq[0]:
            print(f"[{i}/{total}] ⏭ SKIPPED: 前置条件未满足 — {prereq[1]}")
            continue
        run_single(mode, path)


def main():
    parser = argparse.ArgumentParser(description="Skill Craft Adapter CLI")
    parser.add_argument("mode", choices=MODES, help="执行模式")
    parser.add_argument("--path", required=True, help="目标 Skill 路径")
    parser.add_argument("--flow", help="串联模式 (如 check,fix)")
    args = parser.parse_args()

    if args.flow:
        modes = [m.strip() for m in args.flow.split(",")]
        invalid = [m for m in modes if m not in MODES]
        if invalid:
            print(f"未知模式: {', '.join(invalid)}。可用模式: {', '.join(MODES)}", file=sys.stderr)
            sys.exit(1)
        run_flow(modes, args.path)
    else:
        run_single(args.mode, args.path)


if __name__ == "__main__":
    main()
