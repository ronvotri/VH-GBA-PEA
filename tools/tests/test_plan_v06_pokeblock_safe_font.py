#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plan_v06_pokeblock_safe_font import plan_v06,RELOCATION

PINNED=(
    "' '         = 00\n"
    "'='         = 35\n"
    "';'         = 36\n"
    "'d'         = D8\n"
    "'i'         = DD\n"
    "'f'         = DA\n"
    "'w'         = EB\n"
    "'z'         = EE\n"
    "PK          = 53\n"
    "PKMN        = 53 54\n"
    "POKEBLOCK   = 55 56 57 58 59\n"
    "@ Hiragana\n"
)
V05={"đ":"0x56","ì":"0x59","d":"0xD8","i":"0xDD",
     "f":"0xDA","w":"0xEB","z":"0xEE",
     "ấ":"0x30","ằ":"0x31","ắ":"0x32",
     "ế":"0x0E","é":"0x05"}


class PokeBlockSafePlanTests(unittest.TestCase):
    def test_free_33_37_protect_equals_sign_and_pk(self):
        final,qa=plan_v06(V05,PINNED)
        self.assertEqual(final["đ"],"0x33")
        self.assertEqual(final["ì"],"0x37")
        self.assertEqual(final["f"],"0xDA")
        self.assertEqual(final["ấ"],"0x30")
        self.assertTrue(qa["equals_sign_0x35_protected"])
        self.assertEqual(qa["native_special_bytes_preserved"]["POKEBLOCK"],
                         ["0x55","0x56","0x57","0x58","0x59"])

    def test_glyph_slot_35_rejected_as_reserved_equals_sign(self):
        old=RELOCATION["ì"]["target"]
        try:
            RELOCATION["ì"]["target"]=0x35
            with self.assertRaisesRegex(ValueError,"occupied"):
                plan_v06(V05,PINNED)
        finally:
            RELOCATION["ì"]["target"]=old

    def test_occupied_37_is_not_overwritten(self):
        with self.assertRaisesRegex(ValueError,"occupied"):
            plan_v06({**V05,"X":"0x37"},PINNED)

    def test_incorrect_old_slot_refused(self):
        with self.assertRaisesRegex(ValueError,"untrusted"):
            plan_v06({**V05,"đ":"0x57"},PINNED)

    def test_missing_native_token_refused(self):
        with self.assertRaisesRegex(ValueError,"Pokéblock"):
            plan_v06(V05,PINNED.replace("55 56 57 58 59","55 56 57 58"))

    def test_older_f_w_z_safety_still_enforced(self):
        with self.assertRaisesRegex(ValueError,"v0.5"):
            plan_v06({**V05,"f":"0x11"},PINNED)

    def test_no_duplicate_codebook_bytes(self):
        with self.assertRaisesRegex(ValueError,"overlapping"):
            plan_v06({**V05,"unrelated":"0x05"},PINNED)

if __name__=="__main__":
    unittest.main()
