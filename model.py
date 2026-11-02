"""
Implements a runtime data model that can be used to access
the properties contained in the issues JSON.
"""

from typing import List, Dict, Set, Tuple
from enum import Enum
from datetime import datetime, timezone
from dateutil import parser


def _as_utc(value:datetime) -> datetime:
    """
    Returns the datetime as a timezone-aware UTC datetime so that dates
    can always be subtracted from each other safely.
    """
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class State(str, Enum):
    """
    Whether issue is open or closed.
    """
    open = 'open'
    closed = 'closed'


class Event:
    
    def __init__(self, jobj:any):
        self.event_type:str = None
        self.author:str = None
        self.event_date:datetime = None
        self.label:str = None
        self.comment:str = None
        
        if jobj is not None:
            self.from_json(jobj)
    
    def from_json(self, jobj:any):
        self.event_type = jobj.get('event_type')
        self.author = jobj.get('author')
        try:
            self.event_date = parser.parse(jobj.get('event_date'))
        except:
            pass
        self.label = jobj.get('label')
        self.comment = jobj.get('comment')

    @property
    def is_human(self) -> bool:
        """
        True if the event was caused by a real user (not a bot such as
        github-actions[bot] and not an unknown/deleted user).
        """
        return bool(self.author) and not self.author.endswith('[bot]')
        
        
class Issue:
    
    def __init__(self, jobj:any=None):
        self.url:str = None
        self.creator:str = None
        self.labels:List[str] = []
        self.state:State = None
        self.assignees:List[str] = []
        self.title:str = None
        self.text:str = None
        self.number:int = -1
        self.created_date:datetime = None
        self.updated_date:datetime = None
        self.timeline_url:str = None
        self.events:List[Event] = []
        
        if jobj is not None:
            self.from_json(jobj)
    
    def from_json(self, jobj:any):
        self.url = jobj.get('url')
        self.creator = jobj.get('creator')
        self.labels = jobj.get('labels',[])
        self.state = State[jobj.get('state')]
        self.assignees = jobj.get('assignees',[])
        self.title = jobj.get('title')
        self.text = jobj.get('text')
        try:
            self.number = int(jobj.get('number','-1'))
        except:
            pass
        try:
            self.created_date = parser.parse(jobj.get('created_date'))
        except:
            pass
        try:
            self.updated_date = parser.parse(jobj.get('updated_date'))
        except:
            pass
        self.timeline_url = jobj.get('timeline_url')
        self.events = [Event(jevent) for jevent in jobj.get('events',[])]

    @property
    def closed_date(self) -> datetime:
        """
        Date of the most recent 'closed' event, or None if the issue has
        no closing event in the data (some closed issues are missing it).
        """
        dates = [_as_utc(e.event_date) for e in self.events
                 if e.event_type == 'closed' and e.event_date is not None]
        return max(dates) if dates else None

    def days_to_close(self) -> float:
        """
        Number of days between creation and closing. Returns None for issues
        that are still open, have no closing event, or have no creation date.
        """
        closed = self.closed_date
        if self.state != State.closed or closed is None or self.created_date is None:
            return None
        days = (closed - _as_utc(self.created_date)).total_seconds() / 86400
        return days if days >= 0 else None

    def human_comments(self) -> List[Event]:
        """
        All comment events written by real users (bots excluded).
        """
        return [e for e in self.events if e.event_type == 'commented' and e.is_human]
