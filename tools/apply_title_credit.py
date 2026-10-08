#!/usr/bin/env python3
"""Generate and wire the title-screen localization credit into pokeemerald source.

This is intentionally source-level only. It does not patch a ROM and must be
applied only to the localized build workspace, after the shipping-layout/source
mapping work is complete. That keeps the symbol-map workflow pinned to the
unmodified Emerald Arena 0.13.0 layout.

Usage:
    python3 tools/apply_title_credit.py /path/to/workspace

The visible line is:
    Việt hóa bởi Votri Valley
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


CREDIT_TEXT = "Việt hóa bởi Votri Valley"
CREDIT_IMAGE = "graphics/title_screen/translation_credit.png"
FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one source anchor, found {count}")
    return text.replace(old, new, 1)


def choose_font(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            raise FileNotFoundError(f"Font not found: {p}")
        return p
    for candidate in FONT_CANDIDATES:
        p = Path(candidate)
        if p.is_file():
            return p
    raise FileNotFoundError(
        "No DejaVu Sans font found. Install fonts-dejavu-core or pass --font."
    )


def palette_luma(palette: list[int], index: int) -> float:
    r, g, b = palette[index * 3 : index * 3 + 3]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def generate_credit_png(workspace: Path, font_path: Path) -> Path:
    src_path = workspace / "graphics/title_screen/press_start.png"
    if not src_path.is_file():
        raise FileNotFoundError(f"Missing title palette source: {src_path}")

    src = Image.open(src_path).convert("P")
    palette = src.getpalette()
    if palette is None:
        raise RuntimeError("press_start.png has no indexed palette")

    used = {int(v) for v in src.getdata() if int(v) != 0}
    if not used:
        raise RuntimeError("press_start.png has no non-transparent palette colors")

    fg = max(used, key=lambda idx: palette_luma(palette, idx))

    width, height = 160, 16
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    font = ImageFont.truetype(str(font_path), 10)

    bbox = draw.textbbox((0, 0), CREDIT_TEXT, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    if text_w > width:
        raise RuntimeError(f"Credit text is too wide: {text_w}px > {width}px")

    x = (width - text_w) // 2 - bbox[0]
    y = (height - text_h) // 2 - bbox[1]
    draw.text((x, y), CREDIT_TEXT, font=font, fill=255)

    # Hard threshold: keep the sprite crisp and deterministic in 4bpp.
    mask = mask.point(lambda p: 255 if p >= 96 else 0)

    out = Image.new("P", (width, height), 0)
    out.putpalette(palette)
    out_pixels = out.load()
    mask_pixels = mask.load()
    for yy in range(height):
        for xx in range(width):
            if mask_pixels[xx, yy]:
                out_pixels[xx, yy] = fg

    out_path = workspace / CREDIT_IMAGE
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.save(out_path, optimize=False)
    return out_path


def patch_title_screen_source(workspace: Path) -> Path:
    path = workspace / "src/title_screen.c"
    if not path.is_file():
        raise FileNotFoundError(f"Missing source file: {path}")

    text = path.read_text(encoding="utf-8")
    if "sTitleScreenTranslationCreditGfx" in text:
        return path

    text = replace_once(
        text,
        """    TAG_PRESS_START_COPYRIGHT,
    TAG_LOGO_SHINE,
};""",
        """    TAG_PRESS_START_COPYRIGHT,
    TAG_LOGO_SHINE,
    TAG_TRANSLATION_CREDIT,
};""",
        "sprite tag enum",
    )

    text = replace_once(
        text,
        """static void CB2_GoToCopyrightScreen(void);
static void UpdateLegendaryMarkingColor(u8);
""",
        """static void CB2_GoToCopyrightScreen(void);
static void UpdateLegendaryMarkingColor(u8);
static void CreateTranslationCreditBanner(s16, s16);
""",
        "function declarations",
    )

    text = replace_once(
        text,
        """static const u32 sTitleScreenCloudsGfx[] = INCGFX_U32("graphics/title_screen/clouds.png", ".4bpp.lz");


""",
        """static const u32 sTitleScreenCloudsGfx[] = INCGFX_U32("graphics/title_screen/clouds.png", ".4bpp.lz");
static const u32 sTitleScreenTranslationCreditGfx[] = INCGFX_U32(
    "graphics/title_screen/translation_credit.png",
    ".4bpp.lz",
    "-mwidth 4 -mheight 2"
);


