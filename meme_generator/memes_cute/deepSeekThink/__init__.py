import math
import random
from datetime import datetime
from pathlib import Path

from pil_utils import BuildImage, Text2Image

from meme_generator import add_meme
from meme_generator.exception import TextOverLength

img_dir = Path(__file__).parent / "images"

DEFAULT_TEXT = "深度思考中"

# 文字范围由 tools/measure_bubble.py 实测 DSniangThink.png 的气泡得到：
# 气泡外接框 (94, 32, 813, 492)，主体底边 442，按经验比例内缩后取整。
TEXT_AREA = (175, 85, 730, 420)

# TEXT_AREA 宽 555，5 个汉字单行最多排到约 111px。
# 因此 max_fontsize 取 110（实测单行墨迹宽 540，外接框 179..719）；
# 若取 120，「深度思考中」会折成 4+1 行、末行只剩一个孤零零的「中」。
#
# 注意：110 时左右只剩约 15px 余量，而 draw_text 只在「放不下这个矩形」时才继续缩字号——
# 4+1 折行本身仍然放得下，所以它不会帮忙救回来。换一台中文字体更宽的机器（或 Linux 上的
# 回退字体）有可能重新折成 4+1。那属于观感问题、不是错误；要卡死单行只能自己在代码里量。
MAX_FONTSIZE = 110

TEXT_FILL = "#27335d"

# ---------------------------------------------------------------------------
# 短文本额外补一行 DeepSeek 风格的「已思考 （用时 x 秒） >」
#
# 字数少的时候气泡里空，就在用户文字上方加一行状态行，做出「AI 刚思考完」的样子；
# 字数多的时候不加，否则两段挤在一起反而更难看。
#
# 图标和折角都用几何图形画，不用字体里的 ⚛ / › —— 那些字符依赖系统字体
# （Segoe UI Symbol 之类），换台 Linux 机器就可能变成豆腐块。
# ---------------------------------------------------------------------------
SHORT_TEXT_MAX = 8                          # 字数 <= 此值才补状态行，超过就只画文字
SHORT_TEXT_AREA = (175, 147, 730, 377)      # 有状态行时，用户文字的区域

# 状态行与用户文字共用同一条**左对齐边**（模仿 DeepSeek：状态行和答案正文左边齐平）。
# 这一组整体的水平位置按「两者中较宽的那个」在气泡里居中，
# 所以短正文不会孤零零贴在气泡左侧。
# 注意别用 frame.width / 2：素材是 1026 宽而气泡只有 94..813，
# 按整图居中会让内容整体右偏约 60px。
CONTENT_CENTER_X = (TEXT_AREA[0] + TEXT_AREA[2]) / 2

REASON_FONT_SIZE = 34                       # 状态行字号（固定，不参与区域缩放）
REASON_SECONDS_RANGE = (5, 55)              # 「用时 x 秒」的随机范围
REASON_ICON_SIZE = 32                       # 原子图标外接尺寸
REASON_CHEVRON_W = 9                        # 右侧折角的宽
REASON_CHEVRON_H = 18                       # 右侧折角的高
REASON_GAP_ICON_LABEL = 11                  # 图标 -> 「已思考」
REASON_GAP_LABEL_TIME = 9                   # 「已思考」-> 「（用时 x 秒）」
REASON_GAP_TIME_CHEVRON = 24                # 「（用时 x 秒）」-> 折角
REASON_CENTER_Y = 170                       # 状态行**墨迹外接框**在成品图里的目标中心 y

# 状态行先画进一张贴合宽度的透明层，层内用局部坐标；
# 落到成品图的位置由外层按实测墨迹 bbox 决定，这样左右、上下都能精确对齐，
# 也不需要复制 pil_utils 那套「从 max_fontsize 往小试」的字号拟合逻辑。
_REASON_LAYER_H = 60                        # 透明层高度，够放图标与折角即可
_REASON_LAYER_TEXT_TOP = 8                  # 层内文字绘制顶部（draw_on_image 以段落顶为基准）
_REASON_LAYER_ICON_CY = 30                  # 层内图标 / 折角的中心 y
REASON_ICON_FILL = "#4d6bfe"
REASON_LABEL_FILL = "#3d4a63"
REASON_TIME_FILL = "#98a3b8"
REASON_CHEVRON_FILL = "#b9c1ce"

# PIL 的 ellipse / line 没有抗锯齿，放大 4 倍画完再缩回来就平滑了
_SUPERSAMPLE = 4


