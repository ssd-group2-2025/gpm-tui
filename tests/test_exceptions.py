import pytest
from gpm_ssd.exceptions import HttpException


class TestHttpException:
    def test_http_exception_creation(self):
        exc = HttpException("Test error")
        assert str(exc) == "Test error"
    
    def test_from_error_dict_single_field(self):
        error_dict = {"username": ["This field is required."]}
        exc = HttpException.from_error_dict(error_dict)
        assert "username" in str(exc)
        assert "This field is required." in str(exc)
    
    def test_from_error_dict_multiple_fields(self):
        error_dict = {
            "username": ["This field is required."],
            "password": ["This field is required.", "Password too short."]
        }
        exc = HttpException.from_error_dict(error_dict)
        error_msg = str(exc)
        assert "username" in error_msg
        assert "password" in error_msg
        assert "This field is required." in error_msg
        assert "Password too short." in error_msg
    
    def test_from_error_dict_empty(self):
        error_dict = {}
        exc = HttpException.from_error_dict(error_dict)
        assert str(exc) == ""
