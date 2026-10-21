# 🎓 FitPulse AI — Viva Voce Preparation Guide & Examiner Cheat Sheet

### Q1: What is the main objective of FitPulse AI?
**Answer**: FitPulse AI is an intelligent Gym Membership & Subscription Management System. Beyond standard member tracking and billing, it integrates **Supervised Machine Learning (Random Forest)** to predict member churn before subscriptions lapse, uses **dynamic cryptographic QR codes** to eliminate proxy entries, and provides an **AI personalized workout & nutrition recommender** based on biometric calculations (BMR and TDEE).

### Q2: Why did you choose Random Forest for Member Churn Prediction?
**Answer**:
1. **Handling Non-linear Relationships**: Member dropout decisions depend on non-linear interactions between recency of visits, attendance drop ratio, fee structure, and trainer presence.
2. **Robustness Against Overfitting**: As an ensemble of decision trees with bagging (bootstrap aggregating) and random feature subspace selection, Random Forest prevents single-tree overfitting.
3. **Feature Importance Interpretability**: Random Forest calculates Mean Decrease in Impurity (Gini importance), allowing us to show gym managers exactly why a member is at risk (e.g. "Weekly visits dropped 80%").

### Q3: What were your model evaluation metrics?
**Answer**:
- **Accuracy**: 97.00%
- **Precision**: 100.00% (When the model flags a member as churn risk, it is highly reliable, avoiding wasted discount vouchers on loyal members).
- **Recall**: 84.75%
- **F1 Score**: 0.9174
- **ROC-AUC**: 0.9956 (Demonstrating outstanding discriminative power across classification thresholds).

### Q4: How does the dynamic QR check-in work? Why is it better than a static QR code?
**Answer**: A static QR code can be photographed, emailed, or shared on WhatsApp, allowing unauthorized friends to enter the gym. FitPulse AI generates a **dynamic token** hashed using SHA-256 with a unique server timestamp and random cryptographic salt. The token is valid for only **300 seconds (5 minutes)** and is marked as `is_used = 1` immediately upon scanning. Duplicate check-ins within 30 minutes are also rejected.

### Q5: How is the AI Workout & Nutrition plan calculated?
**Answer**:
1. **BMR (Basal Metabolic Rate)** is computed using the medically recognized **Mifflin-St Jeor equation**:
   - Males: $BMR = 10 	imes weight(kg) + 6.25 	imes height(cm) - 5 	imes age + 5$
   - Females: $BMR = 10 	imes weight(kg) + 6.25 	imes height(cm) - 5 	imes age - 161$
2. **TDEE (Total Daily Energy Expenditure)** adjusts BMR by an activity multiplier (Sedentary: 1.2 to Active: 1.725).
3. **Calorie Adjustment**: A 500 kcal deficit for fat loss, or a 350 kcal surplus for muscle hypertrophy.
4. **Macronutrients**: Protein is fixed at 1.8 - 2.2 g/kg, fats at 20-25% of calories, and carbohydrates fill the remainder.

### Q6: What database did you use and why?
**Answer**: We used **SQLite3** because it is a lightweight, zero-configuration, serverless, self-contained relational database. It supports full ACID transactions, foreign keys (`PRAGMA foreign_keys = ON`), and handles standard gym workloads of tens of thousands of members without needing separate server maintenance.

### Q7: Explain the database entities and relationships.
**Answer**:
- `users`: Stores members and admin accounts with Werkzeug hashed passwords.
- `plans`: Stores membership tiers (Starter, Pro, Elite, VIP) and pricing.
- `subscriptions`: 1-to-N relationship between members and plans, tracking start date, end date, payment status, and auto-renewal.
- `checkins`: 1-to-N relationship tracking every entry timestamp, method, and session duration.
- `qr_tokens`: Stores dynamic, temporary tokens with expiration timestamps.
- `ai_predictions`: Logs historical churn scores, risk drivers, and retention actions.

### Q8: What are the primary features influencing member churn in your model?
**Answer**:
1. `avg_weekly_visits` (37.2% importance): Drop in weekly gym frequency.
2. `attendance_drop_ratio` (21.0% importance): Decline in recent 14-day visits compared to historical baseline.
3. `avg_session_mins` (20.3% importance): Shorter, rushed workouts indicate declining motivation.
4. `days_since_last_visit` (17.0% importance): Inactivity gap.
