from pyrogram import emoji
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from languages.languages import get_message
from plugins.utilities import human_format


def create_keyboard_profile_from_inline(username: str, language: str, is_private: bool = False) -> InlineKeyboardMarkup:
    keyboard = []

    if not is_private:
        keyboard.append([
            InlineKeyboardButton(get_message(language, "posts/view"), callback_data=f"inline-open-posts {username}"),
            InlineKeyboardButton(get_message(language, "stories/view"),
                                 callback_data=f"inline-open-stories {username}")
        ])

    keyboard.append([
        InlineKeyboardButton(get_message(language, "keyboards/view_online"),
                             url=f"https://www.instagram.com/{username}")
    ])

    return InlineKeyboardMarkup(keyboard)


def create_keyboard_posts_from_inline(post_likes: int, post_comments: int, num_posts: int,
                                      language: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(f"{emoji.RED_HEART} {human_format(post_likes)}", callback_data="inline_likes"),
            InlineKeyboardButton(f"{emoji.BOOKMARK_TABS} {human_format(post_comments)}",
                                 callback_data="inline_comments")
        ]
    ]

    if num_posts != 1:
        keyboard.append([
            InlineKeyboardButton(f"{emoji.LEFT_ARROW} {get_message(language, 'posts/previous')}",
                                 callback_data="inline_previous_post"),
            InlineKeyboardButton(f"{emoji.RIGHT_ARROW} {get_message(language, 'posts/next')}",
                                 callback_data="inline_next_post")
        ])

    keyboard.append([InlineKeyboardButton(f"{emoji.BACK_ARROW} {get_message(language, 'keyboards/back')}",
                                          callback_data="inline_back_to_profile")])

    return InlineKeyboardMarkup(keyboard)


def create_keyboard_stories_from_inline(num_stories: int, language: str) -> InlineKeyboardMarkup:
    keyboard = []

    if num_stories != 1:
        keyboard.append([
            InlineKeyboardButton(f"{emoji.LEFT_ARROW} {get_message(language, 'stories/previous')}",
                                 callback_data="inline_previous_story"),
            InlineKeyboardButton(f"{emoji.RIGHT_ARROW} {get_message(language, 'stories/next')}",
                                 callback_data="inline_next_story")
        ])

    keyboard.append([
        InlineKeyboardButton(
            f"{emoji.BACK_ARROW} {get_message(language, 'keyboards/back')}",
            callback_data="inline_back_to_profile")
    ])

    return InlineKeyboardMarkup(keyboard)
