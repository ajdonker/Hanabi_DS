import pytest
import hashlib
from unittest.mock import patch
from server.application.commands.login_commands import RegisterCommand, LoginCommand
from database import *
from server.application.user import User
from database.RedisRepository import RedisRepository
from database.mockRedis import MockRedisRepository

# --- TESTS REGISTRATION ---

def test_register_new_user_success(): #ok
    
    mockDB = MockRedisRepository()
    repo = RedisRepository(redis_client = mockDB)
    
    register_cmd = RegisterCommand(repository = repo)

    data = {
        "fullName": "Mario Rossi",
        "email": "mario@test.com",
        "username": "mario88",
        "password": "password123"
    }
    
    event = register_cmd.execute(data)
    
    assert event[0].event == "registration_success"

def test_register_duplicate_username(): #ok

    mockDB = MockRedisRepository()
    repo = RedisRepository(redis_client = mockDB)
    
    register_cmd = RegisterCommand(repository = repo)
    
    user1 = {
        "fullName": "Mario Rossi",
        "email": "mario@test.com",
        "username": "mario88",
        "password": "password123"
    }
    
    register_cmd.execute(user1)
    
    user2 = {
        "fullName": "Mario Bianchi",
        "email": "mario@test.com",
        "username": "mario88",
        "password": "password456"
    }
    
    event = register_cmd.execute(user2)
    
    assert event[0].event == "error"
    assert "already exists" in event[0].data["message"]

# --- TESTS LOGIN ---

def test_login_success():

    mockDB = MockRedisRepository()
    repo = RedisRepository(redis_client = mockDB)
    
    register_cmd = RegisterCommand(repository = repo)
        
    user1 = {
        "fullName": "Mario Rossi",
        "email": "mario@test.com",
        "username": "mario88",
        "password": "password123"
    }
    
    register_cmd.execute(user1)
    
    login_cmd = LoginCommand(repository = repo)
    
    data = {"username": "mario88", "password": "password123"}
    
    event = login_cmd.execute(data)
    
    assert event[0].event == "login_success"

def test_login_wrong_password():
    
    mockDB = MockRedisRepository()
    repo = RedisRepository(redis_client = mockDB)
    
    register_cmd = RegisterCommand(repository = repo)
    
    user1 = {
        "fullName": "Mario Rossi",
        "email": "mario@test.com",
        "username": "mario88",
        "password": "password123"
    }
    
    register_cmd.execute(user1)
    
    login_cmd = LoginCommand(repository = repo)
    
    data = {"username": "mario88", "password": "password456"}
    
    event = login_cmd.execute(data)
    
    assert event[0].event == "error"
    assert "already exists" in event[0].data["message"]

def test_login_user_not_found(): #ok
        
    mockDB = MockRedisRepository()
    repo = RedisRepository(redis_client = mockDB)
    login_cmd = LoginCommand(repository = repo)

    data = {"username": "mario88", "password": "password456"}
    
    event = login_cmd.execute(data)
    
    assert event[0].event == "error"
    assert "not found" in event[0].data["message"]