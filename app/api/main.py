from contextlib import asynccontextmanager

from fastapi import FastAPI, Form, HTTPException
from pydantic import BaseModel

from app.components.compute_metrics import BreachChecker, ComputeMetrics, classify_risk
from app.database.database import Database



# make sure the DB table exists before the app starts serving

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = Database()
    db.create_table()
    yield
    db.close_connection()

app = FastAPI(
    title="Password Risk Intelligence System",
    description="Evaluates password entropy, rule compliance, and breach exposure.",
    version="1.0.0",
    lifespan=lifespan,
)


class PasswordAnalysis(BaseModel):
    entropy: float
    rules: int
    breaches: int          # -1 means "breach API was unreachable"
    risk: str
    message: str


def analyse_password(password: str, db: Database) -> dict:
    """Run entropy + rule + breach checks on one password and log the result."""

    compute = ComputeMetrics(password)

    entropy = compute.calculate_entropy()
    rules_score = compute.rule_score()

    try:
        breaches = compute.check_breach()
    except BreachChecker as exc:
        breaches = -1
        print(f"⚠ Breach check failed: {exc}")

    message, risk = classify_risk(entropy, rules_score, breaches)

    db.insert_log(risk=risk, entropy=entropy, breaches=breaches, rules_score=rules_score)

    return {
        "entropy": entropy,
        "rules": rules_score,
        "breaches": breaches,
        "risk": risk,
        "message": message,
    }

# Routes

@app.post("/api/check-password", response_model=PasswordAnalysis)
async def check_password(password: str = Form(...)):
    """Analyse a single password sent as form data."""
    if not password:
        raise HTTPException(422,"Password must not be empty.")

    db = Database()
    try:
        result = analyse_password(password, db)
    finally:
        db.close_connection()

    return result

