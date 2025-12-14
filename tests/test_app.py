from unittest.mock import patch, MagicMock

import pytest

from gpm_ssd.__main__ import main
from gpm_ssd.app import App
from gpm_ssd.domain import Goal, GoalTitle, GoalDescription, Points, Topic, TopicTitle, GroupProject, GroupName


# ==================== FIXTURES ====================

@pytest.fixture
def sample_goals():
    return [
        Goal(GoalTitle("Goal 1"), GoalDescription("Description 1"), Points.create(5), id=1),
        Goal(GoalTitle("Goal 2"), GoalDescription("Description 2"), Points.create(3), id=2),
        Goal(GoalTitle("Goal 3"), GoalDescription("Description 3"), Points.create(4), id=3),
    ]


@pytest.fixture
def sample_topics():
    return [
        Topic(TopicTitle("Topic 1"), id=1),
        Topic(TopicTitle("Topic 2"), id=2),
    ]


@pytest.fixture
def sample_groups():
    return [
        GroupProject(GroupName("Group 1"), topic_id=1, id=1),
        GroupProject(GroupName("Group 2"), topic_id=2, id=2),
    ]


# ==================== TEST MAIN ====================

@patch('builtins.input', side_effect=['0'])
@patch('builtins.print')
def test_app_main(mocked_print, mocked_input):
    main('__main__')
    mocked_print.assert_any_call('Bye!')
    mocked_input.assert_called()


# ==================== TEST LOGIN ====================

@patch('gpm_ssd.managers.auth_handler.getpass', return_value='test_password')
@patch('requests.Session')
@patch('builtins.input', side_effect=['1', 'test_user', '0'])
def test_login_success(mocked_input, mocked_session_class, mocked_pass):
    mock_session = MagicMock()
    mocked_session_class.return_value = mock_session
    
    mock_session.post.return_value.status_code = 200
    mock_session.post.return_value.json.return_value = {
        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM0MTg3MjAwfQ.fake',
        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNDE4NzIwMH0.fake'
    }
    mock_session.get.return_value.status_code = 200
    mock_session.get.return_value.json.return_value = []

    app = App()
    app.run()

    mocked_input.assert_called()
    mocked_pass.assert_called_once_with('Password: ')

    private_token = getattr(app, '_App__auth').token
    assert mock_session.post.call_count >= 1
    assert private_token is not None


@patch('gpm_ssd.managers.auth_handler.getpass', return_value='wrong_password')
@patch('requests.Session')
@patch('builtins.input', side_effect=['1', 'wrong_user'])
def test_login_failure(mocked_input, mocked_session_class, mocked_pass):
    mock_session = MagicMock()
    mocked_session_class.return_value = mock_session
    
    mock_session.post.return_value.status_code = 401
    mock_session.post.return_value.json.return_value = {'detail': 'Invalid credentials'}

    app = App()
    app.run()
    
    private_token = getattr(app, '_App__auth').token
    assert private_token is None


# ==================== TEST LOGOUT ====================

@patch('builtins.input', side_effect=['6'])
def test_logout_success(mocked_input):
    app = App()
    mock_session = MagicMock()
    mock_session.post.return_value.status_code = 200
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.access = 'test_token'
    app._App__auth.session = mock_session
    
    app.run()

    mock_session.post.assert_called_once_with(
        f"{app._App__base_url}auth/logout/",
        headers={"Authorization": "Bearer test_token"}
    )


@patch('builtins.input', side_effect=['6'])
def test_logout_failure(mocked_input):
    app = App()
    mock_session = MagicMock()
    mock_session.post.return_value.status_code = 401
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.access = 'test_token'
    app._App__auth.session = mock_session
    
    app.run()

    mock_session.post.assert_called_once_with(
        f"{app._App__base_url}auth/logout/",
        headers={"Authorization": "Bearer test_token"}
    )


# ==================== TEST ADD GOAL ====================

