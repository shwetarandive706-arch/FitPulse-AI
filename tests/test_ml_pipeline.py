import unittest
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.churn_predictor import predict_member_churn
from ml.recommender import generate_personalized_plan, calculate_biometrics
from ml.footfall_forecaster import predict_hourly_footfall

class FitPulseMLTestCase(unittest.TestCase):
    def test_01_churn_prediction_low_risk(self):
        """Test churn predictor on loyal/active member"""
        active_member = {
            "age": 28,
            "monthly_fee": 1499.0,
            "tenure_months": 12,
            "has_trainer": 1,
            "payment_delays": 0,
            "avg_weekly_visits": 4.5,
            "days_since_last_visit": 1,
            "attendance_drop_ratio": 0.05,
            "avg_session_mins": 75
        }
        res = predict_member_churn(active_member)
        self.assertIn("churn_probability", res)
        self.assertIn("risk_level", res)
        self.assertEqual(res["risk_level"], "Low")
        self.assertLess(res["churn_probability"], 35.0)

    def test_02_churn_prediction_high_risk(self):
        """Test churn predictor on inactive member with drop-off"""
        high_risk_member = {
            "age": 35,
            "monthly_fee": 1499.0,
            "tenure_months": 2,
            "has_trainer": 0,
            "payment_delays": 2,
            "avg_weekly_visits": 0.8,
            "days_since_last_visit": 21,
            "attendance_drop_ratio": 0.85,
            "avg_session_mins": 30
        }
        res = predict_member_churn(high_risk_member)
        self.assertEqual(res["risk_level"], "High")
        self.assertGreater(res["churn_probability"], 70.0)
        self.assertTrue(len(res["risk_factors"]) > 0)
        self.assertIn("CRITICAL", res["retention_action"])

    def test_03_biometrics_calculation(self):
        """Test Mifflin-St Jeor BMR and TDEE calculations"""
        bio = calculate_biometrics(weight_kg=70.0, height_cm=175.0, age=25, gender="Male", activity_level="Moderate")
        self.assertAlmostEqual(bio["bmi"], 22.9, places=1)
        self.assertEqual(bio["bmi_category"], "Normal Weight")
        self.assertGreater(bio["bmr"], 1600)
        self.assertGreater(bio["tdee"], 2400)

    def test_04_personalized_plan_generation(self):
        """Test complete workout and diet recommendation output"""
        plan = generate_personalized_plan(
            weight_kg=75.0,
            height_cm=178.0,
            age=26,
            gender="Male",
            fitness_goal="Muscle Gain",
            dietary_pref="Non-Vegetarian",
            days_per_week=4
        )
        self.assertEqual(plan["fitness_goal"], "Muscle Gain")
        self.assertGreater(plan["macronutrients"]["protein_g"], 140)
        self.assertTrue(len(plan["weekly_workout_schedule"]) == 4)
        self.assertIn("breakfast", plan["daily_meal_plan"])

    def test_05_footfall_forecasting(self):
        """Test hourly occupancy regression output"""
        res = predict_hourly_footfall(day_of_week=2)
        self.assertIn("hourly_breakdown", res)
        self.assertEqual(len(res["hourly_breakdown"]), 17) # 6 to 22
        # Peak evening hours (18:00) should have higher occupancy than mid-day (12:00)
        occ_18 = next(h["predicted_occupancy"] for h in res["hourly_breakdown"] if h["hour"] == 18)
        occ_12 = next(h["predicted_occupancy"] for h in res["hourly_breakdown"] if h["hour"] == 12)
        self.assertGreater(occ_18, occ_12)

if __name__ == "__main__":
    unittest.main()