def _text_width(text: str, font_size: int) -> float:
    """量一段文字的宽度，用于把状态行各段拼成一行。"""
    return Text2Image.from_text(text, font_size).longest_line


def _draw_atom(frame: BuildImage, cx: float, cy: float, size: float, fill: str) -> None:
    """画 DeepSeek 那个原子图标：两条正交椭圆轨道 + 中心点。

    真图标是两条 ±45° 交叉轨道，但 PIL 的 ellipse 只能画正椭圆；
    改成一横一竖之后轮廓依然是原子感，而且完全不依赖字体。
    """
    ss = _SUPERSAMPLE
    side = int(size * ss)
    layer = BuildImage.new("RGBA", (side, side), (0, 0, 0, 0))
    c = side / 2
    r = side * 0.46
    ring = max(1, int(round(r * 0.11)))
    layer.draw_ellipse((c - r * 0.46, c - r, c + r * 0.46, c + r), outline=fill, width=ring)
    layer.draw_ellipse((c - r, c - r * 0.46, c + r, c + r * 0.46), outline=fill, width=ring)
    dot = r * 0.17
    layer.draw_ellipse((c - dot, c - dot, c + dot, c + dot), fill=fill)
    layer = layer.resize((int(size), int(size)))
    frame.alpha_composite(layer, (int(round(cx - size / 2)), int(round(cy - size / 2))))


def _draw_chevron(frame: BuildImage, x: float, cy: float, fill: str) -> None:
    """画 UI 里那个折叠折角「>」，同样走超采样。"""
    ss = _SUPERSAMPLE
    w, h = REASON_CHEVRON_W, REASON_CHEVRON_H
    layer = BuildImage.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    mid = h * ss / 2
    tip = w * ss * 0.72
    width = max(1, int(round(ss * 1.5)))
    layer.draw_line((0, 0, tip, mid), fill=fill, width=width)
    layer.draw_line((tip, mid, 0, h * ss), fill=fill, width=width)
    layer = layer.resize((w, h))
    frame.alpha_composite(layer, (int(round(x)), int(round(cy - h / 2))))


def _reason_layer(seconds: int) -> BuildImage:
    """把状态行画到一张贴合宽度的透明层上，返回该层。

    状态行各段颜色不同（图标蓝、「已思考」深、「（用时…）」灰、折角更浅），
    而 draw_text 一次只能给一个 fill，所以先量宽、算好每段起点，再逐段点绘。
    层内用局部坐标（左上角为原点），落到成品图的位置由调用方按墨迹 bbox 决定。
    """
    label = "已思考"
    time_part = f"（用时 {seconds} 秒）"

    w_label = _text_width(label, REASON_FONT_SIZE)
    w_time = _text_width(time_part, REASON_FONT_SIZE)
    # 用 ceil 而非 round：Text2Image.longest_line 是 float，上游 draw_on_image
    # 内部 layout 时用的就是 math.ceil(longest_line)；这里也取 ceil 才不会让
    # 透明层最右少 1px（折角是最后画的，最容易被裁到）。
    width = math.ceil(
        REASON_ICON_SIZE
        + REASON_GAP_ICON_LABEL
        + w_label
        + REASON_GAP_LABEL_TIME
        + w_time
        + REASON_GAP_TIME_CHEVRON
        + REASON_CHEVRON_W
    )

    layer = BuildImage.new("RGBA", (width, _REASON_LAYER_H), (0, 0, 0, 0))
    top = _REASON_LAYER_TEXT_TOP
    cy = _REASON_LAYER_ICON_CY

    x = 0
    _draw_atom(layer, x + REASON_ICON_SIZE / 2, cy, REASON_ICON_SIZE, REASON_ICON_FILL)
    x += REASON_ICON_SIZE + REASON_GAP_ICON_LABEL

    # xy 只传 2 个元素时，draw_text 用 font_size 定死字号，不参与区域缩放
    layer.draw_text((x, top), label, font_size=REASON_FONT_SIZE, fill=REASON_LABEL_FILL)
    x += w_label + REASON_GAP_LABEL_TIME

    layer.draw_text((x, top), time_part, font_size=REASON_FONT_SIZE, fill=REASON_TIME_FILL)
    x += w_time + REASON_GAP_TIME_CHEVRON

    _draw_chevron(layer, x, cy, REASON_CHEVRON_FILL)
    return layer


def _alpha_bbox(img: BuildImage):
    """透明层上非透明像素的外接框（PIL 的 getbbox 直接给，不用自己扫像素）。"""
    return img.image.getchannel("A").getbbox()


