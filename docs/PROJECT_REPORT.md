# 📚 ACADEMIC PROJECT REPORT
## P.D.E.A’s Waghire College of Arts, Commerce & Science, Saswad
### Department of Computer Science
**Academic Year 2026-27 | Class: T.Y. B.Sc(CS) Semester V**

---

### A PROJECT REPORT ON:
# **FitPulse AI — Intelligent Gym Membership & Subscription Management System**

**SUBMITTED BY:**
- Pawar Pruthviraj Navnath
- Khamkar Om Dadasaheb
- Kamthe Ganesh Bhauso

**PROJECT GUIDE:**
- Prof. P.K. Zurange Mam

---

## 📑 INDEX
| S.N | Content | Status |
|:---:|:---|:---:|
| 1. | Introduction | Complete |
| 2. | Problem Definition | Complete |
| 3. | Scope of System | Complete |
| 4. | Objectives of Proposed System | Complete |
| 5. | Fact Finding Techniques | Complete |
| 6. | Hardware and Software Specifications | Complete |
| 7. | E-R Diagrams | Complete |
| 8. | UML Diagrams (Use Case, Sequence, Activity, Component, Deployment) | Complete |
| 9. | Data Dictionary | Complete |
| 10. | Output Screens & System Modules | Complete |
| 11. | Reports Generated (Excel CSV & Official Printable PDF) | Complete |
| 12. | Testing & Verification (14/14 Unit Tests Passed) | Complete |
| 13. | Limitations | Complete |
| 14. | Future Enhancements | Complete |
| 15. | Bibliography | Complete |

---

## 1. INTRODUCTION
The **FitPulse AI Gym Membership & Subscription Management System** is a next-generation web application designed to simplify, modernize, and automate fitness facility operations while tackling member attrition using Machine Learning.

Traditional fitness centers rely on manual registers, magnetic swipe cards, or static QR codes. These mechanisms are inefficient, prone to proxy entries (where one membership card is shared among multiple friends), and generate unorganized paperwork. Most crucially, traditional systems are purely retrospective: they only notice that a member has left after their subscription has already expired.

FitPulse AI solves these core bottlenecks through:
- **Dynamic Cryptographic QR Turnstile Access**: 5-minute auto-refreshing SHA-256 tokens that guarantee only the authorized subscriber enters.
- **AI-Powered Member Churn Prediction**: A supervised **Random Forest Classifier** trained on behavioral telemetry that predicts member dropout probabilities with **97% accuracy** and prescribes personalized retention interventions.
- **AI Personalized Workout & Nutrition Recommender**: Computes exact Basal Metabolic Rate (BMR using Mifflin-St Jeor), Total Daily Energy Expenditure (TDEE), and delivers custom exercise splits and macronutrient targets.
- **Gym Peak Footfall Forecaster**: Predicts hourly gym capacity to prevent overcrowding and optimize equipment maintenance.

---

## 2. PROBLEM DEFINITION
1. **High Member Dropout / Churn Rates**: Commercial gyms lose 30% to 50% of subscribers annually. Managers have no proactive early-warning system to identify disengaged members before they quit.
2. **Proxy Gym Check-in Fraud**: Static QR codes and shared membership RFID cards are routinely shared with non-paying friends, resulting in revenue leakage.
3. **Manual Entry & Congestion**: Peak morning and evening hours cause bottlenecks at the reception counter.
4. **Lack of Personalized Fitness Guidance**: New gym goers frequently abandon their subscriptions due to intimidation or lack of tailored workout and diet plans.
5. **Fragmented Records**: Manual tracking makes it difficult to calculate Monthly Recurring Revenue (MRR) or export official audit records.

---

