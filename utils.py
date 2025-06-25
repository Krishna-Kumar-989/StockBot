import pandas as pd

from classes import *

import pandas_ta as ta


import feedparser
from urllib.parse import quote_plus


import os
import requests

from dotenv import load_dotenv








load_dotenv()
PRICE_API_KEY = os.getenv("API_KEY")


BASE_URL = "https://stock.indianapi.in/historical_data"
DEFAULT_FILTER = "price"
DEFAULT_MONTHS = 1


def convert_months_to_period(months: int) -> str:
    """
    Convert number of months to API period string (e.g., 6 -> '6m', 12 -> '1y', 24 -> '2y').
    """
    if months < 12:
        return f"{months}m"
    elif months == 12:
        return "1y"
    else:
        years = months // 12
        return f"{years}y"











######################################################################################################################


##GET PRICE DATA


def fetch_stock_data(stock_name: str, months: int = DEFAULT_MONTHS, filter_type: str = DEFAULT_FILTER) -> list:
    """
    Fetch raw datasets from API for a given stock and period.

    Parameters:
        - stock_name: e.g. 'TCS'
        - months: number of months (default 1)
        - filter_type: metric filter (e.g. 'price' or 'volume')

    Returns:
        list of dataset dicts as received from the API.
    """
    period = convert_months_to_period(months)
    headers = {"x-api-key": PRICE_API_KEY}
    params = {"stock_name": stock_name, "period": period, "filter": filter_type}

    resp = requests.get(BASE_URL, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data.get("datasets", [])


def stock_data(stock_name: str, months: int = DEFAULT_MONTHS, filter_type: str = DEFAULT_FILTER) -> pd.DataFrame:
    """
    Fetches stock historical data and returns a flat pandas DataFrame with columns:
    ['metric', 'label', 'date', 'value', 'delivery'].

    Parameters:
        - stock_name: e.g. 'TCS'
        - months: number of months (default 1)
        - filter_type: metric filter (e.g. 'price' or 'volume')

    Returns:
        pd.DataFrame
    """
    datasets = fetch_stock_data(stock_name, months, filter_type)
    records = []

    for ds in datasets:
        metric = ds.get("metric", "")
        label = ds.get("label", metric)

        for entry in ds.get("values", []):
            
            if metric.lower() == "volume":
                date, volume, meta = entry
                delivery = meta.get("delivery", "")
                records.append({
                    "metric": metric,
                    "label": label,
                    "date": date,
                    "value": volume,
                    "delivery": delivery
                })
            else:
                date, value = entry
                records.append({
                    "metric": metric,
                    "label": label,
                    "date": date,
                    "value": value,
                    "delivery": ""
                })

    
    df = pd.DataFrame(records, columns=["metric", "label", "date", "value", "delivery"])
    return df



















########################################################################################################################




def get_news_data(keyword: str, top_n: int = 10) -> pd.DataFrame:
    """
    Fetches top news articles for a given keyword from Google News RSS
    and returns a pandas DataFrame where each row contains a single
    combined "news" column (title, published date, and summary).

    Parameters:
    - keyword (str): The search term for news articles.
    - top_n (int): Maximum number of articles to fetch.

    Returns:
    - pd.DataFrame: DataFrame containing a single column ['news'].
    """
    keyword = str(keyword)
    encoded_keyword = quote_plus(keyword)
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(rss_url)

    combined_articles = []
    seen_titles = set()

    for entry in feed.entries:
        title = entry.title.strip()
        if title in seen_titles:
            continue
        seen_titles.add(title)

        published = entry.get("published", "").strip()
        summary = entry.get("summary", "").strip()

        
        parts = []
        if title:
            parts.append(f"Title: {title}")
        if published:
            parts.append(f"Published: {published}")
        if summary:
            parts.append(f"Summary: {summary}")

        combined_text = " | ".join(parts)
        combined_articles.append({"news": combined_text})

        if len(combined_articles) >= top_n:
            break

 
    df = pd.DataFrame(combined_articles, columns=["news"])
    return df































##############################################################################################################################
