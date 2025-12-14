import requests
from valid8 import ValidationError, validate

from gpm_ssd.domain import GPM, GroupGoal
from gpm_ssd.managers.ui_helpers import UIHelpers
from gpm_ssd.exceptions import HttpException


class GroupGoalsManager:
    def __init__(self, base_url: str, gpm: GPM, data_loader):
        self.base_url = base_url
        self.gpm = gpm
        self.data_loader = data_loader

    def print_group_goals(self):
        UIHelpers.print_separator(120)
        fmt = '%3s %-30s %-40s %-10s'
        print(fmt % ('Idx', 'GROUP', 'GOAL', 'COMPLETE'))
        UIHelpers.print_separator(120)

        for index in range(self.gpm.number_of_group_goals()):
            gg = self.gpm.group_goal_at_index(index)
            group_name = "Unknown"
            goal_title = "Unknown"
            
            for i in range(self.gpm.number_of_groups):
                g = self.gpm.group_at_index(i)
                if g.id == gg.group_id:
                    group_name = g.name.value
                    break
            
            for i in range(self.gpm.number_of_goals):
                g = self.gpm.goal_at_index(i)
                if g.id == gg.goal_id:
                    goal_title = g.title.value
                    break
            
            print(fmt % (
                index + 1,
                group_name[:30],
                goal_title[:40],
                "✓" if gg.complete else "✗"
            ))
        UIHelpers.print_separator(120)

    def add_group_goal(self, session: requests.Session, headers: dict):
        while True:
            try:
                group_id = UIHelpers.read_input('Group ID', int)
                goal_id = UIHelpers.read_input('Goal ID', int)
                group_goal = GroupGoal(group_id=group_id, goal_id=goal_id)
                self._add_group_goal_backend(group_goal, session, headers)
                break
            except ValidationError as e:
                print(f"\nValidation Error: {e}. Please, try again.")
            except HttpException as e:
                print(f"\nHTTP Error: {e}. Please, try again.")

    def _add_group_goal_backend(self, group_goal: GroupGoal, session: requests.Session, headers: dict):
        res = session.post(
            url=f"{self.base_url}group-goals/",
            json=group_goal.to_dict(),
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
            group_goal_with_id = GroupGoal.from_dict(response_data)
            self.gpm.add_group_goal(group_goal_with_id)
            self.data_loader.index_to_id_group_goals[self.gpm.number_of_group_goals() - 1] = group_goal_with_id.id
            print('Group Goal added!')

    def remove_group_goal(self, session: requests.Session, headers: dict):
        index = int(input('Enter index: '))
        validate("index", index, min_value=1, max_value=self.gpm.number_of_group_goals())
        
        group_goal_id = self.data_loader.index_to_id_group_goals[index - 1]
        
        res = session.delete(
            url=f"{self.base_url}group-goals/{group_goal_id}/",
            headers=headers
        )
        
        if res.status_code != 204:
            print(f"Error removing group goal: {res.status_code}")
        else:
            self.gpm.remove_group_goal(index - 1)
            del self.data_loader.index_to_id_group_goals[index - 1]
            new_mapping = {}
            for i in range(self.gpm.number_of_group_goals()):
                old_index = i if i < index - 1 else i + 1
                new_mapping[i] = self.data_loader.index_to_id_group_goals[old_index]
            self.data_loader.index_to_id_group_goals = new_mapping
            print('Group Goal removed!')

    def toggle_group_goal(self, session: requests.Session, headers: dict):
        index = int(input('Enter index: '))
        validate("index", index, min_value=1, max_value=self.gpm.number_of_group_goals())
        
        group_goal = self.gpm.group_goal_at_index(index - 1)
        group_goal_id = self.data_loader.index_to_id_group_goals[index - 1]
        
        new_complete = not group_goal.complete
        
        res = session.patch(
            url=f"{self.base_url}group-goals/{group_goal_id}/",
            json={"complete": new_complete},
            headers=headers
        )
        
        if res.status_code != 200:
            print(f"Error toggling group goal: {res.status_code}")
        else:
            response_data = res.json()
            updated_group_goal = GroupGoal.from_dict(response_data)
            self.gpm.remove_group_goal(index - 1)
            self.gpm.add_group_goal(updated_group_goal)
            for i in range(self.gpm.number_of_group_goals() - 1, index - 1, -1):
                temp = self.gpm.group_goal_at_index(i)
                self.gpm.remove_group_goal(i)
                if i > index:
                    self.gpm.add_group_goal(temp)
            print('Group Goal toggled!')
