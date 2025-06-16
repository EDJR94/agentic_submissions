from langchain_core.messages import HumanMessage
from graphs.chat_graph import chat_graph

if __name__ == "__main__":

    while True:
        user_input = input()
        message = HumanMessage(content=user_input)
        state = {"messages": [message]}
        config = {"configurable": {"thread_id": "3"}}

        response = chat_graph.invoke(
            state, config=config
        )

        for ans in response["messages"]:
            ans.pretty_print()