from pyrogram import Client, filters, emoji
from pyrogram.types import InputMediaVideo, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton

from classes import Post
from languages.languages import get_language, get_message
from plugins.main_functions import cached_posts, cached_ids
from plugins.utilities import create_caption_posts, create_keyboard_posts, create_caption_likes, create_caption_comments
from wrapper import get_post_details, get_public_post_liker, PostsIterator


@Client.on_callback_query(filters.regex("^next_post"))
async def next_post(_, callback):
    message_id = callback.message.message_id
    chat_id = callback.message.chat.id

    key = f"{chat_id}_{message_id}"

    iterator: PostsIterator = cached_posts.get(key)

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await callback.edit_message_text("", reply_markup="")
        return

    if iterator.right_user_id is None:
        iterator.right_user_id = cached_ids.get(key)

        if iterator.right_user_id is None:
            await callback.answer(get_message(language, "errors/not_cached_stories"), show_alert=True)
            await callback.edit_message_text("", reply_markup="")
            return

    if callback.from_user.id != iterator.right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    post = iterator.next()

    if post == "Fail":
        await callback.answer(get_message(language, "errors/fail"), show_alert=True)
        return

    await callback.answer()

    caption = create_caption_posts(post.caption, post.taken_at, post.views, post.is_video)

    from_profile = len(callback.data.split(' ')) > 1

    keyboard = create_keyboard_posts(post.likes, post.comment_number, iterator.username,
                                     len(iterator.collection), callback.from_user.language_code,
                                     callback.from_user.id, from_profile=from_profile)

    media = InputMediaVideo(post.source) if post.is_video else InputMediaPhoto(post.source)
    media.caption = caption

    await callback.edit_message_media(media, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^previous_post"))
async def previous_post(_, callback):
    message_id = callback.message.message_id
    chat_id = callback.message.chat.id

    key = f"{chat_id}_{message_id}"

    iterator: PostsIterator = cached_posts.get(key)

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await callback.edit_message_text("", reply_markup="")
        return

    if iterator.right_user_id is None:
        iterator.right_user_id = cached_ids.get(key)

        if iterator.right_user_id is None:
            await callback.answer(get_message(language, "errors/not_cached_stories"), show_alert=True)
            await callback.edit_message_text("", reply_markup="")
            return

    if callback.from_user.id != iterator.right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    await callback.answer()

    post: Post = iterator.previous()

    caption = create_caption_posts(post.caption, post.taken_at, post.views, post.is_video)

    from_profile = len(callback.data.split(' ')) > 1

    keyboard = create_keyboard_posts(post.likes, post.comment_number, iterator.username,
                                     len(iterator.collection), callback.from_user.language_code,
                                     callback.from_user.id, from_profile=from_profile)

    media = InputMediaVideo(post.source) if post.is_video else InputMediaPhoto(post.source)
    media.caption = caption

    await callback.edit_message_media(media, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^random_post"))
async def random_post(_, callback):
    message_id = callback.message.message_id
    chat_id = callback.message.chat.id

    key = f"{chat_id}_{message_id}"

    iterator: PostsIterator = cached_posts.get(key)

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await callback.edit_message_text("", reply_markup="")
        return

    if iterator.right_user_id is None:
        iterator.right_user_id = cached_ids.get(key)

        if iterator.right_user_id is None:
            await callback.answer(get_message(language, "errors/not_cached_stories"), show_alert=True)
            await callback.edit_message_text("", reply_markup="")
            return

    if callback.from_user.id != iterator.right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    await callback.answer()

    post: Post = iterator.random()

    caption = create_caption_posts(post.caption, post.taken_at, post.views, post.is_video)

    from_profile = len(callback.data.split(' ')) > 1

    keyboard = create_keyboard_posts(post.likes, post.comment_number, iterator.username,
                                     len(iterator.collection), callback.from_user.language_code,
                                     callback.from_user.id, from_profile=from_profile)

    media = InputMediaVideo(post.source) if post.is_video else InputMediaPhoto(post.source)
    media.caption = caption

    await callback.edit_message_media(media, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^comments"))
async def get_comments(_, callback):
    language = get_language(callback.from_user.id, callback.from_user.language_code)

    message_id = callback.message.message_id
    chat_id = callback.message.chat.id

    key = f"{chat_id}_{message_id}"

    iterator: PostsIterator = cached_posts.get(key)

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await callback.edit_message_text("", reply_markup="")

        return

    if iterator.right_user_id is None:
        iterator.right_user_id = cached_ids.get(key)

        if iterator.right_user_id is None:
            await callback.answer(get_message(language, "errors/not_cached_stories"), show_alert=True)
            await callback.edit_message_text("", reply_markup="")
            return

    if callback.from_user.id != iterator.right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    post = iterator.collection[iterator.index]

    response = get_post_details(post.shortcode)

    if response["status"] != "Success":
        await callback.answer(get_message(language, "errors/fail"), show_alert=True)
        return

    await callback.answer()

    comments_json = response["body"]["edge_media_to_parent_comment"]["edges"]

    comments = create_caption_comments(comments_json, language)

    from_profile = len(callback.data.split(' ')) > 1

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{emoji.BACK_ARROW} {get_message(language, 'keyboards/back')}",
                                 callback_data="back" if not from_profile else "back profile")
        ]
    ])

    await callback.edit_message_caption(comments)
    await callback.edit_message_reply_markup(keyboard)


