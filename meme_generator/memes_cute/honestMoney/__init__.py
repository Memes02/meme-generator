import random
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageFilter
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

DEFAULT_TEXT = "老实赚钱，很枯燥吧"
TOTAL_NUM = 3
help_text = f"图片编号，范围为 1~{TOTAL_NUM}，0 表示随机"

# 素材 1672x941。参考帧（1920x1080）里中文那行墨迹在 y 922..964、x 743..1176，
# 水平中心与图宽中心重合；按 0.871 折算到本素材是 y 803..840，中心 821。
# 字幕区以该行为垂直中心，宽度取画面的 70%（真实字幕一行不会铺满整幅宽），
# 高度按固定字号的 54px 两行排版（142px）留 6px 余量，折行时上下扩展而不是一路向下。
# 换素材必须重新量，这组数字来自这一帧的具体构图（见 docs/adr/0001）。
SUBTITLE_AREA = (251, 748, 1421, 896)
# 字号固定，不随文字长短自适应：同一个表情每次出图大小一致，放大字号时也不会被
# 「长句自动缩字」抵消。代价是字数多了不再自动缩小，折成两行还放不下就抛 TextOverLength。
# 上限约 42 个汉字；改字号要同时改 SUBTITLE_AREA 的高度（见 docs/adr/0003）。
SUBTITLE_FONT_SIZE = 54
# 描边宽度，单位像素（不是比例）：参考帧描边约 3~4px / 字号约 50px。
# 由 alpha 膨胀实现 MaxFilter(2*3+1)，彩色 emoji 才会一起长边（见 docs/adr/0004）。
SUBTITLE_OUTLINE = 3


class Model(MemeArgsModel):
    number: int = Field(0, description=help_text)


args_type = MemeArgsType(
    args_model=Model,
    parser_options=[
        ParserOption(
            names=["-n", "--number"],
            args=[ParserArg(name="number", value="int")],
            help_text=help_text,
        ),
    ],
)


def draw_subtitle(frame: BuildImage, text: str) -> None:
    """把字幕画到 frame 上：先落到透明层，再用 alpha 膨胀长出黑描边。

    不能直接给 `draw_text` 传 `stroke_fill`：彩色 emoji 是位图字形，skia 不认描边 paint，
    `🐷🐷侠` 里的猪会没有任何轮廓，压在浅色皮肤/白衣上直接糊掉。alpha 膨胀对彩色字形
    一样有效，所以描边从「画出来」改成「事后长出来」（见 docs/adr/0004）。
    """
    layer = BuildImage.new("RGBA", (frame.width, frame.height), (0, 0, 0, 0))
    layer.draw_text(
        SUBTITLE_AREA,
        text,
        max_fontsize=SUBTITLE_FONT_SIZE,
        min_fontsize=SUBTITLE_FONT_SIZE,  # 两个值相等 = 固定字号，画不下直接抛 ValueError
        allow_wrap=True,
        lines_align="center",
        fill="white",
    )

    dilated = layer.image.getchannel("A").filter(
        ImageFilter.MaxFilter(SUBTITLE_OUTLINE * 2 + 1)
    )
    outline = Image.new("RGBA", layer.image.size, (0, 0, 0, 0))
    outline.putalpha(dilated)

    base = frame.image.convert("RGBA")
    base.alpha_composite(outline)
    base.alpha_composite(layer.image)
    frame.image = base.convert("RGB")


def honest_money(images, texts: list[str], args: Model):
    text = texts[0]
    if args.number == 0:
        num = random.randint(1, TOTAL_NUM)
    elif 1 <= args.number <= TOTAL_NUM:
        num = args.number
    else:
        raise MemeFeedback(f"图片编号错误，请选择 1~{TOTAL_NUM}")

    frame = BuildImage.open(img_dir / f"{num:02d}.png")
    try:
        draw_subtitle(frame, text)
    except ValueError:
        raise TextOverLength(text)
    return frame.save_png()


add_meme(
    "honest_money",
    honest_money,
    min_texts=1,
    max_texts=1,
    default_texts=[DEFAULT_TEXT],
    args_type=args_type,
    keywords=["老实赚钱", "老实赚钱很枯燥吧"],
    tags={"久留美", "deepseek娘", "小呆毛"},
    date_created=datetime(2026, 10, 29),
    date_modified=datetime(2026, 10, 29),
)
