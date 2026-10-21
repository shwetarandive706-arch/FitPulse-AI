import os
import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "saved_models", "churn_model.joblib")

_model_cache = None

def get_churn_pipeline():
    global _model_cache
    if _model_cache is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Please run ml/train_models.py first.")
        _model_cache = joblib.load(MODEL_PATH)
    return _model_cache

def predict_member_churn(member_data):
    """
    Predicts churn probability and assigns a risk tier.
    member_data: dict with keys:
      age, monthly_fee, tenure_months, has_trainer, payment_delays,
      avg_weekly_visits, days_since_last_visit, attendance_drop_ratio, avg_session_mins
    """
    bundle = get_churn_pipeline()
    scaler = bundle["scaler"]
    model = bundle["model"]
    features = bundle["features"]

    # Provide safe defaults if missing
    row = [
        float(member_data.get("age", 28)),
        float(member_data.get("monthly_fee", 1499.0)),
        float(member_data.get("tenure_months", 6)),
        float(member_data.get("has_trainer", 0)),
        float(member_data.get("payment_delays", 0)),
        float(member_data.get("avg_weekly_visits", 2.5)),
        float(member_data.get("days_since_last_visit", 4)),
        float(member_data.get("attendance_drop_ratio", 0.1)),
        float(member_data.get("avg_session_mins", 50))
    ]

    scaled = scaler.transform(pd.DataFrame([row], columns=features))
    prob = float(model.predict_proba(scaled)[0][1])
    churn_pred = int(prob >= 0.50)

    # Determine risk category
    if prob < 0.35:
        risk_level = "Low"
        risk_badge = "success"
    elif prob < 0.70:
        risk_level = "Medium"
        risk_badge = "warning"
    else:
        risk_level = "High"
        risk_badge = "danger"

    # Identify primary explainable drivers
    factors = []
    days_since = row[6]
    drop_ratio = row[7]
    visits = row[5]
    delays = row[4]
    has_tr = row[3]

    if days_since >= 14:
        factors.append(f"High inactivity: Has not checked in for {int(days_since)} days.")
    elif days_since >= 7:
        factors.append(f"Moderate absence: {int(days_since)} days since last workout.")

    if drop_ratio >= 0.5:
        factors.append(f"Sharp attendance decline: {int(drop_ratio*100)}% drop compared to baseline.")

    if visits < 1.5:
        factors.append(f"Low weekly commitment: averaging only {visits:.1f} visits per week.")

    if delays >= 1:
        factors.append(f"Payment irregularity: {int(delays)} recorded fee payment delays.")

    if not has_tr and prob > 0.45:
        factors.append("No personal trainer assigned; lacks guided fitness accountability.")

    if not factors:
        factors.append("Consistent attendance and good engagement pattern.")

    # Tailored retention strategy recommendation
    if risk_level == "High":
        action = "CRITICAL: Trigger automated retention outreach, offer 1 complimentary personal training session, and offer a 15% discount on plan renewal."
    elif risk_level == "Medium":
        action = "ATTENTION: Send an encouraging workout milestone nudge, invite to a weekend group spin/crossfit session, and check fitness goal satisfaction."
    else:
        action = "EXCELLENT: Member is highly engaged. Good candidate for annual tier upgrade or loyalty rewards."

    return {
        "churn_probability": round(prob * 100, 1),
        "will_churn": churn_pred,
        "risk_level": risk_level,
        "risk_badge": risk_badge,
        "risk_factors": factors,
        "retention_action": action,
        "model_metrics": bundle.get("metrics", {})
    }
