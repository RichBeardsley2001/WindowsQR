"""
Run this once before building to create assets/icon.png and assets/icon.ico.
"""
import os
import random
from PIL import Image, ImageDraw


def build_icon(size: int = 64) -> Image.Image:
    img = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    s = size // 8  # cell size

    def corner(ox: int, oy: int) -> None:
        draw.rectangle([ox, oy, ox + 7 * s - 1, oy + 7 * s - 1], fill=(0, 0, 0, 255))
        draw.rectangle(
            [ox + s, oy + s, ox + 6 * s - 1, oy + 6 * s - 1],
            fill=(255, 255, 255, 255),
        )
        draw.rectangle(
            [ox + 2 * s, oy + 2 * s, ox + 5 * s - 1, oy + 5 * s - 1],
            fill=(0, 0, 0, 255),
        )

    corner(0, 0)
    corner(size - 7 * s, 0)
    corner(0, size - 7 * s)

    rng = random.Random(42)
    for row in range(9, size // s - 1):
        for col in range(9, size // s - 1):
            if rng.random() > 0.55:
                x, y = col * s, row * s
                draw.rectangle([x, y, x + s - 2, y + s - 2], fill=(0, 0, 0, 255))

    return img


if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)

    icon = build_icon(64)
    icon.save("assets/icon.png")

    # Save ICO with multiple resolutions
    icon_16 = icon.resize((16, 16), Image.LANCZOS)
    icon_32 = icon.resize((32, 32), Image.LANCZOS)
    icon_48 = icon.resize((48, 48), Image.LANCZOS)
    icon_64 = icon

    icon_64.save(
        "assets/icon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64)],
        append_images=[icon_16, icon_32, icon_48],
    )

    print("assets/icon.png  OK")
    print("assets/icon.ico  OK")
