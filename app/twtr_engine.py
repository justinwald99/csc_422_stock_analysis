import os
import datetime as dt
import pandas as pd
import requests
import yaml

# global df of stock file
stock_data = None


def twtr_engine():
    ticker = get_ticker_symbol()
    load_stock_data(ticker)
    company_name = get_company_name(ticker)
    start_date, end_date = get_time_frame(ticker)
    response = make_api_call(company_name, start_date, end_date)
    log_response(ticker, response)


def log_response(ticker, response):
    with open(f"data/tweets/{ticker}_twt.csv", "a", encoding="utf-8") as csv:
        csv.write("id,date,tweet\n")
        for index, tweet in enumerate(response["data"]):
            text = tweet['text'].replace('\n', "")
            csv.write(f"{index},{tweet['created_at']},\"{text}\"\n")


def make_api_call(company, start_date, end_date):
    endpoint = "https://api.twitter.com/2/tweets/search/recent"
    auth = {"Authorization": f"Bearer {get_bearer_token()}"}
    request_parameters = {
        "query": f"{company} lang:en",
        "start_time": start_date.replace(tzinfo=dt.timezone.utc).isoformat(timespec="seconds"),
        "end_time": end_date.replace(tzinfo=dt.timezone.utc).isoformat(timespec="seconds"),
        "tweet.fields": "created_at",
        "max_results": 10
    }
    response = requests.get(url=endpoint, params=request_parameters, headers=auth)
    print(response.text)
    return response.json()


def get_bearer_token():
    with open("secrets/secrets.yaml") as secrets:
        creds = yaml.safe_load(secrets)
    return creds["bearer_token"]


def get_time_frame(ticker):
    # determine the earliest and latest dates.
    twitter_start_date = dt.datetime(2006, 3, 21)
    earliest_date = dt.datetime.fromisoformat(stock_data["Date"].min())
    latest_date = dt.datetime.now()

    # ensure earliest date is after the start of twitter
    if (earliest_date < twitter_start_date):
        earliest_date = twitter_start_date
        print("\nData is available from before the start of Twitter, "
              "using twitter's start date (2006-03-21) as a minimum.")
    else:
        print(f"Earliest data available: {earliest_date}.")

    # collect from_date
    print("\nEnter date range(enter for earliest_date -> today): ")
    from_date = None
    while(from_date is None):
        print("Enter the date (yyyy-mm-dd) to start search from:")
        try:
            user_input = input()
            if not user_input:
                user_date = earliest_date
            else:
                user_date = dt.datetime.fromisoformat(user_input)
        except Exception as e:
            print(e)
        if (user_date < earliest_date or user_date > latest_date):
            print("Invalid start date")
        else:
            from_date = user_date

    # collect to_date
    to_date = None
    while(to_date is None):
        print("Enter the date (yyyy-mm-dd) to end search at:")
        try:
            user_input = input()
            if not user_input:
                user_date = latest_date
            else:
                user_date = dt.datetime.fromisoformat(user_input)
        except Exception as e:
            print(e)
        if (user_date > latest_date or user_date < from_date):
            print("Invalid end date")
        else:
            to_date = user_date
    print(f"Selected time-range: {from_date} -> {to_date}")
    return (from_date, to_date)


def get_company_name(ticker):
    company_lookup = pd.read_csv("data/companies/companies.csv")
    company_entry = company_lookup[company_lookup["ticker"] == ticker.upper()]
    company_name = company_entry["short name"].item()
    print(f"Found company: {company_name}")
    return company_name


def get_ticker_symbol():
    # get user input
    print("Enter a ticker symbol you're interested in retrieving tweets for (ex: aapl): ")
    ticker = input()
    stocks = get_stock_file_names()
    # ensure a stock record is available
    if (ticker not in list(stocks["ticker"])):
        exit("Ticker not found in stock archive.")
    return ticker


def get_stock_file_names():
    # retrieve filenames
    stock_history_files = os.listdir("data/stocks")
    # form a list of file names by slicing the last 7 characters from
    # the end of the the filenames (.us.txt)
    return pd.DataFrame([name[:-7] for name in stock_history_files], columns=["ticker"])


def load_stock_data(ticker):
    global stock_data
    stock_data = pd.read_csv(f"data/stocks/{ticker}.us.txt")


if __name__ == "__main__":
    twtr_engine()
