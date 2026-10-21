"""GPT CAD agent: spec -> CadQuery code -> run -> validate STL -> feed failures back, until it passes.

Usage: python cad_agent.py "a wall bracket for a 20mm pipe, 2x M5 screws" [--out out/part.stl]
Key: OPENAI_API_KEY env var, else paper_code/config/config.json.
"""
import argparse, json, os, subprocess, sys, tempfile
import numpy as np, trimesh
from openai import OpenAI

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_ROUNDS = 5

SYSTEM = """You are a rigorous CAD engineer writing CadQuery (Python). Work in this order and reason carefully:
1. PURPOSE: what the part must do, what it mates with, fits and loads.
2. SPEC: a JSON object with every dimension, clearance, wall thickness, and "bbox" = expected overall X,Y,Z in mm.
3. MATH: derive values in code, no magic numbers; holes = nominal + clearance; min wall >= 1.2 mm unless stated.
4. CODE: a complete script, all dimensions as named variables, final solid in a variable `result` (cq.Workplane), single solid, z-up, origin on the print bed.
Reply with exactly two fenced blocks: ```json (the spec) then ```python (the code). Do not export; the harness does."""

def load_key():
    if os.environ.get("OPENAI_API_KEY"):
        return os.environ["OPENAI_API_KEY"]
    with open(os.path.join(HERE, "paper_code/config/config.json")) as f:
        return json.load(f)["OPENAI_API_KEY"]

def extract(text, lang):
    marker = "```" + lang
    if marker not in text:
        raise ValueError(f"reply is missing a ```{lang} block")
    return text.split(marker, 1)[1].split("```", 1)[0].strip()

def build(code, stl_path):
    """Run generated code in a subprocess (timeout) and export `result` to STL."""
    with tempfile.TemporaryDirectory() as d:
        script = os.path.join(d, "model.py")
        with open(script, "w") as f:
            f.write(code + f"\n\nimport cadquery as _cq\n_cq.exporters.export(result, {stl_path!r})\n")
        r = subprocess.run([sys.executable, "-I", script], capture_output=True, text=True, timeout=120)
    if r.returncode:
        return False, "CadQuery error:\n" + r.stderr[-1500:]
    return True, ""

def validate(stl_path, spec):
    m = trimesh.load(stl_path, force="mesh")
    problems = []
    if not m.is_watertight: problems.append("mesh is not watertight")
    if m.volume <= 0: problems.append("non-positive volume (inverted or empty)")
    bodies = len(m.split(only_watertight=False))
    if bodies != 1: problems.append(f"{bodies} separate bodies; expected 1 solid")
    bbox = spec.get("bbox")
    if bbox:
        diff = np.abs(np.sort(m.extents) - np.sort(bbox))
        if diff.max() > 0.3:
            problems.append(f"extents {np.round(m.extents, 2).tolist()} differ from spec bbox {bbox}")
    return problems, m

def run(requirement, out_path, model):
    client = OpenAI(api_key=load_key())
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": requirement}]
    for round_no in range(1, MAX_ROUNDS + 1):
        text = client.chat.completions.create(model=model, messages=messages).choices[0].message.content
        messages.append({"role": "assistant", "content": text})
        try:
            spec, code = json.loads(extract(text, "json")), extract(text, "python")
            os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
            ok, err = build(code, os.path.abspath(out_path))
            problems = [err] if not ok else validate(out_path, spec)[0]
        except Exception as e:
            problems = [f"{type(e).__name__}: {e}"]
        print(f"round {round_no}: {'PASS' if not problems else 'FAIL ' + '; '.join(problems)[:300]}")
        if not problems:
            open(out_path.rsplit(".", 1)[0] + ".py", "w").write(code)
            open(out_path.rsplit(".", 1)[0] + ".spec.json", "w").write(json.dumps(spec, indent=2))
            print(f"saved {out_path} (+ .py, .spec.json)")
            return 0
        messages.append({"role": "user", "content": "Verification failed:\n- " + "\n- ".join(problems) +
                         "\nFix the root cause and resend both blocks in full."})
    print("gave up after", MAX_ROUNDS, "rounds"); return 1

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("requirement"); ap.add_argument("--out", default="out/part.stl")
    ap.add_argument("--model", default=None)
    a = ap.parse_args()
    model = a.model or json.load(open(os.path.join(HERE, "paper_code/config/config.json"))).get("GPT_MODEL", "gpt-4o")
    sys.exit(run(a.requirement, a.out, model))
