from backend.models import User, ActivityLevel

def calculate_bmr(user: User) -> float:
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation"""
    if user.gender == "male":
        bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age + 5
    else:
        bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age - 161
    return bmr

def calculate_tdee(user: User, bmr: float) -> float:
    """Calculate Total Daily Energy Expenditure"""
    activity_multipliers = {
        ActivityLevel.sedentary: 1.2,
        ActivityLevel.light: 1.375,
        ActivityLevel.moderate: 1.55,
        ActivityLevel.active: 1.725
    }
    return bmr * activity_multipliers[user.activity]

def get_daily_calories(user: User) -> float:
    """Get recommended daily calories based on goal"""
    bmr = calculate_bmr(user)
    tdee = calculate_tdee(user, bmr)
    
    if user.goal == "lose":
        return tdee - 500  # Deficit for weight loss
    elif user.goal == "gain":
        return tdee + 500  # Surplus for weight gain
    else:
        return tdee  # Maintenance

def calculate_daily_calories(user: User) -> float:
    """Calculate daily calorie needs based on user profile and goal"""
    return get_daily_calories(user)

def get_macro_targets(user: User, daily_calories: float) -> dict:
    """Calculate macro targets based on goal"""
    if user.goal == "lose":
        # Higher protein, lower carbs for weight loss
        protein_ratio = 0.35
        carb_ratio = 0.35
        fat_ratio = 0.30
    elif user.goal == "gain":
        # Higher carbs for muscle gain
        protein_ratio = 0.30
        carb_ratio = 0.45
        fat_ratio = 0.25
    else:
        # Balanced for maintenance
        protein_ratio = 0.30
        carb_ratio = 0.40
        fat_ratio = 0.30
    
    return {
        "protein": (daily_calories * protein_ratio) / 4,  # 4 cal per gram
        "carbs": (daily_calories * carb_ratio) / 4,      # 4 cal per gram
        "fat": (daily_calories * fat_ratio) / 9          # 9 cal per gram
    }