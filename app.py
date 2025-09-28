from flask import Flask, render_template, request, redirect, url_for
import json
import sys
import io

app = Flask(__name__)

# Load problems from a JSON file
with open("problems.json") as f:
    problems = json.load(f)

def run_code(user_code, test_cases):
    results = []
    for case in test_cases:
        input_data = case["input"]
        expected_output = case["output"]
        output = ""
        try:
            # Redirect stdout to capture print statements
            old_stdout = sys.stdout
            sys.stdout = mystdout = io.StringIO()
            # Prepare code that reads input
            exec_globals = {}
            exec_locals = {}
            # Simulate input() for user's code
            def fake_input():
                return input_data
            exec_globals['input'] = fake_input
            exec(user_code, exec_globals, exec_locals)
            sys.stdout = old_stdout
            output = mystdout.getvalue().strip()
        except Exception as e:
            output = f"Error: {e}"
            sys.stdout = old_stdout
        results.append({
            "input": input_data,
            "expected": expected_output,
            "output": output,
            "passed": output == expected_output
        })
    return results

@app.route("/")
def index():
    return render_template("index.html", problems=problems)

@app.route("/problem/<slug>", methods=["GET", "POST"])
def problem(slug):
    problem = next((p for p in problems if p["slug"] == slug), None)
    if not problem:
        return "Problem not found.", 404

    feedback = None
    code_prefill = problem["solution"]
    if request.method == "POST":
        code = request.form["code"]
        results = run_code(code, problem["test_cases"])
        feedback = results
        code_prefill = code

    return render_template("problem.html", problem=problem, feedback=feedback, code_prefill=code_prefill)

if __name__ == "__main__":
    app.run(debug=True)