from enum import Enum


class StatusResponse(Enum):
    FAIL = "fail"
    SUCCESS = "success"
    NO_STORIES = "no_stories"
    INVALID_USERNAME = "invalid_username"