from typing import TypedDict


class WhiteboardItem(TypedDict):
    created: str
    key: str
    content: str
    username: str
