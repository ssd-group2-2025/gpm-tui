import typeguard
from dataclasses import dataclass, InitVar, field
from valid8 import validate
import requests
import json
import base64

@typeguard.typechecked()
@dataclass(frozen=True)
class Token:
    access: str
    refresh: str
    init_key: InitVar[object] = field(default=None)
    
    __key = object()
    
    def __post_init__(self, _init_key: object):
        validate("key", _init_key, equals=Token.__key)
            
    @staticmethod
    def __validate_token(name: str, token: object):
        validate(name, token, instance_of=str)

        token_parts = token.split(".")
        validate(name + " parts", token_parts, length=3)

        header_b64, payload_b64, signature_b64 = token_parts

        def decode_base64url(part: str):
            # Add padding if needed
            padding = "=" * (-len(part) % 4)
            try:
                return base64.urlsafe_b64decode(part + padding)
            except Exception:
                raise ValueError(f"Invalid base64 encoding in {name}")

        # Validate header
        header_bytes = decode_base64url(header_b64)
        try:
            header = json.loads(header_bytes)
        except Exception:
            raise ValueError(f"{name} header is not valid JSON")

        validate(name + " header", header, instance_of=dict)
        validate(name + " header.alg", header.get("alg"), instance_of=str)
        validate(name + " header.typ", header.get("typ"), instance_of=str)

        # Validate payload
        payload_bytes = decode_base64url(payload_b64)
        try:
            payload = json.loads(payload_bytes)
        except Exception:
            raise ValueError(f"{name} payload is not valid JSON")

        validate(name + " payload", payload, instance_of=dict)
        validate(name + " payload.token_type", payload.get("token_type"), instance_of=str)
        validate(name + " payload.exp", payload.get("exp"), instance_of=int)

        # Signature: must be non-empty and valid base64url
        validate(name + " signature length", signature_b64, min_len=1)
        decode_base64url(signature_b64)  # will raise if invalid
    
    @staticmethod
    def from_response(response_json: dict):
        access = response_json.get('access')
        Token.__validate_token("access token", access)
        refresh = response_json.get('refresh')
        Token.__validate_token("refresh token", refresh)
        return Token(access, refresh, Token.__key)


@typeguard.typechecked()
@dataclass(frozen=True)
class User:
    username: str
    matricola: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    id: int | None = None
    init_key: InitVar[object] = field(default=None)
    
    __key = object()
    
    def __post_init__(self, _init_key: object):
        validate("key", _init_key, equals=User.__key)
        validate("username", self.username, min_len=1, max_len=150)
        validate("matricola", self.matricola, min_len=1)
        if self.email is not None:
            validate("email", self.email, min_len=1)
        if self.first_name is not None:
            validate("first_name", self.first_name, min_len=0)
        if self.last_name is not None:
            validate("last_name", self.last_name, min_len=0)
    
    @staticmethod
    def from_response(response_json: dict):
        return User(
            username=response_json['username'],
            matricola=response_json['matricola'],
            email=response_json.get('email'),
            first_name=response_json.get('firstName'),
            last_name=response_json.get('lastName'),
            id=response_json.get('id'),
            init_key=User.__key
        )


@typeguard.typechecked()
@dataclass(frozen=True)
class Goal:
    title: str
    description: str
    points: int
    id: int | None = None
    init_key: InitVar[object] = field(default=None)
    
    __key = object()
    
    def __post_init__(self, _init_key: object):
        validate("key", _init_key, equals=Goal.__key)
        validate("title", self.title, min_len=1)
        validate("description", self.description, min_len=0)
        validate("points", self.points, min_value=0)
    
    @staticmethod
    def from_response(response_json: dict):
        return Goal(
            title=response_json['title'],
            description=response_json['description'],
            points=response_json['points'],
            id=response_json.get('id'),
            init_key=Goal.__key
        )


@typeguard.typechecked()
@dataclass(frozen=True)
class Topic:
    title: str
    id: int | None = None
    init_key: InitVar[object] = field(default=None)
    
    __key = object()
    
    def __post_init__(self, _init_key: object):
        validate("key", _init_key, equals=Topic.__key)
        validate("title", self.title, min_len=1)
    
    @staticmethod
    def from_response(response_json: dict):
        return Topic(
            title=response_json['title'],
            id=response_json.get('id'),
            init_key=Topic.__key
        )


@typeguard.typechecked()
@dataclass(frozen=True)
class GroupProject:
    name: str
    link_django: str
    link_tui: str
    link_gui: str
    topic: int
    id: int | None = None
    init_key: InitVar[object] = field(default=None)
    
    __key = object()
    
    def __post_init__(self, _init_key: object):
        validate("key", _init_key, equals=GroupProject.__key)
        validate("name", self.name, min_len=1)
        validate("link_django", self.link_django, min_len=0)
        validate("link_tui", self.link_tui, min_len=0)
        validate("link_gui", self.link_gui, min_len=0)
        validate("topic", self.topic, min_value=1)
    
    @staticmethod
    def from_response(response_json: dict):
        return GroupProject(
            name=response_json['name'],
            link_django=response_json['linkDjango'],
            link_tui=response_json['linkTui'],
            link_gui=response_json['linkGui'],
            topic=response_json['topic'],
            id=response_json.get('id'),
            init_key=GroupProject.__key
        )