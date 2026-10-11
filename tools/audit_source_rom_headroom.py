#!/usr/bin/env python3
"""Fail-closed GBA linker capacity audit from real ELF32 PT_LOAD addresses.

The .gba release image is normally padded to 32 MiB, so its file size says
nothing about unused linker space. Derive high-water occupancy from LMA
(p_paddr) and file-backed bytes of ELF load segments; do NOT count RAM BSS.
Read-only: never modifies or distributes copyrighted ROM data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

GBA_BASE = 0x08000000
GBA_LIMIT = 0x0A000000
MAX_ROM_SIZE = GBA_LIMIT - GBA_BASE
PT_LOAD = 1
ELF32_HEADER_FMT = "<HHIIIIIHHHHHH"
ELF32_PHDR_FMT = "<IIIIIIII"
ELF32_HEADER_SIZE = 52
ELF32_PHDR_SIZE = 32


def loadable_rom_segments(elf: bytes) -> list[dict[str, int]]:
    if len(elf) < ELF32_HEADER_SIZE or elf[:4] != b"\x7fELF":
        raise ValueError("missing ELF binary")
    if elf[4] != 1 or elf[5] != 1 or elf[6] != 1:
        raise ValueError("expected 32-bit little-endian ELF")
    header = struct.unpack_from(ELF32_HEADER_FMT, elf, 16)
    machine, program_off, program_entry_size, program_count = (
        header[1], header[4], header[8], header[9])
    if machine != 40:
        raise ValueError("expected ARM ELF e_machine=40")
    if not 0 < program_count <= 100 or program_entry_size != ELF32_PHDR_SIZE:
        raise ValueError("unsupported ELF program header geometry")
    if program_off < ELF32_HEADER_SIZE or program_off + program_count * program_entry_size > len(elf):
        raise ValueError("truncated ELF program header table")

    result = []
    for index in range(program_count):
        offset = program_off + index * program_entry_size
        kind, file_offset, _, load_address, filesz, memsz, _, _ = (
            struct.unpack_from(ELF32_PHDR_FMT, elf, offset))
        if kind != PT_LOAD or not filesz:
            continue
        if file_offset + filesz > len(elf) or filesz > memsz:
            raise ValueError("corrupt file-backed PT_LOAD segment")
        if not GBA_BASE <= load_address < GBA_LIMIT:
            # EWRAM/IWRAM runtime memory segments are not additional ROM
            # unless the ELF physical/load address explicitly names ROM.
            continue
        if load_address + filesz > GBA_LIMIT:
            raise ValueError("ROM segment exceeds GBA 32MiB address range")
        result.append({
            "segment": index,
            "lma": load_address,
            "file_offset": file_offset,
            "file_size": filesz,
            "end_offset": load_address + filesz - GBA_BASE,
        })
    if not result:
        raise ValueError("no linker-backed GBA ROM segments")
    if not any(item["lma"] == GBA_BASE for item in result):
        raise ValueError("missing base ROM load segment at 0x08000000")
    intervals = sorted((x["lma"], x["lma"] + x["file_size"]) for x in result)
    if any(intervals[i][1] > intervals[i+1][0] for i in range(len(intervals)-1)):
        raise ValueError("overlapping file-backed ROM load segments")
    return result


def audit_rom_capacity(elf: bytes, rom: bytes, minimum_free_bytes: int = 49152) -> dict:
    if not 0 <= minimum_free_bytes <= MAX_ROM_SIZE:
        raise ValueError("invalid minimum linker headroom")
    if len(rom) != MAX_ROM_SIZE:
        raise ValueError("expected exactly 32MiB padded GBA source image")
    chunks = loadable_rom_segments(elf)
    highest = max(c["end_offset"] for c in chunks)
    if highest > len(rom):
        raise ValueError("ELF ROM address exceeds source ROM")
    # Do not demand complete byte identity: gbafix legally corrects the GBA
    # game header/checksum AFTER object copying. Header counts as occupied.
    headroom = MAX_ROM_SIZE - highest
    if headroom < minimum_free_bytes:
        raise ValueError(
            f"ROM linker headroom {headroom} bytes below required {minimum_free_bytes}")
    return {
        "schema_version": 1,
        "capacity_bytes": MAX_ROM_SIZE,
        "linker_occupied_bytes": highest,
        "linker_free_bytes": headroom,
        "linker_occupied_percent": round(highest * 100 / MAX_ROM_SIZE, 4),
        "minimum_free_bytes": minimum_free_bytes,
        "rom_load_segments": len(chunks),
        "highest_rom_load_segment_lma": hex(
            max(chunks, key=lambda x: x["end_offset"])["lma"]),
        "elf_load_addresses_verified": True,
        "rom_file_padded_not_used_as_free_space_metric": True,
        "no_ROM_writes": True,
        "font_or_emulator_verified": False,
        "release_ready": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elf", required=True, type=Path)
    parser.add_argument("--rom", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--minimum-free-bytes", type=int, default=49152)
    a = parser.parse_args()
    elf = a.elf.read_bytes()
    rom = a.rom.read_bytes()
    report = audit_rom_capacity(elf, rom, a.minimum_free_bytes)
    report["source_ROM_sha256"] = hashlib.sha256(rom).hexdigest()
    report["ELF_sha256"] = hashlib.sha256(elf).hexdigest()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
