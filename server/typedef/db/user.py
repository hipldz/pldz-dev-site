from typing import TypedDict


class UserRecord(TypedDict):
    username: str
    password: str
    nickname: str
    avatar: str
    isadmin: bool
    role: str
    token: str
    blacklisted: bool
    two_factor_enabled: bool
    two_factor_secret: str
    two_factor_pending_secret: str
