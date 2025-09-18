from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os

from backend.models import (Meal, User, MealSelection, MealRecommendationRequest, 
                          Recommendation, Menu, SAMPLE_MEALS, Gender, ActivityLevel, Goal)
from backend.calculations import calculate_daily_calories, get_macro_targets
from backend.ai_service import get_meal_recommendation, get_optimized_menu

# Cooking method translation function
def translate_cooking_method(method):
    """Translate English cooking methods to Vietnamese"""
    translations = {
        'boiled': 'Luộc',
        'steamed': 'Hấp', 
        'raw': 'Sống/Tươi',
        'baked': 'Nướng lò',
        'grilled': 'Nướng',
        'fried': 'Chiên',
        'scrambled': 'Bác trứng',
        'plain': 'Nguyên chất',
        'spread': 'Phết',
        'drizzled': 'Rưới',
        'sautéed': 'Xào'
    }
    return translations.get(method, method)

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

# Pydantic models for API requests/responses (only needed ones)
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
    fiber_target: float
    user: UserProfileRequest

class BudgetMenuRequest(BaseModel):
    user: UserProfileRequest
    budget: float

class CartItem(BaseModel):
    name: str
    quantity: float  # in grams
    cooking_method: Optional[str] = None
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    price: float

class CartSummary(BaseModel):
    items: List[CartItem]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_fiber: float
    total_cost: float

# Global shopping cart storage (in production, use a database)
shopping_cart = []

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
        "carb": {"name": "🍚 Tinh bột", "meals": []},
        "protein": {"name": "🥩 Chất đạm", "meals": []},
        "good_fat": {"name": "🥜 Chất béo tốt", "meals": []},
        "fiber": {"name": "🥦 Chất xơ", "meals": []}
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
            fiber_target=macro_targets["fiber"],
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
                            name=f"{meal.name} ({translate_cooking_method(method['method'])})",
                            calories=method["calories"],
                            protein=method["protein"],
                            carbs=method["carbs"],
                            fat=method["fat"],
                            fiber=method.get("fiber", 0),
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
                            # Create meal with specific cooking method (all values per 100g)
                            method_data = next((m for m in meal.cooking_methods if m["method"] == method), None)
                            if method_data:
                                # Use Vietnamese name for cooking method
                                vietnamese_method = translate_cooking_method(method_data['method'])
                                processed_meal = Meal(
                                    name=f"{meal.name} ({vietnamese_method})",
                                    calories=method_data["calories"],
                                    protein=method_data["protein"],
                                    carbs=method_data["carbs"],
                                    fat=method_data["fat"],
                                    fiber=method_data.get("fiber", 0),  # Add fiber field with default
                                    price=method_data["price"],
                                    component_type=meal.component_type,
                                    food_type=meal.food_type,
                                    cooking_methods=[method_data]
                                )
                                all_meals.append(processed_meal)
                                all_quantities.append(quantity)  # Use grams for all meals
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

@app.get("/api/cart")
async def get_cart():
    """Get current shopping cart contents"""
    # Calculate totals
    total_calories = sum(item.calories for item in shopping_cart)
    total_protein = sum(item.protein for item in shopping_cart)
    total_carbs = sum(item.carbs for item in shopping_cart)
    total_fat = sum(item.fat for item in shopping_cart)
    total_fiber = sum(item.fiber for item in shopping_cart)
    total_cost = sum(item.price for item in shopping_cart)
    
    cart_summary = CartSummary(
        items=shopping_cart,
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fat=total_fat,
        total_fiber=total_fiber,
        total_cost=total_cost
    )
    
    return cart_summary.model_dump()

@app.post("/api/cart/add")
async def add_to_cart(item: CartItem):
    """Add an item to the shopping cart"""
    # Translate cooking method to Vietnamese if present
    if item.cooking_method:
        item.cooking_method = translate_cooking_method(item.cooking_method)
    
    shopping_cart.append(item)
    return {"message": "Item added to cart", "cart_size": len(shopping_cart)}

@app.delete("/api/cart/clear")
async def clear_cart():
    """Clear all items from the shopping cart"""
    shopping_cart.clear()
    return {"message": "Cart cleared", "cart_size": 0}

@app.delete("/api/cart/item/{item_index}")
async def remove_cart_item(item_index: int):
    """Remove a specific item from the cart by index"""
    if 0 <= item_index < len(shopping_cart):
        removed_item = shopping_cart.pop(item_index)
        return {"message": f"Removed {removed_item.name} from cart", "cart_size": len(shopping_cart)}
    else:
        raise HTTPException(status_code=404, detail="Item not found in cart")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)