#!/usr/bin/env python3
"""First-battle gate: replay the recorded route and check where the game ended up.

Runs tools/qa/route_new_game_to_first_battle.txt on the ROM, then reads game
memory from the resulting state. PASS means the player holds a Pokémon and is
standing in Professor Birch's lab, i.e. the first Arena battle was won and the
game returned to the overworld and carried on. A freeze, a lost battle or a
desynced route all leave the player somewhere else.

usage: verify_first_battle.py --rom ROM --elf ELF --runner gba_runner --workdir DIR
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BIRCHS_LAB = (1, 4)  # MAP_LITTLEROOT_TOWN_PROFESSOR_BIRCHS_LAB = 4 | (1 << 8)


def symbols(elf: Path, nm: str, names: set[str]) -> dict[str, int]:
    out = subprocess.run([nm, str(elf)], capture_output=True, text=True, check=True).stdout
    found = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[2] in names:
            found[parts[2]] = int(parts[0], 16)
    missing = names - set(found)
    if missing:
        raise SystemExit(f"symbols not found in ELF: {sorted(missing)}")
    return found


def peek(runner: Path, rom: Path, state: Path, workdir: Path, commands: list[str]) -> list[int]:
    script = workdir / "_peek.txt"
    script.write_text(f"load {state.as_posix()}\n" + "\n".join(commands) + "\n", encoding="ascii")
    out = subprocess.run([str(runner), str(rom), script.as_posix()],
                         capture_output=True, text=True, check=True).stdout
    return [int(v, 16) for v in re.findall(r"^peek\d+ [0-9A-F]{8} = ([0-9A-F]+)$", out, re.M)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", type=Path, required=True)
    ap.add_argument("--elf", type=Path, required=True)
    ap.add_argument("--runner", type=Path, required=True)
    ap.add_argument("--workdir", type=Path, required=True)
    ap.add_argument("--nm", default="arm-none-eabi-nm")
    args = ap.parse_args()
    runner = args.runner.resolve()

    subprocess.run([sys.executable, str(HERE / "step.py"), str(runner), str(args.rom),
                    str(args.workdir), "--save", "after_battle", "--cols", "3",
                    "@" + str(HERE / "route_new_game_to_first_battle.txt")], check=True)
    state = args.workdir / "after_battle.ss"
    sym = symbols(args.elf, args.nm, {"gSaveBlock1Ptr", "gPlayerPartyCount"})
    block, party = peek(runner, args.rom, state, args.workdir,
                        [f"peek32 {sym['gSaveBlock1Ptr']:08X}", f"peek8 {sym['gPlayerPartyCount']:08X}"])
    location, = peek(runner, args.rom, state, args.workdir, [f"peek16 {block + 4:08X}"])
    where = (location & 0xFF, location >> 8)
    print(f"party count: {party}; map group/num: {where}; expected {BIRCHS_LAB}")
    if party >= 1 and where == BIRCHS_LAB:
        print("PASS: first battle won, back in the overworld, reached Birch's lab")
        return 0
    print("FAIL: the route did not end in Birch's lab with a Pokémon "
          "(freeze, lost battle, or the input route no longer matches this build)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
