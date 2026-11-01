"""How long do Poetry issues wait for their first reply from a developer?

The dataset has no "maintainer" field, so developers are inferred from
activity: anyone who labels, closes, reopens, assigns, milestones or locks an
issue that SOMEONE ELSE created. Actions on one's own issue are ignored,
because issue templates add labels under the creator's name and anyone may
close their own issue.

Results describe response patterns in this data file. A developer may have
answered somewhere else (a pull request, Discord), which is not visible here.
"""
#lets us define small record classes with little code
from dataclasses import dataclass
#datetime for timestamps, timezone.utc for normalising them
from datetime import datetime, timezone
#regular expressions, used to recognise bot account names
import re
#median and mean of the reply times
import statistics
#trims long issue titles so console lines stay readable
from textwrap import shorten

#draws the two charts
import matplotlib.pyplot as plt

#template module: reads --label and other settings
import config
#template module: loads the issues from the JSON file
from data_loader import DataLoader

#Matches bot accounts such as "dependabot[bot]" or "github-actions" so they are never treated as people.
BOT = re.compile(r"\[bot\]$|^(?:dependabot|renovate|stale|github-actions)$", re.I)
#Event types that normally require write access to the repository (triage or maintainer rights).
DEVELOPER_EVENTS = {"labeled", "unlabeled", "closed", "reopened", "assigned",
                    "unassigned", "milestoned", "demilestoned", "locked"}
#status for an issue that got a developer reply
ANSWERED = "answered"
#status for an issue that never got one
NEVER_ANSWERED = "never answered"
#a reply within this many days counts as "fast" in the label chart
FAST_DAYS = 7
#how many labels to show in the label chart
TOP_LABELS = 10
#how many issues to list in each console section
TOP_ISSUES = 5

#Upper bound (exclusive, in days) and label of each response-time bucket.
BUCKETS = [(1, "< 1 day"), (7, "1-7 days"), (30, "1-4 weeks"),
           (90, "1-3 months"), (365, "3-12 months"), (float("inf"), "> 1 year")]


def as_utc(moment):
    """Make naive and timezone-aware datetimes comparable."""
    #missing dates stay missing
    if moment is None:
        return None
    #a date with no timezone attached...
    if moment.tzinfo is None:
        #...is assumed to already be UTC
        return moment.replace(tzinfo=timezone.utc)
    #otherwise convert it to UTC
    return moment.astimezone(timezone.utc)


def is_bot(author):
    #True only for a non-empty name that matches the bot pattern
    return bool(author and BOT.search(author.strip()))


def find_developers(issues):
    """Accounts that triaged or closed at least one issue they did not create."""
    #a set, so each developer is stored once
    developers = set()
    #look at every issue in the data
    for issue in issues:
        #who opened this issue, lowercased for comparison
        creator = (issue.creator or "").casefold()
        #look at everything that happened on the issue
        for event in issue.events:
            #who performed the event ("" if unknown)
            author = (event.author or "").strip()
            #it is a maintainer-type action...
            if (event.event_type in DEVELOPER_EVENTS
                    #...by a known account...
                    and author
                    #...that is not a bot...
                    and not is_bot(author)
                    #...on someone ELSE's issue
                    and author.casefold() != creator):
                #so we treat this account as a developer
                developers.add(author.casefold())
    #lowercase names of all inferred developers
    return developers


def snapshot_date(issues):
    """Latest timestamp in the data, i.e. when the export was taken.

    Waiting time for unanswered issues is measured up to this date rather than
    today, so results do not change depending on when the program is run.
    """
    #every timestamp we can find
    moments = []
    #for each issue...
    for issue in issues:
        #...its created and updated dates
        moments += [as_utc(issue.created_date), as_utc(issue.updated_date)]
        #...and the date of every event
        moments += [as_utc(event.event_date) for event in issue.events]
    #drop missing dates
    moments = [moment for moment in moments if moment is not None]
    #the latest one, or None for empty data
    return max(moments) if moments else None


