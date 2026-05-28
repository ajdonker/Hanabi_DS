import base64
import json

import pytest

from server.application.commands.auth_commands import RegisterCommand, LoginCommand
from server.application.handlers.auth_handlers import RegisterHandler, LoginHandler
from server.application.auth_service import AuthenticationService
from database.RedisRepository import RedisRepository
from database.mockRedis import MockRedisRepository


# --- TESTS REGISTRATION ---


def test_register_new_user_success():
    mock_db = MockRedisRepository()
    repo = RedisRepository(redis_client=mock_db)

    handler = RegisterHandler(repository=repo)

    command = RegisterCommand(
        full_name="Mario Rossi",
        email="mario@test.com",
        username="mario88",
        password="password123",
    )

    events = handler.execute(command)

    assert events[0].event == "registration_success"


def test_register_duplicate_username():
    mock_db = MockRedisRepository()
    repo = RedisRepository(redis_client=mock_db)

    handler = RegisterHandler(repository=repo)

    command1 = RegisterCommand(
        full_name="Mario Rossi",
        email="mario@test.com",
        username="mario88",
        password="password123",
    )
    handler.execute(command1)

    command2 = RegisterCommand(
        full_name="Mario Bianchi",
        email="mario2@test.com",
        username="mario88",
        password="password456",
    )

    events = handler.execute(command2)

    assert events[0].event == "error"
    assert "already exists" in events[0].data["message"]


def test_login_success():
    mock_db = MockRedisRepository()
    repo = RedisRepository(redis_client=mock_db)

    register_handler = RegisterHandler(repository=repo)
    auth_service = AuthenticationService(secret="test-secret")
    login_handler = LoginHandler(repository=repo, auth_service=auth_service)

    register_command = RegisterCommand(
        full_name="Mario Rossi",
        email="mario@test.com",
        username="mario88",
        password="password123",
    )
    register_handler.execute(register_command)

    login_command = LoginCommand(
        username="mario88",
        password="password123",
    )

    events = login_handler.execute(login_command)

    assert events[0].event == "login_success"
    assert auth_service.validate_token(events[0].data["token"]) == "mario88"


def test_login_wrong_password():
    mock_db = MockRedisRepository()
    repo = RedisRepository(redis_client=mock_db)

    register_handler = RegisterHandler(repository=repo)
    login_handler = LoginHandler(repository=repo, auth_service=AuthenticationService(secret="test-secret"))

    register_command = RegisterCommand(
        full_name="Mario Rossi",
        email="mario@test.com",
        username="mario88",
        password="password123",
    )
    register_handler.execute(register_command)

    login_command = LoginCommand(
        username="mario88",
        password="password456",
    )

    events = login_handler.execute(login_command)

    assert events[0].event == "error"
    assert "Invalid" in events[0].data["message"]


def test_login_user_not_found():
    mock_db = MockRedisRepository()
    repo = RedisRepository(redis_client=mock_db)

    login_handler = LoginHandler(repository=repo, auth_service=AuthenticationService(secret="test-secret"))

    login_command = LoginCommand(
        username="mario88",
        password="password456",
    )

    events = login_handler.execute(login_command)

    assert events[0].event == "error"
    assert "not found" in events[0].data["message"]


def test_authentication_service_rejects_tampered_token():
    auth_service = AuthenticationService(secret="test-secret")
    token = auth_service.generate_token("mario88")
    payload = json.loads(base64.b64decode(token.encode("utf-8")).decode("utf-8"))
    payload["username"] = "luigi77"
    tampered_token = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")

    assert auth_service.validate_token(token) == "mario88"
    assert auth_service.validate_token(tampered_token) is None
