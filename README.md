# ⚡ FitPulse AI — Gym Membership & Subscription Intelligence System
### Third Year (T.Y.) B.Sc(CS) / B.E. Computer Engineering Academic Project
**P.D.E.A's Waghire College of Arts, Commerce & Science, Saswad**

![Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.13%20%7C%203.14-blue)
![Framework](https://img.shields.io/badge/Framework-Flask%203.x-black)
![ML](https://img.shields.io/badge/Machine%20Learning-Random%20Forest%20%7C%20Ridge%20%7C%20Content--Based-emerald)
![Tests](https://img.shields.io/badge/Tests-14%2F14%20Passed-brightgreen)

---

## 📌 Project Overview
**FitPulse AI** is an advanced, production-grade **Gym Membership & Subscription Management System** empowered with genuine **Machine Learning models**. 

Traditional fitness centers suffer from severe member dropouts (up to 50% churn within 6 months), manual paper check-ins, unauthorized proxy entries, and generic, unpersonalized workout guidance. FitPulse AI solves these core operational and business bottlenecks with:
1. **Dynamic Cryptographic QR Turnstile Access**: Eliminates proxy entry and shared membership passes via 5-minute time-decaying SHA-256 tokens.
2. **AI Member Churn Prediction (Random Forest Classifier)**: Continuously evaluates behavioral telemetry (visit frequency decline, days inactive, payment delays, tenure) to forecast member dropouts before subscriptions expire, providing actionable retention interventions.
3. **AI Personalized Fitness & Nutrition Engine**: Computes exact BMR (Mifflin-St Jeor), TDEE, macronutrient splits (protein/carbs/fats in grams), and custom multi-day workout splits tailored to member goals and dietary preferences.
4. **Gym Peak Footfall & Occupancy Forecaster**: Predicts hourly gym traffic (6 AM to 10 PM) using regression analysis to optimize staff shifts and equipment availability.
5. **University-Grade Official Reports**: 1-click export of structured **CSV/Excel spreadsheets** and printable attendance records.

---

## 🚀 Quick Start Guide

### Method 1: Instant 1-Click Startup (Windows)
1. Double click **`START_SERVER.bat`** to start the Flask backend.
2. Double click **`RUN_APP.bat`** (or open [http://localhost:5000](http://localhost:5000) in Chrome/Edge/Firefox).

### Method 2: Terminal Execution
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Retrain ML models & generate datasets (if needed)
python ml/train_models.py

# 3. Start application
python app.py
```

---

## 🔑 Demo Login Credentials (With Quick Switcher)

The application features a convenient **1-Click Demo Switcher** in the top bar:

| Role | Username / Identifier | Password | Demonstration Purpose |
|---|---|---|---|
| **Gym Director / Admin** | `admin` | `admin123` | Full administrative dashboard, member CRUD, AI churn scanner, turnstile QR gate, CSV exports |
| **Member 1 (Rahul Sharma)** | `member1` | `1234` | **Active Pro Member**: High weekly attendance, Low Churn Risk (<15%), personal QR pass |
| **Member 3 (Amit Verma)** | `member3` | `1234` | **Critical Churn Risk**: Absent for 18 days, visit frequency dropped by 80%, flagged by AI for retention discount |
| **Member 5 (Rohan Joshi)** | `member5` | `1234` | **Expired Member**: Subscription lapsed, rejected by turnstile QR scanner until renewed |

---

## 📁 Project Directory Structure
```
Gym_Membership_AI_System/
├── app.py                      # Flask Application Server & REST API endpoints
├── database.py                 # SQLite database schema, initialization & seed data
├── models.py                   # Business logic, query helpers, auth, dynamic QR engine
├── requirements.txt            # Python dependencies (flask, scikit-learn, numpy, pandas, joblib)
├── START_SERVER.bat            # 1-Click server launcher
├── RUN_APP.bat                 # 1-Click browser launcher
├── README.md                   # Complete technical manual & guide
├── ml/                         # Machine Learning Pipeline
│   ├── __init__.py
│   ├── train_models.py         # Synthetic dataset generator, feature extraction & training
│   ├── churn_predictor.py      # Random Forest churn inference engine & risk factors
│   ├── recommender.py          # Biometric BMR/TDEE & workout/diet recommendation engine
│   ├── footfall_forecaster.py  # Hourly gym occupancy regression forecaster
│   └── saved_models/
│       ├── churn_model.joblib  # Serialized Random Forest classifier
│       └── footfall_model.joblib # Serialized Footfall model
├── datasets/
│   ├── gym_churn_dataset.csv   # 1,500 record member demographic & behavioral dataset
│   └── exercises_nutrition.json# Structured catalog of exercises, sets/reps & diets
├── static/
│   ├── css/
│   │   └── style.css           # Premium fitness design system (Obsidian, Emerald, Cyan)
│   ├── js/
│   │   ├── app.js              # State manager, toast notifications, demo switcher
│   │   ├── admin.js            # Admin KPI charts, member roster, AI churn scanner
│   │   ├── member.js           # Member pass, dynamic QR generator, AI fitness planner
│   │   ├── qrcode.min.js       # Client-side QR generator
│   │   └── html5-qrcode.min.js # Client-side camera QR scanner
├── templates/
│   └── index.html              # Unified responsive Single Page Application UI
├── tests/
│   ├── __init__.py
│   ├── test_api.py             # 9 REST API automated tests
│   └── test_ml_pipeline.py     # 5 AI/ML pipeline automated tests
└── docs/                       # Academic Submission Documentation
    ├── PROJECT_REPORT.md       # 15-Chapter Academic Project Report (Waghire College Format)
    ├── VIVA_PREPARATION_GUIDE.md # 30+ Examiner Viva Q&A with math/theory
    ├── SYNOPSIS.md             # 2-Page Project Synopsis
    └── UML_DIAGRAMS.md         # ER Diagram & 5 UML Diagrams (Use Case, Sequence, etc.)
```

---

## 🧠 AI / Machine Learning Details

### 1. Member Churn Classifier (`RandomForestClassifier`)
- **Trained on**: 1,500 member behavioral records.
- **Input Features**: `age`, `monthly_fee`, `tenure_months`, `has_trainer`, `payment_delays`, `avg_weekly_visits`, `days_since_last_visit`, `attendance_drop_ratio`, `avg_session_mins`.
- **Model Evaluation**:
  - **Accuracy**: 97.00%
  - **Precision**: 1.0000
  - **Recall**: 84.75%
  - **F1 Score**: 0.9174
  - **ROC-AUC**: 0.9956
- **Primary Feature Importances**:
  1. `avg_weekly_visits`: 37.2%
  2. `attendance_drop_ratio`: 21.0%
  3. `avg_session_mins`: 20.3%
  4. `days_since_last_visit`: 17.0%

### 2. Personalized Biometric & Nutrition Engine
- Uses **Mifflin-St Jeor Equation** for Basal Metabolic Rate (BMR):
  - Males: $BMR = 10 	imes weight + 6.25 	imes height - 5 	imes age + 5$
  - Females: $BMR = 10 	imes weight + 6.25 	imes height - 5 	imes age - 161$
- Calculates Total Daily Energy Expenditure ($TDEE = BMR 	imes Activity\_Multiplier$)
- Formulates exact target protein, carbohydrate, and fat grams alongside goal-tailored exercise splits (PPL, Upper/Lower, Full Body).

---

## 🧪 Automated Testing
All unit tests pass with 100% success:
```bash
python -m unittest discover -s tests -p "test_*.py"
```
**Results: 14/14 tests passed in ~2.0 seconds.**

---

## 🎓 Academic Submission & College Viva
Full documentation matching Pune University / Waghire College requirements is available in the `docs/` folder:
- **`docs/PROJECT_REPORT.md`**: Official 15-chapter project report.
- **`docs/VIVA_PREPARATION_GUIDE.md`**: Examiner Q&A cheat sheet.
- **`docs/UML_DIAGRAMS.md`**: Diagrams for ER, Use Case, Sequence, Activity, Component, and Deployment.
