import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import Ridge
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")
SAVED_MODELS_DIR = os.path.join(BASE_DIR, "ml", "saved_models")
os.makedirs(DATASETS_DIR, exist_ok=True)
os.makedirs(SAVED_MODELS_DIR, exist_ok=True)

def generate_and_save_datasets():
    print("Generating realistic Gym Membership Churn dataset...")
    np.random.seed(42)
    n_samples = 1500

    # Member demographics & subscription attributes
    age = np.random.randint(18, 65, size=n_samples)
    gender = np.random.choice(["Male", "Female", "Other"], size=n_samples, p=[0.55, 0.42, 0.03])
    plan_types = np.random.choice(["Starter Monthly", "Pro Quarterly", "Elite Annual", "VIP Training"], 
                                  size=n_samples, p=[0.40, 0.30, 0.20, 0.10])
    
    plan_price_map = {
        "Starter Monthly": 1499,
        "Pro Quarterly": 3999,
        "Elite Annual": 11999,
        "VIP Training": 24999
    }
    plan_duration_map = {
        "Starter Monthly": 1,
        "Pro Quarterly": 3,
        "Elite Annual": 12,
        "VIP Training": 12
    }
    monthly_fee = [round(plan_price_map[p] / plan_duration_map[p], 2) for p in plan_types]
    tenure_months = np.random.randint(1, 36, size=n_samples)
    has_trainer = np.random.choice([0, 1], size=n_samples, p=[0.75, 0.25])
    payment_delays = np.random.choice([0, 1, 2, 3], size=n_samples, p=[0.65, 0.20, 0.10, 0.05])
    
    # Behavioral and Attendance Metrics
    # Healthy members attend 3-5 times/week, high risk attend < 1.5 times/week
    avg_weekly_visits = np.random.uniform(0.2, 5.5, size=n_samples)
    days_since_last_visit = []
    attendance_drop_ratio = []
    avg_session_mins = []

    for visits in avg_weekly_visits:
        if visits < 1.2:
            days_since = np.random.randint(12, 45)
            drop_ratio = np.random.uniform(0.5, 0.95)
            session_min = np.random.randint(25, 45)
        elif visits < 2.5:
            days_since = np.random.randint(5, 18)
            drop_ratio = np.random.uniform(0.2, 0.6)
            session_min = np.random.randint(40, 65)
        else:
            days_since = np.random.randint(0, 6)
            drop_ratio = np.random.uniform(0.0, 0.25)
            session_min = np.random.randint(55, 90)
        days_since_last_visit.append(days_since)
        attendance_drop_ratio.append(round(drop_ratio, 2))
        avg_session_mins.append(session_min)

    # Churn probability logit calculation
    # Driven heavily by days_since_last_visit, attendance_drop_ratio, low weekly visits, payment delays
    z = (
        -2.2
        + 0.12 * np.array(days_since_last_visit)
        + 3.5 * np.array(attendance_drop_ratio)
        - 0.85 * np.array(avg_weekly_visits)
        + 0.45 * np.array(payment_delays)
        - 0.9 * np.array(has_trainer)
        + 0.0003 * np.array(monthly_fee)
        - 0.04 * np.array(tenure_months)
        + np.random.normal(0, 0.35, size=n_samples)
    )
    churn_prob = 1 / (1 + np.exp(-z))
    churn = (churn_prob > 0.50).astype(int)

    df = pd.DataFrame({
        "age": age,
        "gender": gender,
        "plan_type": plan_types,
        "monthly_fee": monthly_fee,
        "tenure_months": tenure_months,
        "has_trainer": has_trainer,
        "payment_delays": payment_delays,
        "avg_weekly_visits": np.round(avg_weekly_visits, 2),
        "days_since_last_visit": days_since_last_visit,
        "attendance_drop_ratio": attendance_drop_ratio,
        "avg_session_mins": avg_session_mins,
        "churn": churn
    })

    csv_path = os.path.join(DATASETS_DIR, "gym_churn_dataset.csv")
    df.to_csv(csv_path, index=False)
    print(f"Saved {len(df)} records to {csv_path}. Churn distribution: {df['churn'].value_counts().to_dict()}")

    # Exercise and Nutrition Knowledge Base
    exercise_nutrition_data = {
        "goals": {
            "Weight Loss": {
                "calorie_adjustment": -500,
                "protein_per_kg": 2.0,
                "carb_percentage": 0.35,
                "fat_percentage": 0.25,
                "workout_focus": "High Intensity Interval Training (HIIT), Functional Resistance, Cardio End",
                "recommended_splits": ["Full Body Circuit (3 Days)", "Upper / Lower Fat Burn (4 Days)"],
                "routine_details": {
                    "Day 1": ["Barbell Squats: 3x12", "Push-ups: 3x15", "Dumbbell Bent-over Row: 3x12", "Plank: 3x45s", "Treadmill Incline Walk: 15 mins"],
                    "Day 2": ["Rest or 20 min LISS Cardio"],
                    "Day 3": ["Romanian Deadlifts: 3x12", "Dumbbell Overhead Press: 3x12", "Lat Pulldown: 3x12", "Bicycle Crunches: 3x20", "Jump Rope: 10 mins"],
                    "Day 4": ["Rest"],
                    "Day 5": ["Kettlebell Swings: 4x15", "Bodyweight Walking Lunges: 3x15/leg", "Cable Face Pulls: 3x15", "Rowing Machine Intervals: 12 mins"]
                }
            },
            "Muscle Gain": {
                "calorie_adjustment": 350,
                "protein_per_kg": 2.2,
                "carb_percentage": 0.50,
                "fat_percentage": 0.20,
                "workout_focus": "Hypertrophy Resistance, Progressive Overload, Compound Lifts",
                "recommended_splits": ["Push / Pull / Legs (PPL - 6 Days)", "Upper / Lower Split (4 Days)"],
                "routine_details": {
                    "Day 1 (Push)": ["Barbell Bench Press: 4x8-10", "Incline DB Press: 3x10-12", "Standing Overhead Press: 3x8-10", "Tricep Rope Pushdowns: 3x12-15", "Lateral Raises: 4x15"],
                    "Day 2 (Pull)": ["Deadlifts or Rack Pulls: 4x6-8", "Barbell Rows: 4x8-10", "Neutral Grip Lat Pulldown: 3x10-12", "Barbell Bicep Curls: 3x10-12", "Face Pulls: 3x15"],
                    "Day 3 (Legs)": ["Barbell Back Squats: 4x8-10", "Romanian Deadlifts: 3x10-12", "Leg Press: 3x12", "Leg Curls: 3x15", "Standing Calf Raises: 4x15"],
                    "Day 4 (Rest)": ["Active Recovery & Mobility"],
                    "Day 5 (Upper)": ["Incline Barbell Bench: 4x8-10", "Weighted Pull-ups / Lat Pulldown: 4x8-10", "Seated Cable Row: 3x10-12", "Dumbbell Hammer Curls: 3x12", "Overhead Tricep Extension: 3x12"],
                    "Day 6 (Lower)": ["Front Squats / Hack Squats: 4x8-10", "Bulgarian Split Squats: 3x10/leg", "Hamstring Curls: 4x12", "Hanging Leg Raises: 3x15"]
                }
            },
            "Strength & Power": {
                "calorie_adjustment": 200,
                "protein_per_kg": 2.0,
                "carb_percentage": 0.45,
                "fat_percentage": 0.25,
                "workout_focus": "Heavy Compound Movements (1-5 reps), Neural Drive, Long Rest",
                "recommended_splits": ["5x5 Powerlifting Split (3 Days)", "Upper/Lower Strength (4 Days)"],
                "routine_details": {
                    "Day 1": ["Barbell Back Squats: 5x5 (Heavy)", "Bench Press: 5x5", "Barbell Rows: 5x5", "Plank: 3x60s"],
                    "Day 2": ["Rest"],
                    "Day 3": ["Overhead Military Press: 5x5", "Conventional Deadlift: 1x5 (Heavy)", "Chin-ups: 3x6-8", "Farmer Walks: 3x40m"],
                    "Day 4": ["Rest"],
                    "Day 5": ["Paused Squats: 3x5", "Close-Grip Bench: 3x6", "Pendlay Row: 4x6", "Ab Wheel Rollouts: 3x12"]
                }
            },
            "General Fitness": {
                "calorie_adjustment": 0,
                "protein_per_kg": 1.6,
                "carb_percentage": 0.45,
                "fat_percentage": 0.30,
                "workout_focus": "Cardiovascular Health, Core Stability, Balanced Muscular Endurance",
                "recommended_splits": ["Total Body Conditioning (3 Days)"],
                "routine_details": {
                    "Day 1": ["Goblet Squats: 3x12", "Dumbbell Bench Press: 3x12", "Lat Pulldown: 3x12", "Plank: 3x45s", "Stair Climber: 10 mins"],
                    "Day 2": ["Brisk Walk / Cycling: 30 mins"],
                    "Day 3": ["Dumbbell Romanian Deadlift: 3x12", "Seated Dumbbell Shoulder Press: 3x12", "Cable Row: 3x12", "Russian Twists: 3x20"],
                    "Day 4": ["Rest or Yoga / Stretching"]
                }
            }
        },
        "diet_plans": {
            "Vegetarian": {
                "breakfast": "Oats with protein powder or soy milk, chia seeds, almonds, and banana slice.",
                "lunch": "Paneer tikka or tofu bowl with brown rice, mixed greens, dal/lentil soup.",
                "snack": "Sprouted moong salad, Greek yogurt / roasted chickpeas.",
                "dinner": "Quinoa / multigrain roti, mixed vegetables curry, paneer/tofu, cucumber salad."
            },
            "Non-Vegetarian": {
                "breakfast": "3-4 Egg omelette / boiled eggs with whole wheat toast and avocado/peanut butter.",
                "lunch": "Grilled chicken breast or fish fillet with jasmine rice, steamed broccoli, olive oil drizzle.",
                "snack": "Whey protein shake with a handful of walnuts and apple.",
                "dinner": "Lean turkey / chicken stir-fry with mixed peppers, sweet potatoes, and green salad."
            },
            "Vegan": {
                "breakfast": "Overnight oats with pea protein, flaxseeds, almond butter, and blueberries.",
                "lunch": "Tempeh / seasoned tofu scramble with quinoa, black beans, salsa, and avocado.",
                "snack": "Edamame beans, roasted pumpkin seeds, or protein smoothie with spinach.",
                "dinner": "Lentil / chickpea pasta with tomato basil sauce, nutritional yeast, and roasted vegetables."
            },
            "Keto": {
                "breakfast": "Eggs scrambled in grass-fed butter with spinach, avocado, and cheddar cheese.",
                "lunch": "Grilled chicken thighs or salmon with cauli-rice and olive oil Caesar salad.",
                "snack": "Macadamia nuts, string cheese, or keto collagen shake.",
                "dinner": "Pan-seared steak or paneer with grilled asparagus and herb butter."
            }
        }
    }

    json_path = os.path.join(DATASETS_DIR, "exercises_nutrition.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(exercise_nutrition_data, f, indent=2)
    print(f"Saved exercise & nutrition catalog to {json_path}")
    return df

def train_churn_model(df):
    print("\nTraining AI Member Churn Classifier...")
    
    # Feature columns for modeling
    features = [
        "age", "monthly_fee", "tenure_months", "has_trainer", 
        "payment_delays", "avg_weekly_visits", "days_since_last_visit", 
        "attendance_drop_ratio", "avg_session_mins"
    ]
    
    X = df[features]
    y = df["churn"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Random Forest Model
    rf = RandomForestClassifier(n_estimators=100, max_depth=8, min_samples_split=4, random_state=42)
    rf.fit(X_train_scaled, y_train)

    y_pred = rf.predict(X_test_scaled)
    y_prob = rf.predict_proba(X_test_scaled)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_prob)

    print(f"Model Performance Metrics:")
    print(f" - Accuracy:  {acc:.4f} ({acc*100:.2f}%)")
    print(f" - Precision: {prec:.4f}")
    print(f" - Recall:    {rec:.4f}")
    print(f" - F1 Score:  {f1:.4f}")
    print(f" - ROC-AUC:   {roc:.4f}")

    # Feature Importance
    feature_importances = dict(zip(features, rf.feature_importances_))
    sorted_importance = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)
    print("\nTop Churn Drivers (Feature Importance):")
    for feat, imp in sorted_importance[:5]:
        print(f" - {feat}: {imp:.4f}")

    # Save artifacts
    model_payload = {
        "scaler": scaler,
        "model": rf,
        "features": features,
        "feature_importances": feature_importances,
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "roc_auc": round(roc, 4)
        }
    }
    churn_model_path = os.path.join(SAVED_MODELS_DIR, "churn_model.joblib")
    joblib.dump(model_payload, churn_model_path)
    print(f"Saved Churn Prediction Model to {churn_model_path}")

