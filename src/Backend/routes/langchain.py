from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain.tools import DuckDuckGoSearchRun
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

# Groq Model Setup 
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-8b-8192"
)

# All Tools here 
search = DuckDuckGoSearchRun()
tools = [
    Tool(name="DuckDuckGo Search", func=search.run, description="useful for answering search-based questions")
] 

# Memory setup
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Initialize agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory
)

# Function to interact with agent
def run_langchain_agent(message: str): 
    response = agent.run(message)
    return response 


