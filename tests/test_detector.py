from app.detector import FraudDetector


def test_normal_transaction_is_not_blocked():
    result = FraudDetector().score({"amount": 30, "hour": 12, "country": "US", "merchant_category": "grocery", "is_new_device": False, "velocity_1h": 1})
    assert result.decision in {"approved", "review"}
    assert 0 <= result.risk_score <= 100


def test_high_risk_transaction_has_explanations():
    result = FraudDetector().score({"amount": 12000, "hour": 2, "country": "NG", "merchant_category": "cash_withdrawal", "is_new_device": True, "velocity_1h": 10})
    assert result.decision == "blocked"
    assert len(result.reasons) >= 3
