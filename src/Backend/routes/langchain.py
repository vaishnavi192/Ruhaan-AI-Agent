from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain_groq import ChatGroq
from langchain.agents.agent import AgentOutputParser
from langchain.schema.agent import AgentAction, AgentFinish
from langchain.chains import LLMChain
from langchain.schema import AgentAction, AgentFinish
from langchain.memory import ConversationBufferMemory
import re
from typing import List, Union
import os
from dotenv import load_dotenv
import webbrowser
from datetime import datetime
import json
import math
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

load_dotenv()

router = APIRouter()

# Pydantic model for request validation
class CommandRequest(BaseModel):
    command: str

# Tool functions with proper implementations
def open_tab(query: str) -> str:
    """Open a website in the default browser"""
    try:
        # Clean the URL
        url = query.strip().lower()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Open in browser
        webbrowser.open(url)
        return f"Successfully opened {url}"
    except Exception as e:
        return f"Error opening website: {str(e)}"

def set_reminder(query: str) -> str:
    """Set a reminder with time and message"""
    try:
        # Parse the reminder text
        # Example: "remind me to call mom tomorrow at 3pm"
        reminder_data = {
            "message": query,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Save to reminders.json
        reminders_file = "data/reminders.json"
        os.makedirs("data", exist_ok=True)
        
        if os.path.exists(reminders_file):
            with open(reminders_file, 'r') as f:
                reminders = json.load(f)
        else:
            reminders = []
            
        reminders.append(reminder_data)
        
        with open(reminders_file, 'w') as f:
            json.dump(reminders, f, indent=2)
            
        return f"Reminder set: {query}"
    except Exception as e:
        return f"Error setting reminder: {str(e)}"

def save_note(query: str) -> str:
    """Save a note using Windows Sticky Notes and Notepad"""
    try:
        # Sticky Notes open karna
        os.system('start sticky')
        
        # Notepad open karna with the note content
        temp_file = os.path.join(os.environ['TEMP'], 'temp_note.txt')
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(query)
        os.system(f'start notepad {temp_file}')
        
        return f"Note opened in Notepad: {query[:50]}..."
    except Exception as e:
        return f"Error saving note: {str(e)}"

def calculate(query: str) -> str:
    """Perform mathematical calculations"""
    try:
        # Basic safety check
        if any(keyword in query.lower() for keyword in ['import', 'eval', 'exec', 'os', 'system']):
            return "Invalid calculation request"
            
        # Clean the query
        query = query.replace('calculate', '').strip()
        
        # Use eval for calculation (with safety measures)
        result = eval(query, {"__builtins__": {}}, {"math": math})
        return f"Result: {result}"
    except Exception as e:
        return f"Error in calculation: {str(e)}"

# Define tools with updated descriptions
tools = [
    Tool(
        name="open_tab",
        func=open_tab,
        description="Open a website in the default browser. Input should be a URL or website name."
    ),
    Tool(
        name="set_reminder",
        func=set_reminder,
        description="Set a reminder with a message and time. Example: 'remind me to call mom tomorrow at 3pm'"
    ),
    Tool(
        name="save_note",
        func=save_note,
        description="Save a note with timestamp. Input should be the note content."
    ),

    Tool(
        name="calculate",
        func=calculate,
        description="Perform mathematical calculations. Input should be a mathematical expression."
    )
]

# Custom prompt template - Simplified since we know it's a command
class CustomPromptTemplate(StringPromptTemplate):
    template: str
    tools: List[Tool]
    
    def format(self, **kwargs) -> str:
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += f"\nAction: {action}\nObservation: {observation}\n"
        
        kwargs["thoughts"] = thoughts
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)

# Custom output parser
class CustomOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        if "Final Answer:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        
        regex = r"Action:\s*([^\n]+)\n*Arguments:\s*([^\n]+)"
        match = re.search(regex, llm_output, re.DOTALL)
        
        if not match:
            return AgentFinish(
                return_values={"output": "I couldn't understand what to do. Please try again."},
                log=llm_output,
            )
        
        action = match.group(1).strip()
        arguments = match.group(2).strip()

        if action not in [tool.name for tool in tools]:
            return AgentFinish(
                return_values={"output": f"Invalid action: {action}. Please try again."},
                log=llm_output,
            )
        
        return AgentAction(tool=action, tool_input=arguments, log=llm_output)

# Initialize LLM
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-8b-8192"
)

# Initialize memory
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Create prompt template with memory
template = """You are a helpful AI assistant that executes commands. You have access to the following tools:

{tools}

Previous conversation:
{chat_history}

Use the following format:

Command: the command you need to execute
Thought: think about which tool to use
Action: the action to take, should be one of [{tool_names}]
Arguments: the input to the action
Observation: the result of the action
... (this Thought/Action/Arguments/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original command

Begin!

Command: {input}
{thoughts}
Thought:"""

prompt = CustomPromptTemplate(
    template=template,
    tools=tools,
    input_variables=["input", "intermediate_steps", "chat_history"]
)

# Create LLM chain with memory
llm_chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

# Create agent with better configuration
agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=CustomOutputParser(),
    stop=["\nObservation:"],
    allowed_tools=[tool.name for tool in tools],
    handle_parsing_errors=True
)

# Create agent executor with better error handling
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=3
)

def run_langchain_agent(query: str) -> str:
    """Run the LangChain agent with the given command query"""
    try:
        # Add better error handling and logging
        print(f"Executing command: {query}")
        response = agent_executor.run(query)
        print(f"Command execution result: {response}")
        
        # Save to memory
        memory.save_context({"input": query}, {"output": response})
        return response
    except Exception as e:
        error_msg = f"Error executing command: {str(e)}"
        print(error_msg)
        return error_msg

@router.post("/execute")
async def execute_command(request: CommandRequest):
    """Execute a command using LangChain agent"""
    try:
        response = run_langchain_agent(request.command)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools")
async def list_tools():
    """List all available tools and their descriptions"""
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in tools
        ]
    }


