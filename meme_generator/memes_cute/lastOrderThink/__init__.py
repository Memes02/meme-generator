from datetime import datetime
from pathlib import Path

from pil_utils import BuildImage

from meme_generator import add_meme
from meme_generator.exception import TextOverLength

img_dir = Path(__file__).parent / "images"

DEFAULT_TEXT = "好女孩"


def last_order_think(images, texts: list[str], args):
    text = texts[0]
    frame = BuildImage.open(img_dir / "lastOrderThink.png")
    try:
        frame.draw_text(
            (120, 110, 740, 500),
            text,
            min_fontsize=50,
            max_fontsize=140,
            allow_wrap=True,
            lines_align="center",
            fill="#5a3a1c",
        )
    except ValueError:
        raise TextOverLength(text)
    return frame.save_png()


add_meme(
    "last_order_think",
    last_order_think,
    min_texts=1,
    max_texts=1,
    default_texts=[DEFAULT_TEXT],
    keywords=["呆毛想", "小呆毛想"],
    tags={"米哈游", "小呆毛"},
    date_created=datetime(2026, 8, 23),
    date_modified=datetime(2026, 8, 23),
)
