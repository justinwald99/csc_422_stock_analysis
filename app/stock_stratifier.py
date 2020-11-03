import datetime as dt
import sys
import os

import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import pandas as pd

# How many days ahead to compute the average of
DAYS_AHEAD = 20
TIME_DELTA = dt.timedelta(days=DAYS_AHEAD)
# How many samples to take of each strata.
TOP_N = 3
TWITTER_START_DATE = dt.datetime(2007, 1, 1)

# Usage validation
if (len(sys.argv) != 2):
    print("Usage: python stock_stratifer.py [ticker]")
    exit(1)

# Find stock history
ticker = sys.argv[1]
stock_history_files = os.listdir("data/stocks")
tickers = list(pd.DataFrame([name[:-7] for name in stock_history_files], columns=["ticker"])["ticker"])
if ticker not in tickers:
    print("Ticker not found in files.")
    exit(1)

# Read stock history
data = pd.read_csv(f"data/stocks/{ticker}.us.txt")
data["Date"] = pd.to_datetime(data["Date"])
data = data.loc[data["Date"] > TWITTER_START_DATE]
data.reset_index(inplace=True)

# Graph historical data
plt.gcf().set_size_inches([10, 5])
plt.plot("Date", "Close", data=data)
plt.title(f"Strata chart for {ticker} with average gains over next {DAYS_AHEAD} days.")
plt.gca().yaxis.set_major_locator(tick.AutoLocator())
plt.grid(which="both")
plt.gca().yaxis.set_major_formatter("${x}")

avg_chng = pd.DataFrame(columns=["avg_inc", "day"])

# Compute the rolling average change over a period of 20 days.
for index, day in data[:-DAYS_AHEAD].iterrows():
    total_change = 0
    # Determine the average increase in the next DAYS_AHEAD.
    for future_day in range(1, DAYS_AHEAD + 1):
        total_change += (data.iloc[index + future_day]["Close"] - day["Close"]) / day["Close"]
    avg_inc = total_change / DAYS_AHEAD
    new_entry = pd.DataFrame([[avg_inc, day]], columns=["avg_inc", "day"])
    avg_chng = avg_chng.append(new_entry)

# Sort by average percent growth in DAYS_AHEAD business days
sorted_avgs = avg_chng.sort_values("avg_inc", ascending=False)
sorted_avgs.reset_index(drop=True, inplace=True)

# Top increase, top decrease, and neutral.
top_inc = sorted_avgs.head(TOP_N).reset_index(drop=True)
top_dec = sorted_avgs.tail(TOP_N).reset_index(drop=True)
mid_point = int(len(sorted_avgs) / 2)
neutral = sorted_avgs[mid_point: mid_point + TOP_N].reset_index(drop=True)


# top_n_df is ordered in ascending order by percent.
# runner_up_df is ordered in descending order (most desirable first.)
# but the top_n have been removed.
def check_intersects(top_n_df, runner_up_df):
    # Iterate through each candidate
    for index, record in top_n_df[0:-1].iterrows():
        # Get span of date in quesiton
        start_date = record["day"]["Date"]
        end_date = start_date + TIME_DELTA
        # Compare against remaining dates
        for other_index, other_record in top_n_df.iterrows():
            other_date = other_record["day"]["Date"]
            # Ignore self
            if other_index is not index:
                # Is there an intersection?
                if (start_date <= other_date <= end_date or
                        start_date <= other_date + TIME_DELTA <= end_date):
                    # Replace the offending other date with next in runner_up_df.
                    top_n_df.drop(other_index, inplace=True)
                    top_n_df = top_n_df.append(runner_up_df.head(1), ignore_index=True)
                    runner_up_df.drop(0, inplace=True)
                    runner_up_df.reset_index(drop=True, inplace=True)
                    # Retest.
                    return check_intersects(top_n_df, runner_up_df)
    return top_n_df


top_inc = check_intersects(top_inc, sorted_avgs[TOP_N:].reset_index(drop=True))
neutral = check_intersects(neutral, sorted_avgs[mid_point + TOP_N:].reset_index(drop=True))
top_dec = check_intersects(top_dec, sorted_avgs.reindex(index=sorted_avgs.index[::-1])[TOP_N:].reset_index(drop=True))

# Create matplotlib graph.
for index, record in top_inc.iterrows():
    plt.gca().axvspan(record["day"]["Date"], record["day"]["Date"] + TIME_DELTA,
                      alpha=(TOP_N - index) / TOP_N * .8, color="g",
                      label=f"{record['day']['Date'].strftime('%y-%m-%d')} ({round(record['avg_inc'] * 100, 1)}%)")

for index, record in top_dec.iterrows():
    plt.gca().axvspan(record["day"]["Date"], record["day"]["Date"] + TIME_DELTA,
                      alpha=(TOP_N - index) / TOP_N * .8, color="r",
                      label=f"{record['day']['Date'].strftime('%y-%m-%d')} ({round(record['avg_inc'] * 100, 1)}%)")

for index, record in neutral.iterrows():
    plt.gca().axvspan(record["day"]["Date"], record["day"]["Date"] + TIME_DELTA,
                      alpha=(TOP_N - index) / TOP_N * .5, color="b",
                      label=f"{record['day']['Date'].strftime('%y-%m-%d')} ({round(record['avg_inc'] * 100, 1)}%)")

plt.legend(bbox_to_anchor=[1, 1])
plt.tight_layout()

# Write dates to output csv
with open(f"data/strata/{ticker}_strata.csv", "w", encoding="utf-8") as csv:
    csv.write("class,date,percent\n")
    for index, record in top_inc.iterrows():
        csv.write(f"increase,{record['day']['Date']},{round(record['avg_inc'], 2)}\n")
    for index, record in top_dec.iterrows():
        csv.write(f"decrease,{record['day']['Date']},{round(record['avg_inc'], 2)}\n")
    for index, record in neutral.iterrows():
        csv.write(f"neutral,{record['day']['Date']},{round(record['avg_inc'], 2)}\n")

# Save graph
plt.savefig(f"data/strata/{ticker}_strata.jpg", pil_kwargs={"optimize": True, "progressive": True, "quality": 90})

plt.show()
