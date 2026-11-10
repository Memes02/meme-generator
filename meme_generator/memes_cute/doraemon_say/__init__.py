from datetime import datetime
from pathlib import Path

from pil_utils import BuildImage

from meme_generator import add_meme
from meme_generator.exception import TextOverLength

img_dir = Path(__file__).parent / "images"

DEFAULT_TEXT = "开银趴不喊我是吧"


def doraemon_say(images, texts: list[str], args):
    text = texts[0]
    frame = BuildImage.open(img_dir / "0.png")
    try:
        frame.draw_text(
            (228, 11, 340, 164),
            text,
            min_fontsize=20,
            max_fontsize=80,
            allow_wrap=True,
            lines_align="center",
        )
    except ValueError:
        raise TextOverLength(text)
    return frame.save_png()


add_meme(
    "doraemon_say",
    doraemon_say,
    min_texts=1,
    max_texts=1,
    default_texts=[DEFAULT_TEXT],
    keywords=["哆啦A梦说"],
    tags={"哆啦A梦"},
    date_created=datetime(2022, 11, 16),
    date_modified=datetime(2023, 2, 14),
)
