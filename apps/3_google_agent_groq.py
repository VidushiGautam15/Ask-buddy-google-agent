
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Ask Buddy - Google Search Agent",
    page_icon="🤖",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

[data-testid="stSidebar"] {
    min-width: 260px;
}

[data-testid="stSidebar"] button {
    width: 100%;
    text-align: left;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "chats" not in st.session_state:
    st.session_state.chats = {"Chat 1": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

if "memory" not in st.session_state:
    st.session_state.memory = MemorySaver()

# ---------------- MODEL AND SEARCH ----------------
llm = ChatGroq(model="openai/gpt-oss-120b")

search = GoogleSerperAPIWrapper()

@tool
def google_search(query: str) -> str:
    """Search Google for current information about a topic."""
    return search.run(query)

tools = [google_search]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are Ask Buddy, a helpful AI assistant. "
        "Use Google Search when current information is needed. "
        "Give clear, accurate and useful answers."
    ),
    checkpointer=st.session_state.memory
)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🤖 Ask Buddy")

    if st.button("✏️ New Chat", use_container_width=True):
        chat_number = len(st.session_state.chats) + 1
        chat_name = f"Chat {chat_number}"

        while chat_name in st.session_state.chats:
            chat_number += 1
            chat_name = f"Chat {chat_number}"

        st.session_state.chats[chat_name] = []
        st.session_state.current_chat = chat_name
        st.rerun()

    st.divider()
    st.subheader("Explore")
    st.caption("Your AI assistant")

    st.divider()
    st.subheader("Recent Chats")

    if not st.session_state.chats:
        st.caption("No conversations yet.")
    else:
        # Show newest chats first
        for chat_name in reversed(list(st.session_state.chats.keys())):
            messages = st.session_state.chats[chat_name]

            # Use the first user message as the chat title
            first_question = next(
                (
                    message["content"]
                    for message in messages
                    if message["role"] == "user"
                ),
                chat_name
            )

            label = first_question[:28]
            if len(first_question) > 28:
                label += "..."

            if st.button(
                f"💬 {label}",
                key=f"open_{chat_name}",
                use_container_width=True,
                type=(
                    "primary"
                    if chat_name == st.session_state.current_chat
                    else "secondary"
                )
            ):
                st.session_state.current_chat = chat_name
                st.rerun()

    st.divider()
    st.caption("Powered by Groq + Google Search")

# ---------------- MAIN CHAT ----------------
st.title("🤖 Ask Buddy - Google Search Agent")
st.caption("Ask anything. Get intelligent answers with Google Search.")

current_messages = st.session_state.chats[
    st.session_state.current_chat
]

# Display selected conversation
for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- CHAT INPUT ----------------
question = st.chat_input("Ask anything...")

if question:
    # Save and display user message
    current_messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = agent.invoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": question
                            }
                        ]
                    },
                    config={
                        "configurable": {
                            "thread_id": st.session_state.current_chat
                        }
                    }
                )

                answer = response["messages"][-1].content
                st.markdown(answer)

            except Exception as e:
                answer = f"Sorry, something went wrong: {e}"
                st.error(answer)

    # Save assistant response
    current_messages.append({
        "role": "assistant",
        "content": answer
    })

    # Refresh sidebar to show the latest chat title
    st.rerun()
