from datetime import datetime
from typing import List

from pyrogram import emoji
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from classes.Profile import Profile
from languages.languages import get_language, get_message
from classes.Link import Link


def create_keyboard_profile(username: str, language: str, is_private: bool = False) -> InlineKeyboardMarkup:
    keyboard = []

    if not is_private:
        keyboard.append([
            InlineKeyboardButton(get_message(language, "posts/view"), callback_data=f"open-posts {username}"),
            InlineKeyboardButton(get_message(language, "stories/view"),
                                 callback_data=f"open-stories {username}")
        ])

    keyboard.append([
        InlineKeyboardButton(get_message(language, "keyboards/view_online"),
                             url=Link.from_username(username).link)
    ])

    return InlineKeyboardMarkup(keyboard)


def create_keyboard_posts(post_likes: int, post_comments: int, username: str, num_posts: int,
                          language_code: str, user_id: int, from_profile: bool,
                          post_index: int, tot_posts: int, next_max_id: str) -> InlineKeyboardMarkup:
    language = get_language(user_id, language_code)

    keyboard = [
        [
            InlineKeyboardButton(f"{emoji.RED_HEART} {human_format(post_likes)}",
                                 callback_data="likes" if not from_profile else "likes profile"),
            InlineKeyboardButton(f"{emoji.BOOKMARK_TABS} {human_format(post_comments)}",
                                 callback_data="comments" if not from_profile else "comments profile")
        ]
    ]

    if num_posts != 1:
        next_previous_keyboard = []

        if post_index > 0:
            next_previous_keyboard.append(
                InlineKeyboardButton(f"{emoji.LEFT_ARROW} {get_message(language, 'posts/previous')}",
                                     callback_data="previous_post" if not from_profile else "previous_post profile"))
        if post_index < tot_posts-1 or (post_index == tot_posts-1 and next_max_id is not None):
            next_previous_keyboard.append(
                InlineKeyboardButton(f"{emoji.RIGHT_ARROW} {get_message(language, 'posts/next')}",
                                     callback_data="next_post" if not from_profile else "next_post profile"))

        keyboard.append(next_previous_keyboard)

    if from_profile:
        end_button = InlineKeyboardButton(
            f"{emoji.BACK_ARROW} {get_message(language, 'keyboards/back')}",
            callback_data=f"to-profile-back {username}"
        )
    else:
        end_button = InlineKeyboardButton(
            f"{emoji.BOY_LIGHT_SKIN_TONE} {get_message(language, 'keyboards/view_online')}",
            url=Link.from_username(username).link
        )

    keyboard.append([end_button])

    return InlineKeyboardMarkup(keyboard)


def create_keyboard_stories(username: str, num_stories: int, language: str,
                            from_profile: bool = False) -> InlineKeyboardMarkup:
    keyboard = []

    if num_stories != 1:
        keyboard.append([
            InlineKeyboardButton(f"{emoji.LEFT_ARROW} {get_message(language, 'stories/previous')}",
                                 callback_data=f"previous_story profile" if from_profile else "previous_story"),
            InlineKeyboardButton(f"{emoji.RIGHT_ARROW} {get_message(language, 'stories/next')}",
                                 callback_data=f"next_story profile" if from_profile else "next_story")
        ])

    if from_profile:
        keyboard.append([
            InlineKeyboardButton(
                f"{emoji.BACK_ARROW} {get_message(language, 'keyboards/back')}",
                callback_data=f"to-profile-back {username}"
            )
        ])
    else:
        keyboard.append([
            InlineKeyboardButton(f"{emoji.BOY_LIGHT_SKIN_TONE} {get_message(language, 'profile/profile')}",
                                 url=Link.from_username(username).link)
        ])

    return InlineKeyboardMarkup(keyboard)


def create_caption_profile(profile: Profile, language: str, use_link: bool = False) -> str:
    caption = []

    if profile.full_name != "":
        caption.append(f"{get_message(language, 'profile/full_name')}: {profile.full_name}")

    username = f"Username: {profile.username}"

    if profile.is_verified:
        username += " " + emoji.CHECK_MARK_BUTTON

    caption.append(username)

    if profile.category is not None:
        caption.append(f"{get_message(language, 'profile/category')}: {profile.category}")

    if profile.biography != "":
        caption.append(f"{get_message(language, 'profile/biography')}:\n<i>{profile.biography}</i>")

    for thing in [f"Followers: {human_format(profile.followers)}",
                  f"{get_message(language, 'profile/following')}: {human_format(profile.following)}",
                  f"Posts: {human_format(profile.num_posts)}",
                  f"{get_message(language, 'profile/is_private')}: "
                  f"{emoji.THUMBS_UP if profile.is_private else emoji.CROSS_MARK}"]:
        caption.append(thing)

    caption = '\n\n'.join(caption)

    if use_link:
        caption += Link(profile.profile_pic).deeplink()

    return caption


def create_caption_posts(caption: str, date: datetime, views: int, is_video: bool = False, link: str = None) -> str:
    start = format_date(date)

    if is_video:
        start += " " + human_format(views) + " views"

    if link is not None:
        start = Link(link).deeplink(start)

    caption = start + "\n\n" + (caption if caption is not None else "")

    caption = caption if len(caption) < 1024 else (caption[:1000] + "...")

    return caption


def create_caption_likes(likes_json: List[dict], language: str) -> str:
    if len(likes_json) <= 0:
        like_string = f"{get_message(language, 'keyboards/no_likes')} {emoji.CRYING_FACE}"

    else:
        like_string = get_message(language, "profile/liked_from") + ":\n"
        len_comment = len(like_string)
        first_iteration = True

        for like_json in likes_json:
            user = like_json["node"]["username"]
            new_like = f"<b>{Link.start_instastalkie('profile', user).deeplink(f'@{user}')}</b>"
            if not first_iteration:
                new_like = f'\n{new_like}'
            else:
                first_iteration = False

            len_comment += len(new_like)

            if len_comment <= 1000:
                like_string += new_like

    return like_string


def create_caption_comments(comments_json: List[dict], language: str) -> str:
    if len(comments_json) <= 0:
        comments = f"{get_message(language, 'keyboards/no_comments')} {emoji.FACE_WITHOUT_MOUTH}"

    else:
        comments = ""
        len_comment = 0

        for comment_json in comments_json:
            username = comment_json["node"]["owner"]["username"]
            text = comment_json["node"]["text"]
            new_comment = f"<b>{Link.start_instastalkie('profile', username).deeplink(f'@{username}')}</b>: {text}"
            len_comment += len(new_comment)

            if len_comment <= 1000:
                comments += f"\n{new_comment}"

    return comments


def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0

    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0

    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def format_date(date: datetime) -> str:
    minute = date.minute if date.minute >= 10 else f"0{date.minute}"

    date = f"<i>{date.day}/{date.month}/{date.year} {date.hour}:{minute}</i>"

    return date
