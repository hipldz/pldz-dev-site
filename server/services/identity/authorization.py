import base64
import io
import uuid
import bcrypt
import jwt
import pyotp
import qrcode
import qrcode.image.svg
from jwt import PyJWTError
from datetime import datetime, timedelta
from core import Logger, ProjectConfig
from storage.db.json_store import _lock, _read_json, _write_json, get_users_db_path


ALGORITHM = "HS256"
settings = ProjectConfig.get_settings()

SECRET_KEY = settings.secret_key
ADMIN_USERNAME = settings.admin_username
ADMIN_PASSWORD = settings.admin_password
TWO_FACTOR_ISSUER = settings.two_factor_issuer

ACCESS_EXPIRE = timedelta(minutes=settings.access_token_expire_minutes)
REFRESH_EXPIRE = timedelta(days=settings.refresh_token_expire_days)


class AuthenticationError(Exception):
    """An access token is missing, invalid or expired."""


class UserNotFoundError(AuthenticationError):
    """The access token is valid but its user no longer exists."""


class AuthorizationService:

    @classmethod
    def init_admin(cls):
        if cls.get_user_by_username(ADMIN_USERNAME):
            Logger.info(f"✔ 管理员账号已存在，跳过初始化: {ADMIN_USERNAME}")
            return False
        cls.add_user(ADMIN_USERNAME, ADMIN_PASSWORD, "爬楼的猪", "/api/v1/website/image/avatar/admin.jpg")
        Logger.info(f"✔ 初始化管理员账号: {ADMIN_USERNAME}")
        return True

    @classmethod
    def create_token(cls, username: str, expires: timedelta, token_type: str):
        payload = {"sub": username, "type": token_type, "exp": datetime.now() + expires}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")

    @classmethod
    def verify_password(cls, password: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("ascii"))
        except (TypeError, ValueError, UnicodeError):
            return False

    @classmethod
    def _clean_user(cls, user: dict) -> dict:
        result = dict(user)
        result.pop('password', None)
        result.pop('token', None)
        result.pop('blacklisted', None)
        result.pop('two_factor_secret', None)
        result.pop('two_factor_pending_secret', None)
        result['two_factor_enabled'] = bool(user.get('two_factor_enabled'))
        return result

    @classmethod
    def get_user_from_access_token(cls, token: str):
        if not token:
            raise AuthenticationError("Not authenticated")
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if data.get('type') != 'access':
                raise AuthenticationError("Invalid token type")
            username = data.get('sub')
            user = cls.get_user_by_username(username)
            if not user:
                raise UserNotFoundError("User not found")
            return user
        except PyJWTError as e:
            Logger.error(f"✖ JWT 错误: {e}")
            raise AuthenticationError("Invalid or expired token") from e

    @classmethod
    def check_admin(cls, username: str):
        return username == ADMIN_USERNAME

    @classmethod
    def create_access_token(cls, user):
        return cls.create_token(user, ACCESS_EXPIRE, 'access')

    @classmethod
    def create_refresh_token(cls, user):
        tok = cls.create_token(user, REFRESH_EXPIRE, 'refresh')
        cls.update_user_token(user, tok)
        return tok

    @classmethod
    def blacklist_token(cls, token: str) -> bool:
        db = get_users_db_path()
        with _lock:
            data = _read_json(db)
            for user in data.values():
                if user.get('token') == token:
                    user['blacklisted'] = True
                    _write_json(db, data)
                    return True
        return False

    @classmethod
    def is_token_blacklisted(cls, token: str) -> bool:
        with _lock:
            data = _read_json(get_users_db_path())
        for user in data.values():
            if user.get('token') == token and user.get('blacklisted'):
                return True
        return False

    @classmethod
    def add_user(cls, username: str, password: str, nickname: str, avatar: str = "/api/v1/website/image/avatar/default.jpg") -> bool:
        db = get_users_db_path()
        isadmin = cls.check_admin(username)
        hash_password = cls.hash_password(password)
        with _lock:
            data = _read_json(db)
            if username in data:
                data[username].update({
                    'password': hash_password,
                    'nickname': nickname,
                    'avatar': avatar,
                    'isadmin': isadmin,
                    'blacklisted': False,
                })
            else:
                data[username] = {
                    'id': str(uuid.uuid4()),
                    'username': username,
                    'password': hash_password,
                    'nickname': nickname,
                    'avatar': avatar,
                    'isadmin': isadmin,
                    'blacklisted': False,
                    'token': '',
                    'two_factor_enabled': False,
                    'two_factor_secret': '',
                    'two_factor_pending_secret': '',
                }
            _write_json(db, data)
        return True

    @classmethod
    def update_user_token(cls, username: str, token: str) -> bool:
        db = get_users_db_path()
        with _lock:
            data = _read_json(db)
            if username not in data:
                return False
            data[username]['token'] = token
            data[username]['blacklisted'] = False
            _write_json(db, data)
        return True

    @classmethod
    def update_user_password(cls, username: str, password: str) -> bool:
        if len(password) < 8 or len(password) > 128:
            raise ValueError("Password must contain 8-128 characters")
        db = get_users_db_path()
        with _lock:
            data = _read_json(db)
            if username not in data:
                return False
            data[username]["password"] = cls.hash_password(password)
            data[username]["token"] = ""
            data[username]["blacklisted"] = True
            _write_json(db, data)
        return True

    @classmethod
    def get_user_by_username(cls, username: str) -> dict:
        with _lock:
            data = _read_json(get_users_db_path())
        user = data.get(username)
        if not user:
            return None
        return cls._clean_user(user)

    @classmethod
    def get_user_password(cls, username: str) -> str:
        with _lock:
            data = _read_json(get_users_db_path())
        user = data.get(username)
        if not user:
            return None
        return user.get('password', None)

    @classmethod
    def is_two_factor_enabled(cls, username: str) -> bool:
        with _lock:
            data = _read_json(get_users_db_path())
        user = data.get(username)
        return bool(user and user.get('two_factor_enabled') and user.get('two_factor_secret'))

    @classmethod
    def verify_two_factor_code(cls, username: str, code: str) -> bool:
        normalized_code = str(code or '').replace(' ', '').strip()
        if not normalized_code:
            return False
        with _lock:
            data = _read_json(get_users_db_path())
        user = data.get(username)
        secret = user.get('two_factor_secret') if user else None
        if not secret:
            return False
        return pyotp.TOTP(secret).verify(normalized_code, valid_window=1)

    @classmethod
    def start_two_factor_setup(cls, username: str) -> dict:
        secret = pyotp.random_base32()
        provisioning_uri = pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name=TWO_FACTOR_ISSUER)
        svg_buffer = io.BytesIO()
        qr_image = qrcode.make(provisioning_uri, image_factory=qrcode.image.svg.SvgPathImage)
        qr_image.save(svg_buffer)
        qr_code_data_url = f"data:image/svg+xml;base64,{base64.b64encode(svg_buffer.getvalue()).decode('ascii')}"
        db = get_users_db_path()
        with _lock:
            data = _read_json(db)
            if username not in data:
                return None
            data[username]['two_factor_pending_secret'] = secret
            _write_json(db, data)
        return {'secret': secret, 'provisioning_uri': provisioning_uri, 'qr_code': qr_code_data_url, 'issuer': TWO_FACTOR_ISSUER}

    @classmethod
    def confirm_two_factor_setup(cls, username: str, code: str) -> bool:
        normalized_code = str(code or '').replace(' ', '').strip()
        db = get_users_db_path()
        with _lock:
            data = _read_json(db)
            user = data.get(username)
            secret = user.get('two_factor_pending_secret') if user else None
            if not secret or not pyotp.TOTP(secret).verify(normalized_code, valid_window=1):
                return False
            user['two_factor_enabled'] = True
            user['two_factor_secret'] = secret
            user['two_factor_pending_secret'] = ''
            _write_json(db, data)
        return True

    @classmethod
    def disable_two_factor(cls, username: str, code: str) -> bool:
        if not cls.verify_two_factor_code(username, code):
            return False
        db = get_users_db_path()
        with _lock:
            data = _read_json(db)
            if username not in data:
                return False
            data[username]['two_factor_enabled'] = False
            data[username]['two_factor_secret'] = ''
            data[username]['two_factor_pending_secret'] = ''
            _write_json(db, data)
        return True

    @classmethod
    def update_user_avatar(cls, username: str, avatar: str) -> bool:
        db = get_users_db_path()
        with _lock:
            data = _read_json(db)
            if username not in data:
                return False
            data[username]['avatar'] = avatar
            _write_json(db, data)
        return True

    @classmethod
    def get_all_users(cls) -> list:
        with _lock:
            data = _read_json(get_users_db_path())
        result = []
        for user in data.values():
            result.append(cls._clean_user(user))
        return result

    @classmethod
    def delete_user(cls, username: str) -> bool:
        db = get_users_db_path()
        with _lock:
            data = _read_json(db)
            if username not in data:
                return False
            del data[username]
            _write_json(db, data)
        return True