@Client.on_callback_query(filters.regex("^likes"))
async def likes(_, callback):
    language = get_language(callback.from_user.id, callback.from_user.language_code)

    message_id = callback.message.message_id
    chat_id = callback.message.chat.id

    key = f"{chat_id}_{message_id}"

    iterator: PostsIterator = cached_posts.get(key)

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        return

    if iterator.right_user_id is None:
        iterator.right_user_id = cached_ids.get(key)

        if iterator.right_user_id is None:
            await callback.answer(get_message(language, "errors/not_cached_stories"), show_alert=True)
            await callback.edit_message_text("", reply_markup="")
            return

    if callback.from_user.id != iterator.right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    post: Post = iterator.collection[iterator.index]

    response = get_public_post_liker(post.shortcode)

    if response["status"] != "Success":
        await callback.answer(get_message(language, "errors/fail"), show_alert=True)
        return

    await callback.answer()

    likes_json = response["body"]["edge_liked_by"]["edges"]

    like_string = create_caption_likes(likes_json, language)

    from_profile = len(callback.data.split(' ')) > 1

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{emoji.BACK_ARROW} {get_message(language, 'keyboards/back')}",
                                 callback_data="back" if not from_profile else "back profile")
        ]
    ])

    await callback.edit_message_caption(like_string)
    await callback.edit_message_reply_markup(keyboard)


@Client.on_callback_query(filters.regex("^back"))
async def back(_, callback):
    message_id = callback.message.message_id
    chat_id = callback.message.chat.id

    key = f"{chat_id}_{message_id}"

    iterator: PostsIterator = cached_posts.get(key)

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_post"), show_alert=True)
        await callback.edit_message_text("", reply_markup="")
        return

    if iterator.right_user_id is None:
        iterator.right_user_id = cached_ids.get(key)

        if iterator.right_user_id is None:
            await callback.answer(get_message(language, "errors/not_cached_stories"), show_alert=True)
            await callback.edit_message_text("", reply_markup="")
            return

    if callback.from_user.id != iterator.right_user_id:
        await callback.answer(get_message(language, "errors/wrong_id"), show_alert=True)
        return

    await callback.answer()

    post = iterator.collection[iterator.index]

    caption = create_caption_posts(post.caption, post.taken_at, post.views, post.is_video)

    from_profile = len(callback.data.split(' ')) > 1

    keyboard = create_keyboard_posts(post.likes, post.comment_number, iterator.username, len(iterator.collection),
                                     callback.from_user.language_code, callback.from_user.id, from_profile=from_profile)

    await callback.edit_message_caption(caption)
    await callback.edit_message_reply_markup(keyboard)
