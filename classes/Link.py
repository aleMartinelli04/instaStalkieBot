class Link:
    def __init__(self, link: str):
        self.link = link

    @staticmethod
    def from_username(username: str):
        return Link(f"https://instagram.com/{username}")

    @staticmethod
    def start_instastalkie(keyword: str, username: str = ""):
        username = username.replace(".", "-")
        return Link(f"https://t.me/instaStalkieBot?start={keyword}{username}")

    def deeplink(self, text: str = "‎"):
        return f"<a href='{self.link}'>{text}</a>"