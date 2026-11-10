from datetime import datetime
from pathlib import Path

from pil_utils import BuildImage

from meme_generator import add_meme
from meme_generator.utils import FrameAlignPolicy, Maker, make_gif_or_combined_gif

img_dir = Path(__file__).parent / "images"


def rip_clothes(images: list[BuildImage], texts, args):
    def maker(i: int) -> Maker:
        def make(imgs: list[BuildImage]) -> BuildImage:
            img = imgs[0].convert("RGBA").resize((480, 270), keep_ratio=True)
            if i <= 15:
                frame = BuildImage.open(img_dir / f"{i}.png")
                frame.paste(img, (0, 0), below=True)
                return frame
            else:
                return img

        return make

    return make_gif_or_combined_gif(
        images, maker, 20, 0.1, FrameAlignPolicy.extend_last
    )


add_meme(
    "rip_clothes",
    rip_clothes,
    min_images=1,
    max_images=1,
    keywords=["撕衣服"],
    date_created=datetime(2025, 5, 7),
    date_modified=datetime(2025, 6, 3),
)
