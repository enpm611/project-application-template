"""Tests for the developer response time analysis (feature 2).

Run with: python -m unittest discover -v
"""
#redirect_stdout, to capture what the analysis prints
import contextlib
#build expected dates for comparisons
from datetime import datetime, timezone
#StringIO, an in-memory "file" that collects printed text
import io
#Python's built-in test framework
import unittest
#temporarily replace parts of the program during a test
from unittest.mock import patch

#plotting library
import matplotlib
#draw charts off-screen so tests never open a window
matplotlib.use("Agg")
#used to inspect and close test charts
import matplotlib.pyplot as plt

#template data class, so test issues look exactly like real ones
from model import Issue
#the functions and class under test
from developer_response_time import (
    ANSWERED, NEVER_ANSWERED, DeveloperResponseAnalysis, analyze_issue, as_utc,
    bucket_counts, find_developers, first_developer_reply, is_bot,
    label_breakdown, snapshot_date,
)

#default creation date for test issues
CREATED = "2024-01-01T00:00:00+00:00"


def make_issue(events, number=1, creator="reporter", state="open", labels=None,
               created=CREATED):
    """Build an Issue from (event_type, date, author[, comment]) tuples."""
    #events in the same dictionary format as the JSON data file
    rows = []
    #turn each tuple into an event dictionary
    for row in events:
        #the first three values are always present
        event_type, date, author = row[:3]
        rows.append(dict(event_type=event_type, event_date=date, author=author,
                         #comment text is optional
                         comment=row[3] if len(row) > 3 else ""))
    #build a real Issue object from a dictionary
    return Issue(dict(number=number, title=f"Issue {number}",
                      url=f"https://github.com/python-poetry/poetry/issues/{number}",
                      state=state, creator=creator, labels=labels or [],
                      created_date=created, events=rows))


class HelperTests(unittest.TestCase):
    def test_as_utc_handles_naive_aware_and_none(self):
        #a datetime without a timezone
        naive = datetime(2024, 1, 1, 12)
        #gets UTC attached
        self.assertEqual(as_utc(naive).tzinfo, timezone.utc)
        #None passes through unchanged
        self.assertIsNone(as_utc(None))

    def test_is_bot(self):
        #GitHub app accounts end in [bot]
        self.assertTrue(is_bot("dependabot[bot]"))
        #known automation account
        self.assertTrue(is_bot("github-actions"))
        #a real person
        self.assertFalse(is_bot("abn"))
        #missing author is not a bot
        self.assertFalse(is_bot(None))

    def test_bucket_counts_boundaries(self):
        #0.5 -> <1d, 1 -> 1-7d, 7 -> 1-4w, 400 -> >1y
        #values exactly on a boundary go to the next bucket
        self.assertEqual(bucket_counts([0.5, 1, 7, 400]), [1, 1, 1, 0, 0, 1])
        #no data gives six empty buckets
        self.assertEqual(bucket_counts([]), [0] * 6)


class FindDevelopersTests(unittest.TestCase):
    def test_labeling_someone_elses_issue_makes_a_developer(self):
        #someone labels the reporter's issue
        issue = make_issue([("labeled", "2024-01-02T00:00:00+00:00", "Maintainer")])
        #stored lowercased
        self.assertEqual(find_developers([issue]), {"maintainer"})

    def test_actions_on_own_issue_are_ignored(self):
        #Templates label issues under the creator's name; anyone can close their own.
        issue = make_issue([("labeled", CREATED, "reporter"),
                            ("closed", "2024-01-05T00:00:00+00:00", "reporter")])
        #the reporter is not a developer
        self.assertEqual(find_developers([issue]), set())

    def test_bots_and_missing_authors_are_ignored(self):
        #bot action
        issue = make_issue([("labeled", CREATED, "stale[bot]"),
                            #action with no author
                            ("closed", CREATED, None)])
        #neither counts
        self.assertEqual(find_developers([issue]), set())

    def test_comments_alone_do_not_make_a_developer(self):
        #anyone can comment
        issue = make_issue([("commented", CREATED, "helpful_user", "Same here")])
        #so commenting alone proves nothing
        self.assertEqual(find_developers([issue]), set())


