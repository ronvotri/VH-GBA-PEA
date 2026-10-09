#!/usr/bin/env python3
"""Complete move description readiness: 354 source translations, no fake padding.

Every translated move must fit exactly the GBA's two-line, 26-cell description
box, either directly or via a word-boundary rebalance with no lost word.
Checks encoding in the v0.5 collision-free codebook. Source equality/ROM build
and actual 2D pixel rendering remain distinct CI/runtime gates.
"""
import json
import unittest
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from stage_source_descriptions import rebalance_two_line_description
from stage_source_map_translations import encode_text


class AllMoveDescriptionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.codes={ch:int(code,16) for ch,code in
                   json.loads((ROOT/"checkpoints/v05-collision-free-codebook.json")
                              .read_text(encoding="utf-8"))["glyph_bytes"].items()}
        cls.rows={}
        for file in sorted((ROOT/"translations/system-ui").glob("move-descriptions-*.vi.json")):
            for label,value in json.loads(file.read_text(encoding="utf-8"))["translations"].items():
                if label in cls.rows:
                    raise AssertionError(f"duplicate move description: {label}")
                cls.rows[label]=value

    def test_source_manifest_complete(self):
        self.assertEqual(len(self.rows),354)

    def test_all_move_descriptions_fit_two_encoded_lines(self):
        rebalanced=[]
        for label,authored in self.rows.items():
            with self.subTest(move=label):
                self.assertEqual(authored.count(r"\n"),1)
                self.assertNotIn(r"\p",authored)
                self.assertNotIn(r"\l",authored)
                self.assertNotIn("{",authored)
                normalized=authored+"$"
                if any(len(s)>26 for s in authored.split(r"\n")):
                    normalized=rebalance_two_line_description(normalized,26)
                    rebalanced.append(label)
                self.assertEqual(normalized.count(r"\n"),1)
                encoded=encode_text(normalized,self.codes,26)
                self.assertEqual(encoded[-1],0xFF)
                self.assertEqual(encoded.count(0xFE),1)
                self.assertNotIn(0xFF,encoded[:-1])
        self.assertEqual(len(rebalanced),39)


if __name__=="__main__":
    unittest.main()