@patch('builtins.print')
@patch('builtins.input', side_effect=['3', '1', 'Test Goal', 'Test Description', '5', '0', '0'])
def test_add_goal(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.post.return_value.status_code = 201
    mock_session.post.return_value.json.return_value = {
        'id': 1,
        'title': 'Test Goal',
        'description': 'Test Description',
        'points': 5
    }
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.token.access = 'test_token'
    app._App__auth.session = mock_session
    
    app.run()

    mocked_print.assert_any_call('Goal added!')
    mocked_input.assert_called()


@patch('builtins.print')
@patch('builtins.input', side_effect=['3', '1', 'Invalid\nGoal', 'Valid Goal', 'Description', '3', '0', '0'])
def test_add_goal_resists_to_wrong_title(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.post.return_value.status_code = 201
    mock_session.post.return_value.json.return_value = {
        'id': 1,
        'title': 'Valid Goal',
        'description': 'Description',
        'points': 3
    }
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.session = mock_session
    
    app.run()

    mocked_print.assert_any_call('Goal added!')
    mocked_input.assert_called()


# ==================== TEST REMOVE GOAL ====================

@patch('builtins.print')
@patch('builtins.input', side_effect=['3', '1', 'Goal To Remove', 'Description', '4', '3', '2', '1', '0', '0'])
def test_remove_goal(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.post.return_value.status_code = 201
    mock_session.post.return_value.json.return_value = {
        'id': 1,
        'title': 'Goal To Remove',
        'description': 'Description',
        'points': 4
    }
    mock_session.delete.return_value.status_code = 204
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.session = mock_session
    
    app.run()

    mocked_input.assert_called()
    mocked_print.assert_any_call('Goal removed!')


@patch('builtins.input', side_effect=['3', '2', '0', '0', '0'])
@patch('builtins.print')
def test_remove_goal_can_be_cancelled(mocked_print, mocked_input):
    app = App()
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.session = MagicMock()
    
    app.run()

    mocked_input.assert_called()
    mocked_print.assert_any_call('Cancelled!')


# ==================== TEST SORT GOALS ====================

@patch('builtins.input', side_effect=['3', '3', '0'])
@patch('builtins.print')
def test_sort_goals_by_points(mocked_print, mocked_input, sample_goals):
    app = App()
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True

    for goal in sample_goals:
        app._App__gpm.add_goal(goal)

    app.run()

    mocked_input.assert_called()
    mocked_print.assert_any_call('Goals sorted by points!')


# ==================== TEST ADD TOPIC ====================

@patch('builtins.print')
@patch('builtins.input', side_effect=['4', '1', 'Test Topic', '0', '0'])
def test_add_topic(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.post.return_value.status_code = 201
    mock_session.post.return_value.json.return_value = {
        'id': 1,
        'title': 'Test Topic'
    }
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.session = mock_session
    
    app.run()

    mocked_print.assert_any_call('Topic added!')
    mocked_input.assert_called()


@patch('builtins.print')
@patch('builtins.input', side_effect=['4', '1', 'Invalid\nTopic', 'Valid Topic', '0', '0'])
def test_add_topic_resists_to_wrong_title(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.post.return_value.status_code = 201
    mock_session.post.return_value.json.return_value = {
        'id': 1,
        'title': 'Valid Topic'
    }
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.session = mock_session
    
    app.run()

    mocked_print.assert_any_call('Topic added!')
    mocked_input.assert_called()


# ==================== TEST REMOVE TOPIC ====================

@patch('builtins.print')
@patch('builtins.input', side_effect=['4', '1', 'Topic To Remove', '4', '2', '1', '0', '0'])
def test_remove_topic(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.post.return_value.status_code = 201
    mock_session.post.return_value.json.return_value = {
        'id': 1,
        'title': 'Topic To Remove'
    }
    mock_session.delete.return_value.status_code = 204
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.session = mock_session
    
    app.run()

    mocked_input.assert_called()
    mocked_print.assert_any_call('Topic removed!')


@patch('builtins.input', side_effect=['4', '2', '0', '0', '0'])
@patch('builtins.print')
def test_remove_topic_can_be_cancelled(mocked_print, mocked_input):
    app = App()
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.session = MagicMock()
    
    app.run()

    mocked_input.assert_called()
    mocked_print.assert_any_call('Cancelled!')


# ==================== TEST SORT TOPICS ====================

@patch('builtins.input', side_effect=['4', '3', '0'])
@patch('builtins.print')
def test_sort_topics_by_title(mocked_print, mocked_input, sample_topics):
    app = App()
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True

    for topic in reversed(sample_topics):
        app._App__gpm.add_topic(topic)

    app.run()

    mocked_input.assert_called()
    mocked_print.assert_any_call('Topics sorted by title!')


# ==================== TEST ADD GROUP ====================

@patch('builtins.print')
@patch('builtins.input', side_effect=['2', '1', 'Test Group', '1', '', '', '', '0', '0'])
def test_add_group(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.post.return_value.status_code = 201
    mock_session.post.return_value.json.return_value = {
        'id': 1,
        'name': 'Test Group',
        'topic': 1,
        'link_django': '',
        'link_tui': '',
        'link_gui': ''
    }
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.session = mock_session
    
    app.run()

    mocked_print.assert_any_call('Group added!')
    mocked_input.assert_called()


@patch('builtins.print')
@patch('builtins.input', side_effect=['2', '1', 'Invalid\nGroup', 'Valid Group', '1', '', '', '', '0', '0'])
def test_add_group_resists_to_wrong_name(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.post.return_value.status_code = 201
    mock_session.post.return_value.json.return_value = {
        'id': 1,
        'name': 'Valid Group',
        'topic': 1,
        'link_django': '',
        'link_tui': '',
        'link_gui': ''
    }
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.session = mock_session
    
    app.run()

    mocked_print.assert_any_call('Group added!')
    mocked_input.assert_called()


# ==================== TEST JOIN/LEAVE GROUP ====================

@patch('builtins.print')
@patch('builtins.input', side_effect=['2', '2', '1', '0', '0'])
def test_join_group(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.post.return_value.status_code = 200
    
    app._App__auth.token = MagicMock()
    app._App__auth.session = mock_session
    
    app._App__gpm.add_group(GroupProject(GroupName("Test Group"), topic_id=1, id=1))
    app._App__data_loader.index_to_id_groups[0] = 1
    
    app.run()

    mocked_print.assert_any_call('Joined group successfully!')
    mocked_input.assert_called()


@patch('builtins.print')
@patch('builtins.input', side_effect=['2', '3', '1', '0', '0'])
def test_leave_group(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.delete.return_value.status_code = 204
    
    app._App__auth.token = MagicMock()
    app._App__auth.session = mock_session
    
    app._App__gpm.add_group(GroupProject(GroupName("Test Group"), topic_id=1, id=1))
    app._App__data_loader.index_to_id_groups[0] = 1
    
    app.run()

    mocked_print.assert_any_call('Left group successfully!')
    mocked_input.assert_called()


# ==================== TEST REMOVE GROUP ====================

@patch('builtins.print')
@patch('builtins.input', side_effect=['2', '1', 'Group To Remove', '1', '', '', '', '4', '1', '0', '0'])
def test_remove_group(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.post.return_value.status_code = 201
    mock_session.post.return_value.json.return_value = {
        'id': 1,
        'name': 'Group To Remove',
        'topic': 1,
        'link_django': '',
        'link_tui': '',
        'link_gui': ''
    }
    mock_session.delete.return_value.status_code = 204
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.session = mock_session
    
    app.run()

    mocked_input.assert_called()
    mocked_print.assert_any_call('Group removed!')


# ==================== TEST GROUP GOALS ====================

@patch('builtins.print')
@patch('builtins.input', side_effect=['5', '1', '1', '1', '0', '0'])
def test_add_group_goal(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.post.return_value.status_code = 201
    mock_session.post.return_value.json.return_value = {
        'id': 1,
        'group': 1,
        'goal': 1,
        'complete': False
    }
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.session = mock_session
    
    app.run()

    mocked_print.assert_any_call('Group Goal added!')
    mocked_input.assert_called()


@patch('builtins.print')
@patch('builtins.input', side_effect=['5', '1', 'invalid', '1', '1', '0', '0'])
def test_add_group_goal_resists_to_wrong_input(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.post.return_value.status_code = 201
    mock_session.post.return_value.json.return_value = {
        'id': 1,
        'group': 1,
        'goal': 1,
        'complete': False
    }
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.session = mock_session
    
    app.run()

    mocked_print.assert_any_call('Group Goal added!')


@patch('builtins.print')
@patch('builtins.input', side_effect=['5', '2', '1', '0', '0'])
def test_remove_group_goal(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.delete.return_value.status_code = 204
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.session = mock_session
    
    from gpm_ssd.domain import GroupGoal
    app._App__gpm.add_group_goal(GroupGoal(group_id=1, goal_id=1, complete=False, id=1))
    app._App__data_loader.index_to_id_group_goals[0] = 1
    
    app.run()

    mocked_print.assert_any_call('Group Goal removed!')
    mocked_input.assert_called()


@patch('builtins.print')
@patch('builtins.input', side_effect=['5', '3', '1', '0', '0'])
def test_toggle_group_goal(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.patch.return_value.status_code = 200
    mock_session.patch.return_value.json.return_value = {
        'id': 1,
        'group': 1,
        'goal': 1,
        'complete': True
    }
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.session = mock_session
    
    from gpm_ssd.domain import GroupGoal
    app._App__gpm.add_group_goal(GroupGoal(group_id=1, goal_id=1, complete=False, id=1))
    app._App__data_loader.index_to_id_group_goals[0] = 1
    
    app.run()

    mocked_print.assert_any_call('Group Goal toggled!')
    mocked_input.assert_called()


@patch('builtins.print')
@patch('builtins.input', side_effect=['5', '1', '1', '1', '0', '0'])
def test_add_duplicate_group_goal(mocked_input, mocked_print):
    app = App()
    mock_session = MagicMock()
    mock_session.post.return_value.status_code = 201
    mock_session.post.return_value.json.return_value = {
        'non_field_errors': ['The fields group, goal must make a unique set.']
    }
    
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True
    app._App__auth.session = mock_session
    
    app.run()

    mocked_input.assert_called()


# ==================== TEST SORT GROUPS ====================

@patch('builtins.input', side_effect=['2', '5', '0'])
@patch('builtins.print')
def test_sort_groups_by_name(mocked_print, mocked_input, sample_groups):
    app = App()
    app._App__auth.token = MagicMock()
    app._App__auth.token.is_staff.return_value = True

    for group in reversed(sample_groups):
        app._App__gpm.add_group(group)

    app.run()

    mocked_input.assert_called()
    mocked_print.assert_any_call('Groups sorted by name!')


# ==================== TEST LOAD DATA ====================

@patch('gpm_ssd.managers.auth_handler.getpass', return_value='test_password')
@patch('requests.Session')
@patch('builtins.input', side_effect=['1', 'test_user'])
def test_load_data_successfully(mocked_input, mocked_session_class, mocked_pass):
    mock_session = MagicMock()
    mocked_session_class.return_value = mock_session
    
    mock_session.post.return_value.status_code = 200
    mock_session.post.return_value.json.return_value = {
        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM0MTg3MjAwfQ.fake',
        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNDE4NzIwMH0.fake'
    }
    
    def get_side_effect(url, **kwargs):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        
        if 'auth/user' in url:
            mock_resp.json.return_value = {'pk': 1}
        elif 'goals' in url:
            mock_resp.json.return_value = [
                {'id': 1, 'title': 'Goal 1', 'description': 'Desc 1', 'points': 5},
                {'id': 2, 'title': 'Goal 2', 'description': 'Desc 2', 'points': 3}
            ]
        elif 'topics' in url:
            mock_resp.json.return_value = [
                {'id': 1, 'title': 'Topic 1'},
                {'id': 2, 'title': 'Topic 2'}
            ]
        elif 'groups/' in url and 'group-' not in url:
            mock_resp.json.return_value = [
                {'id': 1, 'name': 'Group 1', 'topic': 1, 'link_django': '', 'link_tui': '', 'link_gui': ''}
            ]
        else:
            mock_resp.json.return_value = []
        
        return mock_resp
    
    mock_session.get.side_effect = get_side_effect

    app = App()
    app.run()

    assert app._App__gpm.number_of_goals == 2
    assert app._App__gpm.number_of_topics == 2
    assert app._App__gpm.number_of_groups == 1


# ==================== TEST AUTHENTICATION REQUIRED ====================

@patch('builtins.input', side_effect=['2', '0'])
@patch('builtins.print')
def test_manage_groups_requires_login(mocked_print, mocked_input):
    app = App()
    app.run()
    
    mocked_print.assert_any_call('You must login first')


@patch('builtins.input', side_effect=['3', '0'])
@patch('builtins.print')
def test_manage_goals_requires_login(mocked_print, mocked_input):
    app = App()
    app.run()
    
    mocked_print.assert_any_call('You must login first')


@patch('builtins.input', side_effect=['4', '0'])
@patch('builtins.print')
def test_manage_topics_requires_login(mocked_print, mocked_input):
    app = App()
    app.run()
    
    mocked_print.assert_any_call('You must login first')


@patch('builtins.input', side_effect=['5', '0'])
@patch('builtins.print')
def test_manage_group_goals_requires_login(mocked_print, mocked_input):
    app = App()
    app.run()
    
    mocked_print.assert_any_call('You must login first')