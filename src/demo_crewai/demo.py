import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])  # Added --upgrade

#Import das LIBS
import json
import os
from datetime import datetime

import yfinance as yf

from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

import streamlit as st #Como construir uma aplicação web rapida e facil
from crewai.tools import BaseTool
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults


# Criada função 
def fetch_stock_price(ticket):
    stock = yf.download(ticket, start="2025-01-01", end='2025-01-08')
    stock = yf.Ticker(ticket)
    # Fetch historical price data (price, volume, etc.) for the specified period
    data = {
        "history": stock.history(period="1y")
    }

    data["financials"] = stock.financials
    data["quarterly_financials"] = stock.quarterly_financials


    data["balance_sheet"] = stock.balance_sheet
    data["quarterly_balance_sheet"] = stock.quarterly_balance_sheet


    data["cashflow"] = stock.cashflow
    data["quarterly_cashflow"] = stock.quarterly_cashflow


    data["splits"] = stock.splits


    data["dividends"] = stock.dividends


    data["recommendations"] = stock.recommendations


    data["sustainability"] = stock.sustainability

    key_metrics = {
        "market_cap": stock.info.get("marketCap"),
        "p_e_ratio": stock.info.get("trailingPE"),
        "eps": stock.info.get("trailingEps"),
        "dividend_yield": stock.info.get("dividendYield"),
        "dividend_rate": stock.info.get("dividendRate")
    }
    data["key_metrics"] = key_metrics

    return data

yahoo_finance_tool = Tool(
    name = "Yahoo Finance Tool",
    description = "Fetches stock prices for {ticket} from the last year using Yahoo Finance API.",
    func = lambda ticket: fetch_stock_price(ticket)
)

# Importar LLM
llm = ChatOpenAI(model='gpt-3.5-turbo')

# Create Agent AI
stockPriceAnalyst = Agent(
    llm= llm,
    max_iter = 150,  # Aumentar o limite de iterações
    memory= True,
    tools= [yahoo_finance_tool],
    allow_delegation = False,
    max_execution_time = 300  # Definir um limite de tempo de 5 minutos
)

getStockPrice = Task(
    description = "Analyze the stock {ticket} stock create a detailed report.",
    expected_output = """Your analysis should cover the following aspects: 
        1. Identify any significant price movements (e.g., large price increases or decreases).
        2. Analyze the overall trend of the stock during this period.
        3. Compare the stock's performance over this range to prior performance if available.
        4. Provide insights or possible reasons for price changes, such as market trends, company news, or external factors.""",
    agent = stockPriceAnalyst
)

from crewai.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun


crew = Crew(
    agents = [stockPriceAnalyst],
    tasks = [getStockPrice],
    verbose = True,
    process = Process.hierarchical,
    full_output = True,
    share_crew=False,
    manager_llm = llm,
    max_iter = 150,  # Aumentar o limite de iterações,
    max_execution_time = 600
)

# Executar 
#results = crew.kickoff(inputs={'ticket': 'AAPL'})

with st.sidebar:
    st.header('Enter the stock to Research')

    with st.form(key='research_form'):
        topic = st.text_input("Select the ticket")
        submit_button = st.form_submit_button(label= "Run Research")

if submit_button:
    if not topic:
        st.error("Please fill the ticket field")
    else: 
        results = crew.kickoff(inputs={'ticket': topic})

        st.subheader("Results of your research:")
        print(results)
        st.write(results)