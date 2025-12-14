import pytest
from valid8 import ValidationError

from gpm_ssd.domain import (
    GroupName, TopicTitle, GoalTitle, GoalDescription, Points, Link,
    Topic, Goal, GroupProject, GroupGoal, UserGroup, Token, GPM
)


# ==================== FIXTURES ====================

@pytest.fixture
def sample_topics():
    return [
        Topic(TopicTitle("Topic 1"), id=1),
        Topic(TopicTitle("Topic 2"), id=2),
        Topic(TopicTitle("Topic 3"), id=3),
    ]


@pytest.fixture
def sample_goals():
    return [
        Goal(GoalTitle("Goal 1"), GoalDescription("Description 1"), Points.create(5), id=1),
        Goal(GoalTitle("Goal 2"), GoalDescription("Description 2"), Points.create(3), id=2),
        Goal(GoalTitle("Goal 3"), GoalDescription("Description 3"), Points.create(4), id=3),
    ]


@pytest.fixture
def sample_groups():
    return [
        GroupProject(GroupName("Group 1"), topic_id=1, id=1),
        GroupProject(GroupName("Group 2"), topic_id=2, id=2),
        GroupProject(GroupName("Group 3"), topic_id=3, id=3),
    ]


# ==================== TEST VALUE OBJECTS ====================

def test_wrong_group_name():
    wrong_value = "Invalid\nName"
    with pytest.raises(ValidationError):
        GroupName(wrong_value)


def test_str_group_name():
    group_name = GroupName("Team Alpha")
    assert str(group_name) == "Team Alpha"


def test_wrong_topic_title():
    wrong_value = "Topic\nTitle"
    with pytest.raises(ValidationError):
        TopicTitle(wrong_value)


def test_str_topic_title():
    topic_title = TopicTitle("Machine Learning")
    assert str(topic_title) == "Machine Learning"


def test_wrong_goal_title():
    wrong_value = "Goal\nTitle"
    with pytest.raises(ValidationError):
        GoalTitle(wrong_value)


def test_str_goal_title():
    goal_title = GoalTitle("Complete Project")
    assert str(goal_title) == "Complete Project"


def test_goal_description_empty():
    description = GoalDescription("")
    assert str(description) == ""


def test_goal_description_too_long():
    with pytest.raises(ValidationError):
        GoalDescription("a" * 401)


def test_str_goal_description():
    description = GoalDescription("This is a test description")
    assert str(description) == "This is a test description"


def test_wrong_points():
    with pytest.raises(ValidationError):
        Points.create(0)
    with pytest.raises(ValidationError):
        Points.create(6)


def test_create_points_right():
    points = Points.create(3)
    assert points.value == 3


def test_parse_points_right():
    points = Points.parse("4")
    assert points.value == 4


def test_parse_points_wrong():
    with pytest.raises(ValidationError):
        Points.parse("0")
    with pytest.raises(ValidationError):
        Points.parse("6")
    with pytest.raises(ValidationError):
        Points.parse("abc")


def test_str_points():
    points = Points.create(5)
    assert str(points) == "5"


def test_link_empty():
    link = Link("")
    assert str(link) == ""


def test_link_too_long():
    with pytest.raises(ValidationError):
        Link("a" * 201)


def test_str_link():
    link = Link("https://github.com/project")
    assert str(link) == "https://github.com/project"


# ==================== TEST TOKEN ====================

def test_token_from_response():
    response = {
        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM0MTg3MjAwLCJpc19zdGFmZiI6dHJ1ZX0.fake_signature',
        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNDE4NzIwMH0.fake_signature'
    }
    token = Token.from_response(response)
    assert token.access == response['access']
    assert token.refresh == response['refresh']


def test_token_is_staff_true():
    staff_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM0MTg3MjAwLCJpc19zdGFmZiI6dHJ1ZX0.fake'
    token = Token.from_response({
        'access': staff_token,
        'refresh': staff_token
    })
    assert token.is_staff() == True


def test_token_is_staff_false():
    non_staff_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM0MTg3MjAwLCJpc19zdGFmZiI6ZmFsc2V9.fake'
    token = Token.from_response({
        'access': non_staff_token,
        'refresh': non_staff_token
    })
    assert token.is_staff() == False


# ==================== TEST ENTITIES ====================

def test_topic_to_dict():
    topic = Topic(TopicTitle("Machine Learning"))
    topic_dict = topic.to_dict()
    assert topic_dict == {
        "title": "Machine Learning"
    }