class FirstReplyTests(unittest.TestCase):
    def test_earliest_developer_comment_wins_even_if_unsorted(self):
        issue = make_issue([
            #listed first but posted later
            ("commented", "2024-01-05T00:00:00+00:00", "dev_b", "later"),
            #posted earlier
            ("commented", "2024-01-03T00:00:00+00:00", "dev_a", "earlier"),
        ])
        reply = first_developer_reply(issue, {"dev_a", "dev_b"})
        #picked by date, not by list order
        self.assertEqual(reply.author, "dev_a")

    def test_non_developer_and_creator_comments_are_skipped(self):
        issue = make_issue([
            #not a developer
            ("commented", "2024-01-02T00:00:00+00:00", "random_user"),
            #the issue's own creator
            ("commented", "2024-01-03T00:00:00+00:00", "reporter"),
        ])
        #Even if the creator is a developer, replying to yourself is not a response.
        self.assertIsNone(first_developer_reply(issue, {"reporter"}))

    def test_case_insensitive_matching(self):
        #capitalised in the data
        issue = make_issue([("commented", "2024-01-02T00:00:00+00:00", "Secrus")])
        #still matches the lowercase developer name
        self.assertIsNotNone(first_developer_reply(issue, {"secrus"}))

    def test_comment_without_date_is_ignored(self):
        #a comment with no timestamp
        issue = make_issue([("commented", None, "dev")])
        #cannot be used to measure a wait
        self.assertIsNone(first_developer_reply(issue, {"dev"}))


class AnalyzeIssueTests(unittest.TestCase):
    #pretend snapshot date, 30 days after CREATED
    ASOF = datetime(2024, 1, 31, tzinfo=timezone.utc)

    def test_answered_wait_in_days(self):
        #reply 2.5 days after creation
        issue = make_issue([("commented", "2024-01-03T12:00:00+00:00", "dev")])
        record = analyze_issue(issue, {"dev"}, self.ASOF)
        #counted as answered
        self.assertEqual(record.status, ANSWERED)
        #wait measured in days, with fractions
        self.assertAlmostEqual(record.days, 2.5)
        #remembers who replied
        self.assertEqual(record.responder, "dev")

    def test_unanswered_waits_until_snapshot(self):
        #an issue with no events at all
        record = analyze_issue(make_issue([]), {"dev"}, self.ASOF)
        #counted as never answered
        self.assertEqual(record.status, NEVER_ANSWERED)
        #waited from creation to the snapshot
        self.assertAlmostEqual(record.days, 30.0)
        #nobody replied
        self.assertIsNone(record.responder)

    def test_missing_creation_date_is_skipped(self):
        #no creation date
        issue = make_issue([], created=None)
        #skipped instead of crashing
        self.assertIsNone(analyze_issue(issue, {"dev"}, self.ASOF))

    def test_snapshot_is_latest_timestamp(self):
        #latest date is the comment
        issues = [make_issue([("commented", "2024-03-01T00:00:00+00:00", "x")])]
        self.assertEqual(snapshot_date(issues),
                         #snapshot equals that latest date
                         datetime(2024, 3, 1, tzinfo=timezone.utc))
        #no issues means no snapshot
        self.assertIsNone(snapshot_date([]))


class LabelBreakdownTests(unittest.TestCase):
    def test_counts_fast_slow_and_never_per_label(self):
        #snapshot date for this test
        asof = datetime(2025, 1, 1, tzinfo=timezone.utc)
        #one known developer
        dev = {"dev"}
        fast = make_issue([("commented", "2024-01-02T00:00:00+00:00", "dev")],
                          #answered after 1 day
                          labels=["kind/bug"])
        slow = make_issue([("commented", "2024-03-01T00:00:00+00:00", "dev")],
                          #answered after about 2 months
                          labels=["kind/bug"])
        #never answered, has two labels
        never = make_issue([], labels=["kind/bug", "area/docs"])
        records = [analyze_issue(i, dev, asof) for i in (fast, slow, never)]
        self.assertEqual(dict(label_breakdown(records)),
                         #[fast, slow, never] per label
                         {"kind/bug": [1, 1, 1], "area/docs": [0, 0, 1]})


