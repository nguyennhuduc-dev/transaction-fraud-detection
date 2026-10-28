import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "fraud_detection.db"


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL, amount REAL NOT NULL, currency TEXT NOT NULL,
            country TEXT NOT NULL, merchant_category TEXT NOT NULL,
            hour INTEGER NOT NULL, is_new_device INTEGER NOT NULL,
            velocity_1h INTEGER NOT NULL, risk_score REAL NOT NULL,
            decision TEXT NOT NULL, reasons TEXT NOT NULL, created_at TEXT NOT NULL
        )""")


def save_transaction(transaction: dict[str, Any], result: Any) -> int:
    with connect() as db:
        cursor = db.execute("""INSERT INTO transactions
            (customer_id, amount, currency, country, merchant_category, hour,
             is_new_device, velocity_1h, risk_score, decision, reasons, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (transaction["customer_id"], transaction["amount"], transaction["currency"],
             transaction["country"], transaction["merchant_category"], transaction["hour"],
             int(transaction["is_new_device"]), transaction["velocity_1h"],
             result.risk_score, result.decision, json.dumps(result.reasons, ensure_ascii=False)))
        return int(cursor.lastrowid)


def list_transactions(limit: int = 100) -> list[dict[str, Any]]:
    with connect() as db:
        rows = db.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(row) | {"reasons": json.loads(row["reasons"])} for row in rows]
