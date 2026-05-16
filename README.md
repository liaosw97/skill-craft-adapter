# Skill Craft Adapter

Claude Code Skill 质量评估插件——基于加权评分框架（8 模块检查、7 反模式评估、3 完备性原则、决策门），用于评估、修复、创建和审计 Claude Code Skill。

本插件基于 [skill-craft](https://github.com/3stoneBrother/skill-craft) 项目改编，转为标准 Claude Code 插件格式。

## 安装

### 方式一：Marketplace 安装（推荐）

```bash
# 1. 添加 Marketplace 源（在 Claude Code 中执行）
/plugin marketplace add liaosw97/skill-craft-adapter

# 2. 安装插件
/plugin install skill-craft-adapter@skill-craft-adapter
```

安装后 5 个命令自动注册，无需额外配置。

### 方式二：CLI 安装

```bash
# 通过 Claude Code CLI 安装（全局）
claude plugin install skill-craft-adapter@skill-craft-adapter --scope user

# 项目级安装
claude plugin install skill-craft-adapter@skill-craft-adapter --scope project
```

`--scope` 可选值：`user`（全局，默认）、`project`（项目级）、`local`（本地级）。

### 方式三：手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/liaosw97/skill-craft-adapter.git

# 2. 使用 --plugin-dir 快速加载（推荐）
claude --plugin-dir ./skill-craft-adapter
```

也可以将目录复制到 `~/.claude/plugins/skill-craft-adapter/`，重启 Claude Code 后生效。

## 使用说明

插件提供 5 个命令：

| 命令 | 用途 | 示例 |
|------|------|------|
| `/skill-craft` | 主入口，按关键词调度到子命令 | `/skill-craft 评估这个 skill` |
| `/skill-check` | 评估单个 Skill 质量 | `/skill-check /path/to/skill` |
| `/skill-fix` | 评估并修复 Skill 缺陷 | `/skill-fix /path/to/skill` |
| `/skill-create` | 创建符合质量标准的新 Skill | `/skill-create 代码安全审计` |
| `/skill-audit` | 多 Skill 系统级一致性审计 | `/skill-audit /path/to/skills/` |

### 主入口调度

`/skill-craft` 根据输入关键词自动匹配模式：

- **评估/检查/check** → 调度到 `/skill-check`
- **修复/fix** → 调度到 `/skill-fix`
- **创建/新建/create** → 调度到 `/skill-create`
- **审计/audit** → 调度到 `/skill-audit`

多模式匹配时按优先级：fix > check > create > audit。

### 命令推荐链

每个命令完成后会推荐下一步操作：

```
skill-check → /skill-fix（修复）或 /skill-audit（审计）
skill-fix   → /skill-check（验证修复效果）
skill-create → /skill-check（评估新 Skill）
skill-audit → /skill-fix（修复具体问题）
```

## Python CLI

除 Claude Code 命令外，还提供独立 Python CLI 用于编排检测流程：

```bash
# 进入脚本目录
cd core/scripts/

# 单步执行
python skill-craft.py check --path /path/to/skill
python skill-craft.py fix --path /path/to/skill
python skill-craft.py create --path /path/to/skill
python skill-craft.py audit --path /path/to/skills/

# 串联执行（check 后自动 fix）
python skill-craft.py check --path /path/to/skill --flow check,fix

# 前置条件检查
python skill-craft.py check --path /nonexistent  # 输出引导信息
```

CLI 仅使用 Python 标准库，无需 `pip install`。

## 质量框架

评分采用加权维度：

| 维度 | 权重 | 说明 |
|------|------|------|
| 8 模块检查 | 55% | 触发条件、行为规则、工具优先级等 8 个必含模块 |
| 7 反模式评估 | 20% | 检测常见 Skill 设计缺陷 |
| 3 完备性原则 | 15% | 覆盖度、一致性、可操作性 |
| 决策门 | 10% | 关键决策点检查 |

## 验证脚本

```bash
# 验证 Skill 前置元数据（名称格式、描述质量）
python core/scripts/validate-metadata.py --path /path/to/skill

# 验证 Skill 结构（8 模块、行数预算、引用完整性）
python core/scripts/validate-structure.py --path /path/to/skill
```

## 致谢

本插件改编自 [skill-craft](https://github.com/3stoneBrother/skill-craft) 原始项目，感谢原作者的贡献。

## License

MIT
