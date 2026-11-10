from pathlib import Path
from pil_utils import BuildImage
from meme_generator import add_meme
from meme_generator.utils import FrameAlignPolicy, Maker, make_gif_or_combined_gif

img_dir = Path(__file__).parent / "images"


def penguin_shake_head(images: list[BuildImage], texts, args):

    base_loc = (78, 40)
    offsets = {
        0: (0, 0),
        1: (3, 1),
        2: (5, 2),
        3: (6, 3),
        4: (7, 4),
        5: (10, 7),
        6: (14, 9),
        7: (16, 11),
        8: (18, 13),
        9: (12, 22),
        10: (4, 28),
        11: (-1, 24),
        12: (-4, 19),
        13: (-2, 14),
        14: (1, 11),
        15: (4, 7),
        16: (7, 5),
        17: (9, 3),
        18: (12, 2),
        19: (18, 6),
        20: (24, 9),
        21: (19, 12),
        22: (16, 14),
        23: (14, 22),
        24: (13, 28),
        25: (10, 27),
        26: (8, 27),
        27: (4, 24),
        28: (-1, 21),
        29: (-3, 15),
        30: (-5, 12),
    }

    def maker(i: int) -> Maker:
        def make(imgs: list[BuildImage]) -> BuildImage:
            user_head = (
                imgs[0]
                .convert("RGBA")
                .resize((130, 150), keep_ratio=True)  
                .circle()
            )

            frame = BuildImage.open(img_dir / f"{i}.png").convert("RGBA")
            offset = offsets.get(i, (0, 0)) 
            user_loc_with_offset = (base_loc[0] + offset[0], base_loc[1] + offset[1])
            frame.paste(user_head, user_loc_with_offset, alpha=True)
            return frame

        return make

    return make_gif_or_combined_gif(
        images,
        maker,
        frame_num=31,
        duration=0.05,
        frame_align=FrameAlignPolicy.extend_loop,
    )


add_meme(
    "penguin_shake_head",
    penguin_shake_head,
    min_images=1,
    max_images=10,
    keywords=["企鹅摇头"],
)