def first_developer_reply(issue, developers):
    """The earliest comment by a developer who is not the issue's creator."""
    #lowercased creator name
    creator = (issue.creator or "").casefold()
    #keep only events that are...
    replies = [event for event in issue.events
               #...comments...
               if event.event_type == "commented"
               #...with a date...
               and event.event_date
               #...written by a developer...
               and (event.author or "").casefold() in developers
               #...who is not the person who opened the issue
               and (event.author or "").casefold() != creator]
    #earliest such comment, or None
    return min(replies, key=lambda event: as_utc(event.event_date), default=None)


@dataclass
class ResponseRecord:
    #the Issue this result is about
    issue: object
    #ANSWERED or NEVER_ANSWERED
    status: str
    #wait until first reply, or time waited so far
    days: float
    #name of the developer who replied first, or None
    responder: str | None


def analyze_issue(issue, developers, asof):
    #when the issue was opened
    created = as_utc(issue.created_date)
    #without a creation date we cannot measure a wait...
    if created is None:
        #...so skip this issue
        return None
    #first developer comment, if any
    reply = first_developer_reply(issue, developers)
    #the issue got a developer reply
    if reply is not None:
        #seconds converted to days
        days = (as_utc(reply.event_date) - created).total_seconds() / 86400
        #never report a negative wait
        return ResponseRecord(issue, ANSWERED, max(days, 0.0), reply.author)
    #no reply: measure up to the snapshot date
    end = asof if asof is not None else created
    #how long it has been waiting, in days
    days = (end - created).total_seconds() / 86400
    #no responder for unanswered issues
    return ResponseRecord(issue, NEVER_ANSWERED, max(days, 0.0), None)


def bucket_counts(days_list):
    #one counter per bucket, all starting at zero
    counts = [0] * len(BUCKETS)
    #for each reply time...
    for days in days_list:
        #...walk the buckets from shortest to longest
        for index, (upper, _) in enumerate(BUCKETS):
            #the first bucket whose upper bound is above the value...
            if days < upper:
                #...gets the count
                counts[index] += 1
                #stop so the value is counted only once
                break
    #list of counts in the same order as BUCKETS
    return counts


def label_breakdown(records, top=TOP_LABELS):
    """Per label: replied within FAST_DAYS, replied later, never replied."""
    #label -> [fast, slow, never]
    totals = {}
    #for each analysed issue...
    for record in records:
        #...and each of its labels
        for label in record.issue.labels or []:
            #create the counters the first time a label is seen
            row = totals.setdefault(label, [0, 0, 0])
            #never got a developer reply
            if record.status == NEVER_ANSWERED:
                row[2] += 1
            #answered within FAST_DAYS
            elif record.days < FAST_DAYS:
                row[0] += 1
            #answered, but later than FAST_DAYS
            else:
                row[1] += 1
    #most common labels first, ties by name
    ranked = sorted(totals.items(), key=lambda item: (-sum(item[1]), item[0]))
    #keep only the top N labels
    return ranked[:top]


def format_days(days):
    #under a day reads better in hours
    if days < 1:
        return f"{days * 24:.1f} hours"
    #otherwise show days with one decimal
    return f"{days:.1f} days"


