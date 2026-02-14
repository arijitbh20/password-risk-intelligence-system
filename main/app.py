import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request
from components.ComputeMetrics import ComputeMetrics,BreachChecker,classify_risk
from Database import Database

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():

    result = None
    error = None
    if request.method == "POST":

        password = request.form.get("password", "")

        compute = ComputeMetrics(password)

        entropy = compute.calculate_entropy()
        rules_score = compute.rule_score()

        try:
            breaches = compute.check_breach()

        except BreachChecker as e:
                breaches = -1
                print(f"\n⚠ Warning: {e}")
                print("Risk assessment will continue without breach data.")

        message,risk = classify_risk(entropy, rules_score, breaches)
        database = Database()
        database.create_table()
        database.insert_log(risk=risk,entropy=entropy,breaches=breaches,rules_score=rules_score)

        result = {
                "entropy": entropy,
                "rules": rules_score,
                "breaches": breaches,
                "risk": risk,
                "message": message
            }

    return render_template("index.html", result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True)
