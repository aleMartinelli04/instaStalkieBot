from pyrogram import Client, filters
from pyrogram.types import InputMediaVideo, InputMediaPhoto

from classes.StoriesIterator import StoriesIterator
from languages.languages import get_language, get_message
from plugins.main_functions import cached_stories, cached_ids
from plugins.utilities import format_date, create_keyboard_stories


@Client.on_callback_query(filters.regex("^next_story"))
async def next_story(_, callback):
    message_id = callback.message.message_id
    chat_id = callback.message.chat.id

    key = f"{chat_id}_{message_id}"

    iterator: StoriesIterator = cached_stories.get(key)

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_stories"), show_alert=True)
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

    story = iterator.next()

    caption = format_date(story.taken_at)

    from_profile = "profile" in callback.data

    keyboard = create_keyboard_stories(iterator.username, len(iterator.collection), language, from_profile=from_profile)

    media = InputMediaVideo(story.url) if story.type_story == "mp4/video/boomerang" \
        else InputMediaPhoto(story.url)
    media.caption = caption

    await callback.edit_message_media(media, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^previous_story"))
async def previous_story(_, callback):
    message_id = callback.message.message_id
    chat_id = callback.message.chat.id

    key = f"{chat_id}_{message_id}"

    iterator: StoriesIterator = cached_stories.get(key)

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    if iterator is None:
        await callback.answer(get_message(language, "errors/not_cached_stories"), show_alert=True)
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

    story = iterator.previous()

    caption = format_date(story.taken_at)

    from_profile = "profile" in callback.data

    keyboard = create_keyboard_stories(iterator.username, len(iterator.collection), language, from_profile=from_profile)

    media = InputMediaVideo(story.url) if story.type_story == "mp4/video/boomerang" \
        else InputMediaPhoto(story.url)
    media.caption = caption

    await callback.edit_message_media(media, reply_markup=keyboard)
