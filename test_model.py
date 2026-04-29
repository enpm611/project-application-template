import unittest
from model import Issue, Event, State


class TestModel(unittest.TestCase):


    def test_event_from_json(self):
        data = {
            "event_type": "labeled",
            "author": "user1",
            "event_date": "2023-01-01T00:00:00Z",
            "label": "bug",
            "comment": "test comment"
        }

        event = Event(data)

        self.assertEqual(event.event_type, "labeled")
        self.assertEqual(event.author, "user1")
        self.assertEqual(event.label, "bug")
        self.assertEqual(event.comment, "test comment")
        self.assertIsNotNone(event.event_date)

    def test_event_bad_date(self):
        data = {
            "event_type": "labeled",
            "author": "user1",
            "event_date": "invalid-date"
        }

        event = Event(data)

        self.assertIsNone(event.event_date)

    
    def test_issue_from_json(self):
        data = {
            "url": "http://example.com",
            "creator": "user1",
            "labels": ["bug"],
            "state": "open",
            "assignees": ["user2"],
            "title": "Test issue",
            "text": "Some text",
            "number": "123",
            "created_date": "2023-01-01T00:00:00Z",
            "updated_date": "2023-01-02T00:00:00Z",
            "timeline_url": "http://timeline",
            "events": [
                {
                    "event_type": "commented",
                    "author": "user2",
                    "event_date": "2023-01-01T01:00:00Z"
                }
            ]
        }

        issue = Issue(data)

        self.assertEqual(issue.creator, "user1")
        self.assertEqual(issue.labels, ["bug"])
        self.assertEqual(issue.state, State.open)
        self.assertEqual(issue.assignees, ["user2"])
        self.assertEqual(issue.number, 123)
        self.assertEqual(len(issue.events), 1)
        self.assertEqual(issue.events[0].author, "user2")

    def test_issue_missing_fields(self):
        data = {
            "state": "closed"
        }

        issue = Issue(data)

        self.assertEqual(issue.state, State.closed)
        self.assertEqual(issue.labels, [])
        self.assertEqual(issue.assignees, [])
        self.assertEqual(issue.number, -1)

    def test_issue_bad_number(self):
        data = {
            "state": "open",
            "number": "not_a_number"
        }

        issue = Issue(data)

        self.assertEqual(issue.number, -1)

    
    def test_issue_bad_dates(self):
        data = {
            "state": "open",
            "created_date": "bad-date",
            "updated_date": "bad-date"
        }

        issue = Issue(data)

        self.assertIsNone(issue.created_date)
        self.assertIsNone(issue.updated_date)
