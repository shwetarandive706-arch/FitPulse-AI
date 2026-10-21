import os
import secrets
import hashlib
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db

def authenticate_user(identifier, password):
    clean_id = str(identifier or "").strip()
    clean_pw = str(password or "").strip()
    if not clean_id or not clean_pw:
        return None

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users 
        WHERE (LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?))
    """, (clean_id, clean_id))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    user = dict(row)
    stored_hash = user.get("password_hash", "")

    valid = False
    if stored_hash == clean_pw:
        valid = True
    else:
        try:
            valid = check_password_hash(stored_hash, clean_pw)
        except Exception:
            valid = False

    if valid:
        del user["password_hash"]
        return user
    return None

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        u = dict(row)
        if "password_hash" in u:
            del u["password_hash"]
        return u
    return None

def get_member_full_profile(member_id):
    conn = get_db()
    cursor = conn.cursor()

    # User row
    cursor.execute("SELECT * FROM users WHERE id = ?", (member_id,))
    u_row = cursor.fetchone()
    if not u_row:
        conn.close()
        return None
    user = dict(u_row)
    if "password_hash" in user:
        del user["password_hash"]

    # Active subscription
    cursor.execute("""
        SELECT s.*, p.name as plan_name, p.tier as plan_tier, p.price as plan_price, p.duration_days
        FROM subscriptions s
        JOIN plans p ON s.plan_id = p.id
        WHERE s.member_id = ?
        ORDER BY s.id DESC LIMIT 1
    """, (member_id,))
    sub_row = cursor.fetchone()
    subscription = dict(sub_row) if sub_row else None

    # Calculate days remaining
    if subscription:
        end_dt = datetime.strptime(subscription["end_date"], "%Y-%m-%d").date()
        today = datetime.now().date()
        days_left = (end_dt - today).days
        subscription["days_remaining"] = days_left
        subscription["is_active"] = (days_left >= 0 and subscription["status"] == "active")

    # Attendance stats
    cursor.execute("""
        SELECT COUNT(*) as total_visits,
               MAX(checkin_time) as last_visit,
               AVG(duration_mins) as avg_duration
        FROM checkins WHERE member_id = ?
    """, (member_id,))
    stats_row = cursor.fetchone()
    stats = dict(stats_row) if stats_row else {}

    # Recent checkins (last 10)
    cursor.execute("""
        SELECT * FROM checkins WHERE member_id = ? ORDER BY checkin_time DESC LIMIT 10
    """, (member_id,))
    recent_checkins = [dict(r) for r in cursor.fetchall()]

    conn.close()

    # Calculate behavioral metrics for AI
    last_visit_str = stats.get("last_visit")
    if last_visit_str:
        try:
            last_dt = datetime.strptime(last_visit_str[:19], "%Y-%m-%d %H:%M:%S")
            days_since_last_visit = (datetime.now() - last_dt).days
        except Exception:
            days_since_last_visit = 5
    else:
        days_since_last_visit = 30

    total_visits = stats.get("total_visits", 0)
    avg_weekly = round(min(7.0, (total_visits / 4.0)), 2)

    user["subscription"] = subscription
    user["total_visits"] = total_visits
    user["last_visit"] = last_visit_str
    user["days_since_last_visit"] = days_since_last_visit
    user["avg_weekly_visits"] = avg_weekly
    user["avg_session_mins"] = int(stats.get("avg_duration") or 60)
    user["recent_checkins"] = recent_checkins

    return user

def list_all_members():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.name, u.email, u.phone, u.username, u.age, u.gender, 
               u.fitness_goal, u.dietary_pref, u.has_trainer, u.created_at,
               s.status as sub_status, s.end_date as sub_end_date, s.total_paid,
               p.name as plan_name, p.tier as plan_tier,
               COUNT(c.id) as total_checkins,
               MAX(c.checkin_time) as last_checkin
        FROM users u
        LEFT JOIN subscriptions s ON s.member_id = u.id AND s.id = (
            SELECT MAX(id) FROM subscriptions WHERE member_id = u.id
        )
        LEFT JOIN plans p ON s.plan_id = p.id
        LEFT JOIN checkins c ON c.member_id = u.id
        WHERE u.role = 'member'
        GROUP BY u.id
        ORDER BY u.id ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    members = []
    today = datetime.now().date()
    for r in rows:
        m = dict(r)
        # Compute days left
        if m.get("sub_end_date"):
            try:
                end_d = datetime.strptime(m["sub_end_date"], "%Y-%m-%d").date()
                m["days_remaining"] = (end_d - today).days
            except Exception:
                m["days_remaining"] = 0
        else:
            m["days_remaining"] = 0

        # Days since last checkin
        if m.get("last_checkin"):
            try:
                last_d = datetime.strptime(m["last_checkin"][:19], "%Y-%m-%d %H:%M:%S")
                m["days_since_last_visit"] = (datetime.now() - last_d).days
            except Exception:
                m["days_since_last_visit"] = 10
        else:
            m["days_since_last_visit"] = 30

        members.append(m)
    return members

def create_member(data):
    conn = get_db()
    cursor = conn.cursor()
    pw_hash = generate_password_hash(data.get("password", "1234"))
    cursor.execute("""
        INSERT INTO users (role, name, email, phone, username, password_hash, age, gender, height_cm, weight_kg, fitness_goal, dietary_pref, has_trainer)
        VALUES ('member', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"], data["email"], data.get("phone", ""), data["username"], pw_hash,
        int(data.get("age", 25)), data.get("gender", "Male"), float(data.get("height_cm", 170)),
        float(data.get("weight_kg", 70)), data.get("fitness_goal", "General Fitness"),
        data.get("dietary_pref", "Vegetarian"), int(data.get("has_trainer", 0))
    ))
    new_id = cursor.lastrowid

    # Assign initial plan if provided
    plan_id = data.get("plan_id")
    if plan_id:
        cursor.execute("SELECT duration_days, price FROM plans WHERE id = ?", (plan_id,))
        p_row = cursor.fetchone()
        if p_row:
            dur, price = p_row["duration_days"], p_row["price"]
            start_date = datetime.now().date()
            end_date = start_date + timedelta(days=dur)
            cursor.execute("""
                INSERT INTO subscriptions (member_id, plan_id, start_date, end_date, status, total_paid, payment_status)
                VALUES (?, ?, ?, ?, 'active', ?, 'paid')
            """, (new_id, plan_id, start_date, end_date, price))

    conn.commit()
    conn.close()
    return get_member_full_profile(new_id)

