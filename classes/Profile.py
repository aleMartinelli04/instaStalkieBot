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