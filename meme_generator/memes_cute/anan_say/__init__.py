import random
from datetime import datetime
from pathlib import Path
from typing import Literal

from pil_utils import BuildImage
from pydantic import Field

from meme_generator import (
    MemeArgsModel,
    MemeArgsType,
    ParserArg,
    ParserOption,
    add_meme,
)
from meme_generator.exception import MemeFeedback, TextOverLength

img_dir = Path(__file__).parent / "images"

EXPRESSIONS = ("angry", "black", "happy", "shy", "speechless")
DEFAULT_TEXT = "吾辈很开心"
help_expression = "表情类型，可选 angry、black、happy、shy、speechless"


class Model(MemeArgsModel):
    expression: Literal[
        "angry",
        "black",
        "happy",
        "shy",
        "speechless",
        "random",
    ] = Field("random", description=help_expression)


args_type = MemeArgsType(
    args_model=Model,
    args_examples=[Model(expression=value) for value in EXPRESSIONS],
    parser_options=[
        ParserOption(
            names=["-e", "--expression"],
            args=[ParserArg(name="expression", value="str")],
            help_text=help_expression,
        ),
    ],
)


def anan_say(images, texts: list[str], args: Model):
    text = texts[0]
    expression = args.expression
    if expression == "random":
        expression = random.choice(EXPRESSIONS)
    elif expression not in EXPRESSIONS:
        raise MemeFeedback(f"表情类型错误，请选择 {'、'.join(EXPRESSIONS)}")

    frame = BuildImage.open(img_dir / f"{expression}.png")
    hand = BuildImage.open(img_dir / "hand.png")

    try:
        frame.draw_text(
            (105, 445, 412, 625),
            text,
            min_fontsize=20,
            max_fontsize=60,
            fill="black",
            allow_wrap=True,
            lines_align="center",
        )
    except ValueError:
        raise TextOverLength(text)

    frame.paste(hand, alpha=True)
    return frame.save_png()


add_meme(
    "anan_say",
    anan_say,
    min_texts=1,
    max_texts=1,
    default_texts=[DEFAULT_TEXT],
    args_type=args_type,
    keywords=["安安说"],
    tags={"夏目安安", "魔法少女的魔女审判"},
    date_created=datetime(2025, 11, 8),
    date_modified=datetime(2025, 11, 8),
)
