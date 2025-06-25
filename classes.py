from typing import Annotated, List, Literal, TypedDict
from enum import Enum, auto
import pandas as pd
import operator
from consts import *
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.messages import AnyMessage










class AppState(TypedDict):
    user_query: str
    ticker: str
    news: pd.DataFrame
    prices: pd.DataFrame
    price_analyst_report: str
    news_analyst_report: str
    final_report: str
    final_response: Annotated[list[AnyMessage], operator.add]
    messages: Annotated[list[AnyMessage], operator.add]
