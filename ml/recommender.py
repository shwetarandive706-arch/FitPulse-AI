import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "datasets", "exercises_nutrition.json")

_kb_cache = None

def get_knowledge_base():
    global _kb_cache
    if _kb_cache is None:
        if not os.path.exists(DATA_PATH):
            from ml.train_models import generate_and_save_datasets
            generate_and_save_datasets()
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            _kb_cache = json.load(f)
    return _kb_cache

def calculate_biometrics(weight_kg, height_cm, age, gender="Male", activity_level="Moderate"):
    """
    Computes BMI, BMR (Mifflin-St Jeor), and TDEE.
    """
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m ** 2), 1)

    if bmi < 18.5:
        bmi_category = "Underweight"
    elif bmi < 25.0:
        bmi_category = "Normal Weight"
    elif bmi < 30.0:
        bmi_category = "Overweight"
    else:
        bmi_category = "Obese"

    # Mifflin-St Jeor Equation
    # Men: 10 * weight + 6.25 * height - 5 * age + 5
    # Women: 10 * weight + 6.25 * height - 5 * age - 161
    if str(gender).strip().lower() == "female":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5

    activity_multipliers = {
        "Sedentary": 1.2,
        "Light": 1.375,
        "Moderate": 1.55,
        "Active": 1.725,
        "Very Active": 1.9
    }
    mult = activity_multipliers.get(activity_level, 1.55)
    tdee = int(bmr * mult)

    return {
        "bmi": bmi,
        "bmi_category": bmi_category,
        "bmr": int(bmr),
        "tdee": tdee
    }

def generate_personalized_plan(weight_kg, height_cm, age, gender, fitness_goal, dietary_pref="Vegetarian", activity_level="Moderate", days_per_week=4):
    kb = get_knowledge_base()
    bio = calculate_biometrics(weight_kg, height_cm, age, gender, activity_level)

    # Goal defaults to General Fitness if not matched
    goals_kb = kb.get("goals", {})
    goal_info = goals_kb.get(fitness_goal, goals_kb.get("General Fitness", {}))

    # Caloric target
    target_calories = bio["tdee"] + goal_info.get("calorie_adjustment", 0)
    target_calories = max(1200, target_calories)  # Safe lower bound

    # Macronutrient breakdown
    protein_per_kg = goal_info.get("protein_per_kg", 1.8)
    protein_g = int(weight_kg * protein_per_kg)
    protein_cals = protein_g * 4

    carb_pct = goal_info.get("carb_percentage", 0.45)
    fat_pct = goal_info.get("fat_percentage", 0.25)

    fat_g = int((target_calories * fat_pct) / 9)
    # Remaining calories for carbs
    rem_cals = target_calories - protein_cals - (fat_g * 9)
    carbs_g = max(50, int(rem_cals / 4))

    # Diet plan lookup
    diet_plans = kb.get("diet_plans", {})
    clean_diet = dietary_pref if dietary_pref in diet_plans else "Vegetarian"
    custom_diet = diet_plans.get(clean_diet, diet_plans["Vegetarian"])

    # Workout Routine
    workout_routine = goal_info.get("routine_details", {})
    routine_days = list(workout_routine.keys())[:days_per_week]
    custom_workout = {day: workout_routine[day] for day in routine_days}

    water_liters = round((weight_kg * 0.033) + 0.5, 1)

    return {
        "biometrics": bio,
        "fitness_goal": fitness_goal,
        "dietary_preference": clean_diet,
        "target_calories": target_calories,
        "macronutrients": {
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
            "protein_cals": protein_cals,
            "carbs_cals": carbs_g * 4,
            "fat_cals": fat_g * 9
        },
        "daily_water_liters": water_liters,
        "workout_focus": goal_info.get("workout_focus", "Balanced Resistance & Cardio"),
        "recommended_splits": goal_info.get("recommended_splits", []),
        "weekly_workout_schedule": custom_workout,
        "daily_meal_plan": custom_diet
    }