""",
        "credit asset declaration",
    )

    credit_data = r'''
static const struct OamData sTranslationCreditOamData =
{
    .y = DISPLAY_HEIGHT,
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_NORMAL,
    .mosaic = FALSE,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(32x16),
    .x = 0,
    .matrixNum = 0,
    .size = SPRITE_SIZE(32x16),
    .tileNum = 0,
    .priority = 0,
    .paletteNum = 0,
    .affineParam = 0,
};

static const union AnimCmd sAnim_TranslationCredit_0[] =
{
    ANIMCMD_FRAME(0, 4),
    ANIMCMD_END,
};
static const union AnimCmd sAnim_TranslationCredit_1[] =
{
    ANIMCMD_FRAME(8, 4),
    ANIMCMD_END,
};
static const union AnimCmd sAnim_TranslationCredit_2[] =
{
    ANIMCMD_FRAME(16, 4),
    ANIMCMD_END,
};
static const union AnimCmd sAnim_TranslationCredit_3[] =
{
    ANIMCMD_FRAME(24, 4),
    ANIMCMD_END,
};
static const union AnimCmd sAnim_TranslationCredit_4[] =
{
    ANIMCMD_FRAME(32, 4),
    ANIMCMD_END,
};

static const union AnimCmd *const sTranslationCreditAnimTable[] =
{
    sAnim_TranslationCredit_0,
    sAnim_TranslationCredit_1,
    sAnim_TranslationCredit_2,
    sAnim_TranslationCredit_3,
    sAnim_TranslationCredit_4,
};

static const struct SpriteTemplate sTranslationCreditSpriteTemplate =
{
    .tileTag = TAG_TRANSLATION_CREDIT,
    .paletteTag = TAG_PRESS_START_COPYRIGHT,
    .oam = &sTranslationCreditOamData,
    .anims = sTranslationCreditAnimTable,
    .images = NULL,
    .affineAnims = gDummySpriteAffineAnimTable,
    .callback = SpriteCallbackDummy,
};

static const struct CompressedSpriteSheet sSpriteSheet_TranslationCredit[] =
{
    {
        .data = sTitleScreenTranslationCreditGfx,
        .size = 0x500,
        .tag = TAG_TRANSLATION_CREDIT
    },
    {},
};

'''

    text = replace_once(
        text,
        """static const struct SpritePalette sSpritePalette_PressStart[] =
{
    {
        .data = gTitleScreenPressStartPal,
        .tag = TAG_PRESS_START_COPYRIGHT
    },
    {},
};

static const struct OamData sPokemonLogoShineOamData =
""",
        """static const struct SpritePalette sSpritePalette_PressStart[] =
{
    {
        .data = gTitleScreenPressStartPal,
        .tag = TAG_PRESS_START_COPYRIGHT
    },
    {},
};

""" + credit_data + """static const struct OamData sPokemonLogoShineOamData =
""",
        "credit sprite data",
    )

    create_func = r'''
static void CreateTranslationCreditBanner(s16 x, s16 y)
{
    u8 i;
    u8 spriteId;

    x -= 64;
    for (i = 0; i < 5; i++, x += 32)
    {
        spriteId = CreateSprite(&sTranslationCreditSpriteTemplate, x, y, 0);
        StartSpriteAnim(&gSprites[spriteId], i);
    }
}

'''

    text = replace_once(
        text,
        """static void CreateCopyrightBanner(s16 x, s16 y)
{
    u8 i;
    u8 spriteId;

    x -= 64;
    for (i = 0; i < NUM_COPYRIGHT_FRAMES; i++, x += 32)
    {
        spriteId = CreateSprite(&sStartCopyrightBannerSpriteTemplate, x, y, 0);
        StartSpriteAnim(&gSprites[spriteId], i + NUM_PRESS_START_FRAMES);
    }
}

#undef sAnimate
""",
        """static void CreateCopyrightBanner(s16 x, s16 y)
{
    u8 i;
    u8 spriteId;

    x -= 64;
    for (i = 0; i < NUM_COPYRIGHT_FRAMES; i++, x += 32)
    {
        spriteId = CreateSprite(&sStartCopyrightBannerSpriteTemplate, x, y, 0);
        StartSpriteAnim(&gSprites[spriteId], i + NUM_PRESS_START_FRAMES);
    }
}

""" + create_func + """#undef sAnimate
""",
        "credit banner constructor",
    )

    text = replace_once(
        text,
        """        LoadCompressedSpriteSheet(&sSpriteSheet_EmeraldVersion[0]);
        LoadCompressedSpriteSheet(&sSpriteSheet_PressStart[0]);
        LoadCompressedSpriteSheet(&sPokemonLogoShineSpriteSheet[0]);
""",
        """        LoadCompressedSpriteSheet(&sSpriteSheet_EmeraldVersion[0]);
        LoadCompressedSpriteSheet(&sSpriteSheet_PressStart[0]);
        LoadCompressedSpriteSheet(&sSpriteSheet_TranslationCredit[0]);
        LoadCompressedSpriteSheet(&sPokemonLogoShineSpriteSheet[0]);
""",
        "credit sprite loading",
    )

    text = replace_once(
        text,
        """        CreatePressStartBanner(START_BANNER_X, 108);
        CreateCopyrightBanner(START_BANNER_X, 148);
""",
        """        CreatePressStartBanner(START_BANNER_X, 108);
        CreateTranslationCreditBanner(START_BANNER_X, 132);
        CreateCopyrightBanner(START_BANNER_X, 148);
""",
        "credit placement",
    )

    path.write_text(text, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--font", help="Path to a TrueType font with Vietnamese glyphs")
    parser.add_argument("--asset-only", action="store_true")
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    font_path = choose_font(args.font)
    png = generate_credit_png(workspace, font_path)

    print(f"Generated: {png}")
    print(f"Credit: {CREDIT_TEXT}")
    print(f"Font: {font_path}")

    if not args.asset_only:
        src = patch_title_screen_source(workspace)
        print(f"Patched: {src}")
        print("Placement: y=132, between PRESS START and copyright")
        print("ROM bytes are not modified by this tool; rebuild from source.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
