from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import yfinance as yf
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun


    
class StockDataTool(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol") 
    period: str = Field(..., description="Historical data period")
    fetch_financials: bool = Field(True, description="Fetch financial data")
    fetch_balance_sheet: bool = Field(True, description="Fetch balance sheet data")
    fetch_cashflow: bool = Field(True, description="Fetch cash flow data")
    fetch_splits: bool = Field(True, description="Fetch stock splits data")
    fetch_dividends: bool = Field(True, description="Fetch dividend data")
    fetch_recommendations: bool = Field(True, description="Fetch analyst recommendations")
    fetch_sustainability: bool = Field(False, description="Fetch sustainability data")
    fetch_key_metrics: bool = Field(True, description="Fetch key metrics data")
    
class StockDataTool(BaseTool):
    name: str = "StockDataTool"
    description: str = "Fetches stock data, financial metrics, and other key data using yfinance"
    args_schema: Type[BaseModel] = StockDataTool
     
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
        print("INFO: Fetching data for", stock)
        

        # Fetch historical price data (price, volume, etc.) for the specified period
        data = {
            "history": stock.history(period=period)
        }
        print("INFO: Fetching historical data for", data)
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


class StockAnalysisInput(BaseModel):
    stock_data: dict = Field(..., description="Stock data to analyze")

class StockAnalysisTool(BaseTool):
    name: str = "StockAnalysisTool"
    description: str = "Analyzes stock data for trends, moving averages, and RSI"
    args_schema: Type[BaseModel] = StockAnalysisInput

    def _run(self, stock_data: dict):
        import pandas as pd
        df = pd.DataFrame(stock_data)
        df['50_MA'] = df['Close'].rolling(window=50).mean()
        df['200_MA'] = df['Close'].rolling(window=200).mean()
        return df.to_dict()
    
class DuckDuckgonput(BaseModel):
    query: str = Field(..., description="Query to search for")
    
class MyCustomDuckDuckGoTool(BaseTool):
        name: str = "DuckDuckGo Search Tool"
        description: str = "Search the web for a given query."
        args_schema: Type[BaseModel] = DuckDuckgonput


        def _run(self, query: str) -> str:
            # Ensure the DuckDuckGoSearchRun is invoked properly.
            duckduckgo_tool = DuckDuckGoSearchRun()
            response = duckduckgo_tool.invoke(query)
            news_list = [result['title'] for result in response]
            return news_list

        def _get_tool(self):
            # Create an instance of the tool when needed
            return MyCustomDuckDuckGoTool()
        
# class DuckDuckGoSearchTool(BaseTool):
#     name: str = "DuckDuckGoSearchTool"  # Added type annotation
#     description: str = "Fetches relevant financial news using DuckDuckGo"  # Added type annotation

#     def _run(self, query: str):
#         from duckduckgo_search import ddg
#         results = ddg(query, max_results=5)
#         news_list = [result['title'] for result in results]
#         return news_list

class ReportInput(BaseModel):
    stock_data: dict = Field(..., description="Stock data to analyze")
    analysis_data: dict = Field(..., description="Analysis data")
    news: list = Field(..., description="List of news articles")
    
class ReportPublisherTool(BaseTool):
    name: str = "ReportPublisherTool"  # Added type annotation
    description: str = "Generates a report from the stock data, analysis, and news"  # Added type annotation
    args_schema: Type[BaseModel] = ReportInput

    def _run(self, stock_data, analysis_data, news):
        report = f"Stock Data: {stock_data}\n\nAnalysis: {analysis_data}\n\nNews: {news}"
        return report


stock_data_tool = StockDataTool()
stock_analysis_tool = StockAnalysisTool()
duckduckgo_search_tool = MyCustomDuckDuckGoTool()
report_publisher_tool = ReportPublisherTool()


# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class stock_crew():
    """ExpandIdea crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def stock_data_fetch_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_data_fetche'],
            allow_delegation=False,
            tools=[stock_data_tool],
            verbose=True
        )
    
    @agent
    def stock_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_analyst'],
            allow_delegation=False,
            tools=[stock_analysis_tool],
            verbose=True
        )
    @agent
    def stock_news_fetch_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_news_fetcher'],
            allow_delegation=False,
            tools=[duckduckgo_search_tool],
            verbose=True
        )
    @agent
    def stock_report_publisher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_report_publisher'],
            allow_delegation=False,
            tools=[report_publisher_tool],
            verbose=True
        )
    
    @agent
    def python_data_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['python_data_analyst'],
            allow_delegation=True,
            allow_code_execution=True,
            verbose=True
        )
     
    @task
    def stock_data_fetch_task(self) -> Task: 
        return Task(
            config=self.tasks_config['task1'],
            agent=self.stock_data_fetch_agent(),
        )
        
    @task
    def stock_analyst_task(self) -> Task: 
        return Task(
            config=self.tasks_config['task2'],
            agent=self.stock_analyst_agent(),
        )
        
    @task
    def stock_news_fetcher_task(self) -> Task: 
        return Task(
            config=self.tasks_config['task3'],
            agent=self.stock_news_fetch_agent(),
        )
        
    @task
    def stock_report_publisher_task(self) -> Task: 
        return Task(
            config=self.tasks_config['task4'],
            agent=self.stock_report_publisher_agent(),
        )
    
    @task
    def python_data_analyst_task(self) -> Task: 
        return Task(
            config=self.tasks_config['task5'],
            agent=self.python_data_analyst_agent(),
        )
           
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            manager_llm=ChatOpenAI(temperature=0, model="gpt-4"),  # Mandatory if manager_agent is not set
            process=Process.hierarchical,
            verbose=True,
        )
        

