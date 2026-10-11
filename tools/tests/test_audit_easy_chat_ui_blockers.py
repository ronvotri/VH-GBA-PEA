import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from audit_easy_chat_ui_blockers import audit

P="src/data/easy_chat/easy_chat_group_greetings.h"
def row(label,english,vietnamese):
    return {"source_file":P,"source_label":"gEasyChatWord_"+label,
            "english":english,"vietnamese":vietnamese}

class AuditEasyChatTests(unittest.TestCase):
    def test_separate_length_glyph_and_valid_conditions(self):
        rows=[
            row("One","HELLO","HI"),
            row("Two","BYE","CHAOBAN"),
            row("Three","HELLO","Ừ"),
            row("Four","HI","HI"),
        ]
        r=audit(rows,{c:i+1 for i,c in enumerate("HIBYELAO")})
        counts=r["totals"]
        self.assertEqual(r["distinct_easy_chat_owners"],4)
        self.assertEqual(counts["eligible_with_current_codebook"],1)
        self.assertEqual(counts["translated_longer_than_english"],1)
        self.assertEqual(counts["glyph_not_in_experimental_codebook"],1)
        self.assertEqual(counts["unchanged_or_empty"],1)
        self.assertFalse(r["source_text_modified"])
        self.assertFalse(r["font_art_generated"])
        self.assertFalse(r["safe_to_expand_UI_width_without_renderer_proof"])

    def test_no_duplicates_and_unrelated_sources(self):
        with self.assertRaisesRegex(ValueError,"duplicate"):
            audit([row("One","A","B"),row("One","A","B")],{"B":1})
        r=audit([{"source_file":"src/strings.c",
                  "source_label":"gEasyChatWord_One",
                  "english":"HELLO","vietnamese":"HI"}],{"H":1,"I":2})
        self.assertEqual(r["distinct_easy_chat_owners"],0)

if __name__=="__main__":
    unittest.main()