def assign_or_renew_subscription(member_id, plan_id, payment_method="UPI"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT duration_days, price FROM plans WHERE id = ?", (plan_id,))
    p_row = cursor.fetchone()
    if not p_row:
        conn.close()
        raise ValueError("Plan not found")

    dur = p_row["duration_days"]
    price = p_row["price"]

    # Check existing active subscription to extend, or start from today
    cursor.execute("""
        SELECT end_date FROM subscriptions 
        WHERE member_id = ? AND status = 'active' AND end_date >= date('now')
        ORDER BY end_date DESC LIMIT 1
    """, (member_id,))
    active_sub = cursor.fetchone()

    today = datetime.now().date()
    if active_sub:
        start_date = datetime.strptime(active_sub["end_date"], "%Y-%m-%d").date() + timedelta(days=1)
    else:
        start_date = today

    end_date = start_date + timedelta(days=dur)

    cursor.execute("""
        INSERT INTO subscriptions (member_id, plan_id, start_date, end_date, status, auto_renew, total_paid, payment_status, payment_method)
        VALUES (?, ?, ?, ?, 'active', 1, ?, 'paid', ?)
    """, (member_id, plan_id, start_date, end_date, price, payment_method))
    sub_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"subscription_id": sub_id, "start_date": str(start_date), "end_date": str(end_date), "price": price}

