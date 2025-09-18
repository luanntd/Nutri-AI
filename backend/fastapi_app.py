from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os

from backend.models import Meal, User, MealSelection, Recommendation, Menu, SAMPLE_MEALS, Gender, ActivityLevel, Goal
from backend.calculations import calculate_daily_calories, get_macro_targets
from backend.ai_service import get_meal_recommendation, get_optimized_menu

app = FastAPI(title="Nutri AI API", description="AI-powered nutrition recommendation system")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
static_path = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Pydantic models for API requests/responses
class UserProfileRequest(BaseModel):
    name: str
    age: int
    gender: str
    height: float
    weight: float
    activity: str
    goal: str

class UserProfileResponse(BaseModel):
    daily_calories: float
    protein_target: float
    carb_target: float
    fat_target: float
    user: UserProfileRequest

class MealRecommendationRequest(BaseModel):
    user: UserProfileRequest
    selected_meals: List[dict]

class BudgetMenuRequest(BaseModel):
    user: UserProfileRequest
    budget: float

class OrderSummary(BaseModel):
    meals: List[dict]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_cost: float

# API Routes

@app.get("/")
async def root():
    """Serve the frontend"""
    static_index = os.path.join(static_path, "index.html")
    if os.path.exists(static_index):
        return FileResponse(static_index)
    return {"message": "Nutri AI API is running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Nutri AI API is running"}

@app.get("/api/meals")
async def get_meals():
    """Get all available meals grouped by category with cooking methods"""
    categories = {
        "carb": {"name": "🍚 Carbs", "meals": []},
        "protein": {"name": "🥩 Protein", "meals": []},
        "good_fat": {"name": "🥜 Good Fats", "meals": []},
        "fiber": {"name": "🥦 Fiber", "meals": []}
    }

    for meal in SAMPLE_MEALS:
        if meal.component_type in categories:
            meal_dict = meal.model_dump()
            # Include cooking methods for frontend selection
            categories[meal.component_type]["meals"].append(meal_dict)

    return {"categories": categories}

