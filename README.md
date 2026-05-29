# ESPCLAW Skill Writer

[中文版本](README_cn.md)

ESPCLAW Skill Writer helps you generate an ESPCLAW hardware skill from a DFRobot sensor repository.

It automates these steps:
- Search DFRobot GitHub repositories by sensor keyword.
- Let you choose a matching repository.
- Clone the selected repository to local workspace.
- Scaffold a new skill folder under the ESPCLAW skills tree.

## What It Generates

After a successful run, the script creates:

- Skill folder: `components/common/skill_builder/skills/<skill_id>/`
- Skill instruction: `SKILL.md`
- Lua script template: `scripts/read_sensor_data.lua`

## Requirements

- Python 3.8+
- Git
- Network access to GitHub

No third-party Python packages are required (standard library only).

## Project Structure

```text
espclaw-skill-writer/
  SKILL.md
  references/
    workflow.md
  scripts/
    create_espclaw_skill.py
```

## Usage

Run from the skill project root.

### 1) List candidate repositories

```powershell
python ./scripts/create_espclaw_skill.py --sensor "bmm350" --list-only
```

### 2) Generate using a specific repo

```powershell
python ./scripts/create_espclaw_skill.py --sensor "bmm350" --repo "DFRobot/DFRobot_BMM350"
```

### 3) Interactive selection (one command)

```powershell
python ./scripts/create_espclaw_skill.py --sensor "bmm350"
```

## Optional Parameters

- `--clone-root`: local folder for cloned repositories. Default: `third_party/dfrobot`
- `--skills-root`: output root for generated skills. Default: `components/common/skill_builder/skills`
- `--force`: overwrite existing scaffold files

## Typical Workflow

1. Search by sensor name.
2. Review and select a repository.
3. Clone repository and scaffold the skill.
4. Open generated `SKILL.md` and Lua file.
5. Replace placeholder Lua logic using the cloned library (`.h`, `.cpp`, examples).

## Notes

- If clone destination already exists, clone is skipped and reused.
- If skill directory exists, run with `--force` to update scaffold files.
- If GitHub API is rate-limited, the script falls back to HTML search automatically.

## Related Files

- Skill definition: [SKILL.md](SKILL.md)
- Workflow reference: [references/workflow.md](references/workflow.md)
- Generator script: [scripts/create_espclaw_skill.py](scripts/create_espclaw_skill.py)
