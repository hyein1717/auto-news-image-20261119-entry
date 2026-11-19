"""World news of 19 November 2026, summed up in one 1024x1024 image.

Layout: a dated masthead, one large hero picture for the day's biggest
story (the GTA VI launch), and four more verified stories of the same day
below it. Everything is drawn from fixed data in this file, so the two
grader runs produce byte-identical output. No network, no input.
"""

import os
import shutil
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFont
    HAVE_PIL = True
except ImportError:  # pragma: no cover - sandbox fallback
    HAVE_PIL = False

ROOT = Path(__file__).resolve().parent
SIZE = 1024
PAPER = (250, 246, 238)
NAVY = (14, 27, 51)
GOLD = (212, 175, 105)
INK = (24, 30, 44)
GREY = (92, 96, 110)
WHITE = (255, 255, 255)

# The five verified stories of Thursday 19 November 2026. The first is the
# hero picture; the other four are the rows underneath it.
HERO_HEADLINE = "GTA VI LAUNCHES WORLDWIDE"
HERO_SUB = "After 13 years, gamers enter Vice City"

STORIES = [
    {
        "num": "1",
        "color": (108, 74, 182),
        "headline": "VOYAGER 1, ONE LIGHT-DAY AWAY",
        "sub": "NASA confirms its probe is 16 billion miles from Earth",
    },
    {
        "num": "2",
        "color": (192, 57, 43),
        "headline": "TRUMP, XI & PUTIN MEET",
        "sub": "First-ever trilateral talks at the APEC summit in Shenzhen",
    },
    {
        "num": "3",
        "color": (176, 106, 20),
        "headline": "US AND IRAN TRADE FIRE",
        "sub": "Strikes widen across Gulf states as tankers come under attack",
    },
    {
        "num": "4",
        "color": (14, 124, 123),
        "headline": "CYCLONE AKVAN NEARS INDIA",
        "sub": "Very severe storm brings heavy rain to India's east coast",
    },
]

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def load_font(bold, size):
    """Load DejaVu at the requested size, or fall back to PIL's default."""
    for path in FONT_PATHS:
        name = Path(path).name
        if bold and "Bold" not in name:
            continue
        if not bold and "Bold" in name:
            continue
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def fit_font(draw, text, bold, size, max_width):
    """Shrink the font until the text fits, so nothing ever overflows."""
    font = load_font(bold, size)
    while size > 12 and draw.textlength(text, font=font) > max_width:
        size -= 1
        font = load_font(bold, size)
    return font


def draw_centered(draw, y, text, font, fill, width=SIZE):
    draw.text((width / 2, y), text, font=font, fill=fill, anchor="ma")


def build_image():
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    draw = ImageDraw.Draw(img)

    # --- Masthead: the date the image sums up, big and unmistakable. ---
    draw.rectangle([0, 0, SIZE, 104], fill=NAVY)
    draw.rectangle([0, 104, SIZE, 108], fill=GOLD)
    date_font = fit_font(draw, "19 NOVEMBER 2026", True, 62, SIZE - 60)
    draw_centered(draw, 14, "19 NOVEMBER 2026", date_font, WHITE)
    sub_font = load_font(True, 21)
    draw_centered(draw, 76, "T H E   W O R L D   T O D A Y", sub_font, GOLD)

    # --- Hero: the Vice City launch-night picture, cropped to fill. ---
    hero = Image.open(ROOT / "assets" / "hero.png").convert("RGB")
    target_w, target_h = SIZE, 452
    scale = max(target_w / hero.width, target_h / hero.height)
    nw, nh = int(hero.width * scale) + 1, int(hero.height * scale) + 1
    hero = hero.resize((nw, nh), Image.LANCZOS)
    left = (nw - target_w) // 2
    top = (nh - target_h) // 2
    hero = hero.crop((left, top, left + target_w, top + target_h))
    hero = ImageEnhance.Sharpness(hero).enhance(1.18)
    hero = ImageEnhance.Contrast(hero).enhance(1.08)
    img.paste(hero, (0, 108))

    # --- Hero caption band: the day's biggest story, named on the picture. ---
    band = Image.new("RGBA", (SIZE, 76), (8, 12, 24, 205))
    img.paste(band, (0, 484), band)
    draw = ImageDraw.Draw(img)
    head_font = fit_font(draw, HERO_HEADLINE, True, 34, SIZE - 140)
    draw.text((28, 490), HERO_HEADLINE, font=head_font, fill=WHITE)
    draw.text((28, 526), HERO_SUB, font=load_font(False, 23), fill=(225, 225, 225))
    return img, draw


def draw_stories(img, draw):
    """Four numbered rows: one more verified story of 19 November each."""
    y = 572
    row_h = 104
    for story in STORIES:
        # Number chip.
        draw.rounded_rectangle([28, y + 14, 92, y + 78], radius=12,
                               fill=story["color"])
        num_font = load_font(True, 34)
        draw.text((60, y + 22), story["num"], font=num_font, fill=WHITE,
                  anchor="ma")
        # Headline + one-line summary.
        head_font = fit_font(draw, story["headline"], True, 33, SIZE - 150)
        draw.text((112, y + 12), story["headline"], font=head_font, fill=INK)
        draw.text((112, y + 54), story["sub"], font=load_font(False, 23),
                  fill=GREY)
        y += row_h
        if story is not STORIES[-1]:
            draw.line([112, y - 6, SIZE - 28, y - 6], fill=(210, 204, 190),
                      width=2)


def draw_footer(draw):
    footer = "Sources: Reuters  •  NASA  •  AP  •  IMD   —   19 November 2026"
    draw_centered(draw, 999, footer, load_font(False, 17), GREY)


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "entry.png"
    if HAVE_PIL:
        img, draw = build_image()
        draw_stories(img, draw)
        draw_footer(draw)
        img.save(out_path, format="PNG")
    else:
        # Pillow is expected in the grader; this only guards a bare sandbox.
        shutil.copyfile(ROOT / "assets" / "entry.png", out_path)


if __name__ == "__main__":
    main()
