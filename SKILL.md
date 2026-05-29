---
name: espclaw-skill-writer
description: 'Create ESPCLAW hardware skills from DFRobot sensor repos. Use when user asks to generate/write/build an ESPCLAW skill, search DFRobot GitHub repos by sensor name, clone selected repo, and scaffold components/common/skill_builder/skills/<skill_id>.'
argument-hint: 'Sensor name, for example: bmm350, matrix lidar, ssd1306'
user-invocable: true
---

# ESPCLAW Skill Writer

## What This Skill Does
- Search `https://github.com/DFRobot` repositories by sensor name.
- Show matching repos for user selection.
- Clone the selected repo locally.
- Scaffold an ESPCLAW skill folder following the same style as `unihiker_expansion_battery`.

## When To Use
- User asks to create a new ESPCLAW sensor skill.
- User wants DFRobot repo discovery before coding the skill.
- User wants a repeatable workflow for clone + scaffold.

## Procedure
1. Run the helper script in list mode:
   - `python ./.github/skills/espclaw-skill-writer/scripts/create_espclaw_skill.py --sensor "<sensor name>" --list-only`
2. Present the matched repositories to the user and ask which repo to use.
3. Run the script again with selected repo:
   - `python ./.github/skills/espclaw-skill-writer/scripts/create_espclaw_skill.py --sensor "<sensor name>" --repo "DFRobot/<repo>"`
4. Or run once without `--repo` and choose by number interactively:
   - `python ./.github/skills/espclaw-skill-writer/scripts/create_espclaw_skill.py --sensor "<sensor name>"`
5. Read the generated files under `components/common/skill_builder/skills/<skill_id>/`.
6. Refine generated Lua script logic using the cloned library files (`.h`, `.cpp`, examples).

## Generated Output
- Skill folder: `components/common/skill_builder/skills/<skill_id>/`
- Main instruction: `SKILL.md`
- Lua script template: `scripts/read_sensor_data.lua`

## Assets
- Automation script: [create_espclaw_skill.py](./scripts/create_espclaw_skill.py)
- Workflow notes: [workflow.md](./references/workflow.md)
