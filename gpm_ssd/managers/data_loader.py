import requests
from gpm_ssd.domain import GPM, GroupProject, Goal, Topic, GroupGoal


class DataLoader:
    def __init__(self, base_url: str, gpm: GPM):
        self.base_url = base_url
        self.gpm = gpm
        self.index_to_id_groups = {}
        self.index_to_id_goals = {}
        self.index_to_id_topics = {}
        self.index_to_id_group_goals = {}
        self.user_groups: set[int] = set()

    def load_all_data(self, session: requests.Session, headers: dict) -> int | None:
        user_id = self._load_user(session, headers)
        self._load_user_groups(session, headers, user_id)
        self._load_groups(session, headers)
        self._load_goals(session, headers)
        self._load_topics(session, headers)
        self._load_group_goals(session, headers)
        return user_id

    def _load_user(self, session: requests.Session, headers: dict) -> int | None:
        res = session.get(url=f"{self.base_url}auth/user/", headers=headers)
        if res.status_code == 200:
            user_data = res.json()
            return user_data.get('pk')
        return None

    def _load_user_groups(self, session: requests.Session, headers: dict, user_id: int | None):
        res = session.get(url=f"{self.base_url}group-users/", headers=headers)
        if res.status_code == 200:
            user_groups_data = res.json()
            self.user_groups.clear()
            for ug in user_groups_data:
                if ug.get('user') == user_id:
                    self.user_groups.add(ug.get('group'))

    def _load_groups(self, session: requests.Session, headers: dict):
        res = session.get(url=f"{self.base_url}groups/", headers=headers)
        if res.status_code == 200:
            groups_data = res.json()
            for g in groups_data:
                try:
                    group = GroupProject.from_dict(g)
                    self.gpm.add_group(group)
                    self.index_to_id_groups[self.gpm.number_of_groups - 1] = group.id
                except Exception as e:
                    print(f"Warning: Failed to load group: {e}")

    def _load_goals(self, session: requests.Session, headers: dict):
        res = session.get(url=f"{self.base_url}goals/", headers=headers)
        if res.status_code == 200:
            goals_data = res.json()
            for g in goals_data:
                try:
                    goal = Goal.from_dict(g)
                    self.gpm.add_goal(goal)
                    self.index_to_id_goals[self.gpm.number_of_goals - 1] = goal.id
                except Exception as e:
                    print(f"Warning: Failed to load goal: {e}")

    def _load_topics(self, session: requests.Session, headers: dict):
        res = session.get(url=f"{self.base_url}topics/", headers=headers)
        if res.status_code == 200:
            topics_data = res.json()
            for t in topics_data:
                try:
                    topic = Topic.from_dict(t)
                    self.gpm.add_topic(topic)
                    self.index_to_id_topics[self.gpm.number_of_topics - 1] = topic.id
                except Exception as e:
                    print(f"Warning: Failed to load topic: {e}")

    def _load_group_goals(self, session: requests.Session, headers: dict):
        res = session.get(url=f"{self.base_url}group-goals/", headers=headers)
        if res.status_code == 200:
            group_goals_data = res.json()
            for gg in group_goals_data:
                try:
                    group_goal = GroupGoal.from_dict(gg)
                    self.gpm.add_group_goal(group_goal)
                    self.index_to_id_group_goals[self.gpm.number_of_group_goals - 1] = group_goal.id
                except Exception as e:
                    print(f"Warning: Failed to load group goal: {e}")

    def clear_all(self):
        self.user_groups.clear()
        self.gpm.clear_all()
        self.index_to_id_groups.clear()
        self.index_to_id_goals.clear()
        self.index_to_id_topics.clear()
        self.index_to_id_group_goals.clear()
