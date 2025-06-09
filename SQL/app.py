from flask import Flask, request, jsonify, render_template
import subprocess
import pandas as pd
import duckdb
import os

app = Flask(__name__)

# Load Excel data into pandas DataFrame
EXCEL_FILE = "\Hack\SQL\Employee.xlsx"
df = pd.read_excel(EXCEL_FILE)

PROMPT_TEMPLATE = """
# You are an expert SQL developer.
# Convert the following natural language request to an SQL query. Analyse the whole data and generate the most appropriate SQL query.
# Use standard SQL syntax.
#
#
# Request:
# {question}
#
# SQL:
"""

def query_ollama(prompt, model="stable-code"):
    command = ['ollama', 'run', model]
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output, _ = process.communicate(prompt)
    return output.strip()

def execute_query(sql):
    try:
        result = duckdb.query(sql).df()
        return result.to_dict(orient='records')
    except Exception as e:
        return str(e)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_sql", methods=["POST"])
def generate_sql():
    data = request.get_json()
    question = data.get("question", "")
    prompt = PROMPT_TEMPLATE.format(question=question)
    sql_query = query_ollama(prompt)

    # Replace table name to match DataFrame duckdb naming
    sql_query = sql_query.replace("FROM employees", "FROM df")

    results = execute_query(sql_query)
    return jsonify({
        "query": sql_query,
        "results": results
    })

if __name__ == "__main__":
    app.run(debug=True)
