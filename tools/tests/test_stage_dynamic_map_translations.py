#!/usr/bin/env python3
"""PLAYER/RIVAL source-level substitution must be byte- and reference-safe."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_dynamic_map_translations import encode_dynamic,signature,stage

CTRL={"PLAYER":b"\xFD\x01","RIVAL":b"\xFD\x06"}
GLYPHS={"M":0xC7,"ẹ":0x5A,":":0xF0," ":0x00,
        "đ":0x56,"ế":0x1D,"n":0xE2,"r":0xE6,"ồ":0x04,
        "i":0xDD,"y":0xED,"ê":0x1C,"u":0xE9,
        "c":0xD7,"o":0xE3,"!":0xAB,",":0xB8,
        "h":0xDC,"ạ":0x1E,"k":0xDF,"à":0x16}

def row(label="LittlerootTown_Text_WaitPlayer",
        english=r"MOM: Wait, {PLAYER}!$",
        vietnamese=r"Mẹ: {PLAYER}, đợi mẹ!$"):
    return {"category":"map-story","source_file":"data/maps/LittlerootTown/scripts.inc",
            "source_label":label,"english":english,"vietnamese":vietnamese}


class DynamicMapTests(unittest.TestCase):
    def test_pinned_placeholder_encoding(self):
        payload=encode_dynamic(r"Mẹ: {PLAYER}!$",GLYPHS,CTRL,26)
        self.assertIn(b"\xFD\x01",payload)
        self.assertEqual(payload[-1],0xFF)
        self.assertEqual(payload.count(0xFD),1)

    def test_rival_encoding(self):
        payload=encode_dynamic(r"{RIVAL}!$",GLYPHS,CTRL,26)
        self.assertEqual(payload,b"\xFD\x06\xAB\xFF")

    def test_pins_name_length(self):
        with self.assertRaisesRegex(ValueError,"dynamic line exceeds"):
            encode_dynamic("M"*23+"{PLAYER}$",GLYPHS,CTRL,26)

    def test_unknown_variable_rejected(self):
        with self.assertRaisesRegex(ValueError,"unsupported dynamic"):
            encode_dynamic("{STR_VAR_1}$",GLYPHS,CTRL,26)

    def test_untrusted_charmap_rejected(self):
        with self.assertRaisesRegex(ValueError,"unverified charmap"):
            encode_dynamic("{PLAYER}$",GLYPHS,{"PLAYER":b"\xFD\x44"},26)

    def test_bad_terminator_rejected(self):
        with self.assertRaisesRegex(ValueError,"end marker"):
            encode_dynamic("M$M$",GLYPHS,CTRL,26)

    def test_source_placeholder_sequence_exact(self):
        self.assertEqual(signature("{PLAYER} & {RIVAL}$"),("PLAYER","RIVAL"))

    def test_stage_reject_changed_token_sequence(self):
        source="LittlerootTown_Text_WaitPlayer:\n\t.string \"MOM: Wait, {PLAYER}!$\"\n"
        candidates=[row(vietnamese=r"Mẹ: {RIVAL}!$")]
        _,accepted,rejected=stage(candidates,
            {"data/maps/LittlerootTown/scripts.inc":source},GLYPHS,CTRL,"data/maps/")
        self.assertFalse(accepted)
        self.assertIn("dynamic token sequence differs from English source",rejected)

    def test_stage_reject_changed_page_count(self):
        source=("LittlerootTown_Text_WaitPlayer:\n"
                '\t.string "MOM: Wait, {PLAYER}!$"\n')
        candidates=[row(vietnamese=r"Mẹ: {PLAYER}!\p$")]
        _,accepted,rejected=stage(candidates,
            {"data/maps/LittlerootTown/scripts.inc":source},GLYPHS,CTRL,"data/maps/")
        self.assertFalse(accepted)
        self.assertIn("page-control count changed",rejected)

    def test_exact_source_label_staged(self):
        source=("LittlerootTown_Text_WaitPlayer:\n"
                '\t.string "MOM: Wait, {PLAYER}!$"\n'
                "Other:\n\t.string \"Hello$\"\n")
        files={"data/maps/LittlerootTown/scripts.inc":source}
        result,accepted,skipped=stage([row()],files,GLYPHS,CTRL,"data/maps/")
        self.assertEqual(len(accepted),1,skipped)
        self.assertIn(".byte ",result["data/maps/LittlerootTown/scripts.inc"])
        self.assertIn('Other:\n\t.string "Hello$"',result["data/maps/LittlerootTown/scripts.inc"])


if __name__=="__main__":
    unittest.main()
