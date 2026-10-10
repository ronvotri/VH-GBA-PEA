#!/usr/bin/env python3
"""Regressions for GBA naming-screen buttons and YES/NO controls."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_naming_controls import (PINNED,EXPECTED,encode,ordered_controls,
                                   verify_charmap,stage,validate_linked_bytes)
CHARS="Di chuyển  OK  Quay lạiCóKhông"
BOOK={c:i+1 for i,c in enumerate(dict.fromkeys(CHARS))}
CHARMAP="DPAD_NONE = F8 0C\nA_BUTTON = F8 00\nB_BUTTON = F8 01\n"

class NamingSourceControls(unittest.TestCase):
    def test_original_engine_controls_untouched(self):
        verify_charmap(CHARMAP)
        for label,record in EXPECTED.items():
            self.assertEqual(ordered_controls(record["english"]),
                             ordered_controls(record["vietnamese"]))
            payload=encode(record["vietnamese"],BOOK,record["max_cells"])
            self.assertEqual(payload[-1],0xFF)
            if label=="gText_MoveOkBack":
                for b in PINNED.values():self.assertEqual(payload.count(b),1)
            else:self.assertEqual(payload.count(0xFE),1)
    def test_unexpected_icons_glyphs_and_font_drift_refused(self):
        with self.assertRaisesRegex(ValueError,"charmap"):
            verify_charmap(CHARMAP.replace("F8 0C","F8 0B"))
        with self.assertRaisesRegex(ValueError,"unsupported"):
            encode("{PLAYER}A",BOOK,30)
        with self.assertRaisesRegex(ValueError,"font glyph"):
            encode("Ố",BOOK,30)
        with self.assertRaisesRegex(ValueError,"too wide"):
            encode("Di chuyển"*6,BOOK,30)
    def test_exact_source_and_linker_payloads(self):
        raw="\n".join('const u8 '+key+'[] = _("'+rec["english"]+'");'
                      for key,rec in EXPECTED.items())+"\n"
        rows=[{"source_label":key,"source_file":"src/strings.c",
               "category":"system-ui","english":rec["english"],
               "vietnamese":rec["vietnamese"]}
              for key,rec in EXPECTED.items()]
        source,installed=stage(rows,raw,CHARMAP,BOOK)
        data=bytearray(b"\0"*400)
        locations=[0x20,0xF0]
        symbol=[]
        for i,(row,offset) in enumerate(zip(installed,locations)):
            p=bytes.fromhex(row["payload_hex"])
            data[offset:offset+len(p)]=p
            symbol.append(f"0800{offset:04X} R {row['label']}")
        checked=validate_linked_bytes(bytes(data),"\n".join(symbol),
                                      source,installed)
        self.assertEqual(len(checked),2)
        with self.assertRaisesRegex(ValueError,"compiled ROM bytes mismatch"):
            validate_linked_bytes(bytes(data),"\n".join(symbol).replace(
                "08000020","08000021"),source,installed)
        with self.assertRaisesRegex(ValueError,"authority drift"):
            stage([dict(rows[0],english="MOVE"),rows[1]],raw,CHARMAP,BOOK)

if __name__=="__main__":unittest.main()
