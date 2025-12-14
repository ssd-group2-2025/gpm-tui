from typing import Tuple
import requests
from valid8 import ValidationError, validate

from gpm_ssd.domain import GPM, Goal, GoalTitle, GoalDescription, Points
from gpm_ssd.managers.ui_helpers import UIHelpers
from gpm_ssd.exceptions import HttpException


class GoalsManager:
    def __init__(self, base_url: str, gpm: GPM, data_loader):
        self.base_url = base_url
        self.gpm = gpm
        self.data_loader = data_loader

    def print_goals(self):
        UIHelpers.print_separator(100)
        fmt = '%3s %-30s %-50s %6s'
        print(fmt % ('Idx', 'TITLE', 'DESCRIPTION', 'POINTS'))
        UIHelpers.print_separator(100)

        for index in range(self.gpm.number_of_goals):
            goal = self.gpm.goal_at_index(index)
            print(fmt % (
                index + 1,
                goal.title.value[:30],
                goal.description.value[:50],
                goal.points.value
            ))
        UIHelpers.print_separator(100)

    def add_goal(self, session: requests.Session, headers: dict):
        while True:
            try:
                goal = Goal(*self._read_goal())
                self._add_goal_backend(goal, session, headers)
                break
            except ValidationError as e:
                print(f"\nValidation Error: {e}. Please, try again.")
            except HttpException as e:
                print(f"\nHTTP Error: {e}. Please, try again.")

    def _add_goal_backend(self, goal: Goal, session: requests.Session, headers: dict):
        res = session.post(
            url=f"{self.base_url}goals/",
            json=goal.to_dict(),
            headers=headers
        )
        if res.status_code != 201:
            error_response = res.json()
            print("Error creating goal:", error_response)
        else:
            response_data = res.json()
            goal_with_id = Goal.from_dict(response_data)
            self.gpm.add_goal(goal_with_id)
            self.data_loader.index_to_id_goals[self.gpm.number_of_goals - 1] = goal_with_id.id
            print('Goal added!')

    def remove_goal(self, session: requests.Session, headers: dict):
        index = int(input('Enter index: '))
        validate("index", index, min_value=0, max_value=self.gpm.number_of_goals)

        if index == 0:
            print('Cancelled!')
            return
        self._remove_goal_backend(index - 1, session, headers)

    def _remove_goal_backend(self, index: int, session: requests.Session, headers: dict):
        goal_id = self.data_loader.index_to_id_goals[index]
        res = session.delete(
            url=f"{self.base_url}goals/{goal_id}/",
            headers=headers
        )
        if res.status_code != 204:
            print("Error removing goal")
        else:
            self.gpm.remove_goal(index)
            del self.data_loader.index_to_id_goals[index]
            new_mapping = {}
            for i in range(self.gpm.number_of_goals):
                old_index = i if i < index else i + 1
                new_mapping[i] = self.data_loader.index_to_id_goals[old_index]
            self.data_loader.index_to_id_goals = new_mapping
            print('Goal removed!')

    def sort_goals(self):
        self.gpm.sort_goals_by_points()
        print('Goals sorted by points!')

    def _read_goal(self) -> Tuple[GoalTitle, GoalDescription, Points]:
        title = UIHelpers.read_input('Goal Title', GoalTitle)
        description = UIHelpers.read_input('Goal Description', GoalDescription)
        points = UIHelpers.read_input('Points (1-5)', Points.parse)
        return title, description, points
