from pathlib import Path

from PIL.Image import Image as IMG
from pil_utils import BuildImage

from meme_generator import add_meme
from meme_generator.utils import save_gif

img_dir = Path(__file__).parent / "images"


def fast_do(images: list[BuildImage], texts, args):
    self_locs = [(116, -8), (109, 3), (130, -10)]
    user_locs = [(2, 177), (12, 172), (6, 158)]
    self_head = (
        images[0]
        .convert("RGBA")
        .resize((122, 122), keep_ratio=True)
        .circle()
        .rotate(15)
    )
    user_head = (
        images[1]
        .convert("RGBA")
        .resize((112, 112), keep_ratio=True)
        .circle()
        .rotate(90)
    )
    frames: list[IMG] = []
    for i in range(3):
        frame = BuildImage.open(img_dir / f"{i}.png")
        frame.paste(user_head, user_locs[i], alpha=True)
        frame.paste(self_head, self_locs[i], alpha=True)
        frames.append(frame.image)
    return save_gif(frames, 0.02)


add_meme(
    "fast_do",
    fast_do,
    min_images=2,
    max_images=2,
    keywords=["狠撅"],
)
