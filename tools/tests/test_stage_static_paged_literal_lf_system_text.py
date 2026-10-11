#!/usr/bin/env python3
"""Paged literal-LF system strings never change page-local authored text."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_static_paged_literal_lf_system_text import stage_paged_lf
from stage_static_paged_map_dialogues import page_words

CODES={ch:i+1 for i,ch in enumerate(" abcdefghijklmnopqrstuvwxyz,.!?")}
FILE="data/text/trainers.inc"
EN=r"abc\nabc\pdef\nxyz$"
VI="abc def\nghi jkl\\pmno pqr\nstu vwx$"
SOURCE='Label::\n\t.string "abc\\nabc\\pdef\\nxyz$"\nUnchanged::\n\t.string "abc$"\n'
ROW={"category":"system-text","source_file":FILE,"source_label":"Label",
     "english":EN,"vietnamese":VI}

class PagedNativeLFTests(unittest.TestCase):
    def test_reflows_only_inside_original_pages(self):
        updated,rows,skip=stage_paged_lf([ROW],{FILE:SOURCE},CODES,1,11)
        self.assertEqual(len(rows),1,skip)
        self.assertEqual(rows[0]["raw_LF_count"],2)
        self.assertEqual(rows[0]["authored_page_count"],2)
        self.assertEqual(rows[0]["page_word_counts"],[4,4])
        self.assertEqual(
            page_words(EN,rows[0]["vietnamese"]),
            page_words(EN,rows[0]["normalized_vietnamese"]))
        self.assertIn("Label::\n\t.byte ",updated[FILE])
        self.assertIn('Unchanged::\n\t.string "abc$"',updated[FILE])

    def test_refuses_moved_page_inserted_control_and_dynamics(self):
        invalid=[
            "abc def\\pmno pqr\nstu vwx$",     # missing first LF
            "abc def\nghi jkl\\pabc\nabc\\lghi$", # changed extra control
            "abc def\nghi jkl\\pmno {PLAYER}\nstu$",
            "abc def\nghi jkl\\pmno đ\nstu vwx$",
            "abc def\nghi jkl\\pmno pqr\nstu  vwx$",
        ]
        for vi in invalid:
            with self.subTest(vi=vi):
                new,rows,skip=stage_paged_lf(
                    [{**ROW,"vietnamese":vi}],{FILE:SOURCE},CODES)
                self.assertFalse(rows)
                self.assertTrue(skip)
                self.assertEqual(new[FILE],SOURCE)

    def test_no_source_mismatch_or_duplicate_identity(self):
        new,rows,skip=stage_paged_lf(
            [ROW],{FILE:SOURCE.replace("abc\\nabc", "wrong")},CODES)
        self.assertFalse(rows)
        self.assertTrue(any("English source is not exact" in x for x in skip))
        with self.assertRaisesRegex(ValueError,"duplicate source owner"):
            stage_paged_lf([ROW,ROW],{FILE:SOURCE},CODES)
        _,rows,_=stage_paged_lf(
            [{**ROW,"category":"map-story"}],{FILE:SOURCE},CODES)
        self.assertFalse(rows)

if __name__=="__main__":
    unittest.main()
