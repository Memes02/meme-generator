from pathlib import Path
from pil_utils import BuildImage
from meme_generator import add_meme
from meme_generator.exception import TextOverLength


img_dir = Path(__file__).parent / "images"


def infinitynikki_start(images: list[BuildImage], texts: list[str], args):
    frame = BuildImage.open(img_dir / "0.png")
    if texts:
        text = texts[0]
        try:
            frame.draw_text(
                (0, frame.height - 75, frame.width, frame.height),
                text,
                max_fontsize=50,
                min_fontsize=30,
                fill="#FF69B4"
            )
        except ValueError:
            raise TextOverLength(text)
        
        screen = (
            images[0]
            .convert("RGBA")
            .resize((147, 63), keep_ratio=True)
            .rotate(16, expand=True)
            .circle_corner(35)
        )
        frame = frame.copy().paste(screen, (236, 183), alpha=True,below=False)

    return frame.save_png()


add_meme(
    "infinitynikki_start",
    infinitynikki_start,
    min_images=1,
    max_images=1,
    min_texts=0,
    max_texts=1,
    default_texts=["无限暖暖，启动！"],
    keywords=["无限暖暖启动"],
)
