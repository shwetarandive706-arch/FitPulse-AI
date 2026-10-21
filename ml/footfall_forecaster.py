import os
import joblib
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "saved_models", "footfall_model.joblib")

_model_cache = None

def get_footfall_bundle():
    global _model_cache
    if _model_cache is None:
        if not os.path.exists(MODEL_PATH):
            from ml.train_models import train_footfall_model
            train_footfall_model()
        _model_cache = joblib.load(MODEL_PATH)
    return _model_cache

def predict_hourly_footfall(day_of_week=None):
    """
    Returns predicted gym occupancy percentage for every hour from 6:00 to 22:00.
    """
    bundle = get_footfall_bundle()
    baselines = bundle.get("hourly_baselines", {})
    max_cap = bundle.get("max_capacity", 100)

    now = datetime.now()
    if day_of_week is None:
        day_of_week = now.weekday()

    results = []
    for hour in range(6, 23):
        base = baselines.get(hour, 20)
        # weekend reduction
        if day_of_week in [5, 6]:
            base = int(base * 0.85)
        
        pct = min(100, int((base / max_cap) * 100))
        if pct >= 75:
            crowd_status = "High / Peak Crowd"
            status_color = "danger"
        elif pct >= 40:
            crowd_status = "Moderate Traffic"
            status_color = "warning"
        else:
            crowd_status = "Low / Ideal Time"
            status_color = "success"

        formatted_hour = f"{hour:02d}:00"
        results.append({
            "hour": hour,
            "time_label": formatted_hour,
            "predicted_occupancy": base,
            "occupancy_percentage": pct,
            "status": crowd_status,
            "color": status_color
        })

    current_hour = now.hour
    curr_data = next((r for r in results if r["hour"] == current_hour), results[0])

    return {
        "day_of_week": day_of_week,
        "current_hour": current_hour,
        "current_status": curr_data,
        "hourly_breakdown": results
    }
