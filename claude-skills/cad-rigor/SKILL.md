---
name: cad-rigor
description: Rigorous workflow for any 3D model / STL / CAD request (OpenSCAD or CadQuery). Forces requirements analysis, dimension math, and verification so the part actually does its intended job. Use for every CAD, STL, enclosure, bracket, gear, adapter or 3D-print request.
---

# CAD rigor workflow

Think hard before writing any geometry. Do not skip steps for "simple" parts.

1. **Purpose** — state what the part must DO (holds, mates with, fits, seals, bears load, prints without supports). List what it connects to and the forces/fits involved.
2. **Spec table** — before coding, write every dimension, tolerance, clearance, wall thickness, and the datum/origin. Flag each assumption explicitly. Ask only if a wrong guess would make the part useless.
3. **Math first** — compute derived values (gear module/pitch, bolt circle, snap-fit deflection, hole = nominal + clearance) in comments or a script. No magic numbers.
4. **Build parametric** — all dimensions as named variables. Prefer CadQuery (robust booleans, STEP export) for complex/assembly parts; OpenSCAD (use the `openscad` skill) for quick parametric prints. Build mating parts in the same coordinate frame.
5. **Verify, don't assume** — run `python ~/.claude/skills/cad-rigor/validate_stl.py part.stl --bbox X Y Z` (watertight, single body, volume, extents, wall thickness). Render several angles and cross-section views and LOOK at them against the spec table.
6. **Functional check** — test the purpose: do mating parts interfere (boolean intersect volume ≈ 0) or clear by the stated gap? Are overhangs printable? Do holes land where the spec says?
7. **Fix and re-verify** — any failure goes back to step 4. Finish only when every spec line is checked, and report the table with PASS/FAIL and remaining assumptions.
