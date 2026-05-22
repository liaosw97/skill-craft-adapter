#!/usr/bin/env python3
"""验证 --ref 参数格式和可达性

用法:
    python3 validate-references.py --ref <ref1> --ref <ref2> ... [--context <project-root>]

参数:
    --ref: 可重复，每个参数为一个参考值
    --context: 可选，项目根目录路径（用于 spec 引用映射），默认为当前目录

退出码:
    0: 全部通过或仅有警告
    1: 存在 FAIL 项
"""

import argparse
import re
import sys


SUPPORTED_EXTENSIONS = ['.md', '.txt', '.yaml', '.yml', '.json']
URL_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9+.-]*://')  # 任意 URL 协议
HTTP_PATTERN = re.compile(r'^https?://')  # 仅 http/https


def validate_url(ref: str) -> tuple:
    """验证 URL 格式

    Returns:
        (status, message): status 为 'PASS', 'WARN', 或 'FAIL'
    """
    if HTTP_PATTERN.match(ref):
        return ('PASS', 'URL 格式有效')
    return ('FAIL', 'URL 格式无效 (仅支持 http/https)')


def validate_local(ref: str, context: str) -> tuple:
    """验证本地文件存在性

    Returns:
        (status, message): status 为 'PASS', 'WARN', 或 'FAIL'
    """
    import os
    path = os.path.join(context, ref) if context and not os.path.isabs(ref) else ref
    if not os.path.exists(path):
        return ('FAIL', f'本地文件不存在: {ref}')
    ext = os.path.splitext(ref)[1].lower()
    if ext and ext not in SUPPORTED_EXTENSIONS:
        return ('WARN', f'文件扩展名不支持: {ext} (支持: {"/".join(SUPPORTED_EXTENSIONS)})')
    return ('PASS', '本地文件存在')


def validate_spec(ref: str, context: str) -> tuple:
    """验证 spec 引用存在性

    Returns:
        (status, message): status 为 'PASS', 'WARN', 或 'FAIL'
    """
    import os
    name = ref.replace('spec:', '')
    specs_dir = os.path.join(context, 'openspec', 'specs') if context else 'openspec/specs'
    if not os.path.isdir(specs_dir):
        return ('FAIL', 'spec 引用需要 openspec 工作区，当前项目无 openspec/specs/ 目录')
    path = os.path.join(specs_dir, f'{name}.md')
    if not os.path.exists(path):
        return ('FAIL', f'spec 引用文件不存在: openspec/specs/{name}.md')
    return ('PASS', 'spec 引用存在')


def main():
    parser = argparse.ArgumentParser(
        description='验证 --ref 参数格式和可达性'
    )
    parser.add_argument(
        '--ref',
        action='append',
        default=[],
        help='参考值（可重复）'
    )
    parser.add_argument(
        '--context',
        default='.',
        help='项目根目录路径'
    )
    args = parser.parse_args()

    if not args.ref:
        print('INFO: 无 --ref 参数，跳过验证')
        return 0

    has_fail = False
    for ref in args.ref:
        # 按优先级识别类型：spec: > URL 协议 > 本地文件
        if ref.startswith('spec:'):
            status, msg = validate_spec(ref, args.context)
        elif URL_PATTERN.match(ref):
            # 任意 URL 协议都走 URL 验证（非 http/https 会 FAIL）
            status, msg = validate_url(ref)
        else:
            status, msg = validate_local(ref, args.context)

        print(f'{status}: {msg}')
        if status == 'FAIL':
            has_fail = True

    return 1 if has_fail else 0


if __name__ == '__main__':
    sys.exit(main())
