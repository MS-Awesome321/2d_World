from smolagents import CodeAgent, InferenceClientModel
from tools import autosearch_tool, calibrate_corners_tool, chip_processing_tool

model = InferenceClientModel()
agent = CodeAgent(
    tools=[autosearch_tool, calibrate_corners_tool, chip_processing_tool],
    model=model,
)

# Now the agent can search the web!
result = agent.run("Can you search this chip for me?")
print(result)
