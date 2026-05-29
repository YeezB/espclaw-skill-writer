# ESPCLAW Skill Writer

[English](README.md)

ESPCLAW Skill Writer 用于从 DFRobot 传感器仓库快速生成 ESPCLAW 硬件技能（skill）。

它会自动完成以下流程：
- 按传感器关键词搜索 DFRobot GitHub 仓库。
- 让你选择匹配的仓库。
- 将选中的仓库克隆到本地。
- 在 ESPCLAW 技能目录下生成新的技能骨架。

## 生成内容

脚本执行成功后会创建：

- 技能目录：`components/common/skill_builder/skills/<skill_id>/`
- 技能说明：`SKILL.md`
- Lua 脚本模板：`scripts/read_sensor_data.lua`

## 环境要求

- Python 3.8+
- Git
- 可访问 GitHub 的网络环境

脚本只依赖 Python 标准库，不需要额外安装第三方包。

## 项目结构

```text
espclaw-skill-writer/
  SKILL.md
  references/
    workflow.md
  scripts/
    create_espclaw_skill.py
```

## 使用方法

请在本项目根目录执行命令。

### 1) 仅列出候选仓库

```powershell
python ./scripts/create_espclaw_skill.py --sensor "bmm350" --list-only
```

### 2) 指定仓库并生成

```powershell
python ./scripts/create_espclaw_skill.py --sensor "bmm350" --repo "DFRobot/DFRobot_BMM350"
```

### 3) 交互式选择（单条命令）

```powershell
python ./scripts/create_espclaw_skill.py --sensor "bmm350"
```

## 可选参数

- `--clone-root`：克隆仓库存放目录。默认：`third_party/dfrobot`
- `--skills-root`：技能输出根目录。默认：`components/common/skill_builder/skills`
- `--force`：覆盖已存在的骨架文件

## 推荐流程

1. 用传感器名称搜索。
2. 查看并选择合适仓库。
3. 克隆仓库并生成技能骨架。
4. 打开生成的 `SKILL.md` 与 Lua 脚本。
5. 参考克隆仓库中的 `.h`、`.cpp`、示例代码，替换 Lua 占位逻辑。

## 说明

- 如果克隆目录已存在，脚本会跳过克隆并复用该目录。
- 如果技能目录已存在，使用 `--force` 可覆盖更新。
- GitHub API 限流时，脚本会自动回退到 HTML 搜索方式。

## 相关文件

- 技能定义： [SKILL.md](SKILL.md)
- 流程说明： [references/workflow.md](references/workflow.md)
- 生成脚本： [scripts/create_espclaw_skill.py](scripts/create_espclaw_skill.py)
