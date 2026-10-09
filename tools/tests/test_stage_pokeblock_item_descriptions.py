#!/usr/bin/env python3
"""POKEBLOCK native glyph item descriptions must preserve 5-byte control."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_pokeblock_item_descriptions import (
    pinned_pokeblock_bytes,encode_item_pokeblock,stage_pokeblock,
)
CODES={"a":0xD5,"b":0xD6,"c":0xD7," ":0x00,".":0xAD,
       "đ":0x33,"ì":0x37}
CM="POKEBLOCK   = 55 56 57 58 59\n@ Hiragana\n"
EN=r"{POKEBLOCK} ingredient.\nPlant in loamy soil\nto grow RAZZ."
VI=r"abc {POKEBLOCK}.\nabc abc\nabc."
SRC=('static const u8 sRazzBerryDesc[] = _(\n'
     '    "{POKEBLOCK} ingredient.\\n"\n'
     '    "Plant in loamy soil\\n"\n'
     '    "to grow RAZZ.");\n'
     'static const u8 sOtherDesc[] = _(\n'
     '    "A letter\\n"\n'
     '    "used for display\\n"\n'
     '    "by itself.");\n')


def row(v=VI,e=EN,label="sRazzBerryDesc"):
    return {"category":"system-ui","source_file":"src/data/text/item_descriptions.h",
            "source_label":label,"english":e,"vietnamese":v}


class PokeBlockSourceTests(unittest.TestCase):
    def test_char_map_is_pinned_native_five_bytes(self):
        self.assertEqual(pinned_pokeblock_bytes(CM),b"\x55\x56\x57\x58\x59")

    def test_malformed_native_token_refused(self):
        with self.assertRaisesRegex(ValueError,"changed"):
            pinned_pokeblock_bytes(CM.replace("58 59","58 60"))

    def test_encoded_three_line_item_contains_true_native_bytes(self):
        payload=encode_item_pokeblock(VI,CODES,b"\x55\x56\x57\x58\x59")
        self.assertEqual(payload.count(b"\x55\x56\x57\x58\x59"),1)
        self.assertEqual(payload.count(b"\xFE"),2)
        self.assertEqual(payload[-1],0xFF)

    def test_word_width_counts_native_bytes_as_five(self):
        sentence="a"*22+"{POKEBLOCK}"+r"\nabc\nabc"
        with self.assertRaisesRegex(ValueError,"exceeds"):
            encode_item_pokeblock(sentence,CODES,b"\x55\x56\x57\x58\x59")

    def test_unknown_dynamic_token_refused(self):
        with self.assertRaisesRegex(ValueError,"unknown dynamic"):
            encode_item_pokeblock(VI+"{PLAYER}",CODES,b"\x55\x56\x57\x58\x59")

    def test_exact_source_label_unchanged_after_byte_encoding(self):
        changed,accepted,errors=stage_pokeblock(
            [row()],SRC,CODES,b"\x55\x56\x57\x58\x59")
        self.assertEqual(len(accepted),1,errors)
        self.assertIn("sRazzBerryDesc[] = {",changed)
        self.assertIn("0x55, 0x56, 0x57, 0x58, 0x59",changed)
        self.assertIn("sOtherDesc[] = _(",changed)
        self.assertEqual(accepted[0]["native_token_occurrences"],1)

    def test_source_token_removed_by_translator_is_not_accepted(self):
        _,accepted,errors=stage_pokeblock(
            [row(v=r"abc abc\nabc abc\nabc")],SRC,CODES,
            b"\x55\x56\x57\x58\x59")
        self.assertFalse(accepted)
        self.assertIn("source token signature differs",errors)

    def test_changed_original_english_is_refused(self):
        _,accepted,errors=stage_pokeblock(
            [row(e=r"{POKEBLOCK} wrong.\nPlant in loamy soil\nto grow RAZZ.")],
            SRC,CODES,b"\x55\x56\x57\x58\x59")
        self.assertFalse(accepted)
        self.assertTrue(any("source drift" in x for x in errors))

    def test_source_three_line_semantics_protected(self):
        _,accepted,errors=stage_pokeblock(
            [row(v=r"abc {POKEBLOCK}.\nabc abc abc")],SRC,CODES,
            b"\x55\x56\x57\x58\x59")
        self.assertFalse(accepted)
        self.assertIn("source three-line layout mismatch",errors)


if __name__=="__main__":
    unittest.main()
