import requests
from valid8 import ValidationError, validate

from gpm_ssd.domain import GPM, Topic, TopicTitle
from gpm_ssd.managers.ui_helpers import UIHelpers
from gpm_ssd.exceptions import HttpException


class TopicsManager:
    def __init__(self, base_url: str, gpm: GPM, data_loader):
        self.base_url = base_url
        self.gpm = gpm
        self.data_loader = data_loader

    def print_topics(self):
        UIHelpers.print_separator(60)
        fmt = '%3s %-50s'
        print(fmt % ('Idx', 'TITLE'))
        UIHelpers.print_separator(60)

        for index in range(self.gpm.number_of_topics):
            topic = self.gpm.topic_at_index(index)
            print(fmt % (index + 1, topic.title.value[:50]))
        UIHelpers.print_separator(60)

    def add_topic(self, session: requests.Session, headers: dict):
        while True:
            try:
                topic = Topic(UIHelpers.read_input('Topic Title', TopicTitle))
                self._add_topic_backend(topic, session, headers)
                break
            except ValidationError as e:
                print(f"\nValidation Error: {e}. Please, try again.")
            except HttpException as e:
                print(f"\nHTTP Error: {e}. Please, try again.")

    def _add_topic_backend(self, topic: Topic, session: requests.Session, headers: dict):
        res = session.post(
            url=f"{self.base_url}topics/",
            json=topic.to_dict(),
            headers=headers
        )
        if res.status_code != 201:
            error_response = res.json()
            print("Error creating topic:", error_response)
        else:
            response_data = res.json()
            topic_with_id = Topic.from_dict(response_data)
            self.gpm.add_topic(topic_with_id)
            self.data_loader.index_to_id_topics[self.gpm.number_of_topics - 1] = topic_with_id.id
            print('Topic added!')

    def remove_topic(self, session: requests.Session, headers: dict):
        index = int(input('Enter index: '))
        validate("index", index, min_value=0, max_value=self.gpm.number_of_topics)

        if index == 0:
            print('Cancelled!')
            return
        self._remove_topic_backend(index - 1, session, headers)

    def _remove_topic_backend(self, index: int, session: requests.Session, headers: dict):
        topic_id = self.data_loader.index_to_id_topics[index]
        res = session.delete(
            url=f"{self.base_url}topics/{topic_id}/",
            headers=headers
        )
        if res.status_code != 204:
            print("Error removing topic")
        else:
            self.gpm.remove_topic(index)
            del self.data_loader.index_to_id_topics[index]
            new_mapping = {}
            for i in range(self.gpm.number_of_topics):
                old_index = i if i < index else i + 1
                new_mapping[i] = self.data_loader.index_to_id_topics[old_index]
            self.data_loader.index_to_id_topics = new_mapping
            print('Topic removed!')

    def sort_topics(self):
        self.gpm.sort_topics_by_title()
        print('Topics sorted by title!')
