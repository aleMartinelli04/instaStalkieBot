from pyrogram import Client, filters, emoji
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from classes.StatusResponse import StatusResponse
from classes.StoriesIterator import StoriesIterator
from languages.languages import get_language, get_flag, get_message
from plugins.utilities import create_caption_posts, create_keyboard_posts, format_date, create_keyboard_stories, \
    create_caption_profile, create_keyboard_profile
from classes.Link import Link
from wrapper import get_user_posts, get_user_id, _request_story, get_email_and_details
from classes.PostsIterator import PostsIterator

cached_posts = {}
cached_stories = {}
cached_profiles = {}
cached_ids = {}


@Client.on_message(filters.command("start"))
async def on_start(_, message):
    argument = " ".join(message.command[1:]) if len(message.command) > 1 else ""

    if argument[0 : len("profile")] == "profile":
        username = argument[len("profile"):]
        username = username.replace("-", ".")

        await on_profile(_, message, username)
        return

    if argument[0 : len("stories")] == "stories":
        username = argument[len("stories"):]
        username = username.replace("-", ".")

        await on_stories(_, message, username)
        return

    if argument[0 : len("posts")] == "posts":
        username = argument[len("posts"):]
        username = username.replace("-", ".")

        await on_posts(_, message, username)
        return

    if argument == "languages":
        await on_languages(_, message)

    elif message.chat.type == "private":
        language = get_language(message.from_user.id, message.from_user.language_code)

        text = get_message(language, "menu")

        await message.reply_text('\n'.join(text))


@Client.on_message(filters.command("languages"))
async def on_languages(_, message):
    language = get_language(message.from_user.id, message.from_user.language_code)

    if message.chat.type == "private":
        text = get_message(language, 'languages/click_to_choose')

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"{get_flag(language)} {get_message(language, 'languages/language')}",
                                     callback_data="open_languages_menu")
            ]
        ])

    else:
        text = get_message(language, 'languages/redirect_text')

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(emoji.LOCKED, url=Link.start_instastalkie("languages").link)
            ]
        ])

    await message.reply_text(text, reply_markup=keyboard)


@Client.on_message(filters.command("posts"))
async def on_posts(_, message, username: str = None):
    if username is None:
        username = ' '.join(message.command[1:])

    language = get_language(message.from_user.id, message.from_user.language_code)

    if username == "":
        await message.reply_text(get_message(language, "errors/username_not_specified"))
        return

    wait_message = await message.reply_text(get_message(language, "loading"))

    await message.forward(chat_id=config.private_chat_id, disable_notification=True)

    posts = get_user_posts(username)

    if posts == "Fail":
        await message.reply_text(get_message(language, "errors/fail"))
        return

    next_max_id = posts.get("next_max_id")

    iterator = PostsIterator(posts["post_list"], username, next_max_id, message.from_user.id)

    post = iterator.next()

    caption = create_caption_posts(post.caption, post.taken_at, post.views, post.is_video)

    keyboard = create_keyboard_posts(post.likes, post.comment_number, iterator.username, len(iterator.collection),
                                     message.from_user.language_code, message.from_user.id, False, iterator.index,
                                     len(iterator.collection), iterator.next_max_id)

    try:
        await wait_message.delete()
    except:
        pass

    if post.is_video:
        message = await message.reply_video(post.source, caption=caption, reply_markup=keyboard)

    else:
        message = await message.reply_photo(post.source, caption=caption, reply_markup=keyboard)

    key = f"{message.chat.id}_{message.message_id}"

    cached_posts[key] = iterator


@Client.on_message(filters.command("stories"))
async def on_stories(_, message, username: str = None):
    if username is None:
        username = ' '.join(message.command[1:])

    language = get_language(message.from_user.id, message.from_user.language_code)

    if username == "":
        await message.reply_text(get_message(language, "errors/username_not_specified"))
        return

    user = get_user_id(username)

    if user == StatusResponse.INVALID_USERNAME:
        await message.reply_text(get_message(language, "errors/fail"))
        return

    wait_message = await message.reply_text(get_message(language, "loading"))

    await message.forward(chat_id=config.private_chat_id, disable_notification=True)

    stories = _request_story(int(user))

    if stories == StatusResponse.NO_STORIES:
        await message.reply_text(get_message(language, "errors/no_stories"))
        return

    iterator = StoriesIterator(stories, username, message.from_user.id)

    story = iterator.next()

    date = format_date(story.taken_at)

    keyboard = create_keyboard_stories(username, len(iterator.collection), language, from_profile=False)

    try:
        await wait_message.delete()
    except:
        pass

    if story.type_story == "mp4/video/boomerang":
        message = await message.reply_video(story.url, caption=date, reply_markup=keyboard)

    else:
        message = await message.reply_photo(story.url, caption=date, reply_markup=keyboard)

    key = f"{message.chat.id}_{message.message_id}"

    cached_stories[key] = iterator


@Client.on_message(filters.command("profile"))
async def on_profile(_, message, username: str = None):
    if username is None:
        username = ' '.join(message.command[1:])

    language = get_language(message.from_user.id, message.from_user.language_code)

    user = get_user_id(username)

    wait_message = await message.reply_text(get_message(language, "loading"))

    await message.forward(chat_id=config.private_chat_id, disable_notification=True)

    if user == StatusResponse.INVALID_USERNAME:
        await message.reply_text(get_message(language, "errors/non_existent_profile"))
        return

    profile = get_email_and_details(int(user))

    if profile == "error":
        await message.reply_text(get_message(language, "errors/non_existent_profile"))
        return

    right_user_id = message.from_user.id

    caption = create_caption_profile(profile, language)

    keyboard = create_keyboard_profile(profile.username, language, profile.is_private)

    try:
        await wait_message.delete()
    except:
        pass

    message = await message.reply_photo(profile.profile_pic, caption=caption, reply_markup=keyboard)

    key = f"{message.chat.id}_{message.message_id}"

    cached_profiles[key] = profile
    cached_ids[key] = right_user_id


@Client.on_message(filters.command("link"))
async def on_link(_, message):
    username = " ".join(message.command[1:])

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Profile", url=Link.start_instastalkie("profile", username).link),
            InlineKeyboardButton("Posts", url=Link.start_instastalkie("posts", username).link),
            InlineKeyboardButton("Stories", url=Link.start_instastalkie("stories", username).link)
        ]
    ])

    await message.reply_text(emoji.LINK, reply_markup=keyboard)
