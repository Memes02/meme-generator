from pathlib import Path

from pil_utils import BuildImage
from pydantic import Field

from meme_generator import (
    MemeArgsModel,
    MemeArgsType,
    ParserArg,
    ParserOption,
    add_meme,
)
from meme_generator.exception import TextOverLength

img_dir = Path(__file__).parent / "images"
help_text = "牌子名称"


class Model(MemeArgsModel):
    name: str = Field("", description=help_text)


args_type = MemeArgsType(
    args_model=Model,
    parser_options=[
        ParserOption(
            names=["-n", "--name"],
            args=[ParserArg(name="name", value="str")],
            help_text=help_text,
        ),
    ],
)


def police_warn(images, texts: list[str], args: Model):
    name = args.name or "警惕小南梁"
    text = texts[0]
    frame = BuildImage.open(img_dir / "0.png")

    try:
        frame.draw_text(
            (-frame.width + 220, 0, frame.width, frame.height + 260),
            name,
            allow_wrap=True,
            lines_align="center",
            min_fontsize=10,
            max_fontsize=25,
            fill="white",
        )
    except ValueError:
        raise TextOverLength(name)

    try:
        frame.draw_text(
            (250, 50, frame.width - 50, frame.height - 50),
            text,
            allow_wrap=True,
            lines_align="center",
            max_fontsize=200,
            min_fontsize=10,
            fill="white",
        )
    except ValueError:
        raise TextOverLength(texts)

    return frame.save_png()


add_meme(
    "police_warn",
    police_warn,
    default_texts=["警惕小南梁"],
    min_texts=1,
    max_texts=1,
    args_type=args_type,
    keywords=["警方提醒"],
)
