from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.chat_models.azure_openai import AzureChatOpenAI
from langchain_experimental.tools import PythonREPLTool

load_dotenv()

tools = [PythonREPLTool()]

instructions = """You are an agent designed to write and execute python code to answer questions.
You have access to a python REPL, which you can use to execute python code.
If you get an error, debug your code and try again.
Only use the output of your code to answer the question. 
You might know the answer without running any code, but you should still run the code to get the answer.
If it does not seem like you can write code to answer the question, just return "I don't know" as the answer.
"""
base_prompt = hub.pull("langchain-ai/openai-functions-template")
prompt = base_prompt.partial(instructions=instructions)

llm = AzureChatOpenAI(
    model="gpt-4o-East-US2",
    api_key="a096090373464949980ad13a8291afa3",
    api_version="2024-02-01",
    azure_endpoint="https://regioneastus2.openai.azure.com/",
    temperature=0)

agent = create_openai_functions_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


agent_executor.invoke({"input": "What is the 10th fibonacci number?"})


if __name__ == "__main__":
    agent_executor.invoke({"input": "What is the 10th fibonacci number?"})