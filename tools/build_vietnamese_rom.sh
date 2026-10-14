#!/usr/bin/env bash
# Build the Vietnamese ROM from a pristine, already-buildable Arena 0.13.0
# workspace (pinned pokeemerald + Arena patch + agbcc installed + assets generated).
# The workspace must be reset to that baseline first (git checkout -- .), because
# the translation applier locates strings by their pinned line/column.
#
# usage: tools/build_vietnamese_rom.sh WORKSPACE [TITLE_FONT.ttf]
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
ws="$(cd "$1" && pwd)"
font="${2:-}"
out="$repo/private/work"
mkdir -p "$out"

# Some translated strings (map names) live in headers generated from JSON at
# build time; create them fresh before translating so none are missed or stale.
make -C "$ws" clean-generated > /dev/null
make -C "$ws" tools > "$out/make_tools.log" 2>&1
make -C "$ws" generated >> "$out/make_tools.log" 2>&1

python3 "$repo/tools/compact_arena_linker_gaps.py" --workspace "$ws" --apply \
  --report "$out/compact.json" > /dev/null
python3 "$repo/tools/build_vietnamese_source_font.py" --workspace "$ws" \
  --sheet-dir "$out/sheets" --codebook-out "$repo/checkpoints/source-build-vietnamese-codebook.json"
python3 "$repo/tools/apply_source_translations.py" --workspace "$ws" \
  --translations "$repo/translations" --report "$out/apply.json" \
  --sites-out "$out/sites.json" --reflow-width "${REFLOW_WIDTH:-208}" \
  ${SKIP_KEYS:+--skip-keys "$SKIP_KEYS"}
python3 "$repo/tools/widen_source_text_arrays.py" --workspace "$ws"
if [ -n "$font" ]; then
  python3 "$repo/tools/apply_title_credit.py" "$ws" --font "$font"
else
  python3 "$repo/tools/apply_title_credit.py" "$ws"
fi
make -C "$ws" -j"${JOBS:-6}" > "$out/make_vi.log" 2>&1 || {
  grep -E 'warning:|error' "$out/make_vi.log" | sort | uniq -c | sort -rn | head -n 40
  exit 1
}
grep -E 'ROM:' "$out/make_vi.log"
sha256sum "$ws/pokeemerald.gba"
