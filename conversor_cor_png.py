from pathlib import Path
from PIL import Image


SPRITES_DIR = Path("assets/sprites/buttons")


def convert_png_to_white(path: Path) -> None:
    img = Image.open(path).convert("RGBA")
    pixels = img.load()

    width, height = img.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a != 0:  # mantém pixels transparentes intactos
                pixels[x, y] = (255, 255, 255, a)

    img.save(path)


def main() -> None:
    if not SPRITES_DIR.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {SPRITES_DIR}")

    for png in SPRITES_DIR.glob("*.png"):
        convert_png_to_white(png)


if __name__ == "__main__":
    main()
