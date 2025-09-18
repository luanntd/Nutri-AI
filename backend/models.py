from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

class Gender(str, Enum):
    male = "male"
    female = "female"

class ActivityLevel(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    active = "active"

class Goal(str, Enum):
    lose = "lose"
    maintain = "maintain"
    gain = "gain"

class User(BaseModel):
    name: str
    age: int
    gender: Gender
    height: float  # cm
    weight: float  # kg
    activity: ActivityLevel
    goal: Goal

class Meal(BaseModel):
    name: str
    calories: float
    protein: float  # g
    carbs: float  # g
    fat: float  # g
    fiber: float  # g
    price: float  # VND
    component_type: str  # carb, protein, good_fat, fiber
    food_type: str  # specific type within component (e.g., grains, poultry, etc.)
    cooking_methods: List[Dict[str, Any]]  # List of cooking methods (all values per 100g)
    # Additional attributes for display
    method: Optional[str] = None
    quantity: Optional[float] = None

class MealSelection(BaseModel):
    meals: List[Meal]
    quantities: List[float]  # grams

class MealRecommendationRequest(BaseModel):
    user: User
    selection: MealSelection

class Recommendation(BaseModel):
    adjusted_meals: List[Meal]
    adjusted_quantities: List[float]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_fiber: float
    total_cost: float
    explanation: str

class Menu(BaseModel):
    breakfast: List[Meal]
    lunch: List[Meal]
    dinner: List[Meal]
    total_cost: float
    total_calories: float
    explanation: str

# Sample meals data organized by categories
SAMPLE_MEALS = [
    # Carbs
    Meal(name="Gạo lứt", calories=130, protein=2.7, carbs=27, fat=1, fiber=2.8, price=2500, component_type="carb", food_type="grains",
         cooking_methods=[
             {"method": "boiled", "calories": 216, "protein": 4.5, "carbs": 45, "fat": 1.7, "fiber": 4.6, "price": 4000},
             {"method": "steamed", "calories": 216, "protein": 4.5, "carbs": 45, "fat": 1.7, "fiber": 4.6, "price": 4000}
         ]),
    Meal(name="Yến mạch", calories=379, protein=13.2, carbs=66.3, fat=6.9, fiber=10.1, price=12500, component_type="carb", food_type="grains",
         cooking_methods=[
             {"method": "boiled", "calories": 307, "protein": 10.7, "carbs": 54.1, "fat": 5.6, "fiber": 8.2, "price": 10000},
             {"method": "raw", "calories": 189, "protein": 6.6, "carbs": 33.2, "fat": 3.5, "fiber": 5.1, "price": 6250}
         ]),
    Meal(name="Khoai lang", calories=86, protein=1.6, carbs=20, fat=0.1, fiber=3.0, price=4000, component_type="carb", food_type="tubers",
         cooking_methods=[
             {"method": "baked", "calories": 129, "protein": 2.4, "carbs": 30, "fat": 0.2, "fiber": 4.5, "price": 6000},
             {"method": "boiled", "calories": 129, "protein": 2.4, "carbs": 30, "fat": 0.2, "fiber": 4.5, "price": 6000}
         ]),
    Meal(name="Quả chuối", calories=89, protein=1.1, carbs=23, fat=0.3, fiber=2.6, price=2500, component_type="carb", food_type="fruits",
         cooking_methods=[
             {"method": "raw", "calories": 105, "protein": 1.3, "carbs": 27, "fat": 0.4, "fiber": 3.1, "price": 3000}
         ]),

    # Protein
    Meal(name="Ức gà", calories=165, protein=31, carbs=0, fat=3.6, fiber=0, price=40000, component_type="protein", food_type="poultry",
         cooking_methods=[
             {"method": "grilled", "calories": 248, "protein": 46.5, "carbs": 0, "fat": 5.4, "fiber": 0, "price": 20000},
             {"method": "boiled", "calories": 248, "protein": 46.5, "carbs": 0, "fat": 5.4, "fiber": 0, "price": 20000},
             {"method": "baked", "calories": 248, "protein": 46.5, "carbs": 0, "fat": 5.4, "fiber": 0, "price": 20000}
         ]),
    Meal(name="Trứng gà", calories=155, protein=13, carbs=1.1, fat=11, fiber=0, price=1500, component_type="protein", food_type="eggs",
         cooking_methods=[
             {"method": "boiled", "calories": 155, "protein": 13, "carbs": 1.1, "fat": 11, "fiber": 0, "price": 3000},
             {"method": "fried", "calories": 184, "protein": 13, "carbs": 1.1, "fat": 14, "fiber": 0, "price": 3000},
             {"method": "scrambled", "calories": 170, "protein": 13, "carbs": 1.1, "fat": 12, "fiber": 0, "price": 3000}
         ]),
    Meal(name="Cá hồi", calories=208, protein=22, carbs=0, fat=13, fiber=0, price=60000, component_type="protein", food_type="fish",
         cooking_methods=[
             {"method": "baked", "calories": 312, "protein": 33, "carbs": 0, "fat": 19.5, "fiber": 0, "price": 60000},
             {"method": "grilled", "calories": 312, "protein": 33, "carbs": 0, "fat": 19.5, "fiber": 0, "price": 60000}
         ]),
    Meal(name="Sữa chua", calories=61, protein=3.5, carbs=4.7, fat=3.3, fiber=0, price=7500, component_type="protein", food_type="dairy",
         cooking_methods=[
             {"method": "plain", "calories": 122, "protein": 7, "carbs": 9.4, "fat": 6.6, "fiber": 0, "price": 15000}
         ]),

    # Good Fat
    Meal(name="Hạnh nhân", calories=579, protein=21.2, carbs=21.6, fat=49.9, fiber=12.5, price=17500, component_type="good_fat", food_type="nuts",
         cooking_methods=[
             {"method": "raw", "calories": 173, "protein": 6.4, "carbs": 6.5, "fat": 15, "fiber": 3.8, "price": 5250}
         ]),
    Meal(name="Bơ", calories=717, protein=2.5, carbs=4.4, fat=81.1, fiber=10, price=22500, component_type="good_fat", food_type="dairy",
         cooking_methods=[
             {"method": "spread", "calories": 107, "protein": 0.4, "carbs": 0.7, "fat": 12.2, "fiber": 1.5, "price": 3375}
         ]),
    Meal(name="Dầu ô liu", calories=884, protein=0, carbs=0, fat=100, fiber=0, price=12500, component_type="good_fat", food_type="oils",
         cooking_methods=[
             {"method": "drizzled", "calories": 132, "protein": 0, "carbs": 0, "fat": 15, "fiber": 0, "price": 1875}
         ]),

    # Fiber
    Meal(name="Bông cải", calories=34, protein=2.8, carbs=6.6, fat=0.4, fiber=2.6, price=7500, component_type="fiber", food_type="vegetables",
         cooking_methods=[
             {"method": "steamed", "calories": 51, "protein": 4.2, "carbs": 9.9, "fat": 0.6, "fiber": 3.9, "price": 11250},
             {"method": "boiled", "calories": 51, "protein": 4.2, "carbs": 9.9, "fat": 0.6, "fiber": 3.9, "price": 11250},
             {"method": "raw", "calories": 51, "protein": 4.2, "carbs": 9.9, "fat": 0.6, "fiber": 3.9, "price": 8000}
         ]),
    Meal(name="Cà chua", calories=18, protein=0.9, carbs=3.9, fat=0.2, fiber=1.2, price=5000, component_type="fiber", food_type="vegetables",
         cooking_methods=[
             {"method": "raw", "calories": 36, "protein": 1.8, "carbs": 7.8, "fat": 0.4, "fiber": 2.4, "price": 10000}
         ]),
    Meal(name="Cải xoăn", calories=49, protein=4.3, carbs=8.8, fat=0.9, fiber=3.6, price=6000, component_type="fiber", food_type="vegetables",
         cooking_methods=[
             {"method": "steamed", "calories": 98, "protein": 8.6, "carbs": 17.6, "fat": 1.8, "fiber": 7.2, "price": 10000},
             {"method": "sautéed", "calories": 98, "protein": 8.6, "carbs": 17.6, "fat": 1.8, "fiber": 7.2, "price": 10000},
             {"method": "raw", "calories": 98, "protein": 8.6, "carbs": 17.6, "fat": 1.8, "fiber": 7.2, "price": 5000}
         ]),
    Meal(name="Táo", calories=52, protein=0.3, carbs=13.8, fat=0.2, fiber=2.4, price=4000, component_type="fiber", food_type="fruits",
         cooking_methods=[
             {"method": "raw", "calories": 95, "protein": 0.5, "carbs": 25.1, "fat": 0.3, "fiber": 4.4, "price": 5000}
         ]),
]