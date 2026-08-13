import asyncio
import jwt
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import datetime
import random

from services.identity.authorization import ALGORITHM, SECRET_KEY, AuthorizationService
from core import ProjectConfig
from routes.dependencies import current_user, ensure_admin_user

AUTH_ROUTER = APIRouter(prefix="/authorization", tags=["authorization"])
settings = ProjectConfig.get_settings()
ACCESS_EXPIRE = datetime.timedelta(minutes=settings.access_token_expire_minutes)
REFRESH_EXPIRE = datetime.timedelta(days=settings.refresh_token_expire_days)


@AUTH_ROUTER.get("/privacy")
async def api_privacy_get():
    """
    处理隐私政策的请求
    """
    return {'data': {
        'icp': settings.site_icp,
        'copyright': settings.site_copyright,
        'ps': settings.site_ps,
    }}


class LoginData(BaseModel):
    username: str
    password: str
    otp_code: str = ''


@AUTH_ROUTER.post('/login')
async def login(data: LoginData):
    """
    处理登录请求
    :param username: 用户名
    :param password: 密码
    """
    user = AuthorizationService.get_user_by_username(data.username)
    if not user:
        await asyncio.sleep(random.uniform(0.1, 0.3))
        return {'data': {"flag": False, 'log': '用户名或密码错误'}}
    # 验证密码
    if not data.password:
        await asyncio.sleep(random.uniform(0.1, 0.3))
        return {'data': {"flag": False, 'log': '密码不能为空'}}

    password = AuthorizationService.get_user_password(data.username)
    if not password or not AuthorizationService.verify_password(data.password, password):
        return {'data': {"flag": False, 'log': '用户名或密码错误'}}

    if AuthorizationService.is_two_factor_enabled(data.username):
        if not data.otp_code:
            return {'data': {"flag": False, "requires_2fa": True, 'log': '请输入两步验证码'}}
        if not AuthorizationService.verify_two_factor_code(data.username, data.otp_code):
            return {'data': {"flag": False, "requires_2fa": True, 'log': '两步验证码错误或已过期'}}

    # 生成访问令牌和刷新令牌
    access = AuthorizationService.create_access_token(data.username)
    refresh = AuthorizationService.create_refresh_token(data.username)

    # 设置响应头和Cookie
    resp = JSONResponse({'data': {"flag": True, **user, 'log': '登录成功'}})

    # 设置Cookie，httponly和samesite属性
    resp.set_cookie('access_token', access, httponly=True, samesite='lax', max_age=int(ACCESS_EXPIRE.total_seconds()))
    resp.set_cookie('refresh_token', refresh, httponly=True, samesite='lax', max_age=int(REFRESH_EXPIRE.total_seconds()))
    return resp


class RegisterData(BaseModel):
    username: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)
    nickname: str = Field(min_length=1, max_length=50)


@AUTH_ROUTER.post('/register')
async def register(data: RegisterData):
    """
    处理注册请求
    :param username: 用户名
    :param password: 密码
    """
    if AuthorizationService.get_user_by_username(data.username):
        await asyncio.sleep(random.uniform(0.1, 0.3))
        return {'data': {'flag': False, 'log': '用户名已存在'}}
    # 存储新用户
    AuthorizationService.add_user(data.username, data.password, data.nickname)
    access = AuthorizationService.create_access_token(data.username)
    refresh = AuthorizationService.create_refresh_token(data.username)

    user = AuthorizationService.get_user_by_username(data.username)
    resp = JSONResponse({'data': {'flag': True, **user, 'log': '注册成功'}})
    # 设置Cookie，httponly和samesite属性
    resp.set_cookie('access_token', access, httponly=True, samesite='lax', max_age=int(ACCESS_EXPIRE.total_seconds()))
    resp.set_cookie('refresh_token', refresh, httponly=True, samesite='lax', max_age=int(REFRESH_EXPIRE.total_seconds()))
    await asyncio.sleep(random.uniform(0.1, 0.3))
    return resp


class TwoFactorCodeData(BaseModel):
    code: str = ''


@AUTH_ROUTER.post('/2fa/setup')
async def api_setup_two_factor(user: dict = Depends(current_user)):
    """
    创建两步验证绑定密钥。
    """
    username = user.get('username')
    if AuthorizationService.is_two_factor_enabled(username):
        return JSONResponse({'data': {'flag': False, 'log': '两步验证已开启'}})

    setup = AuthorizationService.start_two_factor_setup(username)
    if not setup:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    return JSONResponse({'data': {'flag': True, **setup, 'log': '请在验证器应用中添加密钥，并输入验证码完成绑定'}})


