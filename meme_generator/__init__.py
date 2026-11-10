from pathlib import Path

# from meme_generator.config import meme_config as config
from meme_generator.manager import add_meme as add_meme
from meme_generator.manager import get_meme as get_meme
from meme_generator.manager import get_meme_keys as get_meme_keys
from meme_generator.manager import get_memes as get_memes
from meme_generator.manager import load_meme as load_meme
from meme_generator.manager import load_memes as load_memes
from meme_generator.meme import CommandShortcut as CommandShortcut
from meme_generator.meme import Meme as Meme
from meme_generator.meme import MemeArgsModel as MemeArgsModel
from meme_generator.meme import MemeArgsType as MemeArgsType
from meme_generator.meme import MemeParamsType as MemeParamsType
from meme_generator.meme import ParserArg as ParserArg
from meme_generator.meme import ParserOption as ParserOption
from meme_generator.version import __version__ as __version__

MEME_DIRS = ["memes", "memes_jj", "memes_emoji", "memes_other", "memes_emoji_nsfw"]

for dir_name in MEME_DIRS:
    meme_dir = Path(__file__).parent / dir_name
    if not meme_dir.exists():
        continue
    module_prefix = f"meme_generator.{dir_name}"
    for path in meme_dir.iterdir():
        if path.is_dir():
            load_meme(f"{module_prefix}.{path.name}")
