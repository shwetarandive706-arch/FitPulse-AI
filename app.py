import os
import io
import csv
import socket
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template, send_from_directory, Response, make_response, session

import database
import models
from ml.churn_predictor import predict_member_churn
from ml.recommender import generate_personalized_plan, calculate_biometrics
from ml.footfall_forecaster import predict_hourly_footfall

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    template_folder=os.path.join(BASE_DIR, "templates")
)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "fitpulse-ai-gym-super-secret-key-2026")

# Initialize database on startup
database.init_db()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# CORS and Cache-Busting Headers for live updates
@app.after_request
def add_cors_and_cache_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ----------------- WEB VIEWS -----------------
@app.route("/")
def index():
    return render_template("index.html")

# ----------------- SYSTEM & DIAGNOSTICS -----------------
@app.route("/api/health", methods=["GET"])
@app.route("/api/system/status", methods=["GET"])
def system_status():
    local_ip = get_local_ip()
    port = int(os.environ.get("PORT", 5000))
    return jsonify({
        "success": True,
        "status": "online",
        "app_name": "FitPulse AI - Gym Membership & Subscription System",
        "version": "1.0.0-pro",
        "ai_models_loaded": ["RandomForest_ChurnClassifier", "ContentBased_DietWorkoutRecommender", "Footfall_RegressionForecaster"],
        "server_time": datetime.now(timezone.utc).isoformat(),
        "local_ip": local_ip,
        "access_url": f"http://{local_ip}:{port}"
    })

# ----------------- AUTHENTICATION -----------------
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    identifier = data.get("identifier", "").strip()
    password = data.get("password", "").strip()

    if not identifier or not password:
        return jsonify({"success": False, "message": "Identifier and password required."}), 400

    user = models.authenticate_user(identifier, password)
    if not user:
        return jsonify({"success": False, "message": "Invalid username/email or password."}), 401

    session["user_id"] = user["id"]
    session["role"] = user["role"]

    # If member, attach full profile
    if user["role"] == "member":
        full = models.get_member_full_profile(user["id"])
        return jsonify({"success": True, "user": full, "message": f"Welcome back, {user['name']}!"})

    return jsonify({"success": True, "user": user, "message": f"Welcome, {user['name']}!"})

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})

# ----------------- ADMIN PORTAL APIS -----------------
@app.route("/api/admin/dashboard", methods=["GET"])
def admin_dashboard():
    metrics = models.get_admin_dashboard_metrics()
    return jsonify({"success": True, "metrics": metrics})

@app.route("/api/members", methods=["GET", "POST"])
def members_endpoint():
    if request.method == "GET":
        members = models.list_all_members()
        return jsonify({"success": True, "members": members, "count": len(members)})

    if request.method == "POST":
        data = request.get_json() or {}
        required = ["name", "email", "username"]
        for r in required:
            if not data.get(r):
                return jsonify({"success": False, "message": f"Missing required field: {r}"}), 400
        try:
            new_member = models.create_member(data)
            return jsonify({"success": True, "member": new_member, "message": "Member registered successfully."}), 201
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/members/<int:member_id>", methods=["GET"])
def member_detail(member_id):
    profile = models.get_member_full_profile(member_id)
    if not profile:
        return jsonify({"success": False, "message": "Member not found."}), 404
    return jsonify({"success": True, "member": profile})

@app.route("/api/plans", methods=["GET"])
def list_plans():
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plans WHERE is_active = 1 ORDER BY price ASC")
    plans = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "plans": plans})

@app.route("/api/subscriptions/assign", methods=["POST"])
def assign_subscription():
    data = request.get_json() or {}
    member_id = data.get("member_id")
    plan_id = data.get("plan_id")
    payment_method = data.get("payment_method", "UPI")

    if not member_id or not plan_id:
        return jsonify({"success": False, "message": "member_id and plan_id are required."}), 400

    try:
        res = models.assign_or_renew_subscription(member_id, plan_id, payment_method)
        return jsonify({"success": True, "subscription": res, "message": "Subscription renewed/assigned successfully."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# ----------------- DYNAMIC QR CHECK-IN -----------------
@app.route("/api/checkin/generate-token", methods=["POST", "GET"])
def generate_token():
    member_id = request.args.get("member_id") or (request.get_json() or {}).get("member_id")
    tok = models.generate_dynamic_qr_token(member_id)
    return jsonify({"success": True, "token_data": tok})

@app.route("/api/checkin/verify-token", methods=["POST"])
def verify_token():
    data = request.get_json() or {}
    token = data.get("token", "").strip()
    member_id = data.get("member_id")

    if not token:
        return jsonify({"success": False, "message": "Token string is required."}), 400

    res = models.verify_and_checkin(token, member_id)
    return jsonify(res)

@app.route("/api/checkin/recent", methods=["GET"])
def recent_checkins():
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, u.name as member_name, u.email as member_email
        FROM checkins c
        JOIN users u ON c.member_id = u.id
        ORDER BY c.checkin_time DESC LIMIT 20
    """)
    records = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "records": records})

# ----------------- AI / ML PIPELINE APIS -----------------
@app.route("/api/ai/predict-churn/<int:member_id>", methods=["GET"])
def predict_churn_endpoint(member_id):
    profile = models.get_member_full_profile(member_id)
    if not profile:
        return jsonify({"success": False, "message": "Member not found."}), 404

    sub = profile.get("subscription") or {}
    monthly_fee = float(sub.get("plan_price", 1499.0)) / max(1, (sub.get("duration_days", 30) // 30))

    member_data = {
        "age": profile.get("age", 26),
        "monthly_fee": monthly_fee,
        "tenure_months": 6,
        "has_trainer": profile.get("has_trainer", 0),
        "payment_delays": 1 if sub.get("payment_status") == "due" else 0,
        "avg_weekly_visits": profile.get("avg_weekly_visits", 2.0),
        "days_since_last_visit": profile.get("days_since_last_visit", 5),
        "attendance_drop_ratio": 0.8 if profile.get("days_since_last_visit", 0) > 14 else 0.1,
        "avg_session_mins": profile.get("avg_session_mins", 60)
    }

    prediction = predict_member_churn(member_data)
    prediction["member_name"] = profile["name"]
    prediction["member_id"] = profile["id"]

    # Log prediction in DB
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ai_predictions (member_id, churn_prob, risk_level, factors_json, recommended_action)
        VALUES (?, ?, ?, ?, ?)
    """, (member_id, prediction["churn_probability"], prediction["risk_level"], 
          str(prediction["risk_factors"]), prediction["retention_action"]))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "prediction": prediction})

