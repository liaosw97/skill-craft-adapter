#!/usr/bin/env python3
"""Validate Skill security: detect Critical-level security patterns in Skill files.

Usage:
    python3 scripts/validate-security.py --path /path/to/skill-dir
Exit 0 = scan complete. Findings on stderr, summary on stdout.
"""

import argparse
import os
import re
import sys

# (name, regex, category, context_regex_or_None)
# context_regex: when set, both trigger AND context must match for a finding.
PATTERNS = [
    # Credential theft
    ("SSH密钥引用", r"~\/\.ssh\/id_rsa", "credential_theft", None),
    ("AWS凭证引用", r"~\/\.aws\/credentials", "credential_theft", None),
    ("环境变量密钥", r"os\.environ\.get\(['\"][\w_]*(KEY|SECRET|TOKEN|PASSWORD)[\w_]*['\"]", "credential_theft", None),
    (".env文件读取", r"dotenv|load_dotenv|\.env['\"\s/]", "credential_theft", None),
    # Data exfiltration (two-condition: trigger + sensitive data context)
    ("HTTP外发+敏感数据", r"requests\.post|urllib\.request|httpx|fetch\b", "data_exfiltration",
     r"os\.environ|\.env|API_KEY|SECRET|TOKEN|PASSWORD|credentials|private_key"),
    ("Base64+DNS隐蔽外泄", r"base64.*dns|dns.*base64", "data_exfiltration",
     r"os\.environ|\.env|API_KEY|SECRET|TOKEN|PASSWORD|credentials"),
    ("curl数据外泄", r"curl.*(-d|--data|-F|--form)", "data_exfiltration",
     r"os\.environ|API_KEY|SECRET|TOKEN|PASSWORD|credentials|private_key"),
    # Backdoor
    ("authorized_keys写入", r"authorized_keys", "backdoor", None),
    ("sudoers修改", r"sudoers", "backdoor", None),
    ("crontab持久化", r"crontab", "backdoor", None),
    # Command injection
    ("eval动态执行", r"\beval\s*\(", "command_injection", None),
    ("subprocess shell注入", r"subprocess\.\w+.*shell\s*=\s*True", "command_injection", None),
    # Prompt injection
    ("系统提示覆盖", r"(ignore|忽略|disregard).*(previous|above|前述|以上).*(instructions?|指令|指示)", "prompt_injection", None),
    ("角色劫持", r"(you are now|你现在|act as|扮演).*(root|admin|sudo|administrator|超级用户|管理员)", "prompt_injection", None),
    # C2 communication
    ("反向Shell", r"(nc\s+-|ncat|netcat|/dev/tcp)", "c2_communication", None),
    ("WebSocket C2", r"websocket.*connect.*(ngrok|serveo|localhost|\d+\.\d+\.\d+\.\d+)", "c2_communication", None),
]

CATEGORY_LABELS = {
    "credential_theft": "凭证窃取", "data_exfiltration": "数据外泄",
    "backdoor": "后门植入", "command_injection": "命令注入",
    "prompt_injection": "Prompt注入", "c2_communication": "C2通信",
}

EXEMPTION_MAP = {
    "credential_theft": ["ssh", "credential", "密钥", "认证", "密码管理", "aws", "云"],
    "data_exfiltration": ["部署", "deploy", "监控", "日志", "log", "telemetry"],
    "backdoor": ["安全审计", "security audit", "漏洞扫描", "vulnerability"],
    "command_injection": ["repl", "解释器", "interpreter", "构建", "build", "编译", "compile"],
    "prompt_injection": ["安全审计", "security audit", "测试", "test"],
    "c2_communication": ["网络", "network", "调试", "debug", "开发", "develop", "本地", "local"],
}


def parse_frontmatter(skill_path):
    """Extract description from SKILL.md frontmatter.

    NOTE: This function overlaps with validate-metadata.py's parse_frontmatter.
    Changes here should be synced with that script.
    """
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.isfile(skill_md):
        return None
    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    fm = content[3:end]
    for i, line in enumerate(fm.splitlines()):
        if line.startswith("description:"):
            val = line.split(":", 1)[1].strip()
            if val and val != "|":
                return val
            parts = []
            for subsequent in fm.splitlines()[i + 1:]:
                if subsequent.startswith(("  ", "\t")):
                    parts.append(subsequent.strip())
                else:
                    break
            return " ".join(p for p in parts if p)
    return None


def check_exemption(description, category):
    """Check if description matches exemption keywords for the category."""
    if not description:
        return False
    desc_lower = description.lower()
    return any(kw.lower() in desc_lower for kw in EXEMPTION_MAP.get(category, []))


def scan_file(filepath):
    """Scan a single file for security patterns. Returns list of findings."""
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except (IOError, OSError):
        return findings
    full_content = "".join(lines)

    for name, regex, category, ctx_regex in PATTERNS:
        if ctx_regex:
            # Two-condition: trigger AND context must both be present
            trigger_hits = list(re.finditer(regex, full_content, re.IGNORECASE))
            if not trigger_hits or not re.search(ctx_regex, full_content, re.IGNORECASE):
                continue
            for m in trigger_hits:
                ln = full_content[:m.start()].count("\n") + 1
                findings.append((name, category, m.group(0), filepath, ln))
        else:
            for i, line in enumerate(lines, 1):
                m = re.search(regex, line, re.IGNORECASE)
                if m:
                    findings.append((name, category, m.group(0), filepath, i))
    return findings


def get_files_to_scan(skill_path):
    """Collect SKILL.md, references/*.md, scripts/*.py (flat, no recursion)."""
    files = []
    skill_md = os.path.join(skill_path, "SKILL.md")
    if os.path.isfile(skill_md):
        files.append(skill_md)
    for subdir, ext in [("references", ".md"), ("scripts", ".py")]:
        d = os.path.join(skill_path, subdir)
        if os.path.isdir(d):
            files.extend(
                os.path.join(d, f) for f in sorted(os.listdir(d))
                if f.endswith(ext) and os.path.isfile(os.path.join(d, f))
            )
    return files


def main():
    parser = argparse.ArgumentParser(description="Validate Skill security patterns")
    parser.add_argument("--path", required=True, help="Path to Skill directory")
    args = parser.parse_args()
    skill_path = os.path.normpath(args.path)

    if not os.path.isdir(skill_path):
        print(f"[Error] 路径不存在: {args.path}", file=sys.stderr)
        sys.exit(0)

    if not os.path.isfile(os.path.join(skill_path, "SKILL.md")):
        print("[Error] 目标目录不含 SKILL.md", file=sys.stderr)
        sys.exit(0)

    description = parse_frontmatter(skill_path)
    all_findings = []
    for fp in get_files_to_scan(skill_path):
        all_findings.extend(scan_file(fp))

    critical_count = 0
    for name, category, match_text, filepath, line_num in all_findings:
        rel = os.path.relpath(filepath, skill_path).replace("\\", "/")
        if check_exemption(description, category):
            print(f'[Info] [豁免] {name}: {match_text} ({rel}:{line_num}) — 功能声明匹配: "{description}"', file=sys.stderr)
        else:
            label = CATEGORY_LABELS.get(category, category)
            note = " — 无合法用途声明" if description else ""
            print(f"[Critical] {label}: {match_text} 引用 ({rel}:{line_num}){note}", file=sys.stderr)
            critical_count += 1

    print(f"Security scan: {critical_count} Critical findings")
    sys.exit(0)


if __name__ == "__main__":
    main()
