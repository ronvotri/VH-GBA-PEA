import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_first_battle_runtime_report import (
    validate_report, CLEAN_SHA, V04_SHA,
)

CANDIDATE = "a" * 64
SAVE = "b" * 64


def fixture():
    def row(name, digest):
        return {
            "variant": name, "rom_sha256": digest,
            "emulator": "mGBA", "emulator_version": "test-recorded-version",
            "sound_output": "enabled", "save_sha256": SAVE,
            "save_type": "battery_sav", "tested_in_emulator": True,
            "battle_started": True, "battle_completed": True,
            "returned_to_overworld": True, "moved_after_battle": True,
            "save_load_passed": True,
        }
    return {"schema_version": 1, "runs": [
        row("clean", CLEAN_SHA), row("v04", V04_SHA),
        row("candidate", CANDIDATE),
    ]}


class FirstBattleRuntimeEvidenceTests(unittest.TestCase):
    def test_full_evidence_accepts_first_battle_but_not_release(self):
        result = validate_report(fixture())
        self.assertEqual(result["first_battle_runtime_gate"], "PASS")
        self.assertIs(result["release_ready"], False)

    def test_freeze_never_becomes_pass(self):
        test = fixture()
        test["runs"][2]["moved_after_battle"] = False
        self.assertEqual(
            validate_report(test)["first_battle_runtime_gate"], "FAIL")

    def test_missing_real_emulator_and_savestate_refused(self):
        test = fixture()
        test["runs"][1]["tested_in_emulator"] = False
        with self.assertRaisesRegex(ValueError, "real emulator"):
            validate_report(test)
        test = fixture()
        test["runs"][2]["save_type"] = "save_state"
        with self.assertRaisesRegex(ValueError, "save states"):
            validate_report(test)

    def test_wrong_baseline_and_rejected_pointer_build_refused(self):
        test = fixture()
        test["runs"][1]["rom_sha256"] = CANDIDATE
        with self.assertRaisesRegex(ValueError, "approved v0.4"):
            validate_report(test)
        test = fixture()
        test["runs"][2]["rom_sha256"] = (
            "0bf451fda75f1e32c5b2fc865386009f02b6339d191c721d1346bacd8807e11b")
        with self.assertRaisesRegex(ValueError, "rejected"):
            validate_report(test)

    def test_ab_requires_same_exact_settings_and_checkpoint(self):
        for name, val in (
            ("emulator_version", "different"),
            ("sound_output", "disabled"),
            ("save_sha256", "c" * 64),
        ):
            with self.subTest(name=name):
                test = fixture()
                test["runs"][2][name] = val
                with self.assertRaisesRegex(ValueError, "identical"):
                    validate_report(test)

    def test_unobserved_status_and_incomplete_data_refused(self):
        test = fixture()
        test["runs"][2]["battle_completed"] = None
        with self.assertRaisesRegex(ValueError, "observed boolean"):
            validate_report(test)
        test = fixture()
        del test["runs"][0]["emulator"]
        with self.assertRaisesRegex(ValueError, "runtime evidence"):
            validate_report(test)
        test = fixture()
        test["runs"].append(copy.deepcopy(test["runs"][0]))
        with self.assertRaisesRegex(ValueError, "exactly clean"):
            validate_report(test)


if __name__ == "__main__":
    unittest.main()
