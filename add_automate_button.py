#!/usr/bin/env python3
import argparse
import os
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

try:
    import pytesseract
except Exception as e:  # pragma: no cover
    pytesseract = None


def find_word_bbox(image: Image.Image, word: str) -> Optional[Tuple[int, int, int, int]]:
    """Return bounding box (left, top, width, height) of the first occurrence of `word`.

    This uses pytesseract.image_to_data to get word-level boxes.
    """
    if pytesseract is None:
        return None

    try:
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    except Exception:
        return None

    for i, txt in enumerate(data.get("text", [])):
        if txt and txt.strip().lower() == word.lower():
            left = int(data["left"][i])
            top = int(data["top"][i])
            width = int(data["width"][i])
            height = int(data["height"][i])
            return left, top, width, height
    return None


def load_font(preferred_size: int) -> ImageFont.FreeTypeFont:
    """Attempt to load a reasonable TTF font; fall back to default if needed."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, preferred_size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_automate_button(
    image: Image.Image,
    anchor_bbox: Optional[Tuple[int, int, int, int]],
    offset_px: int = 16,
) -> Image.Image:
    """Draw a rounded rectangle button labeled 'Automate' to the right of anchor_bbox.

    If anchor_bbox is None, place the button in a reasonable top toolbar area.
    """
    img = image.convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Button styling
    font = load_font(14)
    label = "Automate"
    text_w, text_h = draw.textsize(label, font=font)

    padding_x = 10
    padding_y = 6
    icon_size = max(10, text_h - 2)
    gap = 8

    btn_w = padding_x + icon_size + gap + text_w + padding_x
    btn_h = padding_y * 2 + max(icon_size, text_h)

    if anchor_bbox is not None:
        left, top, width, height = anchor_bbox
        btn_left = left + width + offset_px
        btn_top = top + (height - btn_h) // 2
    else:
        # Fallback: place near the top ribbon area
        img_w, _ = img.size
        btn_left = min(int(img_w * 0.6), img_w - btn_w - 20)
        btn_top = 55  # approximate toolbar Y

    btn_right = btn_left + btn_w
    btn_bottom = btn_top + btn_h

    # Colors chosen to blend with Windows-like toolbar aesthetics
    background = (235, 235, 235, 255)
    border = (170, 170, 170, 255)
    text_color = (20, 20, 20, 255)
    icon_color = (40, 120, 40, 255)

    # Draw rounded rectangle
    radius = 5
    try:
        draw.rounded_rectangle(
            [btn_left, btn_top, btn_right, btn_bottom],
            radius=radius,
            fill=background,
            outline=border,
            width=1,
        )
    except Exception:
        # Pillow without rounded_rectangle support: approximate with rectangle
        draw.rectangle([btn_left, btn_top, btn_right, btn_bottom], fill=background, outline=border, width=1)

    # Draw a small "play" triangle icon to suggest automation
    icon_left = btn_left + padding_x
    icon_top = btn_top + (btn_h - icon_size) // 2
    triangle = [
        (icon_left, icon_top),
        (icon_left, icon_top + icon_size),
        (icon_left + icon_size, icon_top + icon_size // 2),
    ]
    draw.polygon(triangle, fill=icon_color)

    # Draw label
    text_x = icon_left + icon_size + gap
    text_y = btn_top + (btn_h - text_h) // 2
    draw.text((text_x, text_y), label, font=font, fill=text_color)

    return img


def process(input_path: str, output_path: str) -> None:
    image = Image.open(input_path)
    bbox = find_word_bbox(image, "Publish")
    out = draw_automate_button(image, bbox)
    out.save(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add an 'Automate' button near the 'Publish' button in a UI screenshot.")
    parser.add_argument("--input", required=True, help="Path to input image (png/jpg)")
    parser.add_argument("--output", required=True, help="Path to save edited image")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    process(args.input, args.output)


if __name__ == "__main__":
    main()

