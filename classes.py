from datetime import datetime
from typing import List


class Profile:
    def __init__(self, profile_pic: str, full_name: str, username: str, is_verified: bool, category: str = None,
                 biography: str = None, following: int = None, followers: int = None, num_posts: int = None,
                 is_private: bool = None):
        self.profile_pic = profile_pic
        self.full_name = full_name
        self.username = username
        self.category = category
        self.biography = biography
        self.following = following
        self.followers = followers
        self.num_posts = num_posts
        self.is_private = is_private
        self.is_verified = is_verified


class Comment:
    def __init__(self, from_user: str, comment_text: str):
        self.from_user = from_user
        self.comment_text = comment_text


class Post:
    def __init__(self,
                 shortcode: str,
                 source: str,
                 likes: int,
                 comment_number: int,
                 caption: str,
                 is_video: bool,
                 views: int,
                 taken_at: datetime
                 ):
        self.shortcode = shortcode
        self.source = source
        self.likes = likes
        self.comment_number = comment_number
        self.caption = caption
        self.is_video = is_video
        self.views = views
        self.taken_at = taken_at


class Story:
    def __init__(self, url: str, taken_at: datetime, type_story: str):
        self.url = url
        self.taken_at = taken_at
        self.type_story = type_story


class StoriesIterator:
    def __init__(self, collection: List[Story], username: str, right_user_id: int = None):
        self.collection = collection
        self.username = username
        self.right_user_id = right_user_id
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
