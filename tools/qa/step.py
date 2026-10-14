#!/usr/bin/env python3
"""Drive gba_runner one step at a time and tile its screenshots into a sheet.

usage: step.py RUNNER ROM WORKDIR [--load NAME] [--save NAME] [--sheet OUT.png] "cmd; cmd; ..."
`shot` without an argument auto-numbers; a final screenshot is always taken.
State names live in WORKDIR as NAME.ss.
"""
import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("runner")
ap.add_argument("rom")
ap.add_argument("workdir", type=Path)
ap.add_argument("--load")
ap.add_argument("--save")
ap.add_argument("--sheet", default="sheet.png")
ap.add_argument("--cols", type=int, default=3)
ap.add_argument("commands")
a = ap.parse_args()

a.workdir.mkdir(parents=True, exist_ok=True)
lines, shots = [], []
if a.load:
    lines.append(f"load {(a.workdir / (a.load + '.ss')).as_posix()}")
if a.commands.startswith("@"):  # commands from a route file
    a.commands = ";".join(l for l in Path(a.commands[1:]).read_text(encoding="ascii").splitlines()
                          if not l.startswith("#"))
for raw in a.commands.split(";"):
    cmd = raw.strip()
    if not cmd:
        continue
    if cmd == "save @BEFORE_BATTLE":
        cmd = f"save {(a.workdir / 'before_battle.ss').as_posix()}"
    if cmd == "shot":
        shots.append(a.workdir / f"_shot{len(shots):02d}.png")
        cmd = f"shot {shots[-1].as_posix()}"
    lines.append(cmd)
shots.append(a.workdir / f"_shot{len(shots):02d}.png")
lines.append(f"shot {shots[-1].as_posix()}")
if a.save:
    lines.append(f"save {(a.workdir / (a.save + '.ss')).as_posix()}")
script = a.workdir / "_step.txt"
script.write_text("\n".join(lines) + "\n", encoding="ascii")
res = subprocess.run([str(Path(a.runner).resolve()), a.rom, script.as_posix()], capture_output=True, text=True)
sys.stdout.write(res.stdout)
sys.stderr.write(res.stderr)
if res.returncode:
    sys.exit(res.returncode)
cols = min(a.cols, len(shots))
rows = (len(shots) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 484, rows * 324), "white")
for i, p in enumerate(shots):
    sheet.paste(Image.open(p).convert("RGB").resize((480, 320), Image.NEAREST),
                ((i % cols) * 484 + 2, (i // cols) * 324 + 2))
sheet.save(a.workdir / a.sheet)