def generate_dynamic_qr_token(member_id=None):
    """
    Generates a secure 5-minute dynamic token for contactless gym turnstile check-in.
    """
    raw = f"{member_id}_{datetime.now().timestamp()}_{secrets.token_hex(16)}"
    token = hashlib.sha256(raw.encode()).hexdigest()[:32]
    now = datetime.now()
    expires_at = now + timedelta(minutes=5)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO qr_tokens (token, member_id, created_at, expires_at, is_used)
        VALUES (?, ?, ?, ?, 0)
    """, (token, member_id, now.strftime("%Y-%m-%d %H:%M:%S"), expires_at.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

    return {
        "token": token,
        "member_id": member_id,
        "expires_at": expires_at.isoformat(),
        "valid_seconds": 300
    }

def verify_and_checkin(token, member_id=None):
    """
    Validates QR token and logs gym checkin.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM qr_tokens 
        WHERE token = ? AND is_used = 0 AND expires_at > datetime('now')
    """, (token,))
    tok_row = cursor.fetchone()

    if not tok_row:
        conn.close()
        return {"success": False, "message": "Invalid, expired, or already-used QR token."}

    tok = dict(tok_row)
    target_member_id = tok.get("member_id") or member_id
    if not target_member_id:
        conn.close()
        return {"success": False, "message": "No member associated with this check-in token."}

    # Verify active subscription
    cursor.execute("""
        SELECT s.*, p.name as plan_name 
        FROM subscriptions s
        JOIN plans p ON s.plan_id = p.id
        WHERE s.member_id = ? AND s.status = 'active' AND s.end_date >= date('now')
        ORDER BY s.end_date DESC LIMIT 1
    """, (target_member_id,))
    sub = cursor.fetchone()

    if not sub:
        conn.close()
        return {"success": False, "message": "Access Denied: Member does not have an active subscription."}

    # Prevent duplicate check-in within last 30 minutes
    cursor.execute("""
        SELECT checkin_time FROM checkins 
        WHERE member_id = ? AND checkin_time > datetime('now', '-30 minutes')
    """, (target_member_id,))
    recent = cursor.fetchone()
    if recent:
        conn.close()
        return {"success": False, "message": "Access Notice: Member already checked in recently (within 30 mins)."}

    # Mark token as used
    cursor.execute("UPDATE qr_tokens SET is_used = 1 WHERE id = ?", (tok["id"],))

    # Record Checkin
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO checkins (member_id, checkin_time, method, duration_mins)
        VALUES (?, ?, 'qr_code', 60)
    """, (target_member_id, now_str))

    cursor.execute("SELECT name, email FROM users WHERE id = ?", (target_member_id,))
    user = dict(cursor.fetchone())

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Check-in verified! Welcome to FitPulse Gym, {user['name']}.",
        "member_name": user["name"],
        "plan": sub["plan_name"],
        "checkin_time": now_str
    }

def get_admin_dashboard_metrics():
    conn = get_db()
    cursor = conn.cursor()

    # Total members
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'member'")
    total_members = cursor.fetchone()[0]

    # Active subscribers
    cursor.execute("""
        SELECT COUNT(DISTINCT member_id) FROM subscriptions 
        WHERE status = 'active' AND end_date >= date('now')
    """)
    active_subscriptions = cursor.fetchone()[0]

    # Today's checkins
    cursor.execute("SELECT COUNT(*) FROM checkins WHERE date(checkin_time) = date('now')")
    today_checkins = cursor.fetchone()[0]

    # Total revenue (paid subscriptions)
    cursor.execute("SELECT COALESCE(SUM(total_paid), 0) FROM subscriptions WHERE payment_status = 'paid'")
    total_revenue = round(float(cursor.fetchone()[0]), 2)

    # Attendance by day for the past 7 days
    cursor.execute("""
        SELECT strftime('%Y-%m-%d', checkin_time) as checkin_date, COUNT(*) as count
        FROM checkins
        WHERE checkin_time >= datetime('now', '-7 days')
        GROUP BY checkin_date
        ORDER BY checkin_date ASC
    """)
    weekly_attendance = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "total_members": total_members,
        "active_subscribers": active_subscriptions,
        "today_checkins": today_checkins,
        "total_revenue": total_revenue,
        "weekly_attendance": weekly_attendance
    }
