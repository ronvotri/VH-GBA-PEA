#!/usr/bin/env python3
"""Expand INCLUDE directives of a GNU ld script into one file.

The MSYS2/MinGW build of arm-none-eabi-ld rejects any second linker script
("appears multiple times") because Windows reports no inode numbers, so the
pokeemerald script with its three INCLUDEs cannot be linked as-is there.

usage: inline_linker_includes.py SCRIPT INCLUDE_DIR > OUT
"""
import re
import sys
from pathlib import Path

script, include_dir = Path(sys.argv[1]), Path(sys.argv[2])
for line in script.read_text(encoding="utf-8").splitlines():
    m = re.match(r'^\s*INCLUDE\s+"([^"]+)"\s*$', line)
    if m:
        sys.stdout.write((include_dir / m.group(1)).read_text(encoding="utf-8"))
    else:
        sys.stdout.write(line + "\n")