@AUTH_ROUTER.post('/2fa/confirm')
async def api_confirm_two_factor(data: TwoFactorCodeData, user: dict = Depends(current_user)):
    """
    确认两步验证绑定。
    """
    username = user.get('username')
    if not AuthorizationService.confirm_two_factor_setup(username, data.code):
        return JSONResponse({'data': {'flag': False, 'log': '验证码错误或已过期'}})

    current_user = AuthorizationService.get_user_by_username(username)
    return JSONResponse({'data': {'flag': True, **current_user, 'log': '两步验证已开启'}})


@AUTH_ROUTER.post('/2fa/disable')
async def api_disable_two_factor(data: TwoFactorCodeData, user: dict = Depends(current_user)):
    """
    关闭两步验证。
    """
    username = user.get('username')
    if not AuthorizationService.is_two_factor_enabled(username):
        current_user = AuthorizationService.get_user_by_username(username)
        return JSONResponse({'data': {'flag': True, **current_user, 'log': '两步验证未开启'}})
    if not AuthorizationService.disable_two_factor(username, data.code):
        return JSONResponse({'data': {'flag': False, 'log': '验证码错误或已过期'}})

    current_user = AuthorizationService.get_user_by_username(username)
    return JSONResponse({'data': {'flag': True, **current_user, 'log': '两步验证已关闭'}})


@AUTH_ROUTER.get('/logout')
async def logout(request: Request):
    """ 
    处理登出请求
    :param request: FastAPI Request 对象
    """
    token = request.cookies.get('refresh_token')
    if token:
        # 将刷新令牌加入黑名单
        AuthorizationService.blacklist_token(token)
    resp = JSONResponse({'data': True})
    resp.delete_cookie('access_token')
    resp.delete_cookie('refresh_token')
    return resp


@AUTH_ROUTER.post('/refresh')
async def refresh(request: Request):
    """
    刷新访问令牌
    :param request: FastAPI Request 对象
    """
    token = request.cookies.get('refresh_token')
    if not token or AuthorizationService.is_token_blacklisted(token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('type') != 'refresh' or not payload.get('sub'):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    new_access = AuthorizationService.create_access_token(payload['sub'])
    user = AuthorizationService.get_user_by_username(payload['sub'])
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    resp = JSONResponse(
        {'data': {'flag': True, **user, 'log': '刷新成功'}})
    resp.set_cookie('access_token', new_access, httponly=True, samesite='lax', max_age=int(ACCESS_EXPIRE.total_seconds()))
    return resp


class AvatarData(BaseModel):
    avatar: str


@AUTH_ROUTER.post('/update/avatar')
async def api_update_avatar(data: AvatarData, user: dict = Depends(current_user)):
    """
    更新用户头像
    """
    if not user or not data.avatar:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="用户名和头像不能为空")

    username = user.get('username')
    # 更新头像
    AuthorizationService.update_user_avatar(username, data.avatar)

    return JSONResponse({'data': {'flag': True, 'log': '头像更新成功'}})


@AUTH_ROUTER.get('/usermanagement/all')
async def api_get_all_user(user: dict = Depends(current_user)):
    """
    获取所有用户信息
    """
    ensure_admin_user(
        user,
        login_detail="未授权访问，请先登录!",
        forbidden_detail="您没有权限访问此资源!",
    )

    users = AuthorizationService.get_all_users()
    return JSONResponse({'data': {'flag': True, 'data': users, 'log': '获取所有用户信息成功.'}})


class DeleteUserRequest(BaseModel):
    username: str


@AUTH_ROUTER.post('/usermanagement/delete')
async def api_delete_user(data: DeleteUserRequest, user: dict = Depends(current_user)):
    """
    获取所有用户信息
    """
    ensure_admin_user(
        user,
        login_detail="未授权访问，请先登录!",
        forbidden_detail="您没有权限访问此资源!",
    )
    username = user.get('username')

    if not data.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名不能为空!"
        )
    if data.username == username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除当前登录用户!"
        )
    if not AuthorizationService.get_user_by_username(data.username):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在!"
        )
    # 删除用户
    res = AuthorizationService.delete_user(data.username)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户失败，请稍后再试!"
        )
    # 返回成功响应
    return JSONResponse({'data': {'flag': True, 'log': '用户删除成功'}})
