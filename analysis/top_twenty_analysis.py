import matplotlib.pyplot as plt
import mplcyberpunk              # stylish dark theme + glow
import mplcursors                # hover‑tooltips
import pandas as pd
from typing import List, Set
from collections import Counter

from Utils.data_loader import DataLoader
from models.model import Issue, State


class TopTwentyAnalysis:
    """
    Feature 2 -Resource Utilization
    • Charts use dark cyberpunk style with glow
    • Hovering any bar shows a tooltip
    """

    BOT_REGEX = r"\[bot\]"
    TOP_N     = 20

    # ---------------------------------------------------------------
    def run(self):
        plt.style.use("cyberpunk")        # cool dark background

        issues: List[Issue] = DataLoader().get_issues()

        # =====  build contributor → issue‑set map  =================
        contrib_issues: dict[str, set[int]] = {}
        for issue in issues:
            participants: Set[str] = set()
            if issue.creator:
                participants.add(issue.creator)
            participants.update([a for a in issue.assignees if a])
            participants.update([e.author for e in issue.events if e.author])

            for c in participants:
                contrib_issues.setdefault(c, set()).add(issue.number)

        df_contrib = (
            pd.DataFrame(
                [{"contributor": c, "num_issues": len(s)}
                 for c, s in contrib_issues.items()])
            .query("not contributor.str.contains(@self.BOT_REGEX, case=False)")
            .sort_values("num_issues", ascending=False)
            .reset_index(drop=True)
        )

        if df_contrib.empty:
            print("No real contributors (all bots).");  return

        print(f"Real contributors: {len(df_contrib)}")
        print(f"Top contributor: {df_contrib.iloc[0]['contributor']} "
              f"({df_contrib.iloc[0]['num_issues']} issues)")

        # ---------- Plot 1 – Top contributors ----------------------
        self._plot_barh(
            df_contrib.head(self.TOP_N),
            value_col="num_issues",
            label_col="contributor",
            title=f"Top {self.TOP_N} Contributors by Issues Involved",
            xlabel="# Issues Involved",
            color="C0"
        )

        # ---------- Plot 2 – Top issue creators --------------------
        df_creator_counts = (
            pd.DataFrame([i.creator for i in issues if i.creator], columns=["creator"])
            .query("not creator.str.contains(@self.BOT_REGEX, case=False)")
            .value_counts("creator")
            .reset_index(name="num_created")
            .sort_values("num_created", ascending=False)
        )

        if not df_creator_counts.empty:
            print(f"Top creator: {df_creator_counts.iloc[0]['creator']} "
                  f"({df_creator_counts.iloc[0]['num_created']} issues)")

            self._plot_barh(
                df_creator_counts.head(self.TOP_N),
                value_col="num_created",
                label_col="creator",
                title=f"Top {self.TOP_N} Issue Creators",
                xlabel="# Issues Created",
                color="C1"
            )

        # ----------  Plot 3 – Top 20 Closers ----------

        closers = []
        for issue in issues: # Get all the authors who closes a bug
            if issue.state == State.closed:
                for event in issue.events:
                    if event.event_type == "closed" and event.author is not None:
                        closers.append(event.author) 
                        break

        counts = Counter(closers) # Count how many bugs each author closed
        dframe_closers = ( # Prepare a data frame and sort it
            pd.DataFrame.from_records(
                list(counts.items()),
                columns=["author", "closes"]
            )
            .sort_values("closes", ascending=False)
            .reset_index(drop=True)
        )

        self._plot_barh(
            dframe_closers.head(self.TOP_N),
            value_col="closes",
            label_col="author",
            title=f"Top {self.TOP_N} Closers",
            xlabel="# Issues Closed",
            color="C2"
        )


        plt.show() # Display charts

    # ===============================================================
    def _plot_barh(self, df: pd.DataFrame, *, value_col: str, label_col: str,
                   title: str, xlabel: str, color: str):
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(df[label_col], df[value_col], color=color)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(label_col.capitalize())
        ax.invert_yaxis()
        mplcyberpunk.add_glow_effects()   # neon glow

        # --- hover tool‑tips via mplcursors -----------------------
        cursor = mplcursors.cursor(bars, hover=True)
        @cursor.connect("add")
        def _show_tooltip(sel):
            idx = sel.index
            label = df.iloc[idx][label_col]
            val   = df.iloc[idx][value_col]
            sel.annotation.set_text(f"{label}\n{val}")
            sel.annotation.set_fontsize(10)
            sel.annotation.get_bbox_patch().update(
                {
                    "fc": "#0d1b2acc",
                    "ec": "#00ffe7",
                    "lw": 1.2,
                    "boxstyle": "round,pad=0.35"
                }
            )

        fig.tight_layout()


# ------------------------------------------------------------------
if __name__ == "__main__":
    TopTwentyAnalysis().run()
