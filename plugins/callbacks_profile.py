from pyrogram import Client, filters
from pyrogram.types import InputMediaVideo, InputMediaPhoto

from classes import StoriesIterator, Profile, Post, Story
from languages.languages import get_language, get_message
from plugins.main_functions import cached_posts, cached_profiles, cached_stories, cached_ids
from plugins.utilities import create_caption_posts, create_keyboard_posts, create_caption_profile, \
    create_keyboard_profile, format_date, create_keyboard_stories
from wrapper import get_user_posts, PostsIterator, get_user_id, _request_story


@Client.on_callback_query(filters.regex("^open-posts "))
async def open_posts(_, callback):
    username = callback.data.split(' ')[1]

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    key = f"{callback.message.chat.id}_{callback.message.message_id}"

    profile: Profile = cached_profiles.get(key)
    right_user_id = cached_ids.get(key)

    if profile is None or right_user_id is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await callback.edit_message_text("", reply_markup="")
        return

    if callback.from_user.id != right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    iterator: PostsIterator = cached_posts.get(key)

    if iterator is None:
        posts = get_user_posts(username)

        if posts == "Fail":
            await callback.answer(get_message(language, "errors/fail"), show_alert=True)
            return

        next_max_id = posts.get("next_max_id")

        iterator = PostsIterator(posts["post_list"], username, next_max_id)

        cached_posts[key] = iterator

    await callback.answer()

    post: Post = iterator.next() if iterator.index != -1 else iterator.collection[iterator.index]

    caption = create_caption_posts(post.caption, post.taken_at, post.views, post.is_video)

    keyboard = create_keyboard_posts(post.likes, post.comment_number, iterator.username, len(iterator.collection),
                                     language, callback.from_user.id, True, iterator.index, len(iterator.collection),
                                     iterator.next_max_id)

    media = InputMediaVideo(post.source) if post.is_video else InputMediaPhoto(post.source)
    media.caption = caption

    await callback.edit_message_media(media)
    await callback.edit_message_reply_markup(keyboard)


@Client.on_callback_query(filters.regex("^open-stories "))
async def open_stories(_, callback):
    username = callback.data.split(' ')[1]

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    key = f"{callback.message.chat.id}_{callback.message.message_id}"

    profile: Profile = cached_profiles.get(key)
    right_user_id = cached_ids.get(key)

    if profile is None or right_user_id is None:
        await callback.answer(get_message(language, "errors/no_cached_post"), show_alert=True)
        await callback.edit_message_text("", reply_markup="")
        return

    if callback.from_user.id != right_user_id:
        await callback.answer(get_message(language, 'errors/wrong_id'), show_alert=True)
        return

    iterator: StoriesIterator = cached_stories.get(key)

    if iterator is None:
        user = get_user_id(username)

        if "username" not in user:
            await callback.answer(get_message(language, "errors/fail"))
            return

        stories = _request_story(user["user_id"])

        if stories == "private_account":
            await callback.answer(get_message(language, "errors/private_account"))
            return

        if stories == "no_stories":
            await callback.answer(get_message(language, "errors/no_stories"))
            return

        iterator = StoriesIterator(stories, username)

        cached_stories[key] = iterator

    await callback.answer()

    story: Story = iterator.next() if iterator.index != -1 else iterator.collection[iterator.index]

    caption = format_date(story.taken_at)

    keyboard = create_keyboard_stories(iterator.username, len(iterator.collection), language, from_profile=True)

    media = InputMediaVideo(story.url) if story.type_story == "mp4/video/boomerang" else InputMediaPhoto(story.url)
    media.caption = caption

    await callback.edit_message_media(media, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^to-profile-back "))
async def back_to_profile(_, callback):
    language = get_language(callback.from_user.id, callback.from_user.language_code)

    key = f"{callback.message.chat.id}_{callback.message.message_id}"

    profile: Profile = cached_profiles.get(key)
    right_user_id = cached_ids.get(key)

    if profile is None or right_user_id is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await callback.edit_message_text("", reply_markup="")
        return

    if callback.from_user.id != right_user_id:
        await callback.answer(get_message(language, 'errors/wrong_id'), show_alert=True)
        return

    await callback.answer()

    caption = create_caption_profile(profile, language)

    keyboard = create_keyboard_profile(profile.username, language, profile.is_private)

    await callback.edit_message_media(InputMediaPhoto(profile.profile_pic, caption=caption), reply_markup=keyboard)
