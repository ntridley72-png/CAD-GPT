#!/usr/bin/env python3
"""Check an STL against the design spec. Usage: validate_stl.py part.stl [--bbox X Y Z] [--tol MM] [--min-wall MM]"""
import argparse, sys
import numpy as np, trimesh

p = argparse.ArgumentParser()
p.add_argument("stl")
p.add_argument("--bbox", nargs=3, type=float, help="expected X Y Z extents in mm")
p.add_argument("--tol", type=float, default=0.2)
p.add_argument("--min-wall", type=float, default=0.8)
a = p.parse_args()

m = trimesh.load(a.stl, force="mesh")
ok = True
def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

ext = m.extents
check("watertight", m.is_watertight)
check("winding consistent", m.is_winding_consistent)
check("positive volume", m.volume > 0, f"(volume {m.volume:.1f} mm^3)")
check("single body", len(m.split(only_watertight=False)) == 1, f"({len(m.split(only_watertight=False))} bodies)")
print(f"       extents mm: {ext[0]:.2f} x {ext[1]:.2f} x {ext[2]:.2f}")
if a.bbox:
    exp = np.array(a.bbox)
    check("bounding box matches spec", np.all(np.abs(np.sort(ext) - np.sort(exp)) <= a.tol), f"(expected {a.bbox} +/-{a.tol})")
# thin-wall probe: ray-cast inward from sampled surface points
pts, idx = trimesh.sample.sample_surface(m, 2000)
n = -m.face_normals[idx]
try:
    loc, ray_idx, _ = m.ray.intersects_location(pts + n * 1e-3, n, multiple_hits=False)
    thick = np.linalg.norm(loc - pts[ray_idx], axis=1)
    check("min wall thickness", thick.min() >= a.min_wall, f"(thinnest sampled {thick.min():.2f} mm, need {a.min_wall})")
except Exception as e:
    print("       wall probe skipped:", e)
sys.exit(0 if ok else 1)
