#!/usr/bin/env python3
"""Check all token-free item descriptions against v0.5 GBA font and text box.

Variable-like {POKEBLOCK} is a five-byte charmap ligature, NOT treated as
ordinary text. It stays excluded until the conflicting v0.5 glyph slots
(0x56 for đ, 0x59 for ì) are remapped without breaking native icon glyphs.
"""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FILES=ROOT/"translations/system-ui"
PATCHED={
    "sPremierBallDesc",
    "sBerryJuiceDesc",
    "sSoulDewDesc",
    "sEverstoneDesc",
    "sUpGradeDesc",
    "sTM08Desc",
    "sSilphScopeDesc",
}


class ItemDescriptionGlyphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book=json.loads((ROOT/"checkpoints/v05-collision-free-codebook.json")
                            .read_text(encoding="utf-8"))["glyph_bytes"]
        cls.rows={}
        for path in sorted(FILES.glob("item-descriptions-*.vi.json")):
            for key,val in json.loads(path.read_text(encoding="utf-8"))["translations"].items():
                if key in cls.rows:
                    raise AssertionError(f"duplicate item description: {key}")
                cls.rows[key]=val

    def test_seven_edited_static_item_descriptions(self):
        self.assertEqual(len(PATCHED),7)
        self.assertTrue(PATCHED.issubset(self.rows))
        for label in PATCHED:
            with self.subTest(item=label):
                lines=self.rows[label].split(r"\n")
                self.assertIn(len(lines),(2,3))
                self.assertTrue(all(0<len(line)<=26 for line in lines))
                self.assertFalse(set(self.rows[label].replace(r"\n",""))-set(self.book))

    def test_all_static_item_descriptions_use_supported_font(self):
        # POKEBLOCK-bearing descriptions are blocked until special glyph fix.
        static=[(key,val) for key,val in self.rows.items()
                if "{" not in val and "}" not in val]
        self.assertEqual(len(self.rows),309)
        self.assertEqual(len(static),293)
        for label,text in static:
            with self.subTest(item=label):
                lines=text.split(r"\n")
                self.assertIn(len(lines),(2,3))
                self.assertTrue(all(0<len(line)<=26 for line in lines))
                missing=set(text.replace(r"\n",""))-set(self.book)
                self.assertFalse(missing,(label,missing))

    def test_pinned_source_line_counts_for_last_two_items(self):
        # Original source: Up-Grade has two visible lines; TM09 has three.
        self.assertEqual(self.rows["sUpGradeDesc"].count(r"\\n"),1)
        self.assertEqual(self.rows["sTM09Desc"].count(r"\\n"),2)
        self.assertIn("SILPH CO.",self.rows["sUpGradeDesc"])
        self.assertIn("2 đến 5",self.rows["sTM09Desc"])

    def test_pokeblock_ligatures_still_deliberately_excluded(self):
        has_token={key for key,value in self.rows.items() if "{POKEBLOCK}" in value}
        self.assertEqual(len(has_token),16)
        self.assertEqual(self.book["đ"],"0x56")
        self.assertEqual(self.book["ì"],"0x59")
        self.assertTrue(has_token.isdisjoint(PATCHED))


if __name__=="__main__":
    unittest.main()
