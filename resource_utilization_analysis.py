import matplotlib.pyplot as plt
import mplcyberpunk              # stylish dark theme + glow
import mplcursors                # hover‑tooltips
import pandas as pd
from typing import List, Set

import config
from data_loader import DataLoader
from model import Issue, Event, State


class ResourceUtilizationAnalysis:
    """
    Feature 2 – Resource Utilization
    • Charts use dark cyberpunk style with glow
    • Hovering any bar shows a tooltip
    • If >20 issues are assigned to real contributors, details saved as CSV
    """

    BOT_REGEX = r"\[bot\]"
    TOP_N     = 20
    CSV_NAME  = "assigned_contributor_issues.csv"

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

        # ---------- Plot A – Top contributors ----------------------
        self._plot_barh(
            df_contrib.head(self.TOP_N),
            value_col="num_issues",
            label_col="contributor",
            title=f"Top {self.TOP_N} Contributors by Issues Involved",
            xlabel="# Issues Involved",
            color="C0"
        )

        # ---------- Plot B – Top issue creators --------------------
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
                title=f"Top {self.TOP_N} Issue Creators",
                xlabel="# Issues Created",
                color="C1"
            )

        # ---------- EXTRA – issues assigned to real contributors ---
        real_contrib_set = set(df_contrib["contributor"])
        assigned_rows = []
        for issue in issues:
            real_assignees = [a for a in issue.assignees if a in real_contrib_set]
            if real_assignees:
                assigned_rows.append({
                    "issue_number": issue.number,
                    "title": issue.title,
                    "creator": issue.creator,
                    "assignees": ", ".join(real_assignees)
                })

        if not assigned_rows:
            print("\nNo issues assigned to real contributors.")
        elif len(assigned_rows) <= 20:
            print("\nIssues assigned to real contributors:")
            print(pd.DataFrame(assigned_rows)[
                  ["issue_number", "title", "creator", "assignees"]
                  ].to_string(index=False, max_colwidth=60))
        else:
            pd.DataFrame(assigned_rows).to_csv(self.CSV_NAME, index=False)
            print(f"\n{len(assigned_rows)} such issues – saved to {self.CSV_NAME}")

        plt.show()                        # display both charts

    # ===============================================================
    def _plot_barh(self, df: pd.DataFrame, *, value_col: str, label_col: str,
                   title: str, xlabel: str, color: str):
        """Draw horizontal bar‑chart with cyberpunk glow + hover tool‑tips."""
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

        fig.tight_layout()


# ------------------------------------------------------------------
if __name__ == "__main__":
    ResourceUtilizationAnalysis().run()
