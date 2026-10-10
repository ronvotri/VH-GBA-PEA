#!/usr/bin/env python3
"""Regression QA for conservative Vietnamese map dialogue word wrapping."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from wrap_vietnamese_map_text import auto_wrap_script_text
from stage_source_map_translations import plan_rows, encode_text


class TextWrappingTests(unittest.TestCase):
    def test_preserve_short(self):
        self.assertEqual(auto_wrap_script_text("Cậu khỏe không?$"),"Cậu khỏe không?$")

    def test_newline_on_first_overflow(self):
        result=auto_wrap_script_text("Mẹ: Mẹ đã dọn xong rồi con!$")
        self.assertEqual(result,r"Mẹ: Mẹ đã dọn xong rồi\ncon!$")

    def test_scroll_on_second_overflow(self):
        source=r"Ở đây vui mà, đúng không?\nChỉ đứng đây thôi tôi cũng thấy phấn khích!$"
        self.assertEqual(auto_wrap_script_text(source),
                         r"Ở đây vui mà, đúng không?\nChỉ đứng đây thôi tôi cũng\lthấy phấn khích!$")

    def test_quote_is_atomic(self):
        self.assertEqual(
            auto_wrap_script_text(r"Cánh cửa đã khóa.\pTrên cửa có sơn chữ “RM. 1”.$"),
            r"Cánh cửa đã khóa.\pTrên cửa có sơn chữ\n“RM. 1”.$")

    def test_page_break_preserved(self):
        original=r"Chào cậu!\pHẹn gặp lại nhé!$"
        self.assertEqual(auto_wrap_script_text(original),original)

    def test_scroll_preserved(self):
        original=r"Xin chào.\lTạm biệt!$"
        self.assertEqual(auto_wrap_script_text(original),original)

    def test_long_word_rejected(self):
        with self.assertRaisesRegex(ValueError,"word longer"):
            auto_wrap_script_text("a"*27+"$")

    def test_dynamic_rejected(self):
        with self.assertRaisesRegex(ValueError,"dynamic placeholder"):
            auto_wrap_script_text(r"{PLAYER} ơi, về nhà đi nhé!$")

    def test_explicit_third_line_rejected(self):
        with self.assertRaisesRegex(ValueError,"explicit third"):
            auto_wrap_script_text(r"Xin chào\nTạm biệt\nLần sau gặp!$")

    def test_explicit_third_line_opt_in_scrolls_not_pages(self):
        source=r"Xin chào\\nTạm biệt\\nLần sau gặp!$"
        fixed=auto_wrap_script_text(source,page_scroll_reflow=True)
        self.assertEqual(fixed,r"Xin chào\\nTạm biệt\\lLần sau gặp!$")
        self.assertEqual(fixed.count(r"\\p"),source.count(r"\\p"))

    def test_explicit_third_line_opt_in_keeps_page_break(self):
        source=r"Xin chào\\pTạm biệt\\nHôm nay\\nCảm ơn!$"
        fixed=auto_wrap_script_text(source,page_scroll_reflow=True)
        self.assertEqual(fixed,r"Xin chào\\pTạm biệt\\nHôm nay\\lCảm ơn!$")

    def test_unknown_control_rejected(self):
        with self.assertRaisesRegex(ValueError,"unrecognized"):
            auto_wrap_script_text(r"Có gì\c kỳ lạ?$")

    def test_double_spaces_rejected(self):
        with self.assertRaisesRegex(ValueError,"ambiguous"):
            auto_wrap_script_text("Chào  cậu!$")

    def test_missing_terminator_rejected(self):
        with self.assertRaisesRegex(ValueError,"terminator"):
            auto_wrap_script_text("Chào cậu")

    def test_length_not_just_less_than_limit(self):
        wrapped=auto_wrap_script_text("abc abc abc abc abc abc abc abc abc$",10)
        codes={"a":0xD5,"b":0xD6,"c":0xD7," ":0x00}
        blob=encode_text(wrapped,codes,10)
        self.assertEqual(blob[-1],0xFF)
        self.assertIn(0xFE,blob)
        self.assertIn(0xFA,blob)

    def test_plan_rows_opt_in(self):
        row={"source_label":"X","source_file":"data/maps/X/scripts.inc",
             "category":"map-story","english":"something else$",
             "vietnamese":"abc abc abc abc abc abc$"}
        codes={"a":0xD5,"b":0xD6,"c":0xD7," ":0x00}
        blocked,_=plan_rows([row],codes,"data/maps/",12,20,False)
        self.assertEqual(len(blocked),0)
        accepted,_=plan_rows([row],codes,"data/maps/",12,20,True)
        self.assertEqual(len(accepted),1)
        self.assertTrue(accepted[0][0]["auto_wrapped"])
        self.assertEqual(accepted[0][0]["authored_vietnamese"],row["vietnamese"])


if __name__=="__main__":
    unittest.main()
