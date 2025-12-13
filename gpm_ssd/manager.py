import requests
import typeguard
from .exceptions import HttpException
from .models import Token, User, Goal, Topic, GroupProject

@typeguard.typechecked()
class TUIManager:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.__base_url = base_url
        self.__session = requests.Session()
        self.__token: Token | None = None
    
    @property
    def is_authenticated(self):
        return self.__token is not None
    
    def __get_auth_headers(self) -> dict:
        if not self.is_authenticated:
            raise HttpException("Not authenticated. Please login first.")
        return {
            'Authorization': f'Bearer {self.__token.access}'
        }
    
    def __handle_response(self, response: requests.Response):
        if response.status_code == 400:
            raise HttpException.from_error_dict(response.json())
        elif response.status_code == 401:
            raise HttpException(response.json().get('detail', 'Unauthorized'))
        elif response.status_code == 404:
            raise HttpException("Resource not found")
        elif response.status_code >= 500:
            raise HttpException(f"Server error: {response.status_code}")
    
    # ==================== AUTH ====================
    
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
    
    # ==================== USERS ====================
    
    def get_users(self) -> list[User]:
        url = f"{self.__base_url}/api/v1/users/"
        response = self.__session.get(url=url, headers=self.__get_auth_headers())
        
        if response.status_code != 200:
            self.__handle_response(response)
        
        users_data = response.json()
        return [User.from_response(user_json) for user_json in users_data]
    
    def get_user(self, user_id: int) -> User:
        url = f"{self.__base_url}/api/v1/users/{user_id}/"
        response = self.__session.get(url=url, headers=self.__get_auth_headers())
        
        if response.status_code != 200:
            self.__handle_response(response)
        
        return User.from_response(response.json())
    
    def create_user(self, username: str, matricola: str, email: str | None = None, 
                    first_name: str | None = None, last_name: str | None = None) -> User:
        body = {
            'username': username,
            'matricola': matricola
        }
        if email is not None:
            body['email'] = email
        if first_name is not None:
            body['firstName'] = first_name
        if last_name is not None:
            body['lastName'] = last_name
        
        url = f"{self.__base_url}/api/v1/users/"
        response = self.__session.post(url=url, json=body, headers=self.__get_auth_headers())
        
        if response.status_code != 201:
            self.__handle_response(response)
        
        return User.from_response(response.json())
    
    def update_user(self, user_id: int, username: str, matricola: str, 
                    email: str | None = None, first_name: str | None = None, 
                    last_name: str | None = None) -> User:
        body = {
            'username': username,
            'matricola': matricola
        }
        if email is not None:
            body['email'] = email
        if first_name is not None:
            body['firstName'] = first_name
        if last_name is not None:
            body['lastName'] = last_name
        
        url = f"{self.__base_url}/api/v1/users/{user_id}/"
        response = self.__session.put(url=url, json=body, headers=self.__get_auth_headers())
        
        if response.status_code != 200:
            self.__handle_response(response)
        
        return User.from_response(response.json())
    
    def delete_user(self, user_id: int):
        url = f"{self.__base_url}/api/v1/users/{user_id}/"
        response = self.__session.delete(url=url, headers=self.__get_auth_headers())
        
        if response.status_code != 204:
            self.__handle_response(response)
    
    # ==================== GOALS ====================
    
    def get_goals(self) -> list[Goal]:
        url = f"{self.__base_url}/api/v1/goals/"
        response = self.__session.get(url=url, headers=self.__get_auth_headers())
        
        if response.status_code != 200:
            self.__handle_response(response)
        
        goals_data = response.json()
        return [Goal.from_response(goal_json) for goal_json in goals_data]
    
    def get_goal(self, goal_id: int) -> Goal:
        url = f"{self.__base_url}/api/v1/goals/{goal_id}/"
        response = self.__session.get(url=url, headers=self.__get_auth_headers())
        
        if response.status_code != 200:
            self.__handle_response(response)
        
        return Goal.from_response(response.json())
    
    def create_goal(self, title: str, description: str, points: int) -> Goal:
        body = {
            'title': title,
            'description': description,
            'points': points
        }
        
        url = f"{self.__base_url}/api/v1/goals/"
        response = self.__session.post(url=url, json=body, headers=self.__get_auth_headers())
        
        if response.status_code != 201:
            self.__handle_response(response)
        
        return Goal.from_response(response.json())
    
    def update_goal(self, goal_id: int, title: str, description: str, points: int) -> Goal:
        body = {
            'title': title,
            'description': description,
            'points': points
        }
        
        url = f"{self.__base_url}/api/v1/goals/{goal_id}/"
        response = self.__session.put(url=url, json=body, headers=self.__get_auth_headers())
        
        if response.status_code != 200:
            self.__handle_response(response)
        
        return Goal.from_response(response.json())
    
    def delete_goal(self, goal_id: int):
        url = f"{self.__base_url}/api/v1/goals/{goal_id}/"
        response = self.__session.delete(url=url, headers=self.__get_auth_headers())
        
        if response.status_code != 204:
            self.__handle_response(response)
    
    # ==================== TOPICS ====================
    
    def get_topics(self) -> list[Topic]:
        url = f"{self.__base_url}/api/v1/topics/"
        response = self.__session.get(url=url, headers=self.__get_auth_headers())
        
        if response.status_code != 200:
            self.__handle_response(response)
        
        topics_data = response.json()
        return [Topic.from_response(topic_json) for topic_json in topics_data]
    
    def get_topic(self, topic_id: int) -> Topic:
        url = f"{self.__base_url}/api/v1/topics/{topic_id}/"
        response = self.__session.get(url=url, headers=self.__get_auth_headers())
        
        if response.status_code != 200:
            self.__handle_response(response)
        
        return Topic.from_response(response.json())
    
    def create_topic(self, title: str) -> Topic:
        body = {'title': title}
        
        url = f"{self.__base_url}/api/v1/topics/"
        response = self.__session.post(url=url, json=body, headers=self.__get_auth_headers())
        
        if response.status_code != 201:
            self.__handle_response(response)
        
        return Topic.from_response(response.json())
    
    def update_topic(self, topic_id: int, title: str) -> Topic:
        body = {'title': title}
        
        url = f"{self.__base_url}/api/v1/topics/{topic_id}/"
        response = self.__session.put(url=url, json=body, headers=self.__get_auth_headers())
        
        if response.status_code != 200:
            self.__handle_response(response)
        
        return Topic.from_response(response.json())
    
    def delete_topic(self, topic_id: int):
        url = f"{self.__base_url}/api/v1/topics/{topic_id}/"
        response = self.__session.delete(url=url, headers=self.__get_auth_headers())
        
        if response.status_code != 204:
            self.__handle_response(response)
    
    # ==================== GROUPS ====================
    
    def get_groups(self) -> list[GroupProject]:
        url = f"{self.__base_url}/api/v1/groups/"
        response = self.__session.get(url=url, headers=self.__get_auth_headers())
        
        if response.status_code != 200:
            self.__handle_response(response)
        
        groups_data = response.json()
        return [GroupProject.from_response(group_json) for group_json in groups_data]
    
    def get_group(self, group_id: int) -> GroupProject:
        url = f"{self.__base_url}/api/v1/groups/{group_id}/"
        response = self.__session.get(url=url, headers=self.__get_auth_headers())
        
        if response.status_code != 200:
            self.__handle_response(response)
        
        return GroupProject.from_response(response.json())
    
    def create_group(self, name: str, link_django: str, link_tui: str, 
                     link_gui: str, topic: int) -> GroupProject:
        body = {
            'name': name,
            'linkDjango': link_django,
            'linkTui': link_tui,
            'linkGui': link_gui,
            'topic': topic
        }
        
        url = f"{self.__base_url}/api/v1/groups/"
        response = self.__session.post(url=url, json=body, headers=self.__get_auth_headers())
        
        if response.status_code != 201:
            self.__handle_response(response)
        
        return GroupProject.from_response(response.json())
    
    def update_group(self, group_id: int, name: str, link_django: str, 
                     link_tui: str, link_gui: str, topic: int) -> GroupProject:
        body = {
            'name': name,
            'linkDjango': link_django,
            'linkTui': link_tui,
            'linkGui': link_gui,
            'topic': topic
        }
        
        url = f"{self.__base_url}/api/v1/groups/{group_id}/"
        response = self.__session.put(url=url, json=body, headers=self.__get_auth_headers())
        
        if response.status_code != 200:
            self.__handle_response(response)
        
        return GroupProject.from_response(response.json())
    
    def delete_group(self, group_id: int):
        url = f"{self.__base_url}/api/v1/groups/{group_id}/"
        response = self.__session.delete(url=url, headers=self.__get_auth_headers())
        
        if response.status_code != 204:
            self.__handle_response(response)
    
    def join_group(self, group_id: int) -> GroupProject:
        url = f"{self.__base_url}/api/v1/groups/{group_id}/join/"
        response = self.__session.post(url=url, headers=self.__get_auth_headers())
        
        if response.status_code != 200:
            self.__handle_response(response)
        
        return GroupProject.from_response(response.json())