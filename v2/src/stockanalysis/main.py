#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
from stockanalysis.crew import stock_crew as Stockanalysis
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def calculate_start_date(analysis_date: str, information_range: str):
    analysis_datetime = datetime.strptime(analysis_date, '%Y-%m-%d')

    # Calculate the start date based on the information range
    if information_range == '1m':
        start_datetime = analysis_datetime - relativedelta(months=1)
    elif information_range == '3m':
            start_datetime = analysis_datetime - relativedelta(months=3)
    elif information_range == '6m':
        start_datetime = analysis_datetime - relativedelta(months=6)
    elif information_range == '1y':
        start_datetime = analysis_datetime - relativedelta(years=1)
    elif information_range == '2y':
        start_datetime = analysis_datetime - relativedelta(years=2)
    elif information_range == '5y':
        start_datetime = analysis_datetime - relativedelta(years=5)
    else:
        raise ValueError("Invalid information range. Please choose from ['1m', '3m', '6m', '1y', '2y', '5y'].")

    return start_datetime.strftime('%Y-%m-%d')

def run():
    """
    Run the crew.
    """
def run():
    """
    Run the crew.
    """

    # Get user inputs
    ticker = input("Please enter the ticker symbol for analysis (e.g., AAPL for Apple Inc.): ").upper()
    user_prompt = input("Please enter additional words or custom prompt for analysis: ")
    analysis_date = input("Please enter the date for the analysis (YYYY-MM-DD): ")
    information_range = input("Please enter the information range (1m, 3m, 6m, 1y, 2y, 5y): ").lower()

    # Calculate the start date
    start_date = calculate_start_date(analysis_date, information_range)

    # Mark the current date
    current_date = datetime.now().strftime("%Y-%m-%d")

    inputs = {
        "ticker": ticker,
        "user_prompt": user_prompt,
        "start_date": start_date,
        "analysis_date": analysis_date,
        "information_range": information_range,
        "current_date": current_date
    }

    try:
        Stockanalysis().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

