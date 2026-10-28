from typing import Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from .database import init_db, list_transactions, save_transaction
from .detector import FraudDetector

app = FastAPI(title="Transaction Fraud Detection API", version="0.1.0")
detector = FraudDetector()


class Transaction(BaseModel):
    customer_id: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    country: str = Field(default="US", min_length=2, max_length=2)
    merchant_category: str = "grocery"
    hour: int = Field(default=12, ge=0, le=23)
    is_new_device: bool = False
    velocity_1h: int = Field(default=1, ge=1, le=100)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/transactions/score")
def score_transaction(transaction: Transaction) -> dict:
    payload = transaction.model_dump()
    result = detector.score(payload)
    transaction_id = save_transaction(payload, result)
    return {"transaction_id": transaction_id, **result.__dict__}


@app.get("/transactions")
def transactions(limit: int = Query(default=100, ge=1, le=1000)) -> list[dict]:
    return list_transactions(limit)


@app.get("/metrics")
def metrics() -> dict:
    rows = list_transactions(10000)
    total = len(rows)
    return {
        "total_transactions": total,
        "flagged": sum(row["decision"] != "approved" for row in rows),
        "blocked": sum(row["decision"] == "blocked" for row in rows),
        "review": sum(row["decision"] == "review" for row in rows),
        "average_risk_score": round(sum(row["risk_score"] for row in rows) / total, 2) if total else 0,
    }
