from dotenv import load_dotenv
load_dotenv()

from langchain_community.tools import GoogleSerperRun
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver

llm = ChatGroq(model="openai/gpt-oss-120b")

search = GoogleSerperRun()
memory = MemorySaver()

agent = create_agent(
    model=llm,
    tools=[search],
    system_prompt="You are a helpful assistant that can answer questions using Google search.",
    checkpointer=memory
)

while True:
    question = input("user: ")

    if question.lower() == "exit":
        break

    response = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": question}
            ]
        },
        config={"configurable": {"thread_id": "1"}},
    )

    print("bot:", response["messages"][-1].content)