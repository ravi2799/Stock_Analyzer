from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import yfinance as yf
from typing import Dict, Any


class YahooFinanceInput(BaseModel):
    ticket: str = Field(..., description="The stock ticker symbol")

class YahooFinanceTool(BaseTool):
    name: str = "Yahoo Finance Tool"
    description: str = "Fetches comprehensive stock data for a given ticker symbol using Yahoo Finance API."
    args_schema: type[BaseModel] = YahooFinanceInput

    def _run(self, ticket: str) -> Dict[str, Any]:
        stock = yf.Ticker(ticket)
        
        data = {
            "history": stock.history(period="1y").to_dict(),
            "financials": stock.financials.to_dict(),
            "quarterly_financials": stock.quarterly_financials.to_dict(),
            "balance_sheet": stock.balance_sheet.to_dict(),
            "quarterly_balance_sheet": stock.quarterly_balance_sheet.to_dict(),
            "cashflow": stock.cashflow.to_dict(),
            "quarterly_cashflow": stock.quarterly_cashflow.to_dict(),
            "splits": stock.splits.to_dict(),
            "dividends": stock.dividends.to_dict(),
            "recommendations": stock.recommendations.to_dict() if stock.recommendations is not None else None,
            "sustainability": stock.sustainability.to_dict() if stock.sustainability is not None else None,
            "key_metrics": {
                "market_cap": stock.info.get("marketCap"),
                "p_e_ratio": stock.info.get("trailingPE"),
                "eps": stock.info.get("trailingEps"),
                "dividend_yield": stock.info.get("dividendYield"),
                "dividend_rate": stock.info.get("dividendRate")
            }
        }
        
        return data


