#!/usr/bin/env python3
"""Regression cases for read-only GBA source-reference opcode triage."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from triage_actual_script_ownership import script_opcode_evidence


class ReferenceOwnershipOpcodeTests(unittest.TestCase):
    def test_loadword_at_two(self):
        blob = b"\x0f\x00" + (0x08203FCB).to_bytes(4, "little") + b"\x09"
        self.assertEqual(script_opcode_evidence(
            blob, 2, 0, "D", "DewfordTown_EventScript_LandedSlateport"),
            "candidate:script-loadword-opcode-0F")

    def test_trainerbattle_intro_at_six(self):
        blob = b"\x5c\x00\x56\x01\x00\x00" + (0x082AFFC5).to_bytes(4, "little")
        self.assertEqual(script_opcode_evidence(
            blob, 6, 0, "D", "Route114_EventScript_Nolan"),
            "candidate:trainerbattle-opcode-5C")

    def test_trainerbattle_defeat_at_ten(self):
        blob = (b"\x5c\x00\x56\x01\x00\x00" +
                (0x082AFFC5).to_bytes(4, "little") +
                (0x082B0029).to_bytes(4, "little"))
        self.assertEqual(script_opcode_evidence(
            blob, 10, 0, "D", "Route114_EventScript_Nolan"),
            "candidate:trainerbattle-opcode-5C")

    def test_unknown_script_command_not_promoted(self):
        self.assertEqual(script_opcode_evidence(
            b"\x44"*30, 10, 0, "D", "Route114_EventScript_Nolan"),
            "candidate:event-script-other-command")

    def test_aligned_data_table(self):
        self.assertEqual(script_opcode_evidence(
            b"\0"*64, 20, 0, "R", "sTVTrainerFanClubTextGroup"),
            "candidate:aligned-data-pointer-table")

    def test_unaligned_data_table(self):
        self.assertEqual(script_opcode_evidence(
            b"\0"*64, 5, 0, "R", "sTVTrainerFanClubTextGroup"),
            "review:unaligned-data-table-site")

    def test_graphic_bytes_not_text(self):
        self.assertEqual(script_opcode_evidence(
            b"\0"*20, 4, 0, "R", "gMonFrontPic_Numel"),
            "incidental-graphics-data")
        self.assertEqual(script_opcode_evidence(
            b"\0"*20, 4, 0, "R", "gRaySceneTakesFlight_Bg_Tilemap"),
            "incidental-graphics-data")

    def test_instruction_bytes_not_text(self):
        self.assertEqual(script_opcode_evidence(
            b"\0"*20, 4, 0, "t", "MoveWordSelectCursor"),
            "incidental-executable-code")

    def test_out_of_range_never_promoted(self):
        self.assertEqual(script_opcode_evidence(
            b"\0"*20, 18, 0, "D", "Route_EventScript_Random"),
            "invalid-reference-range")


if __name__ == "__main__":
    unittest.main()
