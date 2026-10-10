#!/usr/bin/env python3
"""The visible Birch runtime label is a C string, not the unused asm twin."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_birch_runtime_pokemon_c import encode,verify_rom,ENGLISH,SUFFIX,CONTROL

class BirchRuntimeCTests(unittest.TestCase):
    def setUp(self):
        self.glyphs={c:i+1 for i,c in enumerate("Đây là một POKéMON.")}
        self.row={"category":"system-ui","source_file":"src/strings.c",
                  "source_label":"gText_ThisIsAPokemon","english":ENGLISH,
                  "vietnamese":"Đây là một POKéMON."+SUFFIX}
    def test_controls_exact_and_unique(self):
        payload,_=encode([self.row],self.glyphs,"PAUSE = FC 08")
        self.assertTrue(payload.endswith(CONTROL))
        self.assertEqual(payload.count(0xFF),1)
        self.assertEqual(payload[-5:],b"\xFC\x08\x60\xFB\xFF")
    def test_invalid_tokens_or_bad_owner_rejected(self):
        r=dict(self.row,vietnamese="Đây là một POKéMON."+r"\p")
        with self.assertRaisesRegex(ValueError,"PAUSE"):
            encode([r],self.glyphs,"PAUSE = FC 08")
        with self.assertRaisesRegex(ValueError,"charmap"):
            encode([self.row],self.glyphs,"PAUSE = FC 09")
        with self.assertRaisesRegex(ValueError,"source drift"):
            encode([dict(self.row,source_file="data/text/birch_speech.inc")],self.glyphs,"PAUSE = FC 08")
        with self.assertRaisesRegex(ValueError,"ambiguous"):
            encode([self.row,self.row],self.glyphs,"PAUSE = FC 08")
    def test_binary_symbol_payload(self):
        payload,_=encode([self.row],self.glyphs,"PAUSE = FC 08")
        rom=bytes(0x30)+payload+bytes(30)
        report={"payload_hex":payload.hex()}
        result=verify_rom(rom,"08000030 R gText_ThisIsAPokemon",report)
        self.assertTrue(result["compiled_rom_byte_verified"])
        with self.assertRaisesRegex(ValueError,"not present"):
            verify_rom(rom,"08000031 R gText_ThisIsAPokemon",report)

if __name__=="__main__":
    unittest.main()