class DeveloperResponseAnalysis:
    """Measure time to first developer reply across the project."""

    def __init__(self):
        #Optional --label parameter narrows the analysis to one kind of issue.
        #None when --label was not given
        self.label = config.get_parameter("label")

    def run(self):
        #load every issue from the data file
        all_issues = DataLoader().get_issues()
        #Infer developers from ALL issues so a label filter cannot hide them.
        developers = find_developers(all_issues)
        #"now" for this dataset
        asof = snapshot_date(all_issues)

        #start with everything...
        issues = all_issues
        #...and if a label was given...
        if self.label:
            #...keep only issues with it
            issues = [issue for issue in issues if self.label in (issue.labels or [])]
        #nothing matched the label
        if not issues:
            #tell the user instead of crashing
            print(f"No issues found for label {self.label!r}.")
            #stop here
            return

        #analyse each issue, drop skipped ones
        records = [r for r in (analyze_issue(i, developers, asof) for i in issues) if r]
        #issues with a developer reply
        answered = [r for r in records if r.status == ANSWERED]
        #issues without one
        unanswered = [r for r in records if r.status == NEVER_ANSWERED]
        #reply times in days, for the statistics
        waits = [r.days for r in answered]

        #console output
        self.print_summary(records, answered, unanswered, waits, developers, asof)
        #only draw charts when there is something to show
        if records:
            self.plot(answered, unanswered, records)

    def print_summary(self, records, answered, unanswered, waits, developers, asof):
        #number of issues analysed
        total = len(records)
        #header with the selected label
        print(f"\nDEVELOPER RESPONSE TIME | {self.label or 'all labels'}")
        #the question (required by the assignment)
        print("Question: How long do issues wait for a first reply from a developer?")
        print("Method: Developers = accounts that labeled, closed or assigned someone "
              #the method (required by the assignment)
              "else's issue; measure issue creation to their first comment.")
        print(f"Developers inferred: {len(developers)} | Data snapshot: "
              #how many developers and the snapshot date
              f"{asof.date().isoformat() if asof else 'unknown'}")
        print(f"Analyzed {total:,} issues | {len(answered)} answered | "
              #headline counts
              f"{len(unanswered)} never answered ({100 * len(unanswered) / total:.0f}%)")

        #at least one issue was answered
        if waits:
            #sort to find the 90th percentile
            ordered = sorted(waits)
            #value 90% of the way through the list
            p90 = ordered[min(len(ordered) - 1, int(0.9 * len(ordered)))]
            print(f"\nTime to first developer reply (answered issues):")
            #typical wait
            print(f"  Median: {format_days(statistics.median(waits))} | "
                  #average wait, pulled up by very slow replies
                  f"Mean: {format_days(statistics.mean(waits))} | "
                  #the slowest 10% waited at least this long
                  f"90th percentile: {format_days(p90)}")
            #share answered within 1 day, 1 week, 1 month
            for limit in (1, 7, 30):
                #percentage under the limit
                share = 100 * sum(w < limit for w in waits) / len(waits)
                print(f"  Answered within {limit:>2} day(s): {share:.0f}%")
        #no developer replied to any issue in this selection
        else:
            print("\nNo issues in this selection received a developer reply.")

        #unanswered issues that are still open
        open_unanswered = sum(r.issue.state == "open" for r in unanswered)
        print(f"\nNever answered: {open_unanswered} still open, "
              #the rest were closed
              f"{len(unanswered) - open_unanswered} closed without a developer comment")

        print(f"\nSlowest first replies (top {TOP_ISSUES}):")
        #longest waits first
        self.print_issues(sorted(answered, key=lambda r: -r.days)[:TOP_ISSUES])
        #only open issues are still waiting; a closed issue is no longer waiting for anything
        still_waiting = [r for r in unanswered if r.issue.state == "open"]
        #date the waiting time is measured up to
        as_of = asof.date().isoformat() if asof else "the data snapshot"
        print(f"\nOpen issues waiting for a developer reply (as of {as_of}, top {TOP_ISSUES}):")
        #oldest still-waiting issues first
        self.print_issues(sorted(still_waiting, key=lambda r: -r.days)[:TOP_ISSUES])

        #developer name -> number of issues they replied to first
        counts = {}
        #count first replies per developer
        for record in answered:
            counts[record.responder] = counts.get(record.responder, 0) + 1
        #five busiest, ties by name
        top = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:5]
        #only print the section if someone replied
        if top:
            print("\nDevelopers who most often replied first:")
            for name, count in top:
                print(f"  {name}: {count} issues")

        print("\nNote: replies made outside GitHub issues (pull requests, chat) are "
              #limitation shown to the user
              "not visible, and developer detection is an inference.")

    @staticmethod
    def print_issues(records):
        #empty list
        if not records:
            print("  None.")
        #one block per issue
        for record in records:
            #shorten long titles
            title = shorten(record.issue.title or "(untitled)", width=70, placeholder="...")
            #who replied, if anyone
            who = f" by {record.responder}" if record.responder else ""
            #"open"/"closed" instead of "State.open"
            state = getattr(record.issue.state, "value", record.issue.state)
            #issue number, state and title
            print(f"  #{record.issue.number} [{state}] {title}")
            #wait, responder and link
            print(f"    {format_days(record.days)}{who} | {record.issue.url or '(no URL)'}")

    def plot(self, answered, unanswered, records):
        #one figure with two side-by-side panels
        fig, (time_ax, label_ax) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle("How quickly do developers first reply to Poetry issues?"
                     #overall title, mentions the label if used
                     + (f" (label: {self.label})" if self.label else ""))

        #Panel 1: distribution of reply times, plus a separate never-answered bar.
        #x-axis categories
        names = [name for _, name in BUCKETS] + ["Never"]
        #bar heights
        counts = bucket_counts([r.days for r in answered]) + [len(unanswered)]
        #blue for answered buckets, orange for "Never"
        colors = ["#2a78d6"] * len(BUCKETS) + ["#eb6834"]
        #draw the bars
        bars = time_ax.bar(names, counts, color=colors)
        #print the count above each bar
        time_ax.bar_label(bars, padding=3)
        time_ax.set(title="Time from issue creation to first developer reply",
                    #titles and axis labels
                    xlabel="Time to first developer reply", ylabel="Number of issues")
        #leave room above the tallest bar for its label
        time_ax.set_ylim(0, max(counts + [1]) * 1.15)
        #tilt bucket names so they do not overlap
        time_ax.tick_params(axis="x", rotation=30)
        time_ax.legend(handles=[bars[0], bars[-1]],
                       #explain the two colours
                       labels=["Got a developer reply", "No developer reply"])

        #Panel 2: share of each common label answered fast, slowly, or never.
        #[(label, [fast, slow, never]), ...]
        rows = label_breakdown(records)
        #at least one issue had a label
        if rows:
            #reversed so the most common label is at the top
            labels = [label for label, _ in rows][::-1]
            #counts converted to percentages
            shares = [[100 * n / sum(row) for n in row] for _, row in rows][::-1]
            #where each stacked segment starts
            left = [0] * len(rows)
            #green segment
            parts = [(f"Reply within {FAST_DAYS} days", "#1baf7a"),
                     #blue segment
                     (f"Reply after {FAST_DAYS}+ days", "#2a78d6"),
                     #orange segment
                     ("Never replied", "#eb6834")]
            #draw one segment type at a time
            for index, (name, color) in enumerate(parts):
                #this segment's width for every label
                widths = [share[index] for share in shares]
                #horizontal stacked bar
                label_ax.barh(labels, widths, left=left, color=color, label=name)
                #next segment starts where this one ended
                left = [a + b for a, b in zip(left, widths)]
            label_ax.set(title=f"Developer reply outcome by label (top {len(rows)})",
                         #titles, axis label, 0-100 scale
                         xlabel="Share of issues with this label (%)", xlim=(0, 100))
            label_ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12),
                            #legend below the axis so it covers no bars
                            ncol=3, fontsize=9, frameon=False)
        #no labels at all in the selection
        else:
            #placeholder message
            label_ax.text(0.5, 0.5, "No labeled issues", ha="center", va="center")
            #hide the empty axes
            label_ax.set_axis_off()

        #fit everything without overlapping the main title
        fig.tight_layout(rect=[0, 0, 1, 0.94])
        #open the chart window (the program waits until it is closed)
        plt.show()


#only when this file is run directly, not when imported
if __name__ == "__main__":
    DeveloperResponseAnalysis().run()
