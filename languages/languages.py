import json
from pyrogram import emoji
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

language_names = {'it': 'Italiano', 'en': 'English', 'fr': 'Français'}
saved_users = json.load(open("languages/saved_users.json", "r"))
languages_all = {language: json.load(open(f"languages/jsons/{language}.json", "r")) for language in
                 language_names.keys()}


def get_language(user_id: int, language: str = None) -> str:
    user_id = str(user_id)

    if language is None:
        return saved_users.get(user_id, "en")

    if user_id not in saved_users:
        saved_users[user_id] = language if language in language_names else "en"

        with open("languages/data.json", "w") as x:
            json.dump(saved_users, x, indent=4)

    return saved_users[user_id]


def create_languages_keyboard(language: str) -> InlineKeyboardMarkup:
    keyboard = [
        []
    ]

    for language_name in language_names.keys():
        if len(keyboard[-1]) >= 3:
            keyboard.append([])

        button = InlineKeyboardButton(f"{full_name(language_name)} {get_flag(language_name)}",
                                      callback_data=f"selected-language_{language_name}")

        keyboard[-1].append(button)

    back_button = InlineKeyboardButton(get_message(language, "keyboards/back"), callback_data="languages_back")
    keyboard.append([back_button])

    return InlineKeyboardMarkup(keyboard)


def get_message(language: str, message_location: str) -> str:
    language_data = languages_all[language]

    message_location = message_location.split('/')

    for location in message_location:
        language_data = language_data[location]

    return language_data


def full_name(language: str) -> str:
    return language_names[language]


def get_flag(language: str) -> emoji:
    if language == "it":
        return emoji.FLAG_ITALY

    if language == "en":
        return emoji.FLAG_UNITED_KINGDOM

    if language == "fr":
        return emoji.FLAG_FRANCE


def change_language(user: int, language: str):
    saved_users[str(user)] = language

    with open("languages/saved_users.json", "w") as x:
        json.dump(saved_users, x, indent=4)
