import argparse
import os

from tools import autosearch_tool, calibrate_corners_tool, chip_processing_tool
os.environ['OPENAI_API_KEY'] = ''
from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    
    OpenAIServerModel,
)
def parse_args():
    parser = argparse.ArgumentParser(description="2D Material Auto-Exfoliation System Control Program")
    parser.add_argument(
        "task", type=str, help="Task description, e.g.: 'Place a new chip on the exfoliation stage and complete the exfoliation process'"
    )
    parser.add_argument("--model-id", type=str, default="gpt-4o", help="Model ID to use")
    parser.add_argument("--max-steps", type=int, default=20, help="Maximum execution steps")
    parser.add_argument("--verbosity", type=int, default=2, help="Verbosity level (0-3)")
    return parser.parse_args()
custom_role_conversions = {"tool-call": "assistant", "tool-response": "user"}
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
def create_agent(model_id="gpt-4o",max_steps=20, verbosity_level=2):
    model = OpenAIServerModel(
        model_id,
        custom_role_conversions=custom_role_conversions,
        max_completion_tokens=4096,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    # Create all tools
    AUTOSEARCH_TOOLS = [autosearch_tool, calibrate_corners_tool, chip_processing_tool]
        
    # Create specialized agents for each hardware function
    autosearch_agent = ToolCallingAgent(
        model=model,
        tools=AUTOSEARCH_TOOLS,
        max_steps=12,
        verbosity_level=verbosity_level,
        name="autosearch_agent",
        description="This agent calibrates the chip and conducts autosearching for the flakes on the chip.",
    )
    autosearch_agent.prompt_templates["system_prompt"] += """
You are an AI agent that controls the autosearch process for an exfoliation stage.
You can call chip_processing_tool to finish the entire process of calibrating corners and autosearching.
If further refinement is needed, you can adjust the parameters and re-run the tools as necessary.
"""
    return autosearch_agent

def main():
    print("Starting system initialization...")
    args = parse_args()
    try:
        print("starting agent creation...")
        agent = create_agent(
            model_id=args.model_id,
            max_steps=args.max_steps,
            verbosity_level=args.verbosity
        )

        print("System initialization complete, starting task execution...")
        answer = agent.run(args.task)
        print(f"Task completed! Result: {answer}")
    except Exception as e:
        print(f"System error: {e}")
        print("Please check serial port connections and hardware status")

if __name__ == "__main__":
    main()
# python autosearch_agent.py "Can you search this chip for me?"