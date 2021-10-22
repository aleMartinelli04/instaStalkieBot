from typing import List

from classes.Post import Post
from wrapper import get_user_posts


class PostsIterator:
    def __init__(self, collection: List[Post], username: str, next_max_id: str, right_user_id: int = None):
        self.collection = collection
        self.username = username
        self.next_max_id = next_max_id
        self.right_user_id = right_user_id
        self.index = -1

    def next(self):
        self.index += 1

        if self.index >= len(self.collection):
            if self.next_max_id is not None:
                response = get_user_posts(self.username, self.next_max_id)

                if response == "Fail":
                    self.index -= 1
                    return "Fail"

                post_list = response["post_list"]

                for post in post_list:
                    self.collection.append(post)

                self.next_max_id = response.get("next_max_id")
            else:
                self.index = 0

        return self.collection[self.index]

    def previous(self):
        self.index -= 1

        if self.index < 0:
            self.index = len(self.collection) - 1

        return self.collection[self.index]