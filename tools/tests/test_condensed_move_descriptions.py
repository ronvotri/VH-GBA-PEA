#!/usr/bin/env python3
"""Editorial regression for the 62 short, accented Gen III move descriptions.

The 62 revisions were independently reviewed for mechanics and then checked
against the actual source-build v0.5 glyph codebook. Protect them from drift
toward overlong rows, unknown accents, page controls, or lost key values.
This does NOT certify emulator pixel width or visual typography.
"""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
FILES=ROOT/"translations/system-ui"
CODEBOOK=ROOT/"checkpoints/v05-collision-free-codebook.json"
LABELS="""
sGustDescription sJumpKickDescription sTakeDownDescription
sThrashDescription sPoisonStingDescription sBlizzardDescription
sHyperBeamDescription sPetalDanceDescription sEarthquakeDescription
sToxicDescription sSmokescreenDescription sBideDescription
sMetronomeDescription sSelfDestructDescription sLickDescription
sSmogDescription sSludgeDescription sHiJumpKickDescription
sPoisonGasDescription sLovelyKissDescription sExplosionDescription
sBonemerangDescription sConversionDescription sStruggleDescription
sThiefDescription sMindReaderDescription sNightmareDescription
sSnoreDescription sConversion2Description sSpiteDescription
sPowderSnowDescription sSludgeBombDescription sZapCannonDescription
sOutrageDescription sSwaggerDescription sFrustrationDescription
sDynamicPunchDescription sBatonPassDescription sPursuitDescription
sIronTailDescription sVitalThrowDescription sMirrorCoatDescription
sPsychUpDescription sWhirlpoolDescription sFakeOutDescription
sSpitUpDescription sSmellingSaltDescription sFollowMeDescription
sRevengeDescription sKnockOffDescription sGrudgeDescription
sNeedleArmDescription sBlastBurnDescription sHydroCannonDescription
sAstonishDescription sAromatherapyDescription sSignalBeamDescription
sExtrasensoryDescription sSandTombDescription sFrenzyPlantDescription
sBulkUpDescription sWaterPulseDescription
""".split()
MECHANICS={
    "sThrashDescription":("2-3", "bối rối"),
    "sOutrageDescription":("2-3", "bối rối"),
    "sPetalDanceDescription":("2-3", "bối rối"),
    "sBideDescription":("2 lượt", "gấp đôi"),
    "sNightmareDescription":("1/4 HP",),
    "sBonemerangDescription":("hai lần",),
    "sHyperBeamDescription":("lượt sau", "nghỉ"),
    "sPoisonGasDescription":("trúng độc",),
    "sZapCannonDescription":("tê", "trượt"),
    "sVitalThrowDescription":("sau cùng", "chắc chắn"),
    "sMirrorCoatDescription":("gấp đôi",),
    "sRevengeDescription":("gấp đôi", "trong lượt"),
    "sGrudgeDescription":("PP", "0"),
    "sBlastBurnDescription":("nghỉ",),
    "sHydroCannonDescription":("nghỉ",),
    "sFrenzyPlantDescription":("nghỉ",),
    "sBulkUpDescription":("ATTACK", "DEFENSE"),
}


def source_rows():
    rows={}
    for f in sorted(FILES.glob("move-descriptions-*.vi.json")):
        source=json.loads(f.read_text(encoding="utf-8"))
        for label,value in source["translations"].items():
            if label in rows:
                raise AssertionError(f"Duplicate translated move description: {label}")
            rows[label]=value
    return rows


class CondensedMoveDescriptionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=source_rows()
        cls.codebook=json.loads(CODEBOOK.read_text(encoding="utf-8"))["glyph_bytes"]

    def test_all_62_labels_preserved(self):
        self.assertEqual(len(LABELS),62)
        self.assertEqual(len(set(LABELS)),62)
        self.assertTrue(set(LABELS).issubset(self.rows),
                        sorted(set(LABELS)-set(self.rows)))

    def test_each_move_has_two_lines_under_26_cells(self):
        for label in LABELS:
            with self.subTest(move=label):
                value=self.rows[label]
                lines=value.split(r"\n")
                self.assertEqual(len(lines),2)
                for line in lines:
                    self.assertTrue(0<len(line)<=26,(label,len(line),line))
                self.assertNotIn("$",value)
                self.assertNotIn("{",value)
                self.assertNotIn(r"\p",value)
                self.assertNotIn(r"\l",value)
                self.assertNotIn("  ",value)

    def test_no_unsupported_vietnamese_glyphs(self):
        for label in LABELS:
            unknown=set(self.rows[label].replace(r"\n",""))-set(self.codebook)
            self.assertFalse(unknown,(label,unknown))

    def test_move_mechanics_survive_shortening(self):
        for label,parts in MECHANICS.items():
            text=self.rows[label].replace(r"\n"," ")
            for part in parts:
                self.assertIn(part,text,(label,part))


if __name__=="__main__":
    unittest.main()
