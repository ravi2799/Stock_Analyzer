from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import yfinance as yf

class StockDataTool(BaseTool):
    name: str = "Stock Data Tool"
    description: str = "Fetches stock data, financial metrics, and other key data using yfinance"

    def _run(self, ticker: str, period: str = "5y",
             fetch_financials: bool = True,
             fetch_balance_sheet: bool = True,
             fetch_cashflow: bool = True,
             fetch_splits: bool = True,
             fetch_dividends: bool = True,
             fetch_recommendations: bool = True,
             fetch_sustainability: bool = False,
             fetch_key_metrics: bool = True):

        # Fetch stock data from yfinance
        stock = yf.Ticker(ticker)

        # Fetch historical price data (price, volume, etc.) for the specified period
        data = {
            "history": stock.history(period=period)
        }

        # Optionally fetch financial data
        if fetch_financials:
            data["financials"] = stock.financials
            data["quarterly_financials"] = stock.quarterly_financials

        # Optionally fetch balance sheet
        if fetch_balance_sheet:
            data["balance_sheet"] = stock.balance_sheet
            data["quarterly_balance_sheet"] = stock.quarterly_balance_sheet

        # Optionally fetch cash flow
        if fetch_cashflow:
            data["cashflow"] = stock.cashflow
            data["quarterly_cashflow"] = stock.quarterly_cashflow

        # Optionally fetch stock splits
        if fetch_splits:
            data["splits"] = stock.splits

        # Optionally fetch dividend data
        if fetch_dividends:
            data["dividends"] = stock.dividends

        # Optionally fetch analyst recommendations
        if fetch_recommendations:
            data["recommendations"] = stock.recommendations

        # Optionally fetch sustainability scores (ESG)
        if fetch_sustainability:
            data["sustainability"] = stock.sustainability

        # Optionally fetch key metrics (P/E ratio, market cap, EPS, dividend yield)
        if fetch_key_metrics:
            key_metrics = {
                "market_cap": stock.info.get("marketCap"),
                "p_e_ratio": stock.info.get("trailingPE"),
                "eps": stock.info.get("trailingEps"),
                "dividend_yield": stock.info.get("dividendYield"),
                "dividend_rate": stock.info.get("dividendRate")
            }
            data["key_metrics"] = key_metrics

        return data


class StockAnalysisTool(BaseTool):
    name: str = "Stock Analysis Tool"  # Added type annotation
    description: str = "Analyzes stock data for trends, moving averages, and RSI"  # Added type annotation

    def _run(self, stock_data):
        import pandas as pd
        stock_data['50_MA'] = stock_data['Close'].rolling(window=50).mean()
        stock_data['200_MA'] = stock_data['Close'].rolling(window=200).mean()
        return stock_data

class DuckDuckGoSearchTool(BaseTool):
    name: str = "News Search Tool"  # Added type annotation
    description: str = "Fetches relevant financial news using DuckDuckGo"  # Added type annotation

    def _run(self, query: str):
        from duckduckgo_search import ddg
        results = ddg(query, max_results=5)
        news_list = [result['title'] for result in results]
        return news_list

class ReportPublisherTool(BaseTool):
    name: str = "Report Publisher Tool"  # Added type annotation
    description: str = "Generates a report from the stock data, analysis, and news"  # Added type annotation

    def _run(self, stock_data, analysis_data, news):
        report = f"Stock Data: {stock_data}\n\nAnalysis: {analysis_data}\n\nNews: {news}"
        return report

