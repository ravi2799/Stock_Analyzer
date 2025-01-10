from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
import os
from datetime import datetime

import yfinance as yf

from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

import streamlit as st #Como construir uma aplicação web rapida e facil
from crewai.tools import BaseTool
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults
# from custom_tool import YahooFinanceTool

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

@CrewBase
class DemoCrewai():
	"""DemoCrewai crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def stockPriceAnalyst(self) -> Agent:
		return Agent(
			config=self.agents_config['stockPriceAnalyst'],
			tools= [YahooFinanceTool()],
			allow_delegation = False,
			llm= ChatOpenAI(model='gpt-4o-mini'),
   			max_execution_time = 300, 
			verbose=True,
			max_iter=120,
		)
  
	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			allow_delegation = False,
			llm= ChatOpenAI(model='gpt-4o-mini'),
   			max_execution_time = 300, 
			verbose=True,
			max_iter=120,
		)

	@task
	def getStockPrice_task(self) -> Task:
		return Task(
			config=self.tasks_config['getStockPrice_task'],
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			output_file='report.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the DemoCrewai crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
