from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

db=SQLDatabase.from_uri("sqlite:///mytasks.db") 

print("Database connected successfully.")