from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import numpy as np
from sklearn.ensemble import IsolationForest


@dataclass
class DetectionResult:
    risk_score: float
    decision: str
    reasons: list[str]
    anomaly_score: float


class FraudDetector:
    """Hybrid detector: unsupervised anomaly model plus explainable rules."""

    COUNTRIES = ["US", "GB", "DE", "SG", "VN", "JP", "AU", "NG"]
    CATEGORIES = ["grocery", "fuel", "restaurant", "electronics", "travel", "cash_withdrawal"]

    def __init__(self) -> None:
        self.model = IsolationForest(
            n_estimators=150, contamination=0.08, random_state=42
        )
        self._fit_baseline()

    def _fit_baseline(self) -> None:
        rng = np.random.default_rng(42)
        rows = []
        for _ in range(1200):
            rows.append([
                max(1, rng.lognormal(3.7, 0.75)),
                rng.integers(0, 24),
                rng.choice(self.COUNTRIES[:-1]),
                rng.choice(self.CATEGORIES[:-1]),
                rng.choice([0, 1], p=[0.9, 0.1]),
                rng.integers(1, 5),
            ])
        self.model.fit(self._encode(rows))

    def _encode(self, rows: list[list[Any]]) -> np.ndarray:
        encoded = []
        for amount, hour, country, category, new_device, velocity in rows:
            encoded.append([
                np.log1p(float(amount)),
                float(hour) / 23,
                self.COUNTRIES.index(country) / (len(self.COUNTRIES) - 1)
                if country in self.COUNTRIES else 1.0,
                self.CATEGORIES.index(category) / (len(self.CATEGORIES) - 1)
                if category in self.CATEGORIES else 1.0,
                float(new_device),
                min(float(velocity), 20) / 20,
            ])
        return np.asarray(encoded, dtype=float)

    def score(self, transaction: dict[str, Any]) -> DetectionResult:
        amount = float(transaction["amount"])
        hour = int(transaction.get("hour", datetime.now(timezone.utc).hour))
        country = transaction.get("country", "US")
        category = transaction.get("merchant_category", "grocery")
        new_device = bool(transaction.get("is_new_device", False))
        velocity = int(transaction.get("velocity_1h", 1))
        row = [[amount, hour, country, category, int(new_device), velocity]]
        raw = float(-self.model.score_samples(self._encode(row))[0])
        anomaly_score = float(np.clip((raw - 0.05) / 0.65, 0, 1))

        reasons: list[str] = []
        rule_points = 0
        if amount >= 5000:
            rule_points += 30
            reasons.append("Số tiền giao dịch rất lớn")
        if hour <= 5 or hour >= 23:
            rule_points += 15
            reasons.append("Giao dịch vào khung giờ bất thường")
        if country not in self.COUNTRIES[:-1]:
            rule_points += 20
            reasons.append("Quốc gia chưa có trong baseline")
        if new_device:
            rule_points += 15
            reasons.append("Thiết bị mới")
        if velocity >= 6:
            rule_points += 25
            reasons.append("Tần suất giao dịch cao trong 1 giờ")
        if category == "cash_withdrawal" and amount >= 2000:
            rule_points += 15
            reasons.append("Rút tiền mặt với giá trị lớn")

        risk_score = float(np.clip(anomaly_score * 55 + rule_points, 0, 100))
        decision = "review" if risk_score >= 45 else "approved"
        if risk_score >= 75:
            decision = "blocked"
        if not reasons and anomaly_score >= 0.65:
            reasons.append("Mẫu giao dịch khác biệt so với baseline")
        return DetectionResult(round(risk_score, 2), decision, reasons, round(anomaly_score, 4))
