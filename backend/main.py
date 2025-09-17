from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import User, MealSelection, MealRecommendationRequest, SAMPLE_MEALS
from calculations import get_daily_calories
from ai_service import get_meal_recommendation, get_optimized_menu

app = FastAPI(title="Nutri AI Backend", description="AI-powered healthy food recommendation API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Nutri AI API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/calculate-calories")
async def calculate_calories(user: User):
    daily_calories = get_daily_calories(user)
    return {"daily_calories": daily_calories}

@app.post("/recommend-meal")
async def recommend_meal(request: MealRecommendationRequest):
    try:
        recommendation = get_meal_recommendation(request.user, request.selection)
        return recommendation.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize-menu")
async def optimize_menu(user: User, budget: float):
    try:
        menu = get_optimized_menu(user, budget)
        return menu.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meals")
async def get_meals():
    return {"meals": [meal.model_dump() for meal in SAMPLE_MEALS]}

@app.get("/meals/categories")
async def get_meals_by_category():
    categories = {
        "carb": {"name": "Carbs", "meals": []},
        "protein": {"name": "Protein", "meals": []},
        "good_fat": {"name": "Good Fats", "meals": []},
        "fiber": {"name": "Fiber", "meals": []}
    }

    for meal in SAMPLE_MEALS:
        if meal.component_type in categories:
            categories[meal.component_type]["meals"].append(meal.model_dump())

    return {"categories": categories}