class RunTests(unittest.TestCase):
    def setUp(self):
        #small fake dataset used by every test in this class
        self.issues = [
            #makes "dev" a developer
            make_issue([("labeled", "2024-01-01T01:00:00+00:00", "dev"),
                        #and dev replies after 6 hours
                        ("commented", "2024-01-01T06:00:00+00:00", "dev")],
                       number=1, labels=["kind/bug"]),
            #an issue nobody answered
            make_issue([], number=2, labels=["kind/feature"]),
        ]

    def run_analysis(self, label=None):
        #fake data, fake --label value, and no chart window
        with patch("developer_response_time.DataLoader") as loader, \
             patch("developer_response_time.config.get_parameter", return_value=label), \
             patch.object(plt, "show"):
            #DataLoader().get_issues() returns our fake issues
            loader.return_value.get_issues.return_value = self.issues
            #collects the printed output
            out = io.StringIO()
            #capture everything printed by run()
            with contextlib.redirect_stdout(out):
                DeveloperResponseAnalysis().run()
            #free the figure created by the test
            plt.close("all")
        #the printed text, for the assertions
        return out.getvalue()

    def test_full_run_prints_summary(self):
        #no label filter
        text = self.run_analysis()
        #found "dev"
        self.assertIn("Developers inferred: 1", text)
        #headline counts
        self.assertIn("1 answered | 1 never answered (50%)", text)
        #appears in the "replied first" list
        self.assertIn("dev: 1 issues", text)

    def test_label_filter_uses_developers_from_all_issues(self):
        #dev is found from issue 1 even though only issue 2 is analyzed.
        text = self.run_analysis(label="kind/feature")
        #the filter did not hide the developer
        self.assertIn("Developers inferred: 1", text)
        #only issue 2 analysed
        self.assertIn("Analyzed 1 issues | 0 answered | 1 never answered", text)
        #empty statistics handled
        self.assertIn("No issues in this selection received a developer reply.", text)

    def test_closed_issues_are_not_listed_as_waiting(self):
        #a closed issue with no developer reply, much older than the open one
        self.issues.append(make_issue([], number=3, state="closed",
                                      created="2020-01-01T00:00:00+00:00"))
        text = self.run_analysis()
        #the waiting list only covers open issues
        waiting = text.split("Open issues waiting for a developer reply")[1].split("Developers who")[0]
        #the open unanswered issue is listed
        self.assertIn("#2 [open]", waiting)
        #the closed one is not, even though it is older
        self.assertNotIn("#3", waiting)
        #but it is still counted in the summary line
        self.assertIn("1 still open, 1 closed without a developer comment", text)

    def test_unknown_label_does_not_crash(self):
        #a label no issue has
        text = self.run_analysis(label="does/not-exist")
        #friendly message, no exception
        self.assertIn("No issues found for label 'does/not-exist'.", text)

    def test_chart_has_two_panels(self):
        #same setup, output discarded
        with patch("developer_response_time.DataLoader") as loader, \
             patch("developer_response_time.config.get_parameter", return_value=None), \
             patch.object(plt, "show"), contextlib.redirect_stdout(io.StringIO()):
            loader.return_value.get_issues.return_value = self.issues
            DeveloperResponseAnalysis().run()
            #the figure the analysis just drew
            fig = plt.gcf()
            #two panels
            self.assertEqual(len(fig.axes), 2)
            #first panel has a title
            self.assertTrue(fig.axes[0].get_title())
            #and a labelled x-axis
            self.assertTrue(fig.axes[0].get_xlabel())
            #clean up
            plt.close("all")


#allows running this file directly
if __name__ == "__main__":
    unittest.main()
