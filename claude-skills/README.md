# CAD skills for Claude Code

| Skill | Source | What it adds |
|---|---|---|
| `cad-rigor` | this folder | Purpose, spec table, math, parametric build, verification. `validate_stl.py` checks watertight, single body, size and wall thickness. |
| `openscad` | [andreahaku/openscad_claude_skill](https://github.com/andreahaku/openscad_claude_skill) | OpenSCAD with multi-angle preview feedback, printability checks, STL comparison and printer calibration. |
| `text-to-cad` | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) (MIT) | Plugin for STEP/STL/3MF output, manufacturability checks and engineering drawings. |

Run `bash claude-skills/install.sh` to install all three. The third-party skills are fetched from their authors and are not copied into this repo. The installer turns text-to-cad telemetry off.

For GPT, use `cad_agent.py` in the repo root.
