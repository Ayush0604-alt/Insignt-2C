import sys
import os
import duckdb
import pandas as pd
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../..", ".env"))

if len(sys.argv) < 3:
    print("Error: Missing arguments", file=sys.stderr)
    sys.exit(1)

file_path = sys.argv[1]
query = sys.argv[2]

try:
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".json"):
        df = pd.read_json(file_path)
    else:
        df = pd.read_excel(file_path)
except Exception as e:
    print(f"I couldn't load the dataset. Error: {str(e)}")
    sys.exit(0)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "your_api_key_here":
    print("Please set your GEMINI_API_KEY in the .env file.")
    sys.exit(0)

try:
    from google import genai
    client = genai.Client(api_key=api_key)
except ImportError:
    print("google-genai package is not installed.")
    sys.exit(0)

# Step 1: Generate SQL
schema = df.dtypes.to_string()
columns_info = ", ".join(df.columns)

prompt_sql = f"""You are an expert data analyst.
A dataset is loaded as a table named `df`.
The columns are: {columns_info}
Schema details:
{schema}

User asks: "{query}"
Write a DuckDB SQL query to answer this question against the table `df`.
Return ONLY the raw SQL query, no markdown formatting, no explanations, no ```sql tags.
For example, if asked for highest salary: SELECT MAX(salary) FROM df;
"""

try:
    response_sql = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_sql
    )
    sql_query = response_sql.text.strip().strip("`").replace("sql\n", "").strip()
except Exception as e:
    print(f"Error communicating with Gemini API: {str(e)}")
    sys.exit(0)

# Step 2: Execute SQL
try:
    result = duckdb.query(sql_query).df()
    result_text = result.to_string()
except Exception as e:
    result_text = f"Error executing SQL: {str(e)}\nGenerated SQL was:\n{sql_query}"

# Step 3: Summarize result
prompt_summary = f"""User asked: "{query}"
We executed a SQL query on the dataset and got this result:
{result_text}

Provide a concise, conversational answer to the user's question based on the result.
Do not mention the SQL query itself unless there was an error.
"""

try:
    response_answer = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_summary
    )
    print(response_answer.text.strip())
except Exception as e:
    print(f"Result was: \n{result_text}")
