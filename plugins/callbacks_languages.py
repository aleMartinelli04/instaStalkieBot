from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from languages.languages import create_languages_keyboard, get_language, get_message, change_language, get_flag


@Client.on_callback_query(filters.regex("^open_languages_menu$"))
async def select_language(_, callback):
    await callback.answer()

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    keyboard = create_languages_keyboard(language)

    await callback.edit_message_text(get_message(language, "languages/choose_language"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^selected-language_"))
async def change_language_callback(_, callback):
    new_language = (callback.data.split('_'))[1]

    change_language(callback.from_user.id, new_language)

    keyboard = create_languages_keyboard(new_language)

    await callback.answer(get_message(new_language, "languages/changed_language"), show_alert=True)

    await callback.edit_message_text(get_message(new_language, "languages/choose_language"), reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^languages_back$"))
async def languages_back(_, callback):
    await callback.answer()

    language = get_language(callback.from_user.id, callback.from_user.language_code)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{get_flag(language)} {get_message(language, 'languages/language')}",
                                 callback_data="open_languages_menu")
        ]
    ])

    await callback.edit_message_text(get_message(language, 'languages/click_to_choose'), reply_markup=keyboard)
