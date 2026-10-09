#!/usr/bin/env python3
"""Independent multilingual source label attestation regression tests."""
import tempfile
import unittest
from pathlib import Path

from verify_compiled_source_strings import (
    extract_asm_payload, extract_c_payload, validate_byte_string,
    validate_stages,
)


class SourceAttestationTests(unittest.TestCase):
    def test_asm_double_colon_and_multiple_byte_lines(self):
        src=('BattleDome_Text_Potential1::\n'
             '\t.byte 0xC7, 0x0A\n'
             '\t.byte 0xFF\n\n'
             'Other::\n\t.string "English$"\n')
        self.assertEqual(extract_asm_payload(src,"BattleDome_Text_Potential1"),
                         b"\xC7\x0A\xFF")

    def test_native_pokeblock_item_source_byte_attestation(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            dest=root/"src/data/text"
            dest.mkdir(parents=True)
            path=dest/"item_descriptions.h"
            path.write_text(
                "static const u8 sRazzBerryDesc[] = {0xD5, 0x55, 0x56, 0x57, 0x58, 0x59, 0xFE, 0xD6, 0xFE, 0xD7, 0xFF};\n",
                encoding="utf-8")
            report={"pokeblock":{"mode":"apply",
                    "source_file":"src/data/text/item_descriptions.h",
                    "labels_staged":1,
                    "translated":[{"label":"sRazzBerryDesc","visible_lines":3}]}}
            verified=validate_stages(root,report)
            self.assertEqual(verified["source_groups"],{"pokeblock":1})
            path.write_text(
                "static const u8 sRazzBerryDesc[] = {0xD5, 0x55, 0x56, 0x58, 0x59, 0xFE, 0xD6, 0xFE, 0xD7, 0xFF};\n",
                encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"native Pokéblock byte sequence"):
                validate_stages(root,report)

    def test_move_and_item_description_source_attestation(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            folder=root/"src/data/text"
            folder.mkdir(parents=True)
            (folder/"move_descriptions.h").write_text(
                "static const u8 sPoundDescription[] = {0xD5, 0xFE, 0xD6, 0xFF};\n",
                encoding="utf-8")
            (folder/"item_descriptions.h").write_text(
                "static const u8 sMasterBallDesc[] = {0xD5, 0xFE, 0xD6, 0xFE, 0xD7, 0xFF};\n",
                encoding="utf-8")
            reports={
                "move-desc":{"mode":"apply",
                             "source_file":"src/data/text/move_descriptions.h",
                             "labels_staged":1,
                             "translated":[{"label":"sPoundDescription","visible_lines":2}]},
                "item-desc":{"mode":"apply",
                             "source_file":"src/data/text/item_descriptions.h",
                             "labels_staged":1,
                             "translated":[{"label":"sMasterBallDesc","visible_lines":3}]},
            }
            verified=validate_stages(root,reports)
            self.assertEqual(verified["checked_unique_source_labels"],2)
            self.assertEqual(verified["source_groups"],{"move-desc":1,"item-desc":1})
            reports["move-desc"]["source_file"]="src/battle_message.c"
            with self.assertRaises(ValueError):
                validate_stages(root,reports)

    def test_static_battle_c_literal_exact_text(self):
        src='static const u8 sText_CriticalHit[] = {0xC7, 0xFE, 0x10, 0xFF};\n'
        self.assertEqual(extract_c_payload(src,"sText_CriticalHit"),
                         b"\xC7\xFE\x10\xFF")

    def test_battle_c_source_attestation_rejects_ghost_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"src").mkdir()
            (root/"src/battle_message.c").write_text(
                'static const u8 sText_CriticalHit[] = {0xC7, 0xFF};\n',
                encoding="utf-8")
            reports={"battle-c":{"mode":"apply",
                      "source_file":"src/battle_message.c",
                      "labels_staged":1,
                      "translated":[{"label":"sText_CriticalHit"}]}}
            actual=validate_stages(root,reports)
            self.assertEqual(actual["source_groups"],{"battle-c":1})
            reports["battle-c"]["translated"][0]["label"]="sText_FakeMissing"
            with self.assertRaisesRegex(ValueError,"expected one C literal"):
                validate_stages(root,reports)

    def test_c_literal_exact_text(self):
        src='const u8 gText_SaveNotice[] = {0xC7, 0xFE, 0x10, 0xFF};\n'
        self.assertEqual(extract_c_payload(src,"gText_SaveNotice"),
                         b"\xC7\xFE\x10\xFF")

    def test_early_terminator_rejected(self):
        with self.assertRaisesRegex(ValueError,"terminal FF"):
            validate_byte_string(b"\xFF\xC7\xFF","X")

    def test_missing_terminator_rejected(self):
        with self.assertRaisesRegex(ValueError,"terminal FF"):
            validate_byte_string(b"\xC7\x00","X")

    def test_invalid_dynamic_byte_rejected(self):
        with self.assertRaisesRegex(ValueError,"unapproved dynamic"):
            validate_byte_string(b"\xC7\xFD\x90\xFF","X")

    def test_ownership_source_scan(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"data/maps/X").mkdir(parents=True)
            (root/"data/text").mkdir(parents=True)
            (root/"src").mkdir(parents=True)
            (root/"data/maps/X/scripts.inc").write_text(
                'Hello_MapText::\n\t.byte 0xC7, 0xFF\n',encoding="utf-8")
            (root/"data/text/battle_dome.inc").write_text(
                'BattleDome_Text_A::\n\t.byte 0xC7, 0xFF\n',encoding="utf-8")
            (root/"src/strings.c").write_text(
                'const u8 gText_Notice[] = {0xC7, 0xFF};\n',encoding="utf-8")
            def report(labels):
                return {"mode":"apply","labels_staged":len(labels),"translated":labels}
            reports={
                "map":report([{"label":"Hello_MapText","source_file":"data/maps/X/scripts.inc"}]),
                "ui":report([{"label":"gText_Notice"}]),
                "dynamic":{"mode":"apply","labels_staged":0,"accepted":[]},
                "battle":report([{"label":"BattleDome_Text_A","source_file":"data/text/battle_dome.inc"}]),
            }
            reports["ui"]["source_file"]="src/strings.c"
            validated=validate_stages(root,reports)
            self.assertEqual(validated["checked_unique_source_labels"],3)
            self.assertTrue(validated["all_labels_have_exact_terminal_ff"])
            reports["battle"]["translated"][0]["label"]="Hello_MapText"
            with self.assertRaises(ValueError):
                validate_stages(root,reports)

    def test_missing_source_label_fails(self):
        with self.assertRaisesRegex(ValueError,"expected one"):
            extract_asm_payload('Other::\n\t.byte 0xC7,0xFF\n',"NoLabel")


if __name__=="__main__":
    unittest.main()
