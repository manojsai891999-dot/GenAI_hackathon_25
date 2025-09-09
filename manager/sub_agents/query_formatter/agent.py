from google.adk.agents import Agent

query_formatter = Agent(
    name="query_formatter",
    model="gemini-2.0-flash",
    description="An agent that improves and structures natural language user queries.",
    instruction="""
    You are a query formatting assistant.

    When given a user query:
    1. Fix grammar and spelling errors.
    2. Add relevant context if possible.
    3. Structure the query in a clear and precise format.

    Example:
    Input: "how much cement did i use in my factory today"
    Output: "How much cement was consumed in factory usage on the current date?"
    """,
    tools=[],
)
