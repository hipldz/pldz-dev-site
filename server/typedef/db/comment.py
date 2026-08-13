from typing import TypedDict


class CommentRecord(TypedDict):
    id: str
    created: str
    username: str
    content: dict
    avatar: str
    replies: list
    replyToUsername: str