def test_topic_from_dict():
    data = {
        "id": 1,
        "title": "Web Development"
    }
    topic = Topic.from_dict(data)
    assert topic.id == 1
    assert topic.title.value == "Web Development"


def test_goal_to_dict():
    goal = Goal(
        title=GoalTitle("Complete Project"),
        description=GoalDescription("Finish the TUI"),
        points=Points.create(5)
    )
    goal_dict = goal.to_dict()
    assert goal_dict == {
        "title": "Complete Project",
        "description": "Finish the TUI",
        "points": 5
    }


def test_goal_from_dict():
    data = {
        "id": 1,
        "title": "Test Goal",
        "description": "A test description",
        "points": 3
    }
    goal = Goal.from_dict(data)
    assert goal.id == 1
    assert goal.title.value == "Test Goal"
    assert goal.description.value == "A test description"
    assert goal.points.value == 3


def test_group_project_to_dict():
    group = GroupProject(
        name=GroupName("Team Alpha"),
        topic_id=1,
        link_django=Link("https://github.com/django"),
        link_tui=Link("https://github.com/tui"),
        link_gui=Link("https://github.com/gui")
    )
    group_dict = group.to_dict()
    assert group_dict == {
        "name": "Team Alpha",
        "topic": 1,
        "link_django": "https://github.com/django",
        "link_tui": "https://github.com/tui",
        "link_gui": "https://github.com/gui"
    }


def test_group_project_from_dict():
    data = {
        "id": 1,
        "name": "Team Beta",
        "topic": 2,
        "link_django": "https://github.com/django",
        "link_tui": "",
        "link_gui": ""
    }
    group = GroupProject.from_dict(data)
    assert group.id == 1
    assert group.name.value == "Team Beta"
    assert group.topic_id == 2
    assert group.link_django.value == "https://github.com/django"


def test_group_project_with_invalid_topic_id():
    with pytest.raises(ValidationError):
        GroupProject(
            name=GroupName("Team Test"),
            topic_id=0  # invalid: min is 1
        )


def test_group_goal_to_dict():
    group_goal = GroupGoal(group_id=1, goal_id=2, complete=True)
    gg_dict = group_goal.to_dict()
    assert gg_dict == {
        "group": 1,
        "goal": 2,
        "complete": True
    }


def test_group_goal_from_dict():
    data = {
        "id": 1,
        "group": 2,
        "goal": 3,
        "complete": False
    }
    group_goal = GroupGoal.from_dict(data)
    assert group_goal.id == 1
    assert group_goal.group_id == 2
    assert group_goal.goal_id == 3
    assert group_goal.complete == False


def test_user_group_to_dict():
    user_group = UserGroup(user_id=1, group_id=2)
    ug_dict = user_group.to_dict()
    assert ug_dict == {
        "user": 1,
        "group": 2
    }


def test_user_group_from_dict():
    data = {
        "id": 1,
        "user": 5,
        "group": 10
    }
    user_group = UserGroup.from_dict(data)
    assert user_group.id == 1
    assert user_group.user_id == 5
    assert user_group.group_id == 10


# ==================== TEST GPM AGGREGATE ====================

def test_number_of_groups(sample_groups):
    gpm = GPM()
    size = 0
    for g in sample_groups:
        gpm.add_group(g)
        size += 1
        assert gpm.number_of_groups == size
        assert gpm.group_at_index(size - 1) == g


def test_remove_group_from_gpm(sample_groups):
    gpm = GPM()
    for g in sample_groups:
        gpm.add_group(g)
    
    gpm.remove_group(0)
    assert gpm.group_at_index(0) == sample_groups[1]
    
    with pytest.raises(ValidationError):
        gpm.remove_group(-1)
    with pytest.raises(ValidationError):
        gpm.remove_group(gpm.number_of_groups)


def test_clear_groups(sample_groups):
    gpm = GPM()
    for g in sample_groups:
        gpm.add_group(g)
    
    gpm.clear_groups()
    assert gpm.number_of_groups == 0


def test_sort_groups_by_name(sample_groups):
    gpm = GPM()
    for g in reversed(sample_groups):
        gpm.add_group(g)
    
    gpm.sort_groups_by_name()
    assert gpm.group_at_index(0).name.value == "Group 1"
    assert gpm.group_at_index(gpm.number_of_groups - 1).name.value == "Group 3"


