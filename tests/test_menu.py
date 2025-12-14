from unittest.mock import patch, call, Mock

import pytest
from typeguard import TypeCheckError
from valid8 import ValidationError

from gpm_ssd.menu import Description, Key, Entry, Menu


# ==================== TEST DESCRIPTION ====================

def test_description_must_be_string():
    Description('ok')
    with pytest.raises(TypeCheckError):
        Description(0)
    with pytest.raises(TypeCheckError):
        Description(None)


def test_description_must_be_non_empty_string():
    Description('correct')
    with pytest.raises(ValidationError):
        Description('')


def test_description_must_not_exceed_1000_chars():
    Description('a' * 1000)
    with pytest.raises(ValidationError):
        Description('a' * 1001)


def test_description_must_not_contain_special_chars():
    for special_char in ['\n', '\r', '*', '^', '$', '@']:
        with pytest.raises(ValidationError):
            Description(special_char)


def test_str_description():
    desc = Description('Test menu')
    assert str(desc) == 'Test menu'


# ==================== TEST KEY ====================

def test_key_cannot_be_empty():
    with pytest.raises(ValidationError):
        Key('')


def test_key_cannot_exceed_10_chars():
    with pytest.raises(ValidationError):
        Key('a' * 11)


def test_key_cannot_contain_special_chars():
    for special_char in ['\n', '\r', '*', '^', '$', '@', ' ']:
        with pytest.raises(ValidationError):
            Key(special_char)


def test_str_key():
    key = Key('1')
    assert str(key) == '1'


# ==================== TEST ENTRY ====================

def test_entry_on_selected():
    mocked_on_selected = Mock()
    entry = Entry(Key('1'), Description('Say hi'), on_selected=lambda: mocked_on_selected())
    entry.on_selected()
    mocked_on_selected.assert_called_once()


@patch('builtins.print')
def test_entry_on_selected_print_something(mocked_print):
    entry = Entry(Key('1'), Description('Say hi'), on_selected=lambda: print('hi'))
    entry.on_selected()
    assert mocked_print.mock_calls == [call('hi')]


def test_entry_create():
    entry = Entry.create('1', 'Test entry')
    assert entry.key.value == '1'
    assert entry.description.value == 'Test entry'
    assert entry.is_exit == False


def test_entry_create_with_exit():
    entry = Entry.create('0', 'Exit', is_exit=True)
    assert entry.is_exit == True


# ==================== TEST MENU BUILDER ====================

def test_menu_builder_cannot_create_empty_menu():
    menu_builder = Menu.Builder(Description('a description'))
    with pytest.raises(ValidationError):
        menu_builder.build()


def test_menu_builder_cannot_create_menu_without_exit():
    menu_builder = Menu.Builder(Description('a description'))
    menu_builder.with_entry(Entry.create('1', 'first entry'))
    with pytest.raises(ValidationError):
        menu_builder.build()


def test_menu_builder_can_create_menu_with_exit():
    menu_builder = Menu.Builder(Description('a description'))
    menu_builder.with_entry(Entry.create('0', 'exit', is_exit=True))
    menu = menu_builder.build()
    assert menu is not None


def test_menu_builder_cannot_call_two_times_build():
    menu_builder = Menu.Builder(Description('a description'))
    menu_builder.with_entry(Entry.create('1', 'first entry', is_exit=True))
    menu_builder.build()
    with pytest.raises(ValidationError):
        menu_builder.build()


def test_menu_does_not_contain_duplicates():
    menu_builder = Menu.Builder(Description('a description'))
    menu_builder.with_entry(Entry.create('1', 'first entry'))
    with pytest.raises(ValidationError):
        menu_builder.with_entry(Entry.create('1', 'duplicate entry'))


def test_menu_builder_with_multiple_entries():
    menu = Menu.Builder(Description('Test menu'))\
        .with_entry(Entry.create('1', 'Option 1'))\
        .with_entry(Entry.create('2', 'Option 2'))\
        .with_entry(Entry.create('3', 'Option 3'))\
        .with_entry(Entry.create('0', 'Exit', is_exit=True))\
        .build()
    assert menu is not None


# ==================== TEST MENU EXECUTION ====================

@patch('builtins.input', side_effect=['1', '0'])
@patch('builtins.print')
def test_menu_selection_call_on_selected(mocked_print, mocked_input):
    menu = Menu.Builder(Description('a description'))\
        .with_entry(Entry.create('1', 'first entry', on_selected=lambda: print('first entry selected')))\
        .with_entry(Entry.create('0', 'exit', is_exit=True))\
        .build()
    menu.run()
    mocked_print.assert_any_call('first entry selected')
    mocked_input.assert_called()


@patch('builtins.input', side_effect=['-1', '0'])
@patch('builtins.print')
def test_menu_selection_on_wrong_key(mocked_print, mocked_input):
    menu = Menu.Builder(Description('a description'))\
        .with_entry(Entry.create('1', 'first entry', on_selected=lambda: print('first entry selected')))\
        .with_entry(Entry.create('0', 'exit', is_exit=True))\
        .build()
    menu.run()
    mocked_print.assert_any_call('Invalid selection. Please, try again...')
    mocked_input.assert_called()


@patch('builtins.input', side_effect=['abc', '1', '0'])
@patch('builtins.print')
def test_menu_selection_on_invalid_input(mocked_print, mocked_input):
    menu = Menu.Builder(Description('a description'))\
        .with_entry(Entry.create('1', 'first entry', on_selected=lambda: print('selected')))\
        .with_entry(Entry.create('0', 'exit', is_exit=True))\
        .build()
    menu.run()
    mocked_print.assert_any_call('Invalid selection. Please, try again...')
    mocked_print.assert_any_call('selected')


@patch('builtins.input', side_effect=['2', '1', '0'])
@patch('builtins.print')
def test_menu_calls_multiple_actions(mocked_print, mocked_input):
    menu = Menu.Builder(Description('Test menu'))\
        .with_entry(Entry.create('1', 'Action 1', on_selected=lambda: print('Action 1 executed')))\
        .with_entry(Entry.create('2', 'Action 2', on_selected=lambda: print('Action 2 executed')))\
        .with_entry(Entry.create('0', 'Exit', is_exit=True))\
        .build()
    menu.run()
    mocked_print.assert_any_call('Action 2 executed')
    mocked_print.assert_any_call('Action 1 executed')


@patch('builtins.input', side_effect=['0'])
@patch('builtins.print')
def test_menu_auto_select_called(mocked_print, mocked_input):
    menu = Menu.Builder(Description('Test menu'), auto_select=lambda: print('Auto selected'))\
        .with_entry(Entry.create('0', 'Exit', is_exit=True))\
        .build()
    menu.run()
    mocked_print.assert_any_call('Auto selected')


@patch('builtins.input', side_effect=['1', '2', '0'])
@patch('builtins.print')
def test_menu_auto_select_called_multiple_times(mocked_print, mocked_input):
    counter = {'count': 0}
    
    def auto_select():
        counter['count'] += 1
        print(f'Called {counter["count"]} times')
    
    menu = Menu.Builder(Description('Test menu'), auto_select=auto_select)\
        .with_entry(Entry.create('1', 'Option 1'))\
        .with_entry(Entry.create('2', 'Option 2'))\
        .with_entry(Entry.create('0', 'Exit', is_exit=True))\
        .build()
    menu.run()
    
    assert counter['count'] == 3