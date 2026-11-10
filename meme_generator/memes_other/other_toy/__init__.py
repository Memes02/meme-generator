from pathlib import Path
from meme_generator import add_meme
from meme_generator.exception import TextOverLength, ImageNumberMismatch
from pil_utils import BuildImage

img_dir = Path(__file__).parent / "images"

def other_toy(images: list[BuildImage], texts: list[str], args):
    frame = BuildImage.open(img_dir / "0.png")
    try:
        self_head = (
        images[0]
        .convert("RGBA")
        .resize((174, 174), keep_ratio=True)
        .circle()
        .rotate(-20)
    )
        user_head = (
        images[1]
        .convert("RGBA")
        .resize((220, 220), keep_ratio=True)
        .circle()
    )
    except ValueError:
        raise ImageNumberMismatch(images)
    frame.paste(
        self_head, 
        (900, 135), 
        alpha=True,
        )
    frame.paste(
        user_head, 
        (180, 800), 
        alpha=True,
        )
    try:
        frame.draw_text(
        (65, 370, 775, 530),
        texts[0], 
        fill="black",
        stroke_fill="black",
        max_fontsize=150,
        min_fontsize=50,
        lines_align="center"
        )
    except ValueError:
        raise TextOverLength(texts)
    
    return frame.save_png()
    

add_meme(
    "other_toy", 
    other_toy, 
    min_images=2, 
    max_images=2, 
    min_texts=1, 
    max_texts=1, 
    default_texts=["狐狐"],
    keywords=["别人的玩物"]
    )