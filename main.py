import os
from dotenv import load_dotenv
import streamlit as st
import textwrap
from langgraph.graph import END, StateGraph
from langchain_groq import ChatGroq
from openbb import obb
from langchain_core.messages import HumanMessage, SystemMessage
from duckduckgo_search import DDGS
from langgraph.prebuilt import tools_condition, ToolNode
import warnings
from PIL import Image
import argparse
import json
import csv




warnings.filterwarnings("ignore")

load_dotenv()

from utils import *
from consts import *
from classes import *

MODEL = "llama-3.1-8b-instant"

llm = ChatGroq(
    temperature=0,
    model_name=MODEL,
    api_key=os.environ.get("GROQKEY"),
)







def ticker_extractor(state: AppState):
    """
    Extracts the ticker or cryptocurrency mentioned in the user's query.

    Args:
        state: An AppState object containing the user's query in 'user_query'.

    Returns:
        A dictionary with the extracted ticker symbol.
    """

    prompt = """
You are an expert in the Indian stock market (NSE & BSE). 
You know the full list of the Nifty Fifty companies and their tickers:

- Apollo Hospitals (APOLLOHOSP)
- Asian Paints (ASIANPAINT)
- Axis Bank (AXISBANK)
- Bajaj Auto (BAJAJ-AUTO)
- Bajaj Finance (BAJFINANCE)
- Bharti Airtel (BHARTIARTL)
- Britannia (BRITANNIA)
- Cipla (CIPLA)
- Coal India (COALINDIA)
- Divi's Labs (DIVISLAB)
- Dr. Reddy's (DRREDDY)
- Eicher Motors (EICHERMOT)
- Grasim Industries (GRASIM)
- HCL Technologies (HCLTECH)
- HDFC Bank (HDFCBANK)
- HDFC Life (HDFCLIFE)
- Hero MotoCorp (HEROMOTOCO)
- Hindalco (HINDALCO)
- Hindustan Unilever (HINDUNILVR)
- ICICI Bank (ICICIBANK)
- ITC (ITC)
- Infosys (INFY)
- JSW Steel (JSWSTEEL)
- Kotak Mahindra Bank (KOTAKBANK)
- Larsen & Toubro (LT)
- Mahindra & Mahindra (M&M)
- Maruti Suzuki (MARUTI)
- Nestlé India (NESTLEIND)
- NTPC (NTPC)
- Oil & Natural Gas Corp (ONGC)
- Power Grid (POWERGRID)
- Reliance Industries (RELIANCE)
- SBI (SBIN)
- Shree Cement (SHREECEM)
- State Bank of India (SBIN)
- Sun Pharma (SUNPHARMA)
- Tata Motors (TATAMOTORS)
- Tata Steel (TATASTEEL)
- TCS (TCS)
- Titan (TITAN)
- UltraTech Cement (ULTRACEMCO)
- UPL (UPL)
- Wipro (WIPRO)

Your job:
1. Read the user’s query (the next message).
2. Identify any of the above companies by name or ticker.
3. Return **only** **single** valid tickers
4. Return nothing else




             """
       
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=state["user_query"])
    ]

    response = llm.invoke(messages)

    # If response is an object like AIMessage, extract the string content
    ticker_result = response.content.strip() if hasattr(response, "content") else str(response).strip()

    print("The ticker is:")
    print(ticker_result)

    return {"ticker": ticker_result}


     
    




##############################################################################
def news_retriever(state: AppState):
    """Retrieves news for the given ticker.

    Args:
        state: An AppState object containing the ticker in "ticker".

    Returns:
        A dictionary with the news data for the ticker.
    """
    ticker = state["ticker"]
    news_df = get_news_data(ticker)
    return {"news": news_df}
##############################################################################



#############################################################################################################################

def price_retriever(state: AppState):
    """Retrieves and processes price data for the given ticker.

    Args:
        state: An AppState object containing the ticker in "ticker".

    Returns:
        A dictionary with processed price data for the ticker.
    """
    ticker = state["ticker"]
    price_df = stock_data(ticker)
  
    return {"prices": price_df}



########################################################################################################
### PRICE analyst


