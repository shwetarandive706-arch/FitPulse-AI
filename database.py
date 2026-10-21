import os
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "gym_system.db"))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Users Table (Admin & Gym Members)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL CHECK(role IN ('admin', 'member')),
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        age INTEGER DEFAULT 25,
        gender TEXT DEFAULT 'Male',
        height_cm REAL DEFAULT 172.0,
        weight_kg REAL DEFAULT 70.0,
        fitness_goal TEXT DEFAULT 'General Fitness',
        dietary_pref TEXT DEFAULT 'Vegetarian',
        has_trainer INTEGER DEFAULT 0,
        emergency_contact TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Membership Plans Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        tier TEXT NOT NULL,
        duration_days INTEGER NOT NULL,
        price REAL NOT NULL,
        description TEXT,
        features_json TEXT,
        is_active INTEGER DEFAULT 1
    );
    """)

    # 3. Subscriptions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER NOT NULL,
        plan_id INTEGER NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('active', 'expired', 'pending', 'cancelled')),
        auto_renew INTEGER DEFAULT 0,
        total_paid REAL NOT NULL,
        payment_status TEXT DEFAULT 'paid' CHECK(payment_status IN ('paid', 'due', 'refunded')),
        payment_method TEXT DEFAULT 'UPI',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (member_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (plan_id) REFERENCES plans(id)
    );
    """)

    # 4. Check-in / Attendance Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checkins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER NOT NULL,
        checkin_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        checkout_time DATETIME,
        method TEXT DEFAULT 'qr_code' CHECK(method IN ('qr_code', 'rfid', 'manual')),
        duration_mins INTEGER DEFAULT 60,
        notes TEXT,
        FOREIGN KEY (member_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 5. Dynamic QR Tokens Table (for fraud-proof turnstile entry)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS qr_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT UNIQUE NOT NULL,
        member_id INTEGER,
        created_at DATETIME NOT NULL,
        expires_at DATETIME NOT NULL,
        is_used INTEGER DEFAULT 0,
        FOREIGN KEY (member_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 6. AI Churn Prediction Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER NOT NULL,
        predicted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        churn_prob REAL NOT NULL,
        risk_level TEXT NOT NULL,
        factors_json TEXT,
        recommended_action TEXT,
        FOREIGN KEY (member_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    seed_data(conn)
    conn.close()

def seed_data(conn):
    cursor = conn.cursor()

    # Check if admin already exists
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if cursor.fetchone():
        return

    print("Seeding initial Gym Membership system data...")
    now = datetime.now()

    # 1. Admin User
    admin_pw = generate_password_hash("admin123")
    cursor.execute("""
    INSERT INTO users (role, name, email, phone, username, password_hash)
    VALUES ('admin', 'Gym Director (Manager)', 'director@fitpulse.gym', '+91 9876543210', 'admin', ?)
    """, (admin_pw,))

    # 2. Membership Plans
    plans_data = [
        ("Starter Monthly", "Bronze", 30, 1499.0, 
         "Essential access to gym equipment and locker rooms.", 
         '["Standard gym floor access", "Locker room access", "General fitness guidance"]'),
        ("Pro Quarterly", "Silver", 90, 3999.0, 
         "Best value for quarterly commitments. Includes group workout classes.", 
         '["All Starter features", "Group spinning & crossfit classes", "1 Free monthly body composition scan", "Discount at juice bar"]'),
        ("Elite Annual", "Gold", 365, 11999.0, 
         "Year-round complete access with steam, sauna, and priority lockers.", 
         '["All Pro features", "Steam & sauna access", "Complimentary gym kit", "Quarterly fitness reassessment", "Guest passes (2/month)"]'),
        ("VIP Personal Training", "Platinum", 365, 24999.0, 
         "Ultimate VIP package with dedicated 1-on-1 personal trainer & meal prep guidance.", 
         '["All Elite features", "Dedicated Personal Trainer (3 sessions/week)", "Personalized AI Diet Blueprint", "VIP priority locker", "Towel service"]')
    ]
    for p in plans_data:
        cursor.execute("""
        INSERT INTO plans (name, tier, duration_days, price, description, features_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """, p)

    # 3. Seed Members
    member_pw = generate_password_hash("1234")
    members_data = [
        # name, email, phone, username, age, gender, height, weight, goal, diet, has_trainer
        ("Rahul Sharma", "rahul.sharma@gmail.com", "+91 9811122233", "member1", 26, "Male", 178.0, 74.5, "Muscle Gain", "Non-Vegetarian", 0),
        ("Priya Patel", "priya.patel@gmail.com", "+91 9822233344", "member2", 24, "Female", 163.0, 58.0, "Weight Loss", "Vegetarian", 0),
        ("Amit Verma", "amit.verma@yahoo.com", "+91 9833344455", "member3", 34, "Male", 172.0, 84.0, "Weight Loss", "Vegetarian", 0),
        ("Sneha Kulkarni", "sneha.k@outlook.com", "+91 9844455566", "member4", 29, "Female", 165.0, 62.0, "General Fitness", "Vegan", 1),
        ("Rohan Joshi", "rohan.joshi@gmail.com", "+91 9855566677", "member5", 22, "Male", 182.0, 71.0, "Strength & Power", "Non-Vegetarian", 0)
    ]

    member_ids = []
    for m in members_data:
        cursor.execute("""
        INSERT INTO users (role, name, email, phone, username, password_hash, age, gender, height_cm, weight_kg, fitness_goal, dietary_pref, has_trainer)
        VALUES ('member', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (m[0], m[1], m[2], m[3], member_pw, m[4], m[5], m[6], m[7], m[8], m[9], m[10]))
        member_ids.append(cursor.lastrowid)

    # 4. Seed Subscriptions
    # member1: Pro Quarterly (Active, 45 days left)
    start1 = str((now - timedelta(days=45)).date())
    end1 = str((now + timedelta(days=45)).date())
    cursor.execute("""
    INSERT INTO subscriptions (member_id, plan_id, start_date, end_date, status, auto_renew, total_paid, payment_status)
    VALUES (?, 2, ?, ?, 'active', 1, 3999.0, 'paid')
    """, (member_ids[0], start1, end1))

    # member2: Elite Annual (Active, 210 days left)
    start2 = str((now - timedelta(days=155)).date())
    end2 = str((now + timedelta(days=210)).date())
    cursor.execute("""
    INSERT INTO subscriptions (member_id, plan_id, start_date, end_date, status, auto_renew, total_paid, payment_status)
    VALUES (?, 3, ?, ?, 'active', 0, 11999.0, 'paid')
    """, (member_ids[1], start2, end2))

    # member3: Starter Monthly (Active but nearing expiry, 3 days left - High Risk)
    start3 = str((now - timedelta(days=27)).date())
    end3 = str((now + timedelta(days=3)).date())
    cursor.execute("""
    INSERT INTO subscriptions (member_id, plan_id, start_date, end_date, status, auto_renew, total_paid, payment_status)
    VALUES (?, 1, ?, ?, 'active', 0, 1499.0, 'paid')
    """, (member_ids[2], start3, end3))

    # member4: VIP Personal Training (Active, 180 days left)
    start4 = str((now - timedelta(days=185)).date())
    end4 = str((now + timedelta(days=180)).date())
    cursor.execute("""
    INSERT INTO subscriptions (member_id, plan_id, start_date, end_date, status, auto_renew, total_paid, payment_status)
    VALUES (?, 4, ?, ?, 'active', 1, 24999.0, 'paid')
    """, (member_ids[3], start4, end4))

    # member5: Starter Monthly (EXPIRED 12 days ago - Critical Risk)
    start5 = str((now - timedelta(days=42)).date())
    end5 = str((now - timedelta(days=12)).date())
    cursor.execute("""
    INSERT INTO subscriptions (member_id, plan_id, start_date, end_date, status, auto_renew, total_paid, payment_status)
    VALUES (?, 1, ?, ?, 'expired', 0, 1499.0, 'due')
    """, (member_ids[4], start5, end5))

    # 5. Seed Attendance / Checkin History
    # member1: very regular (attended yesterday, 3 days ago, 5 days ago, etc.)
    for d in [1, 3, 5, 8, 10, 12, 15, 17, 19, 22, 24, 26, 29]:
        dt = (now - timedelta(days=d, hours=2)).strftime("%Y-%m-%d 18:30:00")
        cursor.execute("INSERT INTO checkins (member_id, checkin_time, duration_mins) VALUES (?, ?, ?)", (member_ids[0], dt, 75))

    # member2: consistent (attended 2, 4, 7, 9, 13, 16, 20, 23, 27 days ago)
    for d in [2, 4, 7, 9, 13, 16, 20, 23, 27]:
        dt = (now - timedelta(days=d, hours=10)).strftime("%Y-%m-%d 07:45:00")
        cursor.execute("INSERT INTO checkins (member_id, checkin_time, duration_mins) VALUES (?, ?, ?)", (member_ids[1], dt, 60))

    # member3: HIGH CHURN RISK - last attended 18 days ago, huge drop!
    for d in [18, 21, 24, 28]:
        dt = (now - timedelta(days=d, hours=3)).strftime("%Y-%m-%d 19:15:00")
        cursor.execute("INSERT INTO checkins (member_id, checkin_time, duration_mins) VALUES (?, ?, ?)", (member_ids[2], dt, 35))

    # member4: VIP member (attended 1, 3, 4, 6, 8, 11, 13, 15, 18, 20, 22, 25, 27 days ago)
    for d in [1, 3, 4, 6, 8, 11, 13, 15, 18, 20, 22, 25, 27]:
        dt = (now - timedelta(days=d, hours=1)).strftime("%Y-%m-%d 17:00:00")
        cursor.execute("INSERT INTO checkins (member_id, checkin_time, duration_mins) VALUES (?, ?, ?)", (member_ids[3], dt, 65))

    # member5: expired member - last attended 25 days ago
    for d in [25, 29]:
        dt = (now - timedelta(days=d)).strftime("%Y-%m-%d 08:15:00")
        cursor.execute("INSERT INTO checkins (member_id, checkin_time, duration_mins) VALUES (?, ?, ?)", (member_ids[4], dt, 40))

    conn.commit()
    print("Seeded 1 Admin, 4 Plans, 5 Members, Subscriptions, and 30-day Check-in records successfully.")

if __name__ == "__main__":
    init_db()
