# from dotenv import load_dotenv
# load_dotenv()  # Load environment variables from .env file  

# from langchain_groq import ChatGroq

# llm = ChatGroq(model="openai/gpt-oss-20b")

# while True:
#     query=input("user: ")

#     if query.lower() == "exit":
#         break

#     res=llm.invoke(query)
#     print("bot: ",res.content)





from dotenv import load_dotenv
load_dotenv()

import streamlit as st
st.set_page_config(layout="wide")
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage

llm = ChatGroq(model="openai/gpt-oss-20b")

st.title("🤖 Ask Buddy - QnA Bot")
st.markdown("My name is Buddy, and I am here to answer your questions. Please ask me anything!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    st.chat_message(role).markdown(content)

query = st.chat_input("Ask me anything...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    st.chat_message("user").markdown(query)

    # Send conversation history to the LLM
    history = []

    for message in st.session_state.messages:
        if message["role"] == "user":
            history.append(HumanMessage(content=message["content"]))
        else:
            history.append(AIMessage(content=message["content"]))

    res = llm.invoke(history)

    st.session_state.messages.append({
        "role": "assistant",
        "content": res.content
    })

    st.chat_message("assistant").markdown(res.content)
