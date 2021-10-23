import json
from datetime import datetime
import random
from typing import List, Union

import requests

from classes.Post import Post
from classes.Profile import Profile
from classes.StatusResponse import StatusResponse
from classes.Story import Story
from config import HEADERS, HEADERS_STORIES

URL = "https://instagram47.p.rapidapi.com"


def _request(url: str, querystring: str) -> dict:
    """
    Replaces requests.get()

    :param url: part after the '/'
    :param querystring: params to request
    :return: a json containing the response
    """
    url = f"{URL}/{url}"

    r = requests.get(url, headers=random.choice(HEADERS), params=json.loads(querystring)).json()

    return r


def _request_story(user_id: int) -> Union[StatusResponse, List[Story]]:
    url = "https://instagram-stories1.p.rapidapi.com/v1/get_stories"

    querystring = {"userid": user_id}

    r = requests.get(url, headers=(HEADERS_STORIES[0]), params=querystring).json()

    if r["status"] == "Fail":
        return StatusResponse.FAIL

    stories_list_json = r["downloadLinks"]

    if len(stories_list_json) == 0:
        return StatusResponse.NO_STORIES

    stories = []

    for story_json in stories_list_json:
        new_story = Story(story_json["url"],
                          datetime.fromtimestamp(story_json["takenAt"]),
                          story_json["type"])

        stories.append(new_story)

    return stories


def get_user_id(username: str) -> Union[str, StatusResponse]:
    """
    Get the id by giving the username

    :param username: username
    :return: the user id
    """
    url = f"{URL}/get_user_id"

    querystring = {"username": username}

    response = requests.get(url, headers=random.choice(HEADERS), params=querystring).json()

    return response.get("user_id", StatusResponse.INVALID_USERNAME)


def get_user_posts(username: str, next_max_id: str = None) -> dict:
    """
    Get a list of posts

    :param username: the user
    :param next_max_id: used for requiring next posts
    :return: {next_max_id, List[Posts]}
    """
    url = "user_posts"

    querystring = {"username": username}

    if next_max_id is not None:
        querystring["next_max_id"] = next_max_id

    response = _request(url, json.dumps(querystring))

    if response["statusCode"] != 404:
        return response["status"]

    posts_json = response["body"]["items"]

    posts = []

    for post_json in posts_json:
        try:
            source = post_json["video_versions"][0]["url"]
            views = post_json["view_count"]
            is_video = True
        except:
            source = post_json["image_versions2"]["candidates"][0]["url"]
            views = None
            is_video = False

        caption = post_json["caption"]["text"] if post_json["caption"] is not None else ""

        taken_at = datetime.fromtimestamp(post_json["taken_at"])

        new_post = Post(
            post_json["code"],
            source,
            post_json["like_count"],
            post_json["comment_count"],
            caption,
            is_video,
            views,
            taken_at
        )

        posts.append(new_post)

    to_return = {"post_list": posts}

    if "next_max_id" in response["body"]:
        to_return["next_max_id"] = response["body"]["next_max_id"]

    return to_return


def get_public_post_liker(shortcode: str) -> dict:
    url = "public_post_likers"

    querystring = {"shortcode": shortcode}

    response = _request(url, json.dumps(querystring))

    return response


def get_post_details(shortcode: str) -> dict:
    url = "post_details"

    querystring = {"shortcode": shortcode}

    response = _request(url, json.dumps(querystring))

    return response


def get_email_and_details(user_id: int) -> Union[str, Profile]:
    url = "email_and_details"

    querystring = {"userid": user_id}

    data = _request(url, json.dumps(querystring))

    if data["status"] != "Success":
        return "error"

    data = data["body"]

    return Profile(data["hd_profile_pic_url_info"]["url"], data.get("full_name", ""), data["username"],
                   data["is_verified"], data.get("category"), data.get("biography", ""), data["following_count"],
                   data["follower_count"], data["media_count"], data["is_private"])


def search(for_what: str) -> Union[str, List[Profile]]:
    url = "search"

    querystring = {"search": for_what}

    response = _request(url, json.dumps(querystring))

    results = response.get("body").get("users") if response.get("body") is not None else None

    if results is None or len(results) == 0:
        return "nothing_found"

    data = response["body"]["users"]

    profiles = []

    for profile_json in data:
        new_profile = Profile(profile_json["user"]["profile_pic_url"], profile_json["user"]["full_name"],
                              profile_json["user"]["username"], profile_json["user"]["is_verified"])

        profiles.append(new_profile)

    return profiles


"""
# np
def get_post_comments(post_id: int):
    url = "post_comments"

    querystring = {"postid": post_id}

    response = _request(url, json.dumps(querystring))


# np
def get_location_posts(location_id: int):
    url = "location_posts"

    querystring = {"locationid": location_id}

    response = _request(url, json.dumps(querystring))


# np
def get_public_user_posts(user_id: int, end_cursor) -> Post:
    url = "public_user_posts"

    querystring = {"userid": user_id, "endcursor": end_cursor}

    response = _request(url, json.dumps(querystring))

    node = response["body"]["edges"][0]["node"]

    caption = node["edge_media_to_caption"]["edges"][0]["node"]["text"] \
        if len(node["edge_media_to_caption"]["edges"]) > 0 else ""

    post = Post(node["shortcode"],
                node["display_url"],
                node["edge_media_preview_like"]["count"],
                node["edge_media_to_comment"]["count"],
                caption)

    return post


# np
def get_related_profiles(user_id: int) -> [Profile]:
    url = "related_profiles"

    querystring = {"userid": user_id}

    response = _request(url, json.dumps(querystring))


# np
def get_user_followers(user_id: int) -> [Profile]:
    url = "user_followers"

    querystring = {"userid": user_id}

    response = _request(url, json.dumps(querystring))


# np
def get_user_following(user_id: int) -> [Profile]:
    url = "user_following"

    querystring = {"userid": user_id}

    response = _request(url, json.dumps(querystring))


# np
def get_user_highlights(user_id: int):
    url = "user_highlights"

    querystring = {"user_id": user_id}

    response = _request(url, json.dumps(querystring))



# np
def get_public_post_comments(shortcode: str) -> Post:
    url = "public_post_comments"

    querystring = {"shortcode": shortcode}

    response = _request(url, json.dumps(querystring))


# np
def get_hashtag_posts(hashtag: str) -> [Post]:
    url = "hashtag_post"

    querystring = {"hashtag": hashtag}

    response = _request(url, json.dumps(querystring))


# np
def get_user_tagged_posts(user_id: int):
    url = "user_tagged_post"

    querystring = {"userid": user_id}

    response = _request(url, json.dumps(querystring))


# np
def search_location(location: str):
    url = "location_search"

    querystring = {"search": location}

    response = _request(url, json.dumps(querystring))
"""
