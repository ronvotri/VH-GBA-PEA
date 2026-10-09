#!/usr/bin/env python3
"""Fail-closed C source localization tests."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_source_ui_translations import replace_c_string,stage

SAMPLE=(
    'const u8 gText_WirelessNotConnected[] = _("The Wireless Adapter is not\\nconnected.");\n'
    'const u8 gText_MainMenuOption[] = _("OPTION");\n'
)
LABEL="gText_WirelessNotConnected"
ENGLISH=r"The Wireless Adapter is not\nconnected."


class CSourceStageTests(unittest.TestCase):
    def test_preserve_other_symbol(self):
        changed=replace_c_string(SAMPLE,LABEL,ENGLISH,b"\xC7\xFF")
        self.assertIn("gText_WirelessNotConnected[] = {0xC7, 0xFF};",changed)
        self.assertIn('gText_MainMenuOption[] = _("OPTION");',changed)

    def test_exact_source_drift_fails(self):
        with self.assertRaisesRegex(ValueError,"source text drift"):
            replace_c_string(SAMPLE,LABEL,"wrong",b"\xC7\xFF")

    def test_duplicate_symbol_fails(self):
        with self.assertRaisesRegex(ValueError,"not unique"):
            replace_c_string(SAMPLE+SAMPLE,LABEL,ENGLISH,b"\xC7\xFF")

    def test_invalid_symbol_name_fails(self):
        with self.assertRaisesRegex(ValueError,"unsupported C label"):
            replace_c_string(SAMPLE,"gText_X; evil()",ENGLISH,b"\xFF")

    def test_early_terminator_fails(self):
        with self.assertRaisesRegex(ValueError,"invalid string terminator"):
            replace_c_string(SAMPLE,LABEL,ENGLISH,b"\xFF\xC7\xFF")

    def test_unknown_dynamic_skipped(self):
        rows=[{"category":"system-ui","source_file":"src/strings.c",
               "source_label":LABEL,"english":ENGLISH,
               "vietnamese":"Mẹ: {PLAYER} hiện ở đây\\nnhé!$"}]
        codes={"M":0xC7,"ẹ":0x11,":":0xF0," ":0,"h":0xDC,"i":0xDD,
               "ệ":0x81,"n":0xE2,"ở":0x19,"đ":0x56,"â":0x68,
               "y":0xED,"!":0xAB}
        _,accepted,skipped=stage(rows,SAMPLE,codes)
        self.assertEqual(accepted,[])
        self.assertTrue(skipped)

    def test_c_ui_source_without_explicit_dollar_is_staged(self):
        rows=[{"category":"system-ui","source_file":"src/strings.c",
               "source_label":LABEL,"english":ENGLISH,
               "vietnamese":r"abc abc abc\nabc abc."}]
        codes={"a":0xD5,"b":0xD6,"c":0xD7," ":0x00,".":0xAD}
        source,accepted,skipped=stage(rows,SAMPLE,codes)
        self.assertEqual(len(accepted),1,skipped)
        self.assertTrue(source.count("0xFF")>=1)
        self.assertFalse(accepted[0]["auto_wrapped"])

    def test_short_ui_label_is_not_selected(self):
        rows=[{"category":"system-ui","source_file":"src/strings.c",
               "source_label":"gText_MainMenuOption","english":"OPTION",
               "vietnamese":"Tùy chọn$"}]
        _,accepted,_=stage(rows,SAMPLE,{})
        self.assertFalse(accepted)

    def test_short_static_ui_is_opt_in_and_skips_prior_label(self):
        rows=[{"category":"system-ui","source_file":"src/strings.c",
               "source_label":"gText_MainMenuOption",
               "english":"OPTION","vietnamese":"Menu"}]
        source=SAMPLE
        codes={"M":0xC7,"e":0xD9,"n":0xE2,"u":0xE9}
        _,blocked,_=stage(rows,source,codes)
        self.assertFalse(blocked)
        edited,allowed,skipped=stage(rows,source,codes,include_short_static=True)
        self.assertEqual(len(allowed),1,skipped)
        self.assertIn("gText_MainMenuOption[] = {0xC7, 0xD9, 0xE2, 0xE9, 0xFF};",
                      edited)
        _,excluded,_=stage(rows,source,codes,include_short_static=True,
                           excluded_labels={"gText_MainMenuOption"})
        self.assertFalse(excluded)

    def test_only_system_ui_selected(self):
        rows=[{"category":"battle","source_file":"src/strings.c",
               "source_label":LABEL,"english":ENGLISH,
               "vietnamese":"test$"}]
        _,accepted,_=stage(rows,SAMPLE,{})
        self.assertFalse(accepted)

    def test_missing_source_symbol_is_skip(self):
        rows=[{"category":"system-ui","source_file":"src/strings.c",
               "source_label":"gText_FakeMissing","english":ENGLISH,
               "vietnamese":r"abc abc abc abc abc abc\\nabc$"}]
        _,accepted,skipped=stage(rows,SAMPLE,
                                  {"a":0xD5,"b":0xD6,"c":0xD7," ":0})
        self.assertFalse(accepted)
        self.assertTrue(skipped)


if __name__=="__main__":
    unittest.main()
