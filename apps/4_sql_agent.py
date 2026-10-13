from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

db=SQLDatabase.from_uri("sqlite:///mytasks.db") 

print("Database connected successfully.")

db.run("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT CHECK(status IN ('pending', 'in_progress', 'completed')) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

print("Table 'tasks' created successfully.")

llm=ChatGroq(model="openai/gpt-oss-120b")
toolkit=SQLDatabaseToolkit(db=db, llm=llm)
tools=toolkit.get_tools()

for tool in tools:
    print(tool.name)