from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent 
import streamlit as st

db=SQLDatabase.from_uri("sqlite:///mytasks.db") 

# print("Database connected successfully.")

db.run("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK(status IN ('pending', 'in_progress', 'completed')) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# print("Table 'tasks' created successfully.")

llm=ChatGroq(model="openai/gpt-oss-120b")
toolkit=SQLDatabaseToolkit(db=db, llm=llm)
tools=toolkit.get_tools()

# for tool in tools:
#     print(tool.name)



system_prompt = """
You are a task management assistant that interacts with a SQL database containing a 'tasks' table.

TASK RULES:
1. Limit SELECT queries to 10 results max with ORDER BY created_at DESC
2. After CREATE/UPDATE/DELETE, confirm with SELECT query
3. If the user requests a list of tasks, present the output in a structured table format

CRUD OPERATIONS:
    CREATE: INSERT INTO tasks(title, description, status)
    READ: SELECT * FROM tasks WHERE ... LIMIT 10
    UPDATE: UPDATE tasks SET status=? WHERE id=? OR title=?
    DELETE: DELETE FROM tasks WHERE id=? OR title=?

Table schema: id, title, description, status(pending/in_progress/completed), created_at.
"""
def get_agent():
    memory = InMemorySaver()
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=memory
    )
    return agent
agent = get_agent() 


st.subheader("📋 TaskBot - Manage Your Tasks")

prompt = st.chat_input("Ask me to manage your tasks ?")
if prompt:
    st.chat_message("user").markdown(prompt)
    with st.chat_message("ai"):
        with st.spinner("Processing...."):
            response = agent.invoke(
                {"messages": [{"role": "user", "content": prompt}]},
                {"configurable": {"thread_id": "1"}}
            )
            result = response["messages"][-1].content
            st.markdown(result)
