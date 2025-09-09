from google.adk.agents import SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from .tools.tools import get_current_time

sequential_agent = SequentialAgent(
    name="query_processing_pipeline",
    model="gemini-2.0-flash",
    description="""
    A sequential agent that performs the following steps:
    1. Format the user natural language query.
    2. Convert the formatted query into a SQL query.
    3. Execute the SQL query in BigQuery.
    4. Append the current timestamp to the final result.
    """,
    steps=[
        query_formatter,
        query_parser,
        bigquery_agent,
    ],
    tools=[
        AgentTool(get_current_time),
    ],
    instruction="""
    1. Receive the user query.
    2. Send it to query_formatter to improve structure.
    3. Pass formatted query to query_parser for SQL generation.
    4. Pass SQL to bigquery_agent for execution.
    5. Attach timestamp using get_current_time tool.
    6. Return final result to the user.
    """,
)
