#!/usr/bin/env python3
"""Pokédex source text is exact-owned, four lines, with no word loss."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stage_source_pokedex_text import (
    FILE, find_dex_block, reflow_four_lines, replace_dex, stage,
)

SRC = (
    'const u8 gBulbasaurPokedexText[] = _(\n'
    '    "BULBASAUR can nap in bright\\n"\n'
    '    "sunlight. It has a seed.\\n"\n'
    '    "Water makes it grow more.\\n"\n'
    '    "It grows progressively.");\n'
    '\n'
    'const u8 gIvysaurPokedexText[] = _(\n'
    '    "An IVYSAUR is friendly.\\n"\n'
    '    "It can play all day.\\n"\n'
    '    "Watch it in the forest.\\n"\n'
    '    "And see its flower grow.");\n'
)
EN = ("BULBASAUR can nap in bright\\n"
      "sunlight. It has a seed.\\n"
      "Water makes it grow more.\\n"
      "It grows progressively.")
VI = (r"BULBASAUR co mot cai hat tren lung, no lon dan theo anh nang\n"
      r"va khi tham duong troi thi no cang khoe\n"
      r"bo canh xanh non trong nang\n"
      r"mot ngay moi")
ROW = {"category": "system-ui", "source_file": FILE,
       "source_label": "gBulbasaurPokedexText",
       "english": EN, "vietnamese": VI}
CODES = {ch: i + 1 for i, ch in enumerate(
    " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,.-!?")}


class PokedexSourceTests(unittest.TestCase):
    def test_exact_four_line_initializer_without_touching_other_symbol(self):
        a, b, decl, original = find_dex_block(SRC, "gBulbasaurPokedexText")
        self.assertEqual(original, EN)
        self.assertTrue(decl.startswith("const u8 gBulbasaur"))
        self.assertTrue(SRC[a:b].endswith('It grows progressively.");\n'))
        converted, rows, reasons = stage([ROW], SRC, CODES, width=40)
        self.assertEqual(len(rows), 1, reasons)
        self.assertIn("const u8 gBulbasaurPokedexText[] = {0x", converted)
        self.assertIn('const u8 gIvysaurPokedexText[] = _(', converted)
        self.assertEqual(rows[0]["vietnamese"].count(r"\n"), 3)
        self.assertTrue(all(len(line) <= 40 for line in
                            rows[0]["vietnamese"].split(r"\n")))
        self.assertEqual(
            rows[0]["vietnamese"].replace(r"\n", " ").split(),
            VI.replace(r"\n", " ").split())

    def test_long_text_four_lines_word_boundary_only(self):
        original = (
            r"very long descriptions are now written here in this one line which does not fit at all\n"
            r"but these must preserve all of their words\n"
            r"yes they do\n"
            r"and the fourth line also")
        result = reflow_four_lines(original, 40)
        self.assertEqual(result.count(r"\n"), 3)
        self.assertTrue(all(len(x) <= 40 for x in result.split(r"\n")))
        self.assertEqual(
            result.replace(r"\n", " ").split(),
            original.replace(r"\n", " ").split())

    def test_reject_control_drift_unknown_glyph_and_missing_exact_source(self):
        for candidate in (
            VI.replace(r"\n", r"\p", 1),
            VI.replace("mot", "một"),
            VI.replace("mot", "mot  "),
            VI + r"\nExtra",
            VI.replace("mot", "{PLAYER}"),
        ):
            with self.subTest(candidate=candidate):
                _, rows, skipped = stage(
                    [{**ROW, "vietnamese": candidate}], SRC, CODES)
                self.assertFalse(rows)
                self.assertTrue(skipped)
        _, rows, skipped = stage(
            [ROW], SRC.replace("BULBASAUR can nap", "WRONG can nap"), CODES)
        self.assertFalse(rows)
        self.assertTrue(skipped)
        with self.assertRaisesRegex(ValueError, "duplicate Pokédex"):
            stage([ROW, ROW], SRC, CODES)

    def test_reject_source_rows_or_overlong_words(self):
        with self.assertRaisesRegex(ValueError, "four-line"):
            reflow_four_lines("one\\ntwo\\nthree", 40)
        with self.assertRaisesRegex(ValueError, "unbreakable"):
            reflow_four_lines(
                r"abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz\n"
                r"other line\n"
                r"more words\n"
                r"last line", 40)
        with self.assertRaisesRegex(ValueError, "English source changed"):
            replace_dex(SRC, "gBulbasaurPokedexText", "WRONG",
                        b"\x01\xff")


if __name__ == "__main__":
    unittest.main()
