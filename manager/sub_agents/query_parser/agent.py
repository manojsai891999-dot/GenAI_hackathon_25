from google.adk.agents import Agent

query_parser = Agent(
    name="query_parser",
    model="gemini-2.0-flash",
    description="""
    An agent that converts improved natural language queries into valid SQL statements.

    Instruction:
    1. Convert the structured natural language query to SQL using the known schema.

    Example:
    Input: "How much cement was consumed in factory usage on the current date?"
    Output: "SELECT SUM(quantity) AS total_cement FROM factory_usage WHERE material = 'cement' AND usage_date = CURRENT_DATE()"
    """,
    tools=[],
)
