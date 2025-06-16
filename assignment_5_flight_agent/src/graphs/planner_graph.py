from langgraph.graph import StateGraph
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from typing import TypedDict
import time
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os
from prompts.itinerary_prompt import ITINERARY_PROMPT

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    api_key=OPENAI_API_KEY
)

search=DuckDuckGoSearchRun()


class State(TypedDict):
    destiny: str
    start_date: str
    end_date: str
    attractions: str
    restaurants: str
    activities: str
    weather: str
    hotels: str
    final_itinerary: str

def itinerary_tool(state:State):
    destiny = state["destiny"]
    start_date = state["start_date"]
    end_date = state["end_date"]

    print("Searching for Attractions...")
    best_att = search.invoke(f"Best Attractions in {destiny}")
    time.sleep(10)

    print("Searching for Restaurants...")
    best_rest = search.invoke(f"Best Restaurants in {destiny}")
    time.sleep(10)

    print("Searching for Activities...")
    best_act = search.invoke(f"Best Activities to do in {destiny}")
    time.sleep(10)

    print("Searching for Hotels...")
    best_hotels = search.invoke(f"Best hotels to do in {destiny}")
    time.sleep(10)

    print("Searching for Weather...")
    best_weather = search.invoke(f"What will be the weather forecasting in {destiny} from {start_date} to {end_date}")


    return {
        "attractions": best_att,
        "restaurants": best_rest,
        "activities": best_act,
        "hotels": best_hotels,
        "weather": best_weather,
    }

def compile_itinerary(state:State):
    template=ITINERARY_PROMPT

    prompt = PromptTemplate(
        template=template,
        input_variables=["destination", "attractions", "restaurants", "activities","hotels","weather"]
    )

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "destination":state["destiny"],
        "attractions":state["attractions"],
        "restaurants":state["restaurants"],
        "activities":state["activities"],
        "hotels":state["hotels"],
        "weather":state["weather"],
    })

    return {"final_itinerary":response}

graph = StateGraph(State)

graph.add_node("planner_agent",itinerary_tool)
graph.add_node("summary_agent",compile_itinerary)

graph.add_edge("planner_agent","summary_agent")

graph.set_entry_point("planner_agent")
graph.set_finish_point("summary_agent")


planner_workflow = graph.compile()