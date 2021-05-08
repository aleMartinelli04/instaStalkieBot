import random
from typing import List

from pyrogram import Client, filters, emoji
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from classes import Post, Profile, Story
from languages.languages import get_language, get_message
from plugins.inline import inline_cached_posts, inline_cached_profiles, inline_cached_stories
from plugins.utilities import create_caption_posts, create_caption_likes, create_caption_comments, \
    create_caption_profile, format_date
from plugins.utilities_inline import create_keyboard_posts_from_inline, create_keyboard_profile_from_inline, \
    create_keyboard_stories_from_inline
from wrapper import get_user_posts, get_public_post_liker, get_post_details, get_user_id, _request_story


class InlinePostsIterator:
    def __init__(self, collection: List[Post], username: str, next_max_id: str):
        self.collection = collection
        self.username = username
        self.next_max_id = next_max_id
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

    def random(self):
        new_index = random.randint(0, len(self.collection))

        while new_index == self.index:
            new_index = random.randint(0, len(self.collection))

        self.index = new_index

        return self.collection[self.index]


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

    def random(self):
        new_index = random.randint(0, len(self.collection))

        while new_index == self.index:
            new_index = random.randint(0, len(self.collection))

        self.index = new_index

        return self.collection[self.index]


@Client.on_callback_query(filters.regex("^inline-open-posts "))
async def open_posts_inline(client, callback):
    username = callback.data.split(' ')[1]

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    key = callback.inline_message_id

    iterator: InlinePostsIterator = inline_cached_posts.get(key)

    profile_userid: List[Profile, int] = inline_cached_profiles.get(key)

    if profile_userid is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    right_user_id = profile_userid[1]

    if callback.from_user.id != right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    if iterator is None:
        posts = get_user_posts(username)

        if posts == "Fail":
            await callback.answer(get_message(language, "errors/fail"), show_alert=True)
            return

        next_max_id = posts.get("next_max_id")

        iterator = InlinePostsIterator(posts["post_list"], username, next_max_id)

    await callback.answer()

    post = iterator.next() if iterator.index == -1 else iterator.collection[iterator.index]

    caption = create_caption_posts(post.caption, post.taken_at, post.views, post.is_video, link=post.source)

    keyboard = create_keyboard_posts_from_inline(post.likes, post.comment_number, len(iterator.collection), language)

    await client.edit_inline_text(key, caption, disable_web_page_preview=False, reply_markup=keyboard)

    inline_cached_posts[key] = iterator


