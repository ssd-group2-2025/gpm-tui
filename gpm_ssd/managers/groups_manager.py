from typing import Tuple
import requests
from valid8 import ValidationError, validate

from gpm_ssd.domain import GPM, GroupProject, GroupName, Link
from gpm_ssd.managers.ui_helpers import UIHelpers
from gpm_ssd.exceptions import HttpException


class GroupsManager:
    def __init__(self, base_url: str, gpm: GPM, data_loader):
        self.base_url = base_url
        self.gpm = gpm
        self.data_loader = data_loader

    def print_groups(self):
        UIHelpers.print_separator(120)
        fmt = '%3s %-30s %-10s %-25s %-25s %-25s'
        print(fmt % ('Idx', 'NAME', 'TOPIC_ID', 'LINK_DJANGO', 'LINK_TUI', 'LINK_GUI'))
        UIHelpers.print_separator(120)

        for index in range(self.gpm.number_of_groups):
            group = self.gpm.group_at_index(index)
            print(fmt % (
                index + 1,
                group.name.value[:30],
                group.topic_id,
                group.link_django.value[:25],
                group.link_tui.value[:25],
                group.link_gui.value[:25]
            ))
        UIHelpers.print_separator(120)

    def add_group(self, session: requests.Session, headers: dict):
        while True:
            try:
                group = GroupProject(*self._read_group())
                self._add_group_backend(group, session, headers)
                break
            except ValidationError as e:
                print(f"\nValidation Error: {e}. Please, try again.")
            except HttpException as e:
                print(f"\nHTTP Error: {e}. Please, try again.")

    def _add_group_backend(self, group: GroupProject, session: requests.Session, headers: dict):
        res = session.post(
            url=f"{self.base_url}groups/",
            json=group.to_dict(),
            headers=headers
        )
        if res.status_code != 201:
            error_response = res.json()
            non_field_errors = error_response.get("non_field_errors", [])
            if non_field_errors:
                print(non_field_errors[0])
            else:
                print("Unknown error:", res.text)
        else:
            response_data = res.json()
            group_with_id = GroupProject.from_dict(response_data)
            self.gpm.add_group(group_with_id)
            self.data_loader.index_to_id_groups[self.gpm.number_of_groups - 1] = group_with_id.id
            print('Group added!')

    def remove_group(self, session: requests.Session, headers: dict):
        index = int(input('Enter index: '))
        validate("index", index, min_value=0, max_value=self.gpm.number_of_groups)

        if index == 0:
            print('Cancelled!')
            return
        self._remove_group_backend(index - 1, session, headers)

    def _remove_group_backend(self, index: int, session: requests.Session, headers: dict):
        group_id = self.data_loader.index_to_id_groups[index]
        res = session.delete(
            url=f"{self.base_url}groups/{group_id}/",
            headers=headers
        )
        if res.status_code != 204:
            print("Error removing group")
        else:
            self.gpm.remove_group(index)
            del self.data_loader.index_to_id_groups[index]
            new_mapping = {}
            for i in range(self.gpm.number_of_groups):
                old_index = i if i < index else i + 1
                new_mapping[i] = self.data_loader.index_to_id_groups[old_index]
            self.data_loader.index_to_id_groups = new_mapping
            print('Group removed!')

    def join_group(self, session: requests.Session, headers: dict):
        index = int(input('Enter group index to join: '))
        validate("index", index, min_value=1, max_value=self.gpm.number_of_groups)

        group_id = self.data_loader.index_to_id_groups[index - 1]
        res = session.post(
            url=f"{self.base_url}groups/{group_id}/join/",
            headers=headers
        )
        if res.status_code not in [200, 201]:
            print(f"Error joining group: {res.text}")
        else:
            self.data_loader.user_groups.add(group_id)
            print('Joined group successfully!')

    def leave_group(self, session: requests.Session, headers: dict):
        index = int(input('Enter group index to leave: '))
        validate("index", index, min_value=1, max_value=self.gpm.number_of_groups)

        group_id = self.data_loader.index_to_id_groups[index - 1]
        res = session.delete(
            url=f"{self.base_url}groups/{group_id}/leave/",
            headers=headers
        )
        if res.status_code != 204:
            print(f"Error leaving group: {res.text}")
        else:
            self.data_loader.user_groups.discard(group_id)
            print('Left group successfully!')

    def sort_groups(self):
        self.gpm.sort_groups_by_name()
        print('Groups sorted by name!')

    def _read_group(self) -> Tuple[GroupName, int, Link, Link, Link]:
        name = UIHelpers.read_input('Group Name', GroupName)
        topic_id = UIHelpers.read_input('Topic ID', int)
        link_django = UIHelpers.read_input('Link Django (optional)', lambda x: Link(x) if x else Link(""))
        link_tui = UIHelpers.read_input('Link TUI (optional)', lambda x: Link(x) if x else Link(""))
        link_gui = UIHelpers.read_input('Link GUI (optional)', lambda x: Link(x) if x else Link(""))
        return name, topic_id, link_django, link_tui, link_gui
