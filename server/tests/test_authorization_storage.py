from services.identity.authorization import AuthorizationService


def test_clean_user_never_exposes_credentials():
    user = {
        "username": "person@example.com",
        "password": "hash",
        "token": "refresh-token",
        "two_factor_secret": "secret",
    }

    cleaned = AuthorizationService._clean_user(user)

    assert "password" not in cleaned
    assert "token" not in cleaned
    assert "two_factor_secret" not in cleaned


def test_init_admin_does_not_replace_existing_account(monkeypatch):
    monkeypatch.setattr("services.identity.authorization.Logger.info", lambda message: None)
    monkeypatch.setattr(
        AuthorizationService,
        "get_user_by_username",
        lambda username: {"username": username},
    )
    calls = []
    monkeypatch.setattr(
        AuthorizationService,
        "add_user",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    assert AuthorizationService.init_admin() is False
    assert calls == []


def test_update_user_password_rejects_weak_password():
    try:
        AuthorizationService.update_user_password("person@example.com", "short")
    except ValueError as error:
        assert "8-128" in str(error)
    else:
        raise AssertionError("weak password was accepted")
