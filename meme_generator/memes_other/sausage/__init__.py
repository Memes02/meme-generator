from pathlib import Path

from meme_generator import add_meme
from PIL.Image import Image as IMG
from pil_utils import BuildImage

img_dir = Path(__file__).parent / "images"


def sausage(images: list[BuildImage], texts, args):
    frame = BuildImage.open(img_dir / "01.png")
    img = (
        images[0]
        .convert("RGBA")
        .resize((350, 350), keep_ratio=True)
        .circle()
        .rotate(-15)
    )
    
    frame.paste(
        img, 
        (580,150), 
        alpha=True
    )
    
    return frame.save_png()

add_meme(
    "sausage",
    sausage,
    min_images=1,
    max_images=1,
    keywords=["烤肠", "鉴定为烤肠"],
)