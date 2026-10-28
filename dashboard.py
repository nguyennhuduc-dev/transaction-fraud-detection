import pandas as pd
import requests
import streamlit as st

API = st.sidebar.text_input("API URL", "http://127.0.0.1:8000")
st.set_page_config(page_title="Fraud Detection", page_icon="🛡️", layout="wide")
st.title("🛡️ Transaction Fraud Detection")

try:
    metrics = requests.get(f"{API}/metrics", timeout=3).json()
    cols = st.columns(4)
    cols[0].metric("Tổng giao dịch", metrics["total_transactions"])
    cols[1].metric("Cần kiểm tra", metrics["review"])
    cols[2].metric("Bị chặn", metrics["blocked"])
    cols[3].metric("Điểm rủi ro TB", metrics["average_risk_score"])
except requests.RequestException:
    st.warning("Chưa kết nối được API. Hãy chạy uvicorn trước.")

st.subheader("Kiểm tra giao dịch")
with st.form("score"):
    c1, c2, c3 = st.columns(3)
    customer_id = c1.text_input("Customer ID", "cust-demo")
    amount = c1.number_input("Số tiền", min_value=1.0, value=120.0)
    country = c2.selectbox("Quốc gia", ["US", "VN", "GB", "SG", "NG", "XX"])
    category = c2.selectbox("Danh mục", ["grocery", "fuel", "restaurant", "electronics", "travel", "cash_withdrawal"])
    hour = c3.slider("Giờ giao dịch", 0, 23, 12)
    new_device = c3.checkbox("Thiết bị mới")
    velocity = c3.number_input("Số giao dịch trong 1 giờ", min_value=1, value=1)
    submitted = st.form_submit_button("Phân tích")
if submitted:
    payload = {"customer_id": customer_id, "amount": amount, "currency": "USD", "country": country,
               "merchant_category": category, "hour": hour, "is_new_device": new_device, "velocity_1h": velocity}
    response = requests.post(f"{API}/transactions/score", json=payload, timeout=10)
    response.raise_for_status()
    result = response.json()
    st.success(f"Kết quả: {result['decision'].upper()} — Risk score: {result['risk_score']}")
    st.write("Lý do:", ", ".join(result["reasons"]) or "Không phát hiện yếu tố rõ ràng")

st.subheader("Giao dịch gần đây")
try:
    data = requests.get(f"{API}/transactions?limit=100", timeout=3).json()
    if data:
        frame = pd.DataFrame(data)
        st.dataframe(frame[["id", "customer_id", "amount", "country", "risk_score", "decision", "created_at"]], use_container_width=True)
    else:
        st.info("Chưa có giao dịch.")
except requests.RequestException:
    pass
