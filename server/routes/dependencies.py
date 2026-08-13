from fastapi import HTTPException, Request, status

from services.identity.authorization import AuthenticationError, AuthorizationService, UserNotFoundError


def current_user(request: Request) -> dict:
    """Translate authorization domain errors into HTTP responses."""
    try:
        return AuthorizationService.get_user_from_access_token(request.cookies.get("access_token", ""))
    except UserNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except AuthenticationError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error


def optional_current_user(request: Request) -> dict | None:
    try:
        return current_user(request)
    except HTTPException as error:
        if error.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND):
            return None
        raise


def ensure_authenticated(
    user: dict,
    *,
    detail: str,
    status_code: int = status.HTTP_401_UNAUTHORIZED,
) -> dict:
    if not user:
        raise HTTPException(status_code=status_code, detail=detail)
    return user


def ensure_admin_user(
    user: dict,
    *,
    login_detail: str,
    forbidden_detail: str,
) -> dict:
    current_user = ensure_authenticated(user, detail=login_detail)
    if not AuthorizationService.check_admin(current_user.get("username")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=forbidden_detail,
        )
    return current_user
