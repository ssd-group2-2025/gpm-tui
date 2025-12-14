from getpass import getpass
import requests
from valid8 import ValidationError

from gpm_ssd.domain import Token


class AuthHandler:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token: Token | None = None
        self.session: requests.Session | None = None
        self.user_id: int | None = None

    def login(self, load_data_callback) -> bool:
        if self.token is not None:
            return False
            
        try:
            username = input('Username: ')
            password = getpass('Password: ')
            self.session = requests.Session()
            res = self.session.post(
                f"{self.base_url}auth/login/",
                json={'username': username, 'password': password},
            )
            if res.status_code != 200:
                json = res.json()
                print(f"Login failed: {json.get('detail', 'Unknown error')}")
                self.session = None
                return False
            json_response = res.json()
            self.token = Token.from_response(json_response)
            load_data_callback()
            print("Login successful!")
            return True
        except ValidationError as e:
            print(f"Token validation error: {e}")
            self.session = None
            return False
        except Exception as e:
            print(f"Login error: {e}")
            self.session = None
            return False

    def logout(self, clear_data_callback) -> bool:
        if self.token is None:
            print("You are not logged in")
            return False
        
        if self.session is None:
            print("No active session")
            return False
        
        res = self.session.post(
            f"{self.base_url}auth/logout/",
            headers={"Authorization": f"Bearer {self.token.access}"}
        )
        if res.status_code not in [200]:
            print(f"Logout failed (status code: {res.status_code})")
            return False
        else:
            print("Logout successful")
            self.token = None
            self.session = None
            self.user_id = None
            clear_data_callback()
            return True

    def is_authenticated(self) -> bool:
        return self.token is not None

    def is_staff(self) -> bool:
        return self.token is not None and self.token.is_staff()

    def get_headers(self) -> dict:
        if self.token is None:
            return {}
        return {"Authorization": f"Bearer {self.token.access}"}