def test_number_of_goals(sample_goals):
    gpm = GPM()
    size = 0
    for g in sample_goals:
        gpm.add_goal(g)
        size += 1
        assert gpm.number_of_goals == size
        assert gpm.goal_at_index(size - 1) == g


def test_remove_goal_from_gpm(sample_goals):
    gpm = GPM()
    for g in sample_goals:
        gpm.add_goal(g)
    
    gpm.remove_goal(0)
    assert gpm.goal_at_index(0) == sample_goals[1]
    
    with pytest.raises(ValidationError):
        gpm.remove_goal(-1)
    with pytest.raises(ValidationError):
        gpm.remove_goal(gpm.number_of_goals)


def test_clear_goals(sample_goals):
    gpm = GPM()
    for g in sample_goals:
        gpm.add_goal(g)
    
    gpm.clear_goals()
    assert gpm.number_of_goals == 0


def test_sort_goals_by_points(sample_goals):
    gpm = GPM()
    for g in sample_goals:
        gpm.add_goal(g)
    
    gpm.sort_goals_by_points()
    assert gpm.goal_at_index(0).points.value == 5
    assert gpm.goal_at_index(1).points.value == 4
    assert gpm.goal_at_index(2).points.value == 3


def test_number_of_topics(sample_topics):
    gpm = GPM()
    size = 0
    for t in sample_topics:
        gpm.add_topic(t)
        size += 1
        assert gpm.number_of_topics == size
        assert gpm.topic_at_index(size - 1) == t


def test_remove_topic_from_gpm(sample_topics):
    gpm = GPM()
    for t in sample_topics:
        gpm.add_topic(t)
    
    gpm.remove_topic(0)
    assert gpm.topic_at_index(0) == sample_topics[1]
    
    with pytest.raises(ValidationError):
        gpm.remove_topic(-1)
    with pytest.raises(ValidationError):
        gpm.remove_topic(gpm.number_of_topics)


def test_clear_topics(sample_topics):
    gpm = GPM()
    for t in sample_topics:
        gpm.add_topic(t)
    
    gpm.clear_topics()
    assert gpm.number_of_topics == 0


def test_sort_topics_by_title(sample_topics):
    gpm = GPM()
    for t in reversed(sample_topics):
        gpm.add_topic(t)
    
    gpm.sort_topics_by_title()
    assert gpm.topic_at_index(0).title.value == "Topic 1"
    assert gpm.topic_at_index(gpm.number_of_topics - 1).title.value == "Topic 3"


def test_group_goals():
    gpm = GPM()
    gg1 = GroupGoal(group_id=1, goal_id=1, complete=False, id=1)
    gg2 = GroupGoal(group_id=1, goal_id=2, complete=True, id=2)
    
    gpm.add_group_goal(gg1)
    gpm.add_group_goal(gg2)
    
    assert gpm.number_of_group_goals() == 2
    assert gpm.group_goal_at_index(0) == gg1
    assert gpm.group_goal_at_index(1) == gg2


def test_remove_group_goal():
    gpm = GPM()
    gg1 = GroupGoal(group_id=1, goal_id=1, id=1)
    gg2 = GroupGoal(group_id=1, goal_id=2, id=2)
    
    gpm.add_group_goal(gg1)
    gpm.add_group_goal(gg2)
    
    gpm.remove_group_goal(0)
    assert gpm.number_of_group_goals() == 1
    assert gpm.group_goal_at_index(0) == gg2


def test_clear_group_goals():
    gpm = GPM()
    gpm.add_group_goal(GroupGoal(group_id=1, goal_id=1, id=1))
    gpm.add_group_goal(GroupGoal(group_id=1, goal_id=2, id=2))
    
    gpm.clear_group_goals()
    assert gpm.number_of_group_goals() == 0


def test_clear_all():
    gpm = GPM()
    gpm.add_group(GroupProject(GroupName("Test"), topic_id=1, id=1))
    gpm.add_goal(Goal(GoalTitle("Test"), GoalDescription(""), Points.create(1), id=1))
    gpm.add_topic(Topic(TopicTitle("Test"), id=1))
    gpm.add_group_goal(GroupGoal(group_id=1, goal_id=1, id=1))
    
    gpm.clear_all()
    assert gpm.number_of_groups == 0
    assert gpm.number_of_goals == 0
    assert gpm.number_of_topics == 0
    assert gpm.number_of_group_goals() == 0