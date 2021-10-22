from datetime import datetime


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