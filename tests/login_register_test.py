import pytest
from unittest.mock import MagicMock, patch
from server.application.commands.user_commands import RegisterCommand, LoginCommand # Aggiusta il path se necessario
from server.presentation.websocket_handler import Event

class TestUserApplicationLayer:

    @patch('web.backend.database.RedisRepository.RedisRepository')
    def test_register_success(self, MockRepo):
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.load_user.return_value = None
        
        command = RegisterCommand()
        data = {
            "fullName": "Mario Rossi",
            "email": "mario@example.com",
            "username": "marior",
            "password": "securepassword123"
        }

        results = command.execute(data)

        assert len(results) == 1
        assert results[0].type == "registration_success"
        mock_repo_instance.save_user.assert_called_once()

    @patch('web.backend.database.RedisRepository.RedisRepository')
    def test_register_username_already_exists(self, MockRepo):

        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.load_user.return_value = {"username": "marior"} 
        
        command = RegisterCommand()
        data = {"fullName": "M", "email": "e", "username": "marior", "password": "p"}

        results = command.execute(data)

        assert results[0].type == "error"
        assert "already exists" in results[0].payload["message"]

    @patch('web.backend.database.RedisRepository.RedisRepository')
    def test_login_success(self, MockRepo):

        import hashlib
        hashed_pw = hashlib.sha256("password123".encode('utf-8')).hexdigest()
        
        mock_user = MagicMock()
        mock_user._hashedPass = hashed_pw
        
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.load_user.return_value = mock_user

        command = LoginCommand()
        data = {"username": "marior", "password": "password123"}

        results = command.execute(data)

        assert results[0].type == "login_success"

    @patch('web.backend.database.RedisRepository.RedisRepository')
    def test_login_wrong_password(self, MockRepo):
        mock_user = MagicMock()
        mock_user._hashedPass = "hash_di_un_altra_password"
        
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.load_user.return_value = mock_user

        command = LoginCommand()
        data = {"username": "marior", "password": "password_sbagliata"}

        results = command.execute(data)

        assert results[0].type == "error"
        assert "Invalid username or password" in results[0].payload["message"]