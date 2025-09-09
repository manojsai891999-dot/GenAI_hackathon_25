from google.adk.agents import Agent
from google.cloud import bigquery
from datetime import datetime

def run_bigquery_query(sql_query: str, config: Dict[str, str]) -> str:
    project_id = config.get("gcp_project_id", "default-project-id")
    client = bigquery.Client(project=project_id)

    try:
        query_job = client.query(sql_query)
        results = query_job.result()

        rows = []
        for row in results:
            rows.append({field.name: row[field.name] for field in results.schema})

        result_str = "Query Results:\n"
        for idx, row in enumerate(rows, start=1):
            result_str += f"{idx}. {row}\n"

        result_str += f"\n[Executed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
        return result_str

    except Exception as e:
        return f"Query execution failed: {str(e)}"

bigquery_agent = Agent(
    name="bigquery_agent",
    model="gemini-2.0-flash",
    description="Executes SQL query against a specified BigQuery project and schema.",
    instruction="1. Execute the query on the configured project and dataset.",
    tools=[AgentTool(run_bigquery_query)],
    config={
        "gcp_project_id": "gcp-project-id",
        "dataset": "factory_data",
    }
)

