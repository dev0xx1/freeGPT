from enum import Enum

from pydantic import BaseModel
import datetime as dt


class DBModel(BaseModel):
    table_name: str


# STATE
class Story(DBModel):
    table_name: str = 'freegpt.stories'

    created_at: dt.datetime
    updated_at: dt.datetime
    id: int
    content: str


class Reflection(DBModel):
    table_name: str = 'freegpt.reflections'
    created_at: dt.datetime
    updated_at: dt.datetime
    id: int
    content: str


class DecisionChoices(Enum):
    POST_TWEET = 'post_tweet'
    DO_NOTHING = 'do_nothing'


class Decision(DBModel):
    table_name: str = 'freegpt.decisions'
    created_at: dt.datetime
    name: str
