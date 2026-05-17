# 测试清单

## 运行方法

所有测试仅依赖 Python 标准库，无需 `pip install`。

```bash
cd core/scripts/

# 运行全部测试
python test_runtime.py
python test_cli.py
python test_security.py

# 使用环境变量指定测试目标（默认为 ../skill-craft）
SKILL_TARGET=/path/to/skill python test_runtime.py
SKILL_TARGET=/path/to/skill python test_cli.py
```

## 测试覆盖矩阵

### test_runtime.py — 运行时验证 (T6.1~T6.4, T6.6)

| 测试组 | 覆盖项 | 场景 |
|--------|--------|------|
| T6.1 插件注册 | plugin.json 格式、4 Skill 存在、frontmatter name 一致 | SC-02 |
| T6.2 主入口调度 | 调度逻辑标题、4 模式关键词、优先级说明、空参数处理 | SC-03 |
| T6.3 前置条件阻断 | check/fix/create/audit 各自前置条件引导 | PG-01~PG-04 |
| T6.4 端到端 | check 模式 Python CLI 代理执行 | CMD-01 |
| T6.6 推荐链 | 4 Skill SKILL.md 推荐节 + CLI 推荐一致性 | PG-05 |

### test_cli.py — Python CLI 功能验证 (CLI-01~CLI-06)

| 场景 | 覆盖项 |
|------|--------|
| 场景 1 | check 单步执行：退出码、结构化输出、validate 脚本调用、推荐链 |
| 场景 2 | fix 单步执行 |
| 场景 3 | create 单步执行：创建清单、无 validate 脚本执行、推荐链 |
| 场景 4 | audit 前置条件：≥2 Skill 通过 / <2 Skill 阻断 |
| 场景 5 | 前置阻断：路径不存在 |
| 场景 6 | 前置阻断：SKILL.md 缺失 |
| 场景 7 | 无效模式 |
| 场景 8 | 串联执行：成功路径 |
| 场景 9 | 串联执行：失败跳过 |
| 场景 10 | 标准库约束 |

### test_security.py — 安全验证 (场景 1-11)

| 场景 | 覆盖项 |
|------|--------|
| 场景 1 | 凭证窃取检测 (SSH/AWS) — Critical |
| 场景 2 | 数据外泄检测 (requests/DNS) — Critical |
| 场景 3 | 后门检测 (authorized_keys/sudoers/crontab) — Critical |
| 场景 4 | 豁免：合法用途声明 |
| 场景 5 | 豁免：无合法声明保持 Critical |
| 场景 6 | 无安全模式匹配 — Pass |
| 场景 7 | 输出格式兼容性 |
| 场景 8 | 多文件扫描覆盖 |
| 场景 9 | 标准库约束 |
| 场景 10 | 边界条件（不存在/空目录/空文件/无 md） |
| 场景 11 | 命令注入/Prompt 注入/C2 通信 |

## 手动验证清单

见 `test_runtime.py` 末尾输出的 Claude Code 手动验证清单（T6.1~T6.6），需在安装插件后执行。
