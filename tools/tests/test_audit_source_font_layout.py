#!/usr/bin/env python3
"""Guard source font digest verification against silent mismatches."""
import hashlib,sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import audit_source_font_layout as audit


class FontSourceDigestTests(unittest.TestCase):
    def setUp(self):
        self.data=bytes(range(128))*16
        self.symbols={n:i*128 for i,n in enumerate(audit.FONT_NAMES)}
        self.expected={n:hashlib.sha256(self.data[i*128:(i+1)*128]).hexdigest()
                       for i,n in enumerate(audit.FONT_NAMES)}

    def run_audit(self,data=None,expected=None):
        with patch.object(audit,"ROM_BYTES",len(self.data)),patch.object(
            audit,"GLYPH_BLOCK_SIZE",128):
            return audit.audit_font_blocks(
                self.data if data is None else data,self.symbols,
                self.expected if expected is None else expected)

    def test_exact_font_blobs_pass(self):
        self.assertEqual(self.run_audit(),self.expected)

    def test_one_glyph_byte_mismatch_rejected(self):
        changed=bytearray(self.data)
        changed[133]^=1
        with self.assertRaisesRegex(ValueError,"differs from clean glyph layout"):
            self.run_audit(bytes(changed))

    def test_bad_expected_digest_rejected(self):
        wrong=dict(self.expected)
        wrong[audit.FONT_NAMES[0]]="0"*64
        with self.assertRaisesRegex(ValueError,"differs from clean glyph layout"):
            self.run_audit(expected=wrong)

    def test_out_of_bounds_rejected(self):
        positions=dict(self.symbols)
        positions[audit.FONT_NAMES[0]]=len(self.data)-12
        with patch.object(audit,"ROM_BYTES",len(self.data)),patch.object(
            audit,"GLYPH_BLOCK_SIZE",128):
            with self.assertRaisesRegex(ValueError,"out-of-range"):
                audit.audit_font_blocks(self.data,positions,self.expected)


if __name__=="__main__":unittest.main()
