import requests
import typeguard
from .exceptions import HttpException
from .models import Token

@typeguard.typechecked()
class TUIManager:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.__base_url = base_url
        self.__session = requests.Session()
        self.__token: Token | None = None
    
    @property
    def is_authenticated(self):
        return self.__token is not None
    
    def login(self, user: str, password: str):
        body = {
            'username': user,
            'password': password
        }

        url = f"{self.__base_url}/api/v1/auth/login/"
        response = self.__session.post(url=url, json=body)
        response_json = response.json()
        if response.status_code == 400:
            raise HttpException.from_error_dict(response_json)
        elif response.status_code == 401:
            raise HttpException(response_json['detail'])
        elif response.status_code != 200:
            raise HttpException(f"An Unknown error occurred: {str(response_json)}")
        
        self.__token = Token.from_response(response_json)