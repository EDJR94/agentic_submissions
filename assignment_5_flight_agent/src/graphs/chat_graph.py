from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os
from graphs.planner_graph import planner_workflow
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from prompts.chat_prompt import CHAT_PROMPT


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(
    model="gpt-4.1-mini",
    api_key=OPENAI_API_KEY
)

search=DuckDuckGoSearchRun()

def call_model_chat(state:MessagesState):   
    messages = state["messages"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", CHAT_PROMPT),
        ("placeholder", "{messages}")
    ])

    chain = prompt | llm_with_tools

    response = chain.invoke({"messages":messages})
    
    return {
        "messages":[response]
    }

# Insert workflow as tool
planner_tool = planner_workflow.as_tool()
tools = [planner_tool]
tool_node = ToolNode(tools)
llm_with_tools = llm.bind_tools(tools)

memory_chat = InMemorySaver()

# Workflow
chat_workflow = StateGraph(MessagesState)

chat_workflow.add_node("chat_model", call_model_chat)
chat_workflow.add_node("tools", tool_node)
chat_workflow.add_edge(START, "chat_model")
chat_workflow.add_edge("tools", "chat_model")


chat_workflow.add_conditional_edges(
    "chat_model",
    tools_condition
)

chat_graph = chat_workflow.compile(memory_chat)