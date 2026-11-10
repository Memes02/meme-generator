import random
from datetime import datetime
from pathlib import Path

from PIL.Image import Image as IMG
from pil_utils import BuildImage

from meme_generator import add_meme
from meme_generator.utils import save_gif

img_dir = Path(__file__).parent / "images"


def spider(images: list[BuildImage], texts, args):
    head = images[0].convert("RGBA").circle().resize((80, 80))
    # fmt: off
    Xs = [
        174, 174, 174, 169,
        165, 160, 154, 150,
        144, 141, 137, 133,
        130, 119, 115, 113,
        108, 103, 103, 97,
        91, 85, 87, 79,
        74, 79, 75, 75,
        78, 79, 77, 77,
        70, 81, 93, 94,
        104, 110, 119, 123,
        131, 134, 143, 154,
        158, 161, 163, 169,
        174, 173, 174, 173
    ]
    # fmt: on
    frames: list[IMG] = []
    for i in range(52):
        pos = (Xs[i], 24 + random.randint(-1, 1))
        frame = BuildImage.open(img_dir / f"{i}.png")
        frame.paste(head, pos, alpha=True)
        frames.append(frame.image)
    return save_gif(frames, 0.04)


add_meme(
    "spider",
    spider,
    min_images=1,
    max_images=1,
    keywords=["蜘蛛", "蜘蛛爬"],
    date_created=datetime(2025, 4, 27),
    date_modified=datetime(2025, 4, 27),
)
