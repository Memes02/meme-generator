from pathlib import Path
from meme_generator import add_meme
from meme_generator.exception import TextOverLength, ImageNumberMismatch
from pil_utils import BuildImage

img_dir = Path(__file__).parent / "images"


def cool_blanket(images: list[BuildImage], texts: list[str], args):
    frame = BuildImage.open(img_dir / "0.png")
    try:
        frame.paste(
            images[0]
            .convert("RGBA")
            .resize((600, 600), keep_ratio=True)
            .circle(),
            (120, 150),
            below=True
            )
    except ValueError:
        raise ImageNumberMismatch(images)
    try:
        frame.draw_text(
            (25, 80, 330, 140),
            texts[0],
            fill="black",
            min_fontsize=40,
            max_fontsize=100,
            halign="left"
        )
    except ValueError:
        raise TextOverLength(texts)

    return frame.save_png()

add_meme(
    "cool_blanket",
    cool_blanket,
    min_images=1,
    max_images=1,
    min_texts=1,
    max_texts=1,
    keywords=["清凉杯子"],
)
