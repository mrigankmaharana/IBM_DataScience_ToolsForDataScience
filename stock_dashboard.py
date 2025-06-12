import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


def get_stock_data(ticker: str) -> pd.DataFrame:
    """Fetch historical market data for the given ticker."""
    data = yf.Ticker(ticker).history(period="max")
    data.reset_index(inplace=True)
    return data


def get_revenue_data(url: str) -> pd.DataFrame:
    """Scrape revenue data table from Macrotrends."""
    headers = {"User-Agent": "Mozilla/5.0"}
    html_data = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html_data, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        raise ValueError("No tables found. The website structure may have changed.")

    revenue = pd.read_html(str(tables[0]))[0]
    revenue.columns = ["Date", "Revenue"]
    revenue.dropna(inplace=True)
    revenue["Revenue"] = revenue["Revenue"].replace("$", "", regex=True)
    revenue["Revenue"] = revenue["Revenue"].replace(",", "", regex=True)
    revenue["Revenue"] = pd.to_numeric(revenue["Revenue"], errors="coerce")
    revenue.dropna(inplace=True)
    return revenue


def make_dashboard(stock_df: pd.DataFrame, revenue_df: pd.DataFrame, title: str) -> None:
    """Plot stock closing price and revenue on a dual-axis chart."""
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(stock_df["Date"], stock_df["Close"], color="tab:blue", label="Close")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Stock Price ($)", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    ax2 = ax1.twinx()
    ax2.bar(revenue_df["Date"], revenue_df["Revenue"], alpha=0.3, color="tab:gray", label="Revenue")
    ax2.set_ylabel("Revenue (USD)", color="tab:gray")
    ax2.tick_params(axis="y", labelcolor="tab:gray")

    fig.suptitle(title)
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    tesla_data = get_stock_data("TSLA")
    tesla_revenue = get_revenue_data("https://www.macrotrends.net/stocks/charts/TSLA/tesla/revenue")
    make_dashboard(tesla_data, tesla_revenue, "Tesla Stock Price vs Revenue")

    gme_data = get_stock_data("GME")
    gme_revenue = get_revenue_data("https://www.macrotrends.net/stocks/charts/GME/gamestop/revenue")
    make_dashboard(gme_data, gme_revenue, "GameStop Stock Price vs Revenue")