## 3. SCOPE OF SYSTEM
FitPulse AI is designed for commercial fitness clubs, health studios, university gyms, and sports complexes:
- **Gym Manager / Director Portal**: Live KPI dashboard (Members, Active Subscriptions, Today's Checkins, Total Revenue), member directory, subscription renewal manager, AI churn intelligence scanner, and CSV/Excel exports.
- **Member Self-Service Portal**: Digital holographic membership pass, live dynamic QR entry pass, personal attendance history, and the interactive AI Workout & Diet Planner.
- **Turnstile Gate Integration**: Front-desk dynamic QR terminal for touchless, fraud-proof access verification.

---

## 4. OBJECTIVES OF PROPOSED SYSTEM
1. Generate unique, time-limited cryptographic QR tokens (SHA-256) valid for 300 seconds to eliminate proxy entries.
2. Apply machine learning classification to predict member churn and automatically recommend retention strategies.
3. Deliver scientific, biometric-based workout and nutritional blueprints (BMI, BMR, TDEE, protein/carb/fat grams).
4. Provide real-time and predicted facility occupancy analytics.
5. Provide one-click data export to standard Excel/CSV and printable official sheets.

---

## 5. FACT FINDING TECHNIQUES
To establish functional and domain requirements, the following techniques were utilized:
1. **Interviewing Gym Owners and Personal Trainers**: Discovered that members who reduce their weekly visits by over 50% over a 14-day window have an 85% probability of discontinuing their memberships.
2. **Operational Observation**: Observed entrance turnstiles during peak hours (6:00 PM – 8:00 PM) to measure check-in latency.
3. **Literature Review**: Evaluated sports nutrition literature (Mifflin-St Jeor equation) and machine learning classification algorithms (Random Forest vs Logistic Regression).

---

## 6. HARDWARE AND SOFTWARE SPECIFICATIONS

### Hardware Requirements
- **Server/Laptop**: Modern 64-bit CPU (Intel Core i3/i5/i7 or AMD Ryzen), 4 GB RAM minimum, 500 MB free storage.
- **Client Devices**: Any desktop, laptop, tablet, or smartphone equipped with a modern web browser.

### Software Specifications
- **Operating System**: Windows 10 / Windows 11 / Linux / macOS.
- **Backend Language**: Python 3.12+ (tested and verified on Python 3.14).
- **Backend Framework**: Flask 3.x REST API layer.
- **Database**: SQLite3 with foreign key enforcement and relational indexes.
- **Machine Learning Libraries**: `scikit-learn`, `numpy`, `pandas`, `joblib`.
- **Frontend Technologies**: HTML5, CSS3 (Modern responsive design system), Vanilla JavaScript (ES6+).
- **Security**: Werkzeug PBKDF2-SHA256 password hashing, SHA-256 session tokens.

---

## 7. E-R DIAGRAMS
*(Full relational diagram provided in UML_DIAGRAMS.md)*
- Entities: `USERS`, `PLANS`, `SUBSCRIPTIONS`, `CHECKINS`, `QR_TOKENS`, `AI_PREDICTIONS`.
- Primary Keys: `id` across all relational tables.
- Foreign Key Constraints: `member_id` referencing `users(id)`, `plan_id` referencing `plans(id)`.

---

## 8. UML DIAGRAMS
*(Complete specifications and Mermaid diagrams provided in UML_DIAGRAMS.md)*
1. **Use Case Diagram**: Models interactions for Admin and Member actors across 8 primary system use cases.
2. **Sequence Diagram**: Details the step-by-step token generation, transmission, cryptographic validation, and database check-in recording.
3. **Activity Diagram**: Illustrates the AI Member Churn classification pipeline from feature extraction to risk score assignment.
4. **Component Diagram**: Shows the decoupled interaction between Frontend UI, Flask API, ML Inference Engines, and SQLite Database.
5. **Deployment Diagram**: Documents client-server topology over LAN/Internet.

---

## 9. DATA DICTIONARY

### 1. Users Table (`users`)
| Field Name | Data Type | Key / Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique user identifier |
| `role` | TEXT | NOT NULL ('admin', 'member') | Access control role |
| `name` | TEXT | NOT NULL | Full name of user |
| `email` | TEXT | UNIQUE NOT NULL | Email address |
| `phone` | TEXT | NULLABLE | Phone number |
| `username` | TEXT | UNIQUE NOT NULL | Login username |
| `password_hash` | TEXT | NOT NULL | Hashed password |
| `age` | INTEGER | DEFAULT 25 | Member age |
| `gender` | TEXT | DEFAULT 'Male' | Gender |
| `height_cm` | REAL | DEFAULT 172.0 | Height in centimeters |
| `weight_kg` | REAL | DEFAULT 70.0 | Weight in kilograms |
| `fitness_goal` | TEXT | DEFAULT 'General Fitness' | Primary fitness objective |
| `dietary_pref` | TEXT | DEFAULT 'Vegetarian' | Dietary preference |
| `has_trainer` | INTEGER | DEFAULT 0 | Whether 1-on-1 trainer assigned |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Registration timestamp |

### 2. Plans Table (`plans`)
| Field Name | Data Type | Key / Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique plan ID |
| `name` | TEXT | UNIQUE NOT NULL | Plan name (e.g. Pro Quarterly) |
| `tier` | TEXT | NOT NULL | Tier level (Bronze, Silver, Gold, Platinum) |
| `duration_days` | INTEGER | NOT NULL | Active duration (30, 90, 365 days) |
| `price` | REAL | NOT NULL | Subscription fee in INR |
| `features_json` | TEXT | NULLABLE | JSON array of included perks |

### 3. Subscriptions Table (`subscriptions`)
| Field Name | Data Type | Key / Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Subscription record ID |
| `member_id` | INTEGER | FOREIGN KEY (`users.id`) | Subscriber ID |
| `plan_id` | INTEGER | FOREIGN KEY (`plans.id`) | Subscribed Plan ID |
| `start_date` | DATE | NOT NULL | Subscription start date |
| `end_date` | DATE | NOT NULL | Subscription expiration date |
| `status` | TEXT | NOT NULL ('active', 'expired') | Current subscription state |
| `total_paid` | REAL | NOT NULL | Amount paid |
| `payment_status` | TEXT | DEFAULT 'paid' | Billing status |

### 4. Check-ins Table (`checkins`)
| Field Name | Data Type | Key / Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Attendance check-in ID |
| `member_id` | INTEGER | FOREIGN KEY (`users.id`) | Member ID |
| `checkin_time` | DATETIME | DEFAULT CURRENT_TIMESTAMP | Timestamp of entry |
| `method` | TEXT | DEFAULT 'qr_code' | Check-in method |
| `duration_mins` | INTEGER | DEFAULT 60 | Workout session duration |

### 5. Dynamic QR Tokens Table (`qr_tokens`)
| Field Name | Data Type | Key / Constraint | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Token record ID |
| `token` | TEXT | UNIQUE NOT NULL | SHA-256 dynamic token |
| `member_id` | INTEGER | FOREIGN KEY (`users.id`) | Associated member |
| `created_at` | DATETIME | NOT NULL | Generation timestamp |
| `expires_at` | DATETIME | NOT NULL | Expiration timestamp (5 mins) |
| `is_used` | INTEGER | DEFAULT 0 | Consumption flag (anti-replay) |

---

## 10. OUTPUT SCREENS & MODULES
1. **Admin KPI Dashboard**: Displays real-time counts for Enrolled Members, Active Subscriptions, Today's Checkins, Total Revenue, and Peak Hour Footfall forecast bar chart.
2. **Member Directory**: Interactive roster with real-time subscription status, days remaining countdown, total visits, last check-in date, and 1-click renewal.
3. **AI Member Churn Intelligence Hub**: Displays high, medium, and low churn risk counts, member-level probability percentages, underlying behavioral factors, and tailored retention recommendations.
4. **Dynamic Turnstile QR Terminal**: Live self-refreshing QR code screen for front-desk turnstiles alongside a check-in test simulator.
5. **Member Portal & Digital Pass**: Holographic membership card with active tier, days remaining progress bar, personal QR check-in pass, and workout history.
6. **AI Workout & Nutrition Planner**: Interactive calculator providing BMR, TDEE, daily calories, macronutrient grams (protein, carbs, fats), water intake, weekly exercise routine, and meal schedule.

---

## 11. REPORTS GENERATED
- **Member Roster CSV Sheet**: Comprehensive export of all registered members with tier, expiration dates, attendance counts, and contact information.
- **Attendance Log CSV Sheet**: Complete historical log of all turnstile entries with timestamps and workout durations.
- **Printable Official Attendance Sheet**: Clean university-grade printable stylesheet with college/gym header and signature lines.

---

## 12. TESTING & VERIFICATION
The system includes a dedicated unit test suite executed via Python's standard `unittest` framework:
```bash
python -m unittest discover -s tests -p "test_*.py"
```
**Test Results Summary**:
- `test_01_health_status`: PASSED
- `test_02_admin_login`: PASSED
- `test_03_member_login`: PASSED
- `test_04_invalid_login`: PASSED
- `test_05_admin_dashboard_metrics`: PASSED
- `test_06_member_listing`: PASSED
- `test_07_membership_plans`: PASSED
- `test_08_dynamic_qr_generation`: PASSED
- `test_09_csv_exports`: PASSED
- `test_01_churn_prediction_low_risk`: PASSED
- `test_02_churn_prediction_high_risk`: PASSED
- `test_03_biometrics_calculation`: PASSED
- `test_04_personalized_plan_generation`: PASSED
- `test_05_footfall_forecasting`: PASSED

**Total: 14 out of 14 automated tests passed (100% pass rate).**

---

## 13. LIMITATIONS
1. **Hardware Integration**: The current demonstration uses browser-simulated turnstiles; production deployment requires physical IoT turnstiles (e.g. ESP32 or Raspberry Pi relay triggers).
2. **Payment Gateway**: Financial transactions are simulated in local currency without live Razorpay/Stripe webhooks.
3. **Local Database**: SQLite is optimized for single-server setups; scaling to multi-branch gym franchises would benefit from PostgreSQL replication.

---

## 14. FUTURE ENHANCEMENTS
1. **Mobile Application**: Packaging client portals into iOS and Android apps using Capacitor or React Native.
2. **Computer Vision Form Correction**: Integrating OpenCV/MediaPipe for real-time camera-based exercise posture feedback.
3. **Automated WhatsApp / SMS Retention Nudges**: Automatic dispatch of renewal discount promo codes via Twilio when high churn risk is flagged.
4. **Cloud Database Deployment**: Synchronizing attendance across multiple gym locations using Supabase or AWS RDS.

---

## 15. BIBLIOGRAPHY
1. **Machine Learning with Python** — Sebastian Raschka & Vahid Mirjalili, *Python Machine Learning*, Packt Publishing.
2. **Hands-On Machine Learning with Scikit-Learn** — Aurélien Géron, O'Reilly Media.
3. **Flask Web Development** — Miguel Grinberg, *Developing Web Applications with Python*, O'Reilly Media.
4. **Database System Concepts** — Abraham Silberschatz, Henry F. Korth, and S. Sudarshan, McGraw-Hill.
5. **Software Engineering** — Ian Sommerville, Pearson Education.
6. **Mifflin MD, St Jeor ST, et al.** — "A new predictive equation for resting energy expenditure in healthy individuals", *The American Journal of Clinical Nutrition*.
