from uuid import uuid4

from pyrogram import Client, emoji
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent, ChosenInlineResult, InlineQuery, \
    InlineKeyboardMarkup, InlineKeyboardButton

from classes.Profile import Profile
from classes.StatusResponse import StatusResponse
from languages.languages import get_message, get_language
from plugins.utilities import create_caption_profile
from plugins.utilities_inline import create_keyboard_profile_from_inline
from wrapper import search, get_email_and_details, get_user_id


def profiles_not_found(language: str) -> InlineQueryResultArticle:
    return InlineQueryResultArticle(
        title=f'{emoji.CROSS_MARK} {get_message(language, "inline/no_profiles_found")}!',
        description=get_message(language, "inline/change_query"),
        input_message_content=InputTextMessageContent(
            message_text=f'{emoji.CROSS_MARK} <b>{get_message(language, "inline/no_profiles_found")}</b>')
    )


CACHE = {}
inline_cached_profiles = {}
inline_cached_posts = {}
inline_cached_stories = {}


@Client.on_inline_query()
async def on_inline_query(_, query: InlineQuery):
    to_search = query.query

    profile_list = search(to_search)

    inline_query_results = []

    language = get_language(query.from_user.id)

    if profile_list != "nothing_found":
        if len(profile_list) > 30:
            profile_list = profile_list[:30]

        for profile in profile_list:
            id = str(uuid4())
            title = profile.username
            if profile.is_verified:
                title += f" {emoji.CHECK_MARK_BUTTON}"

            new_result = InlineQueryResultArticle(
                title=title, id=id, thumb_url=profile.profile_pic,
                description=profile.full_name or None,
                input_message_content=InputTextMessageContent(message_text=get_message(language, "loading")),
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(get_message(language, "loading"),
                                             url=f"https://www.instagram.com/{profile.username}")
                    ]
                ])
            )

            CACHE[id] = [profile.username, language]

            inline_query_results.append(new_result)

    else:
        inline_query_results.append(profiles_not_found(language))

    await query.answer(inline_query_results, cache_time=0)


@Client.on_chosen_inline_result()
async def on_chosen_inline_result(client, chosen_result: ChosenInlineResult):
    id = chosen_result.result_id
    message_id = chosen_result.inline_message_id

    cached = CACHE.get(str(id))

    username = cached[0]
    language = cached[1]

    profile_id = get_user_id(username)

    if profile_id == StatusResponse.INVALID_USERNAME:
        await client.edit_inline_text(message_id, get_message(language, "errors/fail"))
        return

    profile: Profile = get_email_and_details(int(profile_id))

    if profile == "error":
        await client.edit_inline_text(message_id, get_message(language, "errors/fail"))
        return

    caption = create_caption_profile(profile, language, use_link=True)

    keyboard = create_keyboard_profile_from_inline(profile.username, language, profile.is_private)

    await client.edit_inline_text(message_id, caption, disable_web_page_preview=False, reply_markup=keyboard)

    key = chosen_result.inline_message_id

    inline_cached_profiles[key] = [profile, chosen_result.from_user.id]
