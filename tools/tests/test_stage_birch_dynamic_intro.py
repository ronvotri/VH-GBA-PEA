#!/usr/bin/env python3
"""Birch name placeholders are runtime bytes, never editorial substitutions."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_birch_dynamic_intro import (encode,tokens,verify_engine,stage,
    check_linker,OWNER,LABELS)

GLYPHS={x:i+1 for i,x in enumerate("Vậy cháu là ?Ra vì! sẽ chuyển tớiLITTLEROOT, quê ta.Giờ nhớ rồi")}
CHARMAP="PLAYER = FD 01\nKUN = FD 05\n"
STRINGS='const u8 gText_ExpandedPlaceholder_Kun[] = _("");\nconst u8 gText_ExpandedPlaceholder_Chan[] = _("");\n'

class IntroDynamicTests(unittest.TestCase):
    def test_engine_and_placeholders_exact(self):
        verify_engine(CHARMAP,STRINGS)
        b=encode("Vậy cháu là {PLAYER}{KUN}?$",GLYPHS)
        self.assertEqual(b.count(b"\xFD\x01"),1)
        self.assertEqual(b.count(b"\xFD\x05"),1)
        self.assertEqual(b[-1],0xFF)
    def test_gender_fallback_fails(self):
        with self.assertRaisesRegex(ValueError,"KUN suffix"):
            verify_engine(CHARMAP,STRINGS.replace('Kun[] = _("")','Kun[] = _("-kun")'))
        with self.assertRaisesRegex(ValueError,"charmap"):
            verify_engine(CHARMAP.replace("FD 05","FD 06"),STRINGS)
    def test_dynamic_width_and_tokens_reject_drift(self):
        with self.assertRaisesRegex(ValueError,"26 cells"):
            encode("V"*20+"{PLAYER}{KUN}$",GLYPHS)
        with self.assertRaisesRegex(ValueError,"unsupported placeholder"):
            encode("{RIVAL}$",GLYPHS)
        self.assertEqual(tokens(r"Hi {PLAYER}{KUN}!\nBye$\p"),
                         ("{PLAYER}","{KUN}",r"\n",r"\p"))
        with self.assertRaisesRegex(ValueError,"unknown control"):
            tokens(r"{PLAYER}\x$")
    def test_source_owner_and_control_pagination_pinned(self):
        r1={"category":"system-text","source_file":OWNER,
            "source_label":LABELS[0],"english":"So {PLAYER}{KUN}?$",
            "vietnamese":"Vậy cháu là {PLAYER}{KUN}?$"}
        r2={"category":"system-text","source_file":OWNER,
            "source_label":LABELS[1],"english":r"Hi!\pMeet {PLAYER}{KUN}!\nTown.\lYep!\p$",
            "vietnamese":r"Ra vì!\p{PLAYER}{KUN} sẽ chuyển tới\nLITTLEROOT, quê ta.\lGiờ nhớ rồi!\p$"}
        src=(LABELS[0]+':\n\t.string "So {PLAYER}{KUN}?$"\n\n'
             +LABELS[1]+':\n\t.string "Hi!\\pMeet {PLAYER}{KUN}!\\nTown.\\lYep!\\p$"\n')
        updated,rows=stage([r1,r2],src,CHARMAP,STRINGS,GLYPHS)
        self.assertEqual(len(rows),2)
        self.assertIn(".byte",updated)
        self.assertIn(b"\xFD\x05",bytes.fromhex(rows[1]["payload_hex"]))
        wrong=dict(r2,vietnamese=r"Ra vì!\p{PLAYER}{KUN}!\p$")
        with self.assertRaisesRegex(ValueError,"pagination signature"):
            stage([r1,wrong],src,CHARMAP,STRINGS,GLYPHS)
    def test_linker_symbol_verification(self):
        data=encode("Vậy cháu là {PLAYER}{KUN}?$",GLYPHS)
        src=LABELS[0]+":\n\t.byte "+", ".join("0x%02X"%v for v in data)+"\n"
        row={"label":LABELS[0],"payload_hex":data.hex()}
        rom=bytes(48)+data+bytes(48)
        symbol="08000030 R "+LABELS[0]+"\n"
        self.assertTrue(check_linker(rom,symbol,src,[row])[0]["tokens_verified"])
        with self.assertRaisesRegex(ValueError,"wrong translated"):
            check_linker(rom,"08000031 R "+LABELS[0],src,[row])

if __name__=="__main__":unittest.main()
