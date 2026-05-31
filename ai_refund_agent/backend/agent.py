import os
import json
from openai import OpenAI
from tools import TOOLS_SCHEMA, AVAILABLE_TOOLS

# Initialize client using standard OpenAI SDK. 
# base_url and api_key will be pulled from environment variables,
# allowing easy swapping to Groq, Gemini, or vLLM.
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "dummy-key"),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
)

MODEL = os.environ.get("LLM_MODEL", "gpt-4o")

SYSTEM_PROMPT = """
You are a helpful customer support agent for an e-commerce company.
Your goal is to assist customers with their refund requests.
Always follow the company's refund policy strictly. 
First, query the order. Then, read the policy if you are unsure of the rules. 
If the refund is valid, process the refund. If it is denied, clearly explain why.
"""

from datetime import datetime

def run_agent_loop(messages: list) -> dict:
    """
    Runs the LLM agent loop with tool calling.
    Returns the final assistant message and a list of reasoning logs.
    """
    reasoning_logs = []
    
    # Ensure system prompt is present
    if not messages or messages[0].get("role") != "system":
        current_date = datetime.now().strftime("%B %d, %Y")
        dynamic_system_prompt = f"{SYSTEM_PROMPT}\n\nCRITICAL CONTEXT: Today's date is {current_date}. Use this to calculate time limits."
        messages.insert(0, {"role": "system", "content": dynamic_system_prompt})

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
        )
        
        message = response.choices[0].message
        # Append the assistant's message as a dictionary for easier serialization
        messages.append(message.model_dump(exclude_none=True))
        
        if not message.tool_calls:
            # The model decided to answer without further tool calls
            return {
                "final_message": message.content,
                "reasoning_logs": reasoning_logs,
                "messages": messages
            }
            
        # Handle tool calls
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_to_call = AVAILABLE_TOOLS.get(function_name)
            
            # Log the thought process/intent
            log_entry = {
                "action": "tool_call",
                "tool": function_name,
                "arguments": tool_call.function.arguments,
            }
            
            try:
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)
            except Exception as e:
                function_response = json.dumps({"error": str(e)})
                
            log_entry["result"] = function_response
            reasoning_logs.append(log_entry)
            
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