@app.post("/api/user/calculate", response_model=UserProfileResponse)
async def calculate_user_profile(user_data: UserProfileRequest):
    """Calculate user's daily nutritional targets"""
    try:
        # Create User object
        user = User(
            name=user_data.name,
            age=user_data.age,
            gender=Gender(user_data.gender),
            height=user_data.height,
            weight=user_data.weight,
            activity=ActivityLevel(user_data.activity),
            goal=Goal(user_data.goal)
        )
        
        # Calculate targets
        daily_calories = calculate_daily_calories(user)
        macro_targets = get_macro_targets(user, daily_calories)
        
        return UserProfileResponse(
            daily_calories=daily_calories,
            protein_target=macro_targets["protein"],
            carb_target=macro_targets["carbs"],
            fat_target=macro_targets["fat"],
            user=user_data
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/meals/recommend")
async def recommend_meals(request: MealRecommendationRequest):
    """Get AI recommendations for selected meals"""
    try:
        # Create User object
        user = User(
            name=request.user.name,
            age=request.user.age,
            gender=Gender(request.user.gender),
            height=request.user.height,
            weight=request.user.weight,
            activity=ActivityLevel(request.user.activity),
            goal=Goal(request.user.goal)
        )
        
        # Process selected meals
        meals = []
        quantities = []
        
        for meal_data in request.selected_meals:
            # Find the meal in SAMPLE_MEALS
            meal = next((m for m in SAMPLE_MEALS if m.name == meal_data["name"]), None)
            if meal:
                if meal_data.get("cooking_method"):
                    # Create meal with specific cooking method
                    method = next((m for m in meal.cooking_methods if m["method"] == meal_data["cooking_method"]), None)
                    if method:
                        processed_meal = Meal(
                            name=f"{meal.name} ({method['method']})",
                            calories=method["calories"],
                            protein=method["protein"],
                            carbs=method["carbs"],
                            fat=method["fat"],
                            price=method["price"],
                            component_type=meal.component_type,
                            food_type=meal.food_type,
                            cooking_methods=[method]
                        )
                        meals.append(processed_meal)
                else:
                    meals.append(meal)
                
                quantities.append(meal_data["quantity"])
        
        # Get AI recommendation
        selection = MealSelection(meals=meals, quantities=quantities)
        recommendation = get_meal_recommendation(user, selection)
        
        return recommendation.model_dump()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/daily/recommend")
async def recommend_daily_meals(request: dict):
    """Get AI recommendations for complete daily meal plan"""
    try:
        user_data = request["user"]
        daily_meals = request["daily_meals"]  # breakfast, lunch, dinner structure
        
        # Create User object
        user = User(
            name=user_data["name"],
            age=user_data["age"],
            gender=Gender(user_data["gender"]),
            height=user_data["height"],
            weight=user_data["weight"],
            activity=ActivityLevel(user_data["activity"]),
            goal=Goal(user_data["goal"])
        )
        
        # Process all daily meals
        all_meals = []
        all_quantities = []
        
        for meal_time in ["breakfast", "lunch", "dinner"]:
            if meal_time in daily_meals and daily_meals[meal_time]["meals"]:
                meals_data = daily_meals[meal_time]["meals"]
                quantities_data = daily_meals[meal_time]["quantities"]
                methods_data = daily_meals[meal_time]["methods"]
                
                for i, meal_name in enumerate(meals_data):
                    meal = next((m for m in SAMPLE_MEALS if m.name == meal_name), None)
                    if meal:
                        quantity = quantities_data[i] if i < len(quantities_data) else 100
                        method = methods_data[i] if i < len(methods_data) and methods_data[i] else None
                        
                        if method:
                            # Create meal with specific cooking method
                            method_data = next((m for m in meal.cooking_methods if m["method"] == method), None)
                            if method_data:
                                # Convert grams to servings for cooking methods (assume 100g per serving)
                                servings = quantity / 100.0
                                processed_meal = Meal(
                                    name=f"{meal.name} ({method_data['method']})",
                                    calories=method_data["calories"],
                                    protein=method_data["protein"],
                                    carbs=method_data["carbs"],
                                    fat=method_data["fat"],
                                    price=method_data["price"],
                                    component_type=meal.component_type,
                                    food_type=meal.food_type,
                                    cooking_methods=[method_data]
                                )
                                all_meals.append(processed_meal)
                                all_quantities.append(servings)  # Use servings for cooking methods
                            else:
                                # Fallback to base meal if cooking method not found
                                all_meals.append(meal)
                                all_quantities.append(quantity)  # Use grams for base meals
                        else:
                            all_meals.append(meal)
                            all_quantities.append(quantity)  # Use grams for base meals
        
        # Get AI recommendation for full day
        if all_meals:
            selection = MealSelection(meals=all_meals, quantities=all_quantities)
            recommendation = get_meal_recommendation(user, selection)
            return recommendation.model_dump()
        else:
            return {"error": "No meals selected"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/budget/optimize")
async def optimize_budget_menu(request: BudgetMenuRequest):
    """Get optimized menu within budget"""
    try:
        # Create User object
        user = User(
            name=request.user.name,
            age=request.user.age,
            gender=Gender(request.user.gender),
            height=request.user.height,
            weight=request.user.weight,
            activity=ActivityLevel(request.user.activity),
            goal=Goal(request.user.goal)
        )
        
        # Get optimized menu
        menu = get_optimized_menu(user, request.budget)
        
        return menu.model_dump()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/order/calculate")
async def calculate_order(meals: List[dict]):
    """Calculate total nutrition and cost for selected meals"""
    try:
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_cost = 0
        processed_meals = []
        
        for meal_data in meals:
            # Find the meal in SAMPLE_MEALS
            meal = next((m for m in SAMPLE_MEALS if m.name == meal_data["name"]), None)
            if meal:
                quantity = meal_data.get("quantity", 1)
                
                if meal_data.get("cooking_method"):
                    # Use specific cooking method
                    method = next((m for m in meal.cooking_methods if m["method"] == meal_data["cooking_method"]), None)
                    if method:
                        calories = method["calories"] * quantity
                        protein = method["protein"] * quantity
                        carbs = method["carbs"] * quantity
                        fat = method["fat"] * quantity
                        cost = method["price"] * quantity
                        
                        processed_meals.append({
                            "name": f"{meal.name} ({method['method']})",
                            "quantity": quantity,
                            "calories": calories,
                            "protein": protein,
                            "carbs": carbs,
                            "fat": fat,
                            "cost": cost
                        })
                else:
                    # Use base meal data (per 100g)
                    calories = (meal.calories * quantity) / 100
                    protein = (meal.protein * quantity) / 100
                    carbs = (meal.carbs * quantity) / 100
                    fat = (meal.fat * quantity) / 100
                    cost = (meal.price * quantity) / 100
                    
                    processed_meals.append({
                        "name": f"{meal.name} ({quantity}g)",
                        "quantity": quantity,
                        "calories": calories,
                        "protein": protein,
                        "carbs": carbs,
                        "fat": fat,
                        "cost": cost
                    })
                
                total_calories += calories
                total_protein += protein
                total_carbs += carbs
                total_fat += fat
                total_cost += cost
        
        return OrderSummary(
            meals=processed_meals,
            total_calories=total_calories,
            total_protein=total_protein,
            total_carbs=total_carbs,
            total_fat=total_fat,
            total_cost=total_cost
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)