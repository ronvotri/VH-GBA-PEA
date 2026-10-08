# Title-screen localization credit

Requested credit:

**Việt hóa bởi Votri Valley**

The credit is implemented as a dedicated title-screen OBJ sprite strip, positioned at **y = 132**, between the normal **PRESS START** banner and the original copyright banner.

## Why it is a graphic sprite

The title screen does not use the normal dialogue window pipeline. The credit is therefore generated as a small 4bpp sprite asset at build time. This keeps the title logo/background untouched and avoids relying on runtime dialogue-font state.

The generator uses the existing `press_start.png` palette, so no extra OBJ palette is consumed.

## Apply to a localized source workspace

After applying Emerald Arena 0.13.0 to the pinned pokeemerald source, but **only for the localized build**:

```bash
sudo apt-get install -y fonts-dejavu-core
python3 -m pip install --user Pillow
python3 tools/apply_title_credit.py workspace
```

The tool:

1. creates `workspace/graphics/title_screen/translation_credit.png` (160×16);
2. patches `workspace/src/title_screen.c`;
3. adds a five-sprite 32×16 banner using the existing title-screen palette;
4. does not patch a ROM directly.

## Important layout rule

Do **not** run this before the shipping-layout/symbol-map catalog build. Adding source assets/code changes the rebuilt source ROM layout. Keep `.github/workflows/arena-map.yml` pinned to the uncredited shipping layout; apply this only in the final localized build pipeline after offset/reference verification is complete.