@Client.on_callback_query(filters.regex("^inline_likes$"))
async def likes_inline(client, callback):
    language = get_language(callback.from_user.id, callback.from_user.language_code)

    key = callback.inline_message_id

    iterator: InlinePostsIterator = inline_cached_posts.get(key)

    profile_userid: List[Profile, int] = inline_cached_profiles.get(key)

    if profile_userid is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    right_user_id = profile_userid[1]

    if callback.from_user.id != right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    await callback.answer()

    post = iterator.collection[iterator.index]

    response = get_public_post_liker(post.shortcode)

    if response["status"] != "Success":
        await callback.answer(get_message(language, "errors/fail"), show_alert=True)
        return

    likes_json = response["body"]["edge_liked_by"]["edges"]

    like_string = create_caption_likes(likes_json, language)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{emoji.BACK_ARROW} {get_message(language, 'keyboards/back')}",
                                 callback_data="inline_back")
        ]
    ])

    await client.edit_inline_text(key, like_string, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^inline_comments$"))
async def comments_inline(client, callback):
    language = get_language(callback.from_user.id, callback.from_user.language_code)

    key = callback.inline_message_id

    iterator: InlinePostsIterator = inline_cached_posts.get(key)

    profile_userid: List[Profile, int] = inline_cached_profiles.get(key)

    if profile_userid is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    right_user_id = profile_userid[1]

    if callback.from_user.id != right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    await callback.answer()

    post = iterator.collection[iterator.index]

    response = get_post_details(post.shortcode)

    if response["status"] != "Success":
        await callback.answer(get_message(language, "errors/fail"), show_alert=True)
        return

    comments_json = response["body"]["edge_media_to_parent_comment"]["edges"]

    comments = create_caption_comments(comments_json, language)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{emoji.BACK_ARROW} {get_message(language, 'keyboards/back')}",
                                 callback_data="inline_back")
        ]
    ])

    await client.edit_inline_text(key, comments, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^inline_next_post$"))
async def next_post_inline(client, callback):
    key = callback.inline_message_id
    iterator: InlinePostsIterator = inline_cached_posts.get(key)

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    profile_userid: List[Profile, int] = inline_cached_profiles.get(key)

    if profile_userid is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    right_user_id = profile_userid[1]

    if callback.from_user.id != right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    post = iterator.next()

    if post == "Fail":
        await callback.answer(get_message(language, "errors/fail"), show_alert=True)
        return

    await callback.answer()

    caption = create_caption_posts(post.caption, post.taken_at, post.views, post.is_video, link=post.source)

    keyboard = create_keyboard_posts_from_inline(post.likes, post.comment_number, len(iterator.collection), language)

    await client.edit_inline_text(key, caption, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^inline_previous_post$"))
async def previous_post_inline(client, callback):
    key = callback.inline_message_id

    iterator: InlinePostsIterator = inline_cached_posts.get(key)

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    profile_userid: List[Profile, int] = inline_cached_profiles.get(key)

    if profile_userid is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    right_user_id = profile_userid[1]

    if callback.from_user.id != right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    await callback.answer()

    post = iterator.previous()

    caption = create_caption_posts(post.caption, post.taken_at, post.views, post.is_video, link=post.source)

    keyboard = create_keyboard_posts_from_inline(post.likes, post.comment_number, len(iterator.collection), language)

    await client.edit_inline_text(key, caption, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^inline_random_post$"))
async def random_post_inline(client, callback):
    key = callback.inline_message_id

    iterator: InlinePostsIterator = inline_cached_posts.get(key)

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    profile_userid: List[Profile, int] = inline_cached_profiles.get(key)

    if profile_userid is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    right_user_id = profile_userid[1]

    if callback.from_user.id != right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    await callback.answer()

    post = iterator.random()

    caption = create_caption_posts(post.caption, post.taken_at, post.views, post.is_video, link=post.source)

    keyboard = create_keyboard_posts_from_inline(post.likes, post.comment_number, len(iterator.collection), language)

    await client.edit_inline_text(key, caption, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^inline_back$"))
async def back_inline(client, callback):
    key = callback.inline_message_id

    iterator: InlinePostsIterator = inline_cached_posts.get(key)

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    profile_userid: List[Profile, int] = inline_cached_profiles.get(key)

    if profile_userid is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    right_user_id = profile_userid[1]

    if callback.from_user.id != right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    await callback.answer()

    post = iterator.collection[iterator.index]

    caption = create_caption_posts(post.caption, post.taken_at, post.views, post.is_video, link=post.source)

    keyboard = create_keyboard_posts_from_inline(post.likes, post.comment_number, len(iterator.collection), language)

    await client.edit_inline_text(key, caption, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^inline-open-stories "))
async def open_stories_inline(client, callback):
    username = callback.data.split(' ')[1]

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    key = callback.inline_message_id

    iterator: InlineStoriesIterator = inline_cached_stories.get(key)

    profile_userid: List[Profile, int] = inline_cached_profiles.get(key)

    if profile_userid is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    right_user_id = profile_userid[1]

    if callback.from_user.id != right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    if iterator is None:
        user = get_user_id(username)

        if "username" not in user:
            await callback.answer(get_message(language, "errors/fail"), show_alert=True)
            return

        stories = _request_story(user["user_id"])

        if stories == "fail":
            await callback.answer(get_message(language, "errors/fail"), show_alert=True)
            return

        if stories == "no_stories":
            await callback.answer(get_message(language, "errors/no_stories"), show_alert=True)
            return

        iterator = InlineStoriesIterator(stories, username)

    await callback.answer()

    story = iterator.next() if iterator.index == -1 else iterator.collection[iterator.index]

    date = f"<a href='{story.url}'>{format_date(story.taken_at)}</a>"

    keyboard = create_keyboard_stories_from_inline(len(iterator.collection), language)

    await client.edit_inline_text(key, date, reply_markup=keyboard)

    inline_cached_stories[key] = iterator


@Client.on_callback_query(filters.regex("^inline_next_story$"))
async def next_story_inline(client, callback):
    key = callback.inline_message_id

    iterator: InlineStoriesIterator = inline_cached_stories.get(key)

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    profile_userid: List[Profile, int] = inline_cached_profiles.get(key)

    if profile_userid is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    right_user_id = profile_userid[1]

    if callback.from_user.id != right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    await callback.answer()

    story = iterator.next()

    caption = f"<a href='{story.url}'>{format_date(story.taken_at)}</a>"

    keyboard = create_keyboard_stories_from_inline(len(iterator.collection), language)

    await client.edit_inline_text(key, caption, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^inline_random_story$"))
async def random_story_inline(client, callback):
    key = callback.inline_message_id

    iterator: InlineStoriesIterator = inline_cached_stories.get(key)

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    profile_userid: List[Profile, int] = inline_cached_profiles.get(key)

    if profile_userid is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    right_user_id = profile_userid[1]

    if callback.from_user.id != right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    await callback.answer()

    story = iterator.random()

    caption = f"<a href='{story.url}'>{format_date(story.taken_at)}</a>"

    keyboard = create_keyboard_stories_from_inline(len(iterator.collection), language)

    await client.edit_inline_text(key, caption, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^inline_previous_story$"))
async def previous_story_inline(client, callback):
    key = callback.inline_message_id
    iterator: InlineStoriesIterator = inline_cached_stories.get(key)

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    profile_userid: List[Profile, int] = inline_cached_profiles.get(key)

    if profile_userid is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    right_user_id = profile_userid[1]

    if callback.from_user.id != right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    await callback.answer()

    story = iterator.previous()

    caption = f"<a href='{story.url}'>{format_date(story.taken_at)}</a>"

    keyboard = create_keyboard_stories_from_inline(len(iterator.collection), language)

    await client.edit_inline_text(key, caption, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^inline_back_to_profile$"))
async def back_to_profile_inline(client, callback):
    key = callback.inline_message_id

    profile_userid: List[Profile, int] = inline_cached_profiles.get(key)

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    if profile_userid is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await client.edit_inline_text(key, "@instaStalkieBot", reply_markup="")
        return

    profile = profile_userid[0]

    right_user_id = profile_userid[1]

    if callback.from_user.id != right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    await callback.answer()

    caption = create_caption_profile(profile, language, use_link=True)

    keyboard = create_keyboard_profile_from_inline(profile.username, language, profile.is_private)

    await client.edit_inline_text(key, caption, reply_markup=keyboard)
