from typing import List

from classes.Story import Story


class InlineStoriesIterator:
    def __init__(self, collection: List[Story], username: str):
        self.collection = collection
        self.username = username
        self.index = -1

    def next(self):
        self.index += 1

        if self.index >= len(self.collection):
            self.index = 0

        return self.collection[self.index]

    def previous(self):
        self.index -= 1

        if self.index < 0:
            self.index = len(self.collection) - 1

        return self.collection[self.index]