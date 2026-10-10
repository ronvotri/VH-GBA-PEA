#!/usr/bin/env python3
"""Fail-closed smoke tests for source-level Vietnamese map text insertion."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stage_source_map_translations import encode_text, patch_labeled_block, plan_rows, prioritized_rows, normalize_authored_linefeeds, exclude_previously_staged, exclude_explicit_source_labels


class SourceStagingTests(unittest.TestCase):
    codes={"M":0xC7,"ẹ":0x21,":":0xF0," ":0x00,"n":0xE2,
           "h":0xDC,"à":0x16,"!":0xAB,"a":0xD5,"b":0xD6,
           "c":0xD7,"q":0xE5,"u":0xE9,"á":0x17}

    def test_accents_controls(self):
        self.assertEqual(encode_text("Mẹ: nhà!\\p$",self.codes,26),
                         bytes([0xC7,0x21,0xF0,0,0xE2,0xDC,0x16,0xAB,0xFB,0xFF]))

    def test_exact_labeled_assembly_replacement(self):
        source=('Other:\n\t.string "hello$"\n\n'
                'Name:\n\t.string "one\\n"\n\t.string "two$"\n\n'
                'After:\n\t.string "done$"\n')
        updated=patch_labeled_block(source,"Name","one\\ntwo$",b"\xC7\xFF")
        self.assertIn("Name:\n\t.byte 0xC7, 0xFF\n",updated)
        self.assertIn('\t.string "hello$"',updated)
        self.assertIn('\t.string "done$"',updated)
        self.assertNotIn('\t.string "one\\n"',updated)

    def test_fail_closed_source_drift(self):
        with self.assertRaisesRegex(ValueError,"not exact pinned match"):
            patch_labeled_block('Name:\n\t.string "wrong$"\n',
                                "Name","right$",b"\xFF")

    def test_fail_closed_no_label(self):
        with self.assertRaisesRegex(ValueError,"0 source labels"):
            patch_labeled_block('Wrong:\n\t.string "text$"\n',
                                "Name","text$",b"\xFF")

    def test_dynamic_tokens_not_supported(self):
        with self.assertRaisesRegex(ValueError,"unsupported dynamic"):
            encode_text("Mẹ: {PLAYER}$",self.codes,26)

    def test_opt_in_literal_lf_matches_exact_source_controls(self):
        english=r"a\nb$"
        original="a\nb$"
        self.assertEqual(normalize_authored_linefeeds(english,original),english)
        row={"source_label":"A","source_file":"data/maps/Route101/scripts.inc",
             "category":"map-story","english":english,"vietnamese":original}
        unpatched,skipped=plan_rows([row],self.codes,"data/maps/",26,10)
        self.assertFalse(unpatched)
        self.assertTrue(any("missing Vietnamese glyph" in reason for reason in skipped))
        patched,errors=plan_rows([row],self.codes,"data/maps/",26,10,
                                 normalize_literal_newlines=True)
        self.assertFalse(errors)
        self.assertEqual(len(patched),1)
        self.assertEqual(patched[0][1],bytes([0xD5,0xFE,0xD6,0xFF]))
        self.assertEqual(patched[0][0]["authored_vietnamese"],original)
        self.assertTrue(patched[0][0]["literal_newlines_normalized"])

    def test_exact_prior_source_labels_are_excluded_for_incremental_stage(self):
        rows=[
            {"source_label":"A","source_file":"data/maps/A/scripts.inc","category":"map-story"},
            {"source_label":"A","source_file":"data/maps/B/scripts.inc","category":"map-story"},
            {"source_label":"C","source_file":"data/maps/A/scripts.inc","category":"map-story"},
        ]
        prior={"mode":"apply","labels_staged":1,"translated":[
            {"label":"A","source_file":"data/maps/A/scripts.inc"}]}
        remaining,count=exclude_previously_staged(rows,[prior])
        self.assertEqual(count,1)
        self.assertEqual([(r["source_file"],r["source_label"]) for r in remaining],
                         [("data/maps/B/scripts.inc","A"),("data/maps/A/scripts.inc","C")])

    def test_invalid_or_duplicate_prior_stage_reports_are_rejected(self):
        rows=[{"source_label":"A","source_file":"data/maps/A/scripts.inc"}]
        prior={"mode":"dry-run","labels_staged":1,"translated":[
            {"label":"A","source_file":"data/maps/A/scripts.inc"}]}
        with self.assertRaisesRegex(ValueError,"invalid previously"):
            exclude_previously_staged(rows,[prior])
        prior["mode"]="apply"
        with self.assertRaisesRegex(ValueError,"duplicate label"):
            exclude_previously_staged(rows,[prior,prior])

    def test_explicit_source_exclusion_preserves_exact_other_category(self):
        rows=[
            {"source_file":"data/text/birch_speech.inc","source_label":"BirchX",
             "category":"system-text","english":"a$","vietnamese":"b$"},
            {"source_file":"data/text/birch_speech.inc","source_label":"BirchY",
             "category":"system-text","english":"a$","vietnamese":"b$"},
            {"source_file":"data/maps/X/scripts.inc","source_label":"BirchX",
             "category":"map-story","english":"a$","vietnamese":"b$"},
        ]
        filtered=exclude_explicit_source_labels(rows,["BirchX"],
                                                "system-text","data/text/")
        self.assertEqual(len(filtered),2)
        self.assertTrue(any(row["category"]=="map-story" for row in filtered))
        remaining,errors=plan_rows(filtered,self.codes,"data/text/",26,10,
                                   category="system-text")
        self.assertFalse(errors)
        self.assertEqual([row["source_label"] for row,_ in remaining],["BirchY"])
        with self.assertRaisesRegex(ValueError,"duplicate explicit"):
            exclude_explicit_source_labels(rows,["BirchX","BirchX"],
                                           "system-text","data/text/")
        with self.assertRaisesRegex(ValueError,"missing or ambiguous"):
            exclude_explicit_source_labels(rows,["NotARealLabel"],
                                           "system-text","data/text/")

    def test_only_literal_lf_batch_does_not_restage_normal_rows(self):
        rows=[
            {"source_label":"Regular","source_file":"data/maps/Route101/scripts.inc",
             "category":"map-story","english":"a$","vietnamese":"b$"},
            {"source_label":"LiteralLF","source_file":"data/maps/Route101/scripts.inc",
             "category":"map-story","english":r"a\\nb$","vietnamese":"a\nb$"},
        ]
        selected,skipped=plan_rows(rows,self.codes,"data/maps/",26,100,
                                   normalize_literal_newlines=True,
                                   only_literal_newlines=True)
        self.assertFalse(skipped)
        self.assertEqual([row["source_label"] for row,_ in selected],["LiteralLF"])
        self.assertEqual(selected[0][1],bytes([0xD5,0xFE,0xD6,0xFF]))

    def test_literal_lf_must_not_replace_page_or_change_order(self):
        for english,vietnamese in (
            (r"a\pb$","a\nb$"),
            (r"a\nb\p$","a\\p\nb$"),
            ("ab$","a\nb$"),
        ):
            with self.subTest(english=english,vietnamese=vietnamese):
                with self.assertRaisesRegex(ValueError,"control sequence differs"):
                    normalize_authored_linefeeds(english,vietnamese)

    def test_opt_in_never_changes_existing_escaped_controls(self):
        text=r"a\nb\p$"
        self.assertEqual(normalize_authored_linefeeds(text,text),text)

    def test_system_text_static_page_scroll_reflow_has_explicit_gate(self):
        row={"source_label":"SystemStory","source_file":"data/text/a.inc",
             "category":"system-text","english":r"a\nb$",
             "vietnamese":r"aaa aaa aaa aaa\nbbb bbb bbb bbb$"}
        codes={"a":0xD5,"b":0xD6," ":0x00}
        blocked,errors=plan_rows([row],codes,"data/text/",10,100,
                                  auto_wrap=True,category="system-text")
        self.assertFalse(blocked)
        self.assertIn("auto-wrap: explicit third line requires review",errors)
        chosen,errors=plan_rows([row],codes,"data/text/",10,100,
                                 auto_wrap=True,category="system-text",
                                 page_scroll_reflow=True)
        self.assertFalse(errors)
        self.assertEqual(len(chosen),1)
        self.assertTrue(chosen[0][0]["page_scroll_reflowed"])
        self.assertIn(r"\l",chosen[0][0]["vietnamese"])
        self.assertEqual(chosen[0][1][-1],0xFF)

    def test_system_scroll_reflow_rejects_control_drift_and_dynamic(self):
        codes={"a":0xD5,"b":0xD6," ":0x00}
        base={"source_label":"SystemStory","source_file":"data/text/a.inc",
              "category":"system-text","english":r"a\pb$",
              "vietnamese":r"aaa aaa aaa aaa\nbbb bbb bbb bbb$"}
        chosen,errors=plan_rows([base],codes,"data/text/",10,100,
                                 auto_wrap=True,category="system-text",
                                 page_scroll_reflow=True)
        self.assertFalse(chosen)
        self.assertIn("page-scroll: source controls/placeholder drift",errors)
        dyn={**base,"english":r"{PLAYER}\nb$"}
        chosen,_=plan_rows([dyn],codes,"data/text/",10,100,
                            auto_wrap=True,category="system-text",
                            page_scroll_reflow=True)
        self.assertFalse(chosen)

    def test_unknown_glyph_rejected(self):
        with self.assertRaisesRegex(ValueError,"missing Vietnamese glyph"):
            encode_text("Mẹ Æ$",self.codes,26)

    def test_early_terminator_rejected(self):
        with self.assertRaisesRegex(ValueError,"early terminator"):
            encode_text("a$b$",self.codes,26)

    def test_control_byte_collision_rejected(self):
        with self.assertRaisesRegex(ValueError,"collides with control byte"):
            encode_text("a$",{"a":0xFD},26)

    def test_line_length_rejected(self):
        with self.assertRaisesRegex(ValueError,"exceeds"):
            encode_text("a"*27+"$",self.codes,26)

    def test_non_nfc_rejected(self):
        with self.assertRaisesRegex(ValueError,"non-NFC"):
            encode_text("a\u0301$",self.codes,26)

    def test_stable_priority_is_early_game_first(self):
        labels=[
            {"source_file":"data/maps/AbandonedShip/scripts.inc","source_label":"A"},
            {"source_file":"data/maps/LittlerootTown/scripts.inc","source_label":"FIRST"},
            {"source_file":"data/maps/OldaleTown/scripts.inc","source_label":"NEXT"},
            {"source_file":"data/maps/LittlerootTown/scripts.inc","source_label":"SECOND"},
        ]
        ordered=prioritized_rows(labels,[
            "data/maps/LittlerootTown/","data/maps/OldaleTown/"])
        self.assertEqual([x["source_label"] for x in ordered],
                         ["FIRST","SECOND","NEXT","A"])

    def test_prioritized_staging_honors_limit(self):
        rows=[
            {"category":"map-story","source_file":"data/maps/AbandonedShip/scripts.inc",
             "source_label":"OLD","english":"a$","vietnamese":"b$"},
            {"category":"map-story","source_file":"data/maps/LittlerootTown/scripts.inc",
             "source_label":"INTRO","english":"a$","vietnamese":"b$"},
        ]
        chosen,_=plan_rows(rows,self.codes,"data/maps/",26,1,False,
                           ["data/maps/LittlerootTown/"])
        self.assertEqual([r["source_label"] for r,_ in chosen],["INTRO"])

    def test_system_text_is_selected_by_exact_category_not_filename(self):
        rows=[
            {"category":"system-text","source_file":"data/text/cable_club.inc",
             "source_label":"SystemGreeting","english":"a$","vietnamese":"b$"},
            {"category":"battle","source_file":"data/text/cable_club.inc",
             "source_label":"BattleGreeting","english":"a$","vietnamese":"b$"},
        ]
        chosen,rejected=plan_rows(rows,self.codes,"data/text/",26,20,
                                  category="system-text")
        self.assertFalse(rejected)
        self.assertEqual([r["source_label"] for r,_ in chosen],["SystemGreeting"])
        self.assertEqual(chosen[0][1],bytes([0xD6,0xFF]))

    def test_battle_source_is_explicitly_selected(self):
        rows=[
            {"category":"battle","source_file":"data/text/battle_dome.inc",
             "source_label":"BattleDome_Text_Potential1",
             "english":"a$","vietnamese":"b$"},
            {"category":"map-story","source_file":"data/maps/LittlerootTown/scripts.inc",
             "source_label":"Other","english":"a$","vietnamese":"b$"}
        ]
        chosen,_=plan_rows(rows,self.codes,"data/text/",26,10,False,[],"battle")
        self.assertEqual([row["source_label"] for row,_ in chosen],
                         ["BattleDome_Text_Potential1"])

    def test_double_colon_battle_source_matches(self):
        source=('BattleDome_Text_Potential1::\n'
                '\t.string "a$"\n\n'
                'BattleDome_Text_Potential2::\n'
                '\t.string "b$"\n')
        updated=patch_labeled_block(
            source,"BattleDome_Text_Potential1","a$",bytes([0xD6,0xFF]))
        self.assertIn("BattleDome_Text_Potential1::\n\t.byte 0xD6, 0xFF",updated)
        self.assertIn('BattleDome_Text_Potential2::\n\t.string "b$"',updated)

    def test_limited_map_selection(self):
        rows=[{"category":"map-story",
               "source_file":"data/maps/LittlerootTown/scripts.inc",
               "source_label":"X","english":"a$","vietnamese":"b$"},
              {"category":"battle",
               "source_file":"data/maps/LittlerootTown/scripts.inc",
               "source_label":"Y","english":"a$","vietnamese":"b$"}]
        chosen,_=plan_rows(rows,self.codes,"data/maps/LittlerootTown/",26,20)
        self.assertEqual(len(chosen),1)


if __name__=="__main__":unittest.main()
