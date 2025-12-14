import sys
import traceback

from gpm_ssd.domain import GPM
from gpm_ssd.menu import Menu, Entry, Description
from gpm_ssd.managers import (
    AuthHandler,
    DataLoader,
    GroupsManager,
    GoalsManager,
    TopicsManager,
    GroupGoalsManager
)


class App:
    __base_url = 'http://localhost:8000/api/v1/'

    def __init__(self):
        self.__gpm = GPM()
        self.__auth = AuthHandler(self.__base_url)
        self.__data_loader = DataLoader(self.__base_url, self.__gpm)
        self.__groups_mgr = GroupsManager(self.__base_url, self.__gpm, self.__data_loader)
        self.__goals_mgr = GoalsManager(self.__base_url, self.__gpm, self.__data_loader)
        self.__topics_mgr = TopicsManager(self.__base_url, self.__gpm, self.__data_loader)
        self.__group_goals_mgr = GroupGoalsManager(self.__base_url, self.__gpm, self.__data_loader)

        self.__menu = Menu.Builder(Description('Group Project Manager'), auto_select=lambda: self.__print_main_view()) \
            .with_entry(Entry.create('1', 'Login', on_selected=lambda: self.__login())) \
            .with_entry(Entry.create('2', 'Manage Groups', on_selected=lambda: self.__manage_groups())) \
            .with_entry(Entry.create('3', 'Manage Goals', on_selected=lambda: self.__manage_goals())) \
            .with_entry(Entry.create('4', 'Manage Topics', on_selected=lambda: self.__manage_topics())) \
            .with_entry(Entry.create('5', 'Manage Group Goals', on_selected=lambda: self.__manage_group_goals())) \
            .with_entry(Entry.create('6', 'Logout', on_selected=lambda: self.__logout())) \
            .with_entry(Entry.create('0', 'Exit', on_selected=lambda: print('Bye!'), is_exit=True)) \
            .build()

    def __login(self) -> None:
        self.__auth.login(self.__load_data)

    def __logout(self) -> None:
        self.__auth.logout(self.__data_loader.clear_all)

    def __load_data(self) -> None:
        self.__auth.user_id = self.__data_loader.load_all_data(
            self.__auth.session, 
            self.__auth.get_headers()
        )

    def __print_main_view(self) -> None:
        if self.__auth.is_authenticated():
            print(f"\n{'='*80}")
            print(f"Groups: {self.__gpm.number_of_groups} | Goals: {self.__gpm.number_of_goals} | Topics: {self.__gpm.number_of_topics} ")
            print(f"{'='*80}\n")
            pass
        else:
            print("\nYou must login first\n")

    def __manage_groups(self) -> None:
        if not self.__auth.is_authenticated():
            print("You must login first")
            return
        
        builder = Menu.Builder(Description('Manage Groups'), auto_select=lambda: self.__groups_mgr.print_groups())
        builder = builder.with_entry(Entry.create('1', 'Add Group', on_selected=lambda: self.__groups_mgr.add_group(self.__auth.session, self.__auth.get_headers())))
        builder = builder.with_entry(Entry.create('2', 'Join Group', on_selected=lambda: self.__groups_mgr.join_group(self.__auth.session, self.__auth.get_headers())))
        builder = builder.with_entry(Entry.create('3', 'Leave Group', on_selected=lambda: self.__groups_mgr.leave_group(self.__auth.session, self.__auth.get_headers())))
        
        if self.__auth.is_staff():
            builder = builder.with_entry(Entry.create('4', 'Remove Group', on_selected=lambda: self.__groups_mgr.remove_group(self.__auth.session, self.__auth.get_headers())))
            builder = builder.with_entry(Entry.create('5', 'Sort by Name', on_selected=lambda: self.__groups_mgr.sort_groups()))
        
        builder = builder.with_entry(Entry.create('0', 'Back', on_selected=lambda: None, is_exit=True))
        builder.build().run()

    def __manage_goals(self) -> None:
        if not self.__auth.is_authenticated():
            print("You must login first")
            return
        
        builder = Menu.Builder(Description('Manage Goals'), auto_select=lambda: self.__goals_mgr.print_goals())
        
        if self.__auth.is_staff():
            builder = builder.with_entry(Entry.create('1', 'Add Goal', on_selected=lambda: self.__goals_mgr.add_goal(self.__auth.session, self.__auth.get_headers())))
            builder = builder.with_entry(Entry.create('2', 'Remove Goal', on_selected=lambda: self.__goals_mgr.remove_goal(self.__auth.session, self.__auth.get_headers())))
            builder = builder.with_entry(Entry.create('3', 'Sort by Points', on_selected=lambda: self.__goals_mgr.sort_goals()))
        else:
            builder = builder.with_entry(Entry.create('1', 'Sort by Points', on_selected=lambda: self.__goals_mgr.sort_goals()))
        
        builder = builder.with_entry(Entry.create('0', 'Back', on_selected=lambda: None, is_exit=True))
        builder.build().run()

    def __manage_topics(self) -> None:
        if not self.__auth.is_authenticated():
            print("You must login first")
            return
        
        builder = Menu.Builder(Description('Manage Topics'), auto_select=lambda: self.__topics_mgr.print_topics())
        
        if self.__auth.is_staff():
            builder = builder.with_entry(Entry.create('1', 'Add Topic', on_selected=lambda: self.__topics_mgr.add_topic(self.__auth.session, self.__auth.get_headers())))
            builder = builder.with_entry(Entry.create('2', 'Remove Topic', on_selected=lambda: self.__topics_mgr.remove_topic(self.__auth.session, self.__auth.get_headers())))
            builder = builder.with_entry(Entry.create('3', 'Sort by Title', on_selected=lambda: self.__topics_mgr.sort_topics()))
        else:
            builder = builder.with_entry(Entry.create('1', 'Sort by Title', on_selected=lambda: self.__topics_mgr.sort_topics()))
        
        builder = builder.with_entry(Entry.create('0', 'Back', on_selected=lambda: None, is_exit=True))
        builder.build().run()

    def __manage_group_goals(self) -> None:
        if not self.__auth.is_authenticated():
            print("You must login first")
            return
        
        builder = Menu.Builder(Description('Manage Group Goals'), auto_select=lambda: self.__group_goals_mgr.print_group_goals())
        
        if self.__auth.is_staff():
            builder = builder.with_entry(Entry.create('1', 'Assign Goal to Group', on_selected=lambda: self.__group_goals_mgr.add_group_goal(self.__auth.session, self.__auth.get_headers())))
            builder = builder.with_entry(Entry.create('2', 'Remove Goal from Group', on_selected=lambda: self.__group_goals_mgr.remove_group_goal(self.__auth.session, self.__auth.get_headers())))
            builder = builder.with_entry(Entry.create('3', 'Toggle Goal Completion', on_selected=lambda: self.__group_goals_mgr.toggle_group_goal(self.__auth.session, self.__auth.get_headers())))
        
        builder = builder.with_entry(Entry.create('0', 'Back', on_selected=lambda: None, is_exit=True))
        builder.build().run()

    def run(self) -> None:
        try:
            self.__menu.run()
        except:
            traceback.print_exc()
            print('Panic error!', file=sys.stderr)
