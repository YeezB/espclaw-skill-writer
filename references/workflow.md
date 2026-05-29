# Workflow Details

## Script Overview
`create_espclaw_skill.py` performs four tasks:
1. Query DFRobot repositories from GitHub API.
2. Filter by sensor keyword (`--sensor`).
3. Clone selected repository.
4. Generate an ESPCLAW skill scaffold.

## Commands
List candidate repos only:
```powershell
python ./.github/skills/espclaw-skill-writer/scripts/create_espclaw_skill.py --sensor "bmm350" --list-only
```

Clone + scaffold using selected repo:
```powershell
python ./.github/skills/espclaw-skill-writer/scripts/create_espclaw_skill.py --sensor "bmm350" --repo "DFRobot/DFRobot_BMM350"
```

Interactive select + clone + scaffold in one command:
```powershell
python ./.github/skills/espclaw-skill-writer/scripts/create_espclaw_skill.py --sensor "bmm350"
```

## Generated Layout
```text
components/common/skill_builder/skills/<skill_id>/
  SKILL.md
  scripts/read_sensor_data.lua
```

## Notes
- Script uses Python standard library only.
- If destination clone folder already exists, clone is skipped and existing folder is reused.
- If skill folder exists, script updates files in place.
