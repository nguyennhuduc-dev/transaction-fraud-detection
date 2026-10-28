import random
import requests

API = "http://127.0.0.1:8000/transactions/score"
for i in range(30):
    payload = {
        "customer_id": f"cust-{random.randint(1, 8)}", "amount": round(random.lognormvariate(4, .7), 2),
        "currency": "USD", "country": random.choice(["US", "VN", "GB", "SG"]),
        "merchant_category": random.choice(["grocery", "fuel", "restaurant", "electronics"]),
        "hour": random.randint(7, 22), "is_new_device": random.random() < .1, "velocity_1h": random.randint(1, 4)
    }
    response = requests.post(API, json=payload, timeout=5)
    response.raise_for_status()
print("Generated 30 demo transactions")
