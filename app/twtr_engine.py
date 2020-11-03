from datetime import timedelta
import os
import pandas as pd
import requests
import yaml

# global df of stock file
stock_data = None

# Hour of the day to get tweets from (24h)
SAMPLE_HOUR = 17


def twtr_engine():
    ticker = get_ticker_symbol()
    load_stock_data(ticker)
    company_name = get_company_name(ticker)
    time_strata = get_time_strata(ticker)
    for index, date in time_strata.iterrows():
        response = make_api_call(company_name, date["date"])
        log_response(ticker, response, date)


def log_response(ticker, response, date):
    if (os.path.exists(f"data/tweets/{ticker}_twt.csv")):
        output = pd.read_csv(f"data/tweets/{ticker}_twt.csv", index_col="id")
    else:
        output = pd.DataFrame(columns=["date", "class", "percent", "text"])

    for index, tweet in enumerate(response["results"]):
        text = tweet['text'].replace('\n', "")
        new_record = {"date": date["date"].isoformat(), "class": date["class"],
                      "percent": date["percent"], "text": text}
        output = output.append(new_record, ignore_index=True)
    output.to_csv(f"data/tweets/{ticker}_twt.csv", index_label="id")


def make_api_call(company, date):
    endpoint = "https://api.twitter.com/1.1/tweets/search/fullarchive/full.json"
    auth = {"Authorization": f"Bearer {get_bearer_token()}"}
    request_parameters = {
        "query": f"{company} lang: en -has:links -has:images -has:media",
        "maxResults": 100,
        "toDate": date.strftime("%Y%m%d%H%m")
    }
    response = requests.get(url=endpoint, params=request_parameters, headers=auth)
    print(response.text)
    return response.json()


def get_bearer_token():
    with open("secrets/secrets.yaml") as secrets:
        creds = yaml.safe_load(secrets)
    return creds["bearer_token"]


def get_time_strata(ticker):
    # load a list of all the valid strata files
    strata_files = os.listdir("data/strata")

    # ensure ticker has a strata record
    if ticker not in (file[0:file.index("_")] for file in strata_files):
        print(f"Could not find time strata for {ticker}.")
        exit(0)

    # retrieve the strata
    time_strata = pd.read_csv(f"data/strata/{ticker}_strata.csv", parse_dates=["date"])

    # report loaded strata
    print("Loaded the following time strata:")
    time_strata["date"] = time_strata["date"] + timedelta(hours=SAMPLE_HOUR)
    print(time_strata[["class", "date", "percent"]])
    return time_strata


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
