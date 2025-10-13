"""商品评价机器人"""

from .playwright_bot import TaobaoCommentBot as PlaywrightCommentBot
from .selenium_bot import TaobaoCommentSelenium

__all__ = ['PlaywrightCommentBot', 'TaobaoCommentSelenium']

