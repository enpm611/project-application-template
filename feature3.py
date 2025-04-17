import matplotlib.pyplot as plt
import numpy as np
from data_loader import DataLoader


def feature3():
    from model import Issue  # optional but helps for static typing/debugging

    print("✅ Feature 3: Issue Age Distribution started.")
    issues = DataLoader().get_issues()
    print(f"✅ Loaded {len(issues)} issues.")

    days_open_list = []
    valid = 0
    skipped_missing = 0
    skipped_invalid = 0

    for issue in issues:
        created_at = issue.created_date
        closed_at = issue.closed_date

        if not created_at or not closed_at:
            skipped_missing += 1
            continue

        try:
            delta = (closed_at - created_at).days
            if delta >= 0:
                days_open_list.append(delta)
                valid += 1
                if valid <= 5:  # Print first 5 valid for manual check
                    print(f"[VALID] {issue.url} — {delta} days (Created: {created_at}, Closed: {closed_at})")
            else:
                skipped_invalid += 1
                print(f"⚠️ Invalid] Negative delta for {issue.url}: {created_at} -> {closed_at}")
        except Exception as e:
            skipped_invalid += 1
            print(f"[⚠️ Exception] {issue.url} — {e}")

    print("\n📊 Summary:")
    print(f"✅ Issues used in plot: {valid}")
    print(f"❌ Skipped due to missing dates: {skipped_missing}")
    print(f"⚠️ Skipped due to invalid date math: {skipped_invalid}")
    print(f"📈 Final data points plotted: {len(days_open_list)}")

    if not days_open_list:
        print("🚫 No valid issues with closure duration found.")
        return

    # Histogram
    plt.figure(figsize=(10, 6))
    plt.hist(days_open_list, bins=20, edgecolor='black')
    plt.title("Distribution of Issue Time-to-Close")
    plt.xlabel("Days Open")
    plt.ylabel("Number of Issues")
    plt.grid(True)
    plt.show()

    # Box Plot
    plt.figure(figsize=(6, 4))
    plt.boxplot(days_open_list, vert=False)
    plt.title("Box Plot of Issue Closure Times")
    plt.xlabel("Days Open")
    plt.grid(True)
    plt.show()