def _text_kwargs(*, allow_wrap: bool) -> dict:
    return dict(
        min_fontsize=40,
        max_fontsize=MAX_FONTSIZE,
        allow_wrap=allow_wrap,
        lines_align="center",
        fill=TEXT_FILL,
    )


def _render_plain(text: str) -> BuildImage:
    """只有用户文字的原布局（文字多时自动折行）。"""
    frame = BuildImage.open(img_dir / "DSniangThink.png")
    frame.draw_text(TEXT_AREA, text, **_text_kwargs(allow_wrap=True))
    return frame


def _render_with_reason(text: str) -> BuildImage:
    """短文本布局：上方一行状态行 + 下方用户文字，两者**左对齐**。

    只应传不含换行的短文本（由 :func:`deep_seek_think` 把关）。

    实现上先把状态行与正文各画到一张透明层，量出各自的**真实墨迹 bbox**，
    再按「两边墨迹左边缘对齐、整组在气泡里居中」合成。
    这样对齐是像素级的，也不用复制 pil_utils 那套字号拟合逻辑去估算文字宽度。
    """
    reason = _reason_layer(random.randint(*REASON_SECONDS_RANGE))
    r_ink = _alpha_bbox(reason)

    box_l, box_t, box_r, box_b = SHORT_TEXT_AREA
    body = BuildImage.new("RGBA", (box_r - box_l, box_b - box_t), (0, 0, 0, 0))
    # 正文刻意**不折行**：折行会把「八个字也不多啊」排成「八个字也不多 / 啊」，
    # 末行孤零零一个字很难看，而且会顶到状态行。不折行就让 draw_text 一路缩字号，
    # 保证状态行下面始终是干净的一行。
    body.draw_text((0, 0, body.width, body.height), text, **_text_kwargs(allow_wrap=False))
    b_ink = _alpha_bbox(body)
    if r_ink is None or b_ink is None:  # 理论上不会发生，防御一下
        raise ValueError("状态行或正文没有画出任何像素")

    # 左对齐边 + 整组居中：组宽取两者中较宽的那个。
    # 注意 PIL 的 getbbox 返回 (left, top, right, bottom) 是「右下开区间」，
    # 所以宽度就是 right - left，不要 +1（否则整组中心会偏 0.5px）。
    block_w = max(r_ink[2] - r_ink[0], b_ink[2] - b_ink[0])
    left = CONTENT_CENTER_X - block_w / 2

    frame = BuildImage.open(img_dir / "DSniangThink.png")
    # 用墨迹 bbox 反推落点，让两张层的墨迹左边缘都落在 left 上
    frame.alpha_composite(
        reason,
        (int(round(left - r_ink[0])), int(round(REASON_CENTER_Y - (r_ink[1] + r_ink[3]) / 2))),
    )
    frame.alpha_composite(body, (int(round(left - b_ink[0])), box_t))
    return frame


def deep_seek_think(images, texts: list[str], args):
    text = texts[0]

    # 只有「又短、又没有换行」才补状态行。
    #
    # 排除显式换行是必须的：allow_wrap=False 只挡自动折行，挡不住用户自己写的 \n。
    # 多行正文会被 draw_text 压进 SHORT_TEXT_AREA 再纵向居中，一旦行数上去，
    # 首行就顶到状态行上去 —— 实测「上\\n下」「第一行\\n第二行」的正文首行在 y=189，
    # 而状态行底边是 187，只剩 2px，视觉上已经糊在一起。
    # 何况用户自己排了多行，本来也不该再给他叠一行 UI 状态行。
    plain_only = len(text) > SHORT_TEXT_MAX or "\n" in text or "\r" in text

    try:
        if plain_only:
            frame = _render_plain(text)
        else:
            try:
                frame = _render_with_reason(text)
            except ValueError:
                # 加了状态行反而挤不下（文字区域变小了）——
                # 退回原布局，别让本来能画的短文本平白失败。
                # 每次都重新 open，免得把画了一半的状态行留在图上。
                frame = _render_plain(text)
    except ValueError:
        raise TextOverLength(text)
    return frame.save_png()


add_meme(
    "deep_seek_think",
    deep_seek_think,
    min_texts=1,
    max_texts=1,
    default_texts=[DEFAULT_TEXT],
    keywords=["deepseek娘想", "deepseek想"],
    tags={"DeepSeek", "深度求索"},
    date_created=datetime(2026, 9, 13),
    date_modified=datetime(2026, 9, 13),
)
