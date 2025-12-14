import re
import json
import base64
from dataclasses import dataclass, InitVar, field
from typing import Any

from valid8 import validate

from validation.dataclasses import validate_dataclass
from validation.regex import pattern


def decode_base64url(part: str) -> bytes:
    padding = "=" * (-len(part) % 4)
    try:
        return base64.urlsafe_b64decode(part + padding)
    except Exception:
        raise ValueError(f"Invalid base64 encoding")


def decode_jwt_payload(token: str) -> dict:
    payload_b64 = token.split(".")[1]
    payload_bytes = decode_base64url(payload_b64)
    return json.loads(payload_bytes)


@dataclass(frozen=True)
class Token:
    access: str
    refresh: str
    create_key: InitVar[Any] = field(default=None)
    
    __create_key = object()
    
    def __post_init__(self, create_key: Any):
        validate("create_key", create_key, equals=Token.__create_key)
        validate_dataclass(self)
        Token.__validate_token("access token", self.access)
        Token.__validate_token("refresh token", self.refresh)
    
    @staticmethod
    def __validate_token(name: str, token: str):
        validate(name, token, instance_of=str)
        token_parts = token.split(".")
        validate(name + " parts", token_parts, length=3)

        header_b64, payload_b64, signature_b64 = token_parts

        header_bytes = decode_base64url(header_b64)
        try:
            header = json.loads(header_bytes)
        except Exception:
            raise ValueError(f"{name} header is not valid JSON")

        validate(name + " header", header, instance_of=dict)
        validate(name + " header.alg", header.get("alg"), instance_of=str)
        validate(name + " header.typ", header.get("typ"), instance_of=str)

        payload_bytes = decode_base64url(payload_b64)
        try:
            payload = json.loads(payload_bytes)
        except Exception:
            raise ValueError(f"{name} payload is not valid JSON")

        validate(name + " payload", payload, instance_of=dict)
        validate(name + " payload.token_type", payload.get("token_type"), instance_of=str)
        validate(name + " payload.exp", payload.get("exp"), instance_of=int)

        validate(name + " signature length", signature_b64, min_len=1)
        decode_base64url(signature_b64)  
    
    def is_staff(self) -> bool:
        try:
            payload_b64 = self.access.split(".")[1]
            padding = "=" * (-len(payload_b64) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
            payload = json.loads(payload_bytes)
            return payload.get("is_staff", False)
        except Exception:
            return False
    
    @staticmethod
    def from_response(response_json: dict) -> 'Token':
        access = response_json.get('access')
        refresh = response_json.get('refresh')
        return Token(access, refresh, Token.__create_key)


@dataclass(frozen=True, order=True)
class GroupName:
    value: str

    def __post_init__(self):
        validate_dataclass(self)
        validate('value', self.value, min_len=1, max_len=100, custom=pattern(r'^[\x20-\x7E]*$'))

    def __str__(self):
        return self.value


@dataclass(frozen=True, order=True)
class TopicTitle:
    value: str

    def __post_init__(self):
        validate_dataclass(self)
        validate('value', self.value, min_len=1, max_len=100, custom=pattern(r'^[\x20-\x7E]*$'))

    def __str__(self):
        return self.value


@dataclass(frozen=True, order=True)
class GoalTitle:
    value: str

    def __post_init__(self):
        validate_dataclass(self)
        validate('value', self.value, min_len=1, max_len=100, custom=pattern(r'^[\x20-\x7E]*$'))

    def __str__(self):
        return self.value


@dataclass(frozen=True, order=True)
class GoalDescription:
    value: str

    def __post_init__(self):
        validate_dataclass(self)
        validate('value', self.value, min_len=0, max_len=400)

    def __str__(self):
        return self.value


@dataclass(frozen=True, order=True)
class Points:
    value: int
    create_key: InitVar[Any] = field(default=None)

    __create_key = object()

    def __post_init__(self, create_key):
        validate('create_key', create_key, equals=self.__create_key)
        validate_dataclass(self)
        validate('value', self.value, min_value=1, max_value=5)

    def __str__(self):
        return str(self.value)

    @staticmethod
    def create(points: int) -> 'Points':
        return Points(points, Points.__create_key)

    @staticmethod
    def parse(value: str) -> 'Points':
        validate('value', value, custom=pattern(r'[1-5]'))
        return Points.create(int(value))


@dataclass(frozen=True, order=True)
class Link:
    value: str

    def __post_init__(self):
        validate_dataclass(self)
        validate('value', self.value, min_len=0, max_len=200)

    def __str__(self):
        return self.value


@dataclass(frozen=True, order=True)
class Topic:
    title: TopicTitle
    id: int | None = None

    def __post_init__(self):
        validate_dataclass(self)
        if self.id is not None:
            validate('id', self.id, min_value=1)

    def to_dict(self):
        return {
            "title": self.title.value
        }

    @staticmethod
    def from_dict(data: dict) -> 'Topic':
        return Topic(
            title=TopicTitle(data['title']),
            id=data.get('id')
        )


@dataclass(frozen=True, order=True)
class Goal:
    title: GoalTitle
    description: GoalDescription
    points: Points
    id: int | None = None

    def __post_init__(self):
        validate_dataclass(self)
        if self.id is not None:
            validate('id', self.id, min_value=1)

    def to_dict(self):
        return {
            "title": self.title.value,
            "description": self.description.value,
            "points": self.points.value
        }

    @staticmethod
    def from_dict(data: dict) -> 'Goal':
        return Goal(
            title=GoalTitle(data['title']),
            description=GoalDescription(data['description']),
            points=Points.create(data['points']),
            id=data.get('id')
        )


@dataclass(frozen=True, order=True)
class GroupProject:
    name: GroupName
    topic_id: int
    link_django: Link = field(default_factory=lambda: Link(""))
    link_tui: Link = field(default_factory=lambda: Link(""))
    link_gui: Link = field(default_factory=lambda: Link(""))
    id: int | None = None

    def __post_init__(self):
        validate_dataclass(self)
        validate('topic_id', self.topic_id, min_value=1)
        if self.id is not None:
            validate('id', self.id, min_value=1)

    def to_dict(self):
        return {
            "name": self.name.value,
            "topic": self.topic_id,
            "link_django": self.link_django.value,
            "link_tui": self.link_tui.value,
            "link_gui": self.link_gui.value
        }

    @staticmethod
    def from_dict(data: dict) -> 'GroupProject':
        return GroupProject(
            name=GroupName(data['name']),
            topic_id=data['topic'],
            link_django=Link(data.get('link_django', '')),
            link_tui=Link(data.get('link_tui', '')),
            link_gui=Link(data.get('link_gui', '')),
            id=data.get('id')
        )


@dataclass(frozen=True, order=True)
class GroupGoal:
    group_id: int
    goal_id: int
    complete: bool = False
    id: int | None = None

    def __post_init__(self):
        validate_dataclass(self)
        validate('group_id', self.group_id, min_value=1)
        validate('goal_id', self.goal_id, min_value=1)
        if self.id is not None:
            validate('id', self.id, min_value=1)

    def to_dict(self):
        return {
            "group": self.group_id,
            "goal": self.goal_id,
            "complete": self.complete
        }

    @staticmethod
    def from_dict(data: dict) -> 'GroupGoal':
        return GroupGoal(
            group_id=data['group'],
            goal_id=data['goal'],
            complete=data.get('complete', False),
            id=data.get('id')
        )


@dataclass(frozen=True, order=True)
class UserGroup:
    user_id: int
    group_id: int
    id: int | None = None

    def __post_init__(self):
        validate_dataclass(self)
        validate('user_id', self.user_id, min_value=1)
        validate('group_id', self.group_id, min_value=1)
        if self.id is not None:
            validate('id', self.id, min_value=1)

    def to_dict(self):
        return {
            "user": self.user_id,
            "group": self.group_id
        }

    @staticmethod
    def from_dict(data: dict) -> 'UserGroup':
        return UserGroup(
            user_id=data['user'],
            group_id=data['group'],
            id=data.get('id')
        )


@dataclass(frozen=True, order=True)
class GPM:
    __groups: list[GroupProject] = field(default_factory=list, init=False)
    __goals: list[Goal] = field(default_factory=list, init=False)
    __topics: list[Topic] = field(default_factory=list, init=False)
    __group_goals: list[GroupGoal] = field(default_factory=list, init=False)
    
    @property
    def number_of_groups(self) -> int:
        return len(self.__groups)

    def group_at_index(self, index: int) -> GroupProject:
        validate('index', index, min_value=0, max_value=len(self.__groups) - 1)
        return self.__groups[index]

    def add_group(self, group: GroupProject) -> None:
        self.__groups.append(group)

    def remove_group(self, index: int) -> None:
        validate('index', index, min_value=0, max_value=self.number_of_groups - 1)
        self.__groups.pop(index)

    def clear_groups(self) -> None:
        self.__groups.clear()

    def sort_groups_by_name(self) -> None:
        self.__groups.sort(key=lambda g: g.name)
    
    @property
    def number_of_goals(self) -> int:
        return len(self.__goals)

    def goal_at_index(self, index: int) -> Goal:
        validate('index', index, min_value=0, max_value=len(self.__goals) - 1)
        return self.__goals[index]

    def add_goal(self, goal: Goal) -> None:
        self.__goals.append(goal)

    def remove_goal(self, index: int) -> None:
        validate('index', index, min_value=0, max_value=self.number_of_goals - 1)
        self.__goals.pop(index)

    def clear_goals(self) -> None:
        self.__goals.clear()

    def sort_goals_by_points(self) -> None:
        self.__goals.sort(key=lambda g: g.points, reverse=True)
    
    @property
    def number_of_topics(self) -> int:
        return len(self.__topics)

    def topic_at_index(self, index: int) -> Topic:
        validate('index', index, min_value=0, max_value=len(self.__topics) - 1)
        return self.__topics[index]

    def add_topic(self, topic: Topic) -> None:
        self.__topics.append(topic)

    def remove_topic(self, index: int) -> None:
        validate('index', index, min_value=0, max_value=self.number_of_topics - 1)
        self.__topics.pop(index)

    def clear_topics(self) -> None:
        self.__topics.clear()

    def sort_topics_by_title(self) -> None:
        self.__topics.sort(key=lambda t: t.title)

    # ==================== GROUP GOALS ====================
    def number_of_group_goals(self) -> int:
        return len(self.__group_goals)

    def group_goal_at_index(self, index: int) -> GroupGoal:
        validate('index', index, min_value=0, max_value=len(self.__group_goals) - 1)
        return self.__group_goals[index]

    def add_group_goal(self, group_goal: GroupGoal) -> None:
        self.__group_goals.append(group_goal)

    def remove_group_goal(self, index: int) -> None:
        validate('index', index, min_value=0, max_value=self.number_of_group_goals() - 1)
        self.__group_goals.pop(index)

    def clear_group_goals(self) -> None:
        self.__group_goals.clear()

    def clear_all(self) -> None:
        self.clear_groups()
        self.clear_goals()
        self.clear_topics()
        self.clear_group_goals()
