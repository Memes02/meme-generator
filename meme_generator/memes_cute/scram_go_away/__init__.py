from datetime import datetime
from pathlib import Path
from pil_utils import BuildImage
from meme_generator import add_meme

img_dir = Path(__file__).parent / "images"
def scram_go_away(images: list[BuildImage], texts: list[str], args):
    frame = BuildImage.open(img_dir / "01.png")
    img = images[0].convert("RGBA").circle()
    img = img.resize((150, 75))
    frame.paste(img, (120, 149), alpha=True)
    return frame.save_png()

add_meme(
    "scram_go_away",
    scram_go_away,
    min_images=1,
    max_images=1,
    keywords=["扁扁的走开", "扁扁的离开", "滚开"],
    date_created=datetime(2026, 5, 28),
    date_modified=datetime(2026, 5, 28),
)