def train_footfall_model():
    print("\nTraining Gym Footfall & Peak Hours Regression Model...")
    # Generate 180 days of hourly checkin data (6 AM to 10 PM)
    hours = np.tile(np.arange(6, 23), 180)
    day_of_week = np.repeat(np.random.randint(0, 7, size=180), 17)
    
    # Gym traffic curve: morning peak (7-9 AM) and evening peak (5-8 PM)
    traffic = []
    for h, d in zip(hours, day_of_week):
        base = 15
        if 6 <= h <= 9:
            base += 35 + (9 - abs(h - 8)) * 8
        elif 17 <= h <= 20:
            base += 55 + (20 - abs(h - 18)) * 10
        elif 10 <= h <= 16:
            base += 18
        else:
            base += 8
        
        # Weekend adjustment (more spread out)
        if d in [5, 6]:
            base = base * 0.85
        noise = np.random.normal(0, 4)
        traffic.append(max(2, int(base + noise)))

    X = np.column_stack([hours, day_of_week])
    y = np.array(traffic)

    reg = Ridge()
    reg.fit(X, y)

    footfall_payload = {
        "model": reg,
        "max_capacity": 100,
        "hourly_baselines": {
            6: 25, 7: 55, 8: 65, 9: 45, 10: 22, 11: 18, 12: 15,
            13: 14, 14: 16, 15: 22, 16: 38, 17: 72, 18: 88, 19: 82, 20: 58, 21: 30, 22: 12
        }
    }
    footfall_path = os.path.join(SAVED_MODELS_DIR, "footfall_model.joblib")
    joblib.dump(footfall_payload, footfall_path)
    print(f"Saved Footfall Forecast Model to {footfall_path}")

if __name__ == "__main__":
    df = generate_and_save_datasets()
    train_churn_model(df)
    train_footfall_model()
    print("\n=== AI/ML Model Training Pipeline Completed Successfully ===")
