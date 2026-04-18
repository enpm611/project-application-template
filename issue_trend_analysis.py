from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from data_loader import DataLoader

class IssueTrendAnalysis:

    def __init__(self):
        self.issues = DataLoader().get_issues()

    def run(self):
        opened_per_year = defaultdict(int)
        closed_per_year = defaultdict(int)

        for issue in self.issues:
            if not issue.created_date:
                continue
            year = issue.created_date.year
            opened_per_year[year] += 1
            if issue.state == "closed":
                closed_per_year[year] += 1

        years = sorted(opened_per_year.keys())
        opened = [opened_per_year[y] for y in years]
        closed = [closed_per_year[y] for y in years]
        open_rate = [
            round((1 - closed_per_year[y] / opened_per_year[y]) * 100, 1)
            if opened_per_year[y] > 0 else 0
            for y in years
        ]

        print(f"\n{'='*55}")
        print(f"  Issue Volume Trends — python-poetry/poetry")
        print(f"{'='*55}")
        print(f"  {'Year':<8} {'Opened':>8} {'Closed':>8} {'% Still Open':>14}")
        print(f"  {'-'*44}")
        for y, o, c, r in zip(years, opened, closed, open_rate):
            print(f"  {y:<8} {o:>8,} {c:>8,} {r:>13.1f}%")
        print(f"  {'─'*44}")
        print(f"  {'TOTAL':<8} {sum(opened):>8,} {sum(closed):>8,}")

        peak_year = years[opened.index(max(opened))]
        worst_year = years[open_rate.index(max(open_rate))]
        print(f"\n  KEY FINDINGS:")
        print(f"    Peak activity year  : {peak_year} ({max(opened):,} issues opened)")
        print(f"    Highest open rate   : {worst_year} ({max(open_rate):.1f}% still open)")
        print(f"    Total issues        : {sum(opened):,}")
        print(f"    Overall close rate  : {sum(closed)/sum(opened)*100:.1f}%\n")

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), facecolor="#0d0d0d")
        fig.suptitle("Poetry GitHub Issues — Volume Trends Over Time",
                     color="white", fontsize=14, fontweight="bold")

        x = range(len(years))
        width = 0.4

        ax1.bar([i - width/2 for i in x], opened, width=width,
                color="#00d4ff", alpha=0.85, label="Opened")
        ax1.bar([i + width/2 for i in x], closed, width=width,
                color="#39ff14", alpha=0.85, label="Closed")
        for i, (o, c) in enumerate(zip(opened, closed)):
            ax1.text(i - width/2, o + 10, f"{o:,}", ha="center", color="white", fontsize=8)
            ax1.text(i + width/2, c + 10, f"{c:,}", ha="center", color="#39ff14", fontsize=8)
        ax1.set_xticks(list(x))
        ax1.set_xticklabels(years, color="white")
        ax1.set_ylabel("Number of Issues", color="white")
        ax1.set_title("Issues Opened vs Closed per Year", color="white", fontweight="bold")
        ax1.legend(facecolor="#1a1a1a", labelcolor="white")
        ax1.set_facecolor("#0d0d0d")
        ax1.tick_params(colors="grey")
        for sp in ax1.spines.values():
            sp.set_edgecolor("#333")
        ax1.yaxis.grid(True, linestyle="--", alpha=0.2)

        ax2.plot(list(x), open_rate, color="#ff6b35", linewidth=2.5,
                 marker="o", markersize=7)
        ax2.fill_between(list(x), open_rate, alpha=0.15, color="#ff6b35")
        for i, r in enumerate(open_rate):
            ax2.text(i, r + 0.5, f"{r:.1f}%", ha="center", color="white", fontsize=8)
        ax2.set_xticks(list(x))
        ax2.set_xticklabels(years, color="white")
        ax2.set_ylabel("% Still Open", color="white")
        ax2.set_title("Open Rate by Year", color="white", fontweight="bold")
        ax2.set_facecolor("#0d0d0d")
        ax2.tick_params(colors="grey")
        for sp in ax2.spines.values():
            sp.set_edgecolor("#333")
        ax2.yaxis.grid(True, linestyle="--", alpha=0.2)
        ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.0f%%"))

        plt.tight_layout()
        plt.savefig("issue_trends.png", dpi=160, bbox_inches="tight", facecolor="#0d0d0d")
        plt.show()
        print("  Chart saved to issue_trends.png")
