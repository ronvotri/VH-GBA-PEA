#!/usr/bin/env python3
"""System-text paginated source integration must be fail-closed and page-local."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_static_paged_system_text import exclude_source_owners,stage_system_pages
from stage_static_paged_map_dialogues import page_words
from stage_static_zero_page_dialogues import zero_page_words

GLYPHS={ch:i+1 for i,ch in enumerate(" abcdefghijklmnopqrstuvwxyz,.!?")}
FILE="data/text/trainers.inc"
PLAN=[
 {"category":"system-text","source_file":FILE,"source_label":"Intro",
  "english":r"abc\pabc$","vietnamese":r"abc def\pghi jkl$"},
 {"category":"system-text","source_file":FILE,"source_label":"Earlier",
  "english":r"abc\pabc$","vietnamese":r"abc\pdef$"},
]
SOURCE='Intro::\n\t.string "abc\\pabc$"\nEarlier::\n\t.string "abc\\pabc$"\n'

class SystemPagedTests(unittest.TestCase):
 def test_page_local_word_order_and_exact_owner(self):
  report={"mode":"apply","labels_staged":1,"translated":[
   {"source_file":FILE,"label":"Earlier"}]}
  remaining,excluded=exclude_source_owners(PLAN,[report])
  self.assertEqual(excluded,1)
  self.assertEqual([r["source_label"] for r in remaining],["Intro"])
  source,accepted,rejected=stage_system_pages(remaining,{FILE:SOURCE},GLYPHS)
  self.assertEqual(len(accepted),1,rejected)
  self.assertEqual(page_words(PLAN[0]["english"],accepted[0]["vietnamese"]),
                   page_words(PLAN[0]["english"],PLAN[0]["vietnamese"]))
  self.assertIn("Intro::\n\t.byte ",source[FILE])
  self.assertIn('Earlier::\n\t.string "abc\\pabc$"',source[FILE])

 def test_do_not_change_authored_page_boundaries_or_static_rules(self):
  bad=[
   r"abc\p{PLAYER}$",r"abc\pdef\pghi$",
   r"abc\vghi\pdef$",r"abc\p$",r"abc\pđẹp$",
  ]
  for value in bad:
   with self.subTest(value=value):
    candidate={**PLAN[0],"vietnamese":value}
    _,accepted,skipped=stage_system_pages([candidate],{FILE:SOURCE},GLYPHS)
    self.assertEqual(accepted,[])
    self.assertTrue(skipped)

 def test_refuse_duplicate_or_missing_earlier_owner(self):
  earlier={"mode":"apply","labels_staged":1,
           "translated":[{"source_file":FILE,"label":"Earlier"}]}
  with self.assertRaisesRegex(ValueError,"duplicate/missing"):
   exclude_source_owners(PLAN,[earlier,earlier])
  with self.assertRaisesRegex(ValueError,"missing from manifest"):
   exclude_source_owners(PLAN,[{"mode":"apply","labels_staged":1,
      "translated":[{"source_file":FILE,"label":"Unknown"}]}])
  with self.assertRaisesRegex(ValueError,"invalid earlier"):
   exclude_source_owners(PLAN,[{"mode":"dry-run","labels_staged":1,
      "translated":[{"source_file":FILE,"label":"Earlier"}]}])

 def test_skip_wrong_english_and_wrong_category(self):
  row=PLAN[0]
  _,ok,skipped=stage_system_pages([row],{FILE:'Intro::\n\t.string "WRONG$"\n'},GLYPHS)
  self.assertEqual(ok,[])
  self.assertTrue(any("English source is not exact" in why for why in skipped))
  _,ok,_=stage_system_pages([{**row,"category":"map-story"}],{FILE:SOURCE},GLYPHS)
  self.assertEqual(ok,[])

 def test_only_source_owned_inc_files(self):
  row={**PLAN[0],"source_file":"src/strings.c"}
  _,ok,_=stage_system_pages([row],{"src/strings.c":SOURCE},GLYPHS)
  self.assertEqual(ok,[])
  self.assertEqual(len(zero_page_words("abc$",r"abc def$")),2)

if __name__=="__main__":
 unittest.main()