def price_analyst(state: AppState):

     prompt = f"""You are an expert quantitative financial analyst specializing in algorithmic trading. You will be given a CSV file containing an array of daily metric records, each with:

  • metric  – “price” or “volume”  
  • date    – YYYY-MM-DD  
  • value   – numeric (INR for prices; share count for volumes)  
  • delivery – (volume only) percentage of shares delivered  

Your tasks:

1. **Parse & Validate**  
   - Ensure every record has valid “metric”, “date”, and “value” fields; “delivery” only for volume.  
   - Report any missing or malformed entries.

2. **Compute Summaries**  
   - For each metric, calculate count, mean, median, min, max, and standard deviation.  
   - Flag dates with outlier values (>2 σ from the mean).

3. **Trend Analysis**  
   - **Price:** compute month-over-month % change; detect sustained up- or down-trends.  
   - **Volume:** identify volume spikes and note their delivery percentages.

4. **Metric Correlation**  
   - Quantify correlation between price and volume.  
   - Highlight dates where volume spikes coincide with significant price moves.

5. **Reporting**  
   - Produce a structured report with:  
     • Executive summary (key findings)  
     • Tables of summary stats per metric  
     • Trend-analysis narrative  
     • Correlation insights  
     • Actionable points (e.g., “watch for price breakout above ₹X”)

6. **Short-Term Forecast**  
   - Predict daily closing prices for the next two weeks, each on its own line.  
   - Assign a confidence score [0–10] for your forecast.  
   - Provide a 1–3 sentence outlook on the overall trend.

When responding, use clear headings and bullet points. Keep the format concise and machine-readable so both humans and downstream LLMs can parse it easily.

When creating your answer, focus on answering the 
User query: {state["user_query"]}
"""
     
     data = state["prices"]
    
     data_csv =  data.to_csv(index=False)
     messages = [
             SystemMessage(content=prompt),
             HumanMessage(content=data_csv)
         ]

     response = llm.invoke(messages)
     
     return {"price_analyst_report": response.content}
  






##################################################################################################################################################


##news analyst

def news_analyst(state: AppState):

    
    
    prompt = f"""
You are an advanced financial news analyst and Large Language Model (LLM)-assisted trading intelligence engine.

You are given a CSV array of news articles related to a specific publicly traded company.

Each line of CSV file will contain a different news article .

 Each article contains:
- `title` (headline)
- `link` (url)(optional)
- `published` (ISO datetime)
- `summary` (short summary)(optional)




Your tasks are:

---

###  Section 1: Executive Summary
- Overall sentiment and key developments.
- Major headlines or market-moving announcements.
- Media tone: positive / negative / neutral.

---

###  Section 2: Sentiment Analysis
- Per-article and overall sentiment (positive, negative, neutral).
- Emotionally reactive terms (e.g., "crash", "beat estimates").
- Sentiment consistency or contradictions.

---

###  Section 3: Event Detection
- Detect events (earnings, M&A, lawsuits, leadership changes, etc).
- Include event dates, sources.
- Assess potential market implications.

---

###  Section 4: Impact on Algorithmic Trading
How could this news influence algotrading:
- **Volatility Triggers**
- **Volume Signals**
- **Timing Cues**
- **Momentum Catalysts**
- **Macro/sector overlap**

---

###  Section 5: Strategy Mapping
Match news to algotrading strategies:
- Mean Reversion
- Momentum
- News Arbitrage
- Text-based Sentiment Quant

---

###  Section 6: Entity & Keyword Extraction
- Key people, companies, products
- Repeated themes, phrases, keywords

---

###  Section 7: Structured JSON Output
Output structured summary:
```json
{{
  "overall_sentiment": "...",
  "top_events": ["..."],
  "trading_signals": ["..."],
  "momentum_score": 0.0,
  "volatility_risk": "...",
  "noteworthy_articles": [
    {{"title": "...", "url": "...", "summary": "..."}}
  ],
  "recommended_followup": ["..."]
}}

Pick a number for the sentiment between 0 and 100 where:

- 0 is extremely bearish
- 100 is extremely bullish


Also add a short explanation (1-2 sentences) of why.

When creating your answer, focus on answering the 
User query: {state["user_query"]}

"""
    
    news_df = state["news"]
    data_csv =  news_df.to_csv(index=False)
    messages = [
             SystemMessage(content=prompt),
             HumanMessage(content=data_csv)
         ]

    response = llm.invoke(messages)
    return {"news_analyst_report": response.content}







##################################################################################################################################################

##Financial REporter

def financial_reporter(state: AppState):

      
       
       prompt = f"""
You are a financial intelligence engine combining two expert analyses:

1. **News Analysis Report** — which contains sentiment, events, and impact of media on the market.
2. **Price Analysis Report** — which includes statistical summaries, trend detection, and correlations of price/volume.

You will be provided with both pre-generated reports in CSV format.

Your job is to:

---

###  Synthesize & Advise

- Read both the **news** and **price** reports.
- Summarize current market sentiment and trading conditions.
- Analyze how news and price trends agree or conflict.
- Based on both reports, answer the **user query** directly and intelligently.

Include:
-  Executive Insight Summary
-  Market Bias (bullish, bearish, neutral)
-  Reasoning
-  Recommended Action (buy, hold, sell, wait)
-  Matching Strategy (momentum, mean reversion, sentiment, etc.)
-  Confidence Score (0–10)

Focus on precision, concise reasoning, and actionable advice.


When creating your answer, focus on answering the user query:
{state["user_query"]}
"""
       

       price_report = state["price_analyst_report"]
       news_report = state["news_analyst_report"]


       combined_reports = {
        "news_report": news_report,
        "price_report": price_report
    }



       messages = [
             SystemMessage(content=prompt),
              HumanMessage(content=json.dumps(combined_reports, ensure_ascii=False))
         ]

       response = llm.invoke(messages)  




       return {"final_report": response.content}