@app.route("/api/ai/scan-all-churn", methods=["GET"])
def scan_all_churn():
    members = models.list_all_members()
    results = []

    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0

    for m in members:
        monthly_fee = float(m.get("total_paid") or 1499.0)
        data = {
            "age": m.get("age", 25),
            "monthly_fee": monthly_fee,
            "tenure_months": 6,
            "has_trainer": m.get("has_trainer", 0),
            "payment_delays": 1 if m.get("sub_status") == "expired" else 0,
            "avg_weekly_visits": round(float(m.get("total_checkins", 0) / 4.0), 2),
            "days_since_last_visit": m.get("days_since_last_visit", 5),
            "attendance_drop_ratio": 0.75 if m.get("days_since_last_visit", 0) >= 14 else 0.1,
            "avg_session_mins": 55
        }
        pred = predict_member_churn(data)
        pred["member_id"] = m["id"]
        pred["member_name"] = m["name"]
        pred["plan_name"] = m.get("plan_name", "No Active Plan")
        pred["days_remaining"] = m.get("days_remaining", 0)

        if pred["risk_level"] == "High":
            high_risk_count += 1
        elif pred["risk_level"] == "Medium":
            medium_risk_count += 1
        else:
            low_risk_count += 1

        results.append(pred)

    return jsonify({
        "success": True,
        "scanned_count": len(results),
        "risk_breakdown": {
            "high": high_risk_count,
            "medium": medium_risk_count,
            "low": low_risk_count
        },
        "results": results
    })

@app.route("/api/ai/recommend-fitness", methods=["POST"])
def recommend_fitness():
    data = request.get_json() or {}
    weight_kg = float(data.get("weight_kg", 70.0))
    height_cm = float(data.get("height_cm", 172.0))
    age = int(data.get("age", 25))
    gender = data.get("gender", "Male")
    fitness_goal = data.get("fitness_goal", "Weight Loss")
    dietary_pref = data.get("dietary_pref", "Vegetarian")
    activity_level = data.get("activity_level", "Moderate")
    days_per_week = int(data.get("days_per_week", 4))

    plan = generate_personalized_plan(
        weight_kg=weight_kg,
        height_cm=height_cm,
        age=age,
        gender=gender,
        fitness_goal=fitness_goal,
        dietary_pref=dietary_pref,
        activity_level=activity_level,
        days_per_week=days_per_week
    )
    return jsonify({"success": True, "plan": plan})

@app.route("/api/ai/peak-hours", methods=["GET"])
def peak_hours():
    day_of_week = request.args.get("day", type=int)
    forecast = predict_hourly_footfall(day_of_week)
    return jsonify({"success": True, "forecast": forecast})

# ----------------- CSV DATA EXPORTS -----------------
@app.route("/api/export/members.csv", methods=["GET"])
def export_members_csv():
    members = models.list_all_members()
    output = io.StringIO()
    # Write UTF-8 BOM so Excel opens Hindi/Special chars cleanly
    output.write("\ufeff")
    writer = csv.writer(output)
    writer.writerow([
        "Member ID", "Name", "Email", "Phone", "Age", "Gender",
        "Fitness Goal", "Plan Name", "Plan Tier", "Subscription Status",
        "Days Remaining", "Total Checkins", "Last Visit Date"
    ])
    for m in members:
        writer.writerow([
            m["id"], m["name"], m["email"], m["phone"], m["age"], m["gender"],
            m["fitness_goal"], m.get("plan_name", "None"), m.get("plan_tier", "None"),
            m.get("sub_status", "None"), m.get("days_remaining", 0),
            m.get("total_checkins", 0), m.get("last_checkin", "None")
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=FitPulse_Members_{datetime.now().strftime('%Y%m%d')}.csv"}
    )

@app.route("/api/export/attendance.csv", methods=["GET"])
def export_attendance_csv():
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.member_id, u.name as member_name, u.email,
               c.checkin_time, c.duration_mins, c.method
        FROM checkins c
        JOIN users u ON c.member_id = u.id
        ORDER BY c.checkin_time DESC
    """)
    records = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    output.write("\ufeff")
    writer = csv.writer(output)
    writer.writerow(["Checkin ID", "Member ID", "Member Name", "Email", "Check-in Timestamp", "Duration (Mins)", "Entry Method"])
    for r in records:
        writer.writerow([r["id"], r["member_id"], r["member_name"], r["email"], r["checkin_time"], r["duration_mins"], r["method"]])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=FitPulse_Attendance_{datetime.now().strftime('%Y%m%d')}.csv"}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n=======================================================")
    print(f"FitPulse AI - Gym Membership & Subscription System")
    print(f"Server running at: http://127.0.0.1:{port}")
    print(f"Network access:   http://{get_local_ip()}:{port}")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
