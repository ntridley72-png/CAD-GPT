#!/usr/bin/env bash
# Installs every CAD skill used with this repo. Run from the repo root: bash claude-skills/install.sh
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS="$HOME/.claude/skills"
mkdir -p "$SKILLS"

echo "1/4 cad-rigor (spec, math, build, verify workflow + STL validator)"
rm -rf "$SKILLS/cad-rigor" && cp -R "$HERE/cad-rigor" "$SKILLS/cad-rigor"

echo "2/4 openscad skill (andreahaku/openscad_claude_skill)"
if [ -d "$SKILLS/openscad/.git" ]; then git -C "$SKILLS/openscad" pull -q
else git clone -q https://github.com/andreahaku/openscad_claude_skill "$SKILLS/openscad"; fi

echo "3/4 text-to-cad plugin (earthtojake/text-to-cad); needs the claude CLI and uv"
if command -v claude >/dev/null && command -v uvx >/dev/null; then
  claude plugin marketplace add earthtojake/text-to-cad#latest || true
  claude plugin install text-to-cad@earthtojake || true
  uvx cadgen telemetry off   # it sends usage stats by default; remove this line to keep them on
else
  echo "   skipped: install the claude CLI and uv (https://docs.astral.sh/uv/), then re-run"
fi

echo "4/4 python packages for cad_agent.py and validate_stl.py"
python3 -m pip install -q openai cadquery trimesh numpy rtree scipy shapely

echo "Done. Also install OpenSCAD itself (brew install openscad) and restart Claude Code."