#################################################################################################################################################


graph = StateGraph(AppState)
graph.support_multiple_edges = True



def ticker_check(state: AppState):
    if (
        state["ticker"] != "NoCoin"
    ):
        return "yes"
    else:
        return "no"
    




def final_answer(state: AppState):
    print("Final State reached")
    if ticker_check(state) == "no":
        print("I am here at no")
        prompt = f"""You are an expert financial advisor with deep expertise in personal finance, investments, budgeting, taxation, and financial planning. Your goal is to provide precise, actionable, and reliable advice tailored to users' specific financial situations. Ensure your answers are accurate and relevant.

        If you do not know the answer to a question or if the query is unrelated to your expertise, humbly deny it and explain that you cannot provide an answer in that case. When providing advice, clearly communicate any risks, uncertainties, or potential downsides involved to help users make informed decisions. Always strive to answer the user's query in a clear, professional, and trustworthy manner.
        
        
        """
    else:
        print("hey we are here")
        prompt = f"""
        You are an expert financial advisor with deep expertise in personal finance, investments, budgeting, taxation, and financial planning. Your goal is to provide precise, actionable, and reliable advice tailored to users' specific financial situations. Ensure your answers are accurate and relevant.

Additionally, there are pre-generated reports stored in variables that you should refer to when answering the user's query:
	•	News Analyst Report: {state["news_analyst_report"]}
	•	Price Analyst Report: {state["price_analyst_report"]}
	•	Financial Report: {state["final_report"]}

Refer to these reports, if available, to ensure your responses are well-informed and data-driven.

If you do not know the answer to a question, if the query is unrelated to your expertise, or if there is insufficient information to provide an informed response, humbly deny it and explain why. When giving advice, always clearly communicate any risks, uncertainties, or potential downsides involved to help users make informed decisions. Strive to deliver clear, professional, and trustworthy responses to every query.
        
        """

    sys_message = SystemMessage(content=prompt)

    result = [llm.invoke([sys_message] + [HumanMessage(state["user_query"])])]

    return {"final_response": (result)}





############################################################################################################################

graph.add_node("ticker_extractor", ticker_extractor)
graph.add_node("news_retriever", news_retriever)
graph.add_node("price_retriever", price_retriever)
graph.add_node("price_analyst", price_analyst)
graph.add_node("news_analyst", news_analyst)
graph.add_node("financial_reporter", financial_reporter)
graph.add_node("final_answer", final_answer)

graph.add_conditional_edges(
    "ticker_extractor",
    ticker_check,
    {"yes": "price_retriever", "no": "final_answer"},
)


graph.add_edge("price_retriever", "news_retriever")

graph.add_edge("price_retriever", "price_analyst")
graph.add_edge("news_retriever", "news_analyst")
graph.add_edge("news_analyst", "financial_reporter")
graph.add_edge("financial_reporter", "final_answer")


graph.set_entry_point("ticker_extractor")
graph.set_finish_point("final_answer")
app = graph.compile()



#######################################################################################################################################

# App Title
def main():
    st.title("Stock Financial Advisor")


    user_query = st.text_input("Enter your financial query:", "")

    if user_query:
   
        state = app.invoke({"user_query": user_query})  

        
        if ticker_check(state) == "yes":
           
            # st.subheader("📈 Price Analyst Report:")
            # report = state.get("price_analyst_report", "No report available")
            # for line in report.split("\n"):
            #     st.write(textwrap.fill(line, 80))

           
            # st.subheader("📰 News Analyst Report:")
            # news_report = state.get("news_analyst_report", "No report available")
            # for line in news_report.split("\n"):
            #     st.write(textwrap.fill(line, 80))

          
            final = state.get("final_report", None)
            if final:
                st.subheader("📊 Final Report:")
                st.write(final)
                st.subheader("Final Answer:")
                st.write(state["final_response"][-1].content)
            else:
                st.write("No final report available.")
        else:
           
            st.subheader("Final Answer:")
            st.write(state["final_response"][-1].content)
    else:
        st.warning("Please enter a query to get started.")

if __name__ == "__main__":
    main()