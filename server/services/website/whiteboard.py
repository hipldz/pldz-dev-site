
import typing
import datetime
import random

from typedef import WhiteboardItem


INVALID_TIME = 60 * 60 * 24  # 一天
MAX_WHITEBOARD_ITEMS = 900
MIN_RANDOM_KEY = 100
MAX_RANDOM_KEY = 999


class WhiteboardService:
    white_board_list: typing.List[WhiteboardItem] = []

    @classmethod
    def _now(cls) -> datetime.datetime:
        return datetime.datetime.now()

    @classmethod
    def _is_expired(cls, created: str, now: typing.Optional[datetime.datetime] = None) -> bool:
        if not created:
            return False
        current = now or cls._now()
        return (current - datetime.datetime.fromisoformat(created)).total_seconds() > INVALID_TIME

    @classmethod
    def _prune_expired(cls) -> None:
        current = cls._now()
        cls.white_board_list = [
            item for item in cls.white_board_list
            if not cls._is_expired(item['created'], current)
        ]

    @classmethod
    def random_key(cls) -> str:
        """
        生成 100-999 的随机数字密钥，保证全局唯一
        """
        if len(cls.white_board_list) >= MAX_WHITEBOARD_ITEMS:
            raise RuntimeError("Whiteboard capacity exhausted.")
        while True:
            candidate = str(random.randint(MIN_RANDOM_KEY, MAX_RANDOM_KEY))
            if all(item['key'] != candidate for item in cls.white_board_list):
                return candidate

    @classmethod
    def _create_item(cls, username: str) -> WhiteboardItem:
        username = username or ""
        new_item: WhiteboardItem = {
            'created': cls._now().isoformat(),
            'key': cls.random_key(),
            'content': "",
            'username': username,
        }
        cls.white_board_list.append(new_item)
        return new_item

    @classmethod
    def get_items_by_username(cls, username: typing.Optional[str], create_new: bool = False) -> typing.List[WhiteboardItem]:
        """
        获取指定用户名的白板内容列表
        :param username: 用户名，可为空字符串
        :param create_new: 是否为该用户创建一个新的白板
        :return: 白板元素列表
        """
        cls._prune_expired()
        target_username = username or ""
        items = [item for item in cls.white_board_list if item['username'] == target_username]

        if create_new or not items:
            new_item = cls._create_item(target_username)
            # 新创建的白板置顶
            items = [new_item] + [item for item in items if item['key'] != new_item['key']]

        # 按更新时间倒序返回，最近的在前
        return sorted(items, key=lambda x: x['created'], reverse=True)

    @classmethod
    def get_item_by_key(cls, key: str) -> typing.Optional[WhiteboardItem]:
        """
        获取指定键的白板内容
        :param key: 白板项的键
        :return: 白板元素
        """
        if not key:
            return None
        target: typing.Optional[WhiteboardItem] = None
        for item in cls.white_board_list:
            if item['key'] == key:
                if cls._is_expired(item['created']):
                    item['created'] = cls._now().isoformat()
                    item['content'] = ""
                target = item
                break
        cls._prune_expired()
        if target:
            return target
        # 如果没有找到或键为空，返回空
        return None

    @classmethod
    def set_content_by_key(cls, key: str, content: str) -> str:
        """
        设置指定键的白板内容
        :param key: 白板项的键
        :param content: 白板内容
        """
        if not key:
            return ""
        # 检查是否已存在该键的白板项
        for item in cls.white_board_list:
            if item['key'] == key:
                item['content'] = content
                item['created'] = datetime.datetime.now().isoformat()
                return item['created']
        # 如果不存在, 返回空
        return ""
