from datetime import datetime


class Story:
    def __init__(self, url: str, taken_at: datetime, type_story: str):
        self.url = url
        self.taken_at = taken_at
        self.type_story = type_story