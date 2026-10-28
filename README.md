# Transaction Fraud Detection System

MVP phát hiện giao dịch bất thường bằng Python. Hệ thống kết hợp:

- `IsolationForest` để phát hiện mẫu giao dịch khác biệt.
- Luật nghiệp vụ: số tiền lớn, giao dịch ban đêm, quốc gia mới, nhiều giao dịch trong thời gian ngắn.
- FastAPI cho REST API và SQLite để lưu kết quả.
- Streamlit dashboard để xem thống kê và kiểm tra giao dịch.

> Đây là hệ thống hỗ trợ phân loại rủi ro, không nên tự động từ chối giao dịch thật nếu chưa được hiệu chuẩn trên dữ liệu production và có quy trình kiểm duyệt.

## Chạy nhanh

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/generate_data.py
uvicorn app.main:app --reload
```

Mở API docs tại http://127.0.0.1:8000/docs.

Chạy dashboard ở terminal thứ hai:

```bash
streamlit run dashboard.py
```

## API mẫu

```bash
curl -X POST http://127.0.0.1:8000/transactions/score \
  -H "Content-Type: application/json" \
  -d '{"amount":9500,"currency":"USD","country":"NG","merchant_category":"electronics","hour":3,"customer_id":"cust-new","is_new_device":true}'
```

Các endpoint chính:

- `GET /health`
- `POST /transactions/score`
- `GET /transactions?limit=100`
- `GET /metrics`

## Cấu trúc

```text
app/
  detector.py       # feature engineering, model và business rules
  database.py       # SQLite persistence
  main.py           # FastAPI endpoints
dashboard.py        # Streamlit UI
scripts/
  generate_data.py  # dữ liệu demo
tests/
  test_detector.py
```

## Dữ liệu production

Khi triển khai thật, cần bổ sung dữ liệu lịch sử, nhãn fraud/legitimate, đánh giá precision-recall, chống data leakage, monitoring drift, phân quyền và audit log.
