from phi.agent import Agent
from phi.tools.yfinance import YFinanceTools
from phi.model.groq import Groq as groq
from phi.tools.duckduckgo import DuckDuckGo
import openai
from dotenv import load_dotenv

import os
import phi
from phi.playground import Playground, serve_playground_app
# Load environment variables from .env file
load_dotenv()

phi.api=os.getenv("PHI_API_KEY")


class PromptValidator:
    def __init__(self , valid_prompts):
        self.valid_prompts = set(valid_prompts)  # to ensure there are no duplicates

    def is_valid_prompt(self, prompt):
        return prompt.strip() in self.valid_prompts
    
class myModel:
    def __init__(self, agent_model):
        self.agent = agent_model
        self.prompt_validator = None # PromptValidator instance

    def set_validator(self, validator):
        self.prompt_validator = validator # PromptValidator is set

    def get_prompt(self , prompt):
        if self.prompt_validator is None:
            return "Prompt validator not set. Please set the prompt validator."
        if not self.prompt_validator.is_valid_prompt(prompt):
            return "Invalid prompt. Please enter a valid prompt."
        return self.agent.print_response(prompt)
    

web_search_agent = Agent(tools=[DuckDuckGo()],
                            model = groq(id = "llama3-groq-70b-8192-tool-use-preview"),
                            # `description` Tells us about the agent's function
                            description="You Surf through the web for info",       
                            instructions=["Always Include reference sources "],
                            show_tool_calls=True,
                            markdown= True
                            )
        
finance_agent = Agent(tools=[YFinanceTools(stock_price=True , stock_fundamentals=True , analyst_recommendations=True)],
                            model = groq(id = "llama3-groq-70b-8192-tool-use-preview"),
                            description="You are an investment analyst that researches stock prices, analyst recommendations, and stock fundamentals.",       
                            instructions=["Format your response using markdown and use tables to display data where possible."],
                            show_tool_calls=True,
                            markdown= True
                            )


prompt_list = ["stock price", "analyst recommendations", "stock fundamentals"]
#prompt = input("Enter your prompt: ")




multi_agent = Agent(
    team=[web_search_agent, finance_agent],
    description="You are a multi-agent that can access both the web and financial data.",
    instructions=["Format your response using markdown and use tables to display data where possible."],
    show_tool_calls=True,
    markdown=True
)

# multi_agent.print_response(prompt)

app=Playground(agents=[multi_agent]).get_app()

if __name__=="__main__":
    serve_playground_app("L-1:app",reload=True)