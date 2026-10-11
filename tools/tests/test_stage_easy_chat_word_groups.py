#!/usr/bin/env python3
"""Easy Chat group C word arrays: exact source and no menu overflow."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from stage_easy_chat_word_groups import compile_word, replace_exact, stage

FILE = "src/data/easy_chat/easy_chat_group_actions.h"
BADFILE = "src/data/text/abilities.h"
SOURCE = ('const u8 gEasyChatWord_Give[] = _("GIVE");\n'
          'const u8 gEasyChatWord_Meets[] = _("MEETS");\n'
          'const u8 gEasyChatWord_Here[] = _("HERE");\n')
GLYPHS = {c: i + 1 for i, c in enumerate(
    " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")}
GLYPHS["Ặ"] = 0x80
GLYPHS["È"] = 0x81
ROWS = [
    {"category": "system-ui", "source_file": FILE,
     "source_label": "gEasyChatWord_Give", "english": "GIVE",
     "vietnamese": "ĐƯA"},
    {"category": "system-ui", "source_file": FILE,
     "source_label": "gEasyChatWord_Meets", "english": "MEETS",
     "vietnamese": "GẶP"},
]
GLYPHS["Đ"] = 0x82
GLYPHS["Ư"] = 0x83


class EasyChatWordGroupTests(unittest.TestCase):
    def test_exact_word_compiles_and_preserves_unrelated_owner(self):
        result, accepted, skipped = stage(ROWS, {FILE: SOURCE}, GLYPHS)
        self.assertEqual(len(accepted), 2, skipped)
        self.assertIn("gEasyChatWord_Give[] = {", result[FILE])
        self.assertIn("gEasyChatWord_Meets[] = {", result[FILE])
        self.assertIn('gEasyChatWord_Here[] = _("HERE");', result[FILE])
        self.assertEqual(accepted[0]["authored_vietnamese"], "ĐƯA")
        self.assertEqual(accepted[1]["vietnamese"], "GẶP")
        self.assertEqual(
            compile_word("GIVE", "ĐƯA", GLYPHS)[-1], 0xFF)

    def test_long_words_and_unknown_codebook_char_refused(self):
        with self.assertRaisesRegex(ValueError, "original source"):
            compile_word("GO", "ĐƯA", GLYPHS)
        with self.assertRaisesRegex(ValueError, "menu slot"):
            compile_word("A" * 21, "A" * 17, GLYPHS, 15)
        with self.assertRaisesRegex(ValueError, "missing Vietnamese glyph"):
            compile_word("HELLO", "GỌP", GLYPHS)
        for vietnamese in ("G  P", "G\nP", "{PLAYER}", "G\\nP", " G", "G$"):
            with self.subTest(vietnamese=vietnamese):
                with self.assertRaises(ValueError):
                    compile_word("GIVE", vietnamese, GLYPHS)

    def test_source_symbols_reject_wrong_owner_and_drift(self):
        b = compile_word("MEETS", "GẶP", GLYPHS)
        self.assertIn("gEasyChatWord_Meets[] = {",
                      replace_exact(SOURCE, FILE, "gEasyChatWord_Meets",
                                    "MEETS", b))
        with self.assertRaisesRegex(ValueError, "original"):
            replace_exact(SOURCE, FILE, "gEasyChatWord_Meets", "WRONG", b)
        with self.assertRaisesRegex(ValueError, "unapproved"):
            replace_exact(SOURCE, BADFILE, "gEasyChatWord_Meets", "MEETS", b)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            replace_exact(SOURCE + SOURCE, FILE, "gEasyChatWord_Meets",
                          "MEETS", b)

    def test_duplicate_plan_owner_and_unsupported_rows(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            stage([ROWS[0], ROWS[0]], {FILE: SOURCE}, GLYPHS)
        out, added, _ = stage([
            {**ROWS[0], "category": "battle"},
            {**ROWS[0], "source_file": BADFILE},
            {**ROWS[0], "english": "GIVE", "vietnamese": "GIVE"},
        ], {FILE: SOURCE}, GLYPHS)
        self.assertEqual(added, [])
        self.assertEqual(out[FILE], SOURCE)


if __name__ == "__main__":
    unittest.main()
