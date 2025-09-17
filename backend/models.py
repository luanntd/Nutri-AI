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
    price: float  # VND
    component_type: str  # carb, protein, good_fat, fiber
    food_type: str  # specific type within component (e.g., grains, poultry, etc.)
    cooking_methods: List[Dict[str, Any]]  # List of cooking methods with portions

class MealSelection(BaseModel):
    meals: List[Meal]
    quantities: List[float]  # grams or portions

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
    Meal(name="Gạo lứt", calories=130, protein=2.7, carbs=27, fat=1, price=5000, component_type="carb", food_type="grains",
         cooking_methods=[
             {"method": "boiled", "portion": "1 bowl (200g cooked)", "calories": 216, "protein": 4.5, "carbs": 45, "fat": 1.7, "price": 8000},
             {"method": "steamed", "portion": "1 bowl (200g cooked)", "calories": 216, "protein": 4.5, "carbs": 45, "fat": 1.7, "price": 8000}
         ]),
    Meal(name="Yến mạch", calories=379, protein=13.2, carbs=66.3, fat=6.9, price=25000, component_type="carb", food_type="grains",
         cooking_methods=[
             {"method": "boiled", "portion": "1 bowl (200g cooked)", "calories": 307, "protein": 10.7, "carbs": 54.1, "fat": 5.6, "price": 20000},
             {"method": "raw", "portion": "1 bowl (50g dry)", "calories": 189, "protein": 6.6, "carbs": 33.2, "fat": 3.5, "price": 12500}
         ]),
    Meal(name="Khoai lang", calories=86, protein=1.6, carbs=20, fat=0.1, price=8000, component_type="carb", food_type="tubers",
         cooking_methods=[
             {"method": "baked", "portion": "1 medium (150g)", "calories": 129, "protein": 2.4, "carbs": 30, "fat": 0.2, "price": 12000},
             {"method": "boiled", "portion": "1 medium (150g)", "calories": 129, "protein": 2.4, "carbs": 30, "fat": 0.2, "price": 12000}
         ]),
    Meal(name="Quả chuối", calories=89, protein=1.1, carbs=23, fat=0.3, price=5000, component_type="carb", food_type="fruits",
         cooking_methods=[
             {"method": "raw", "portion": "1 medium (120g)", "calories": 105, "protein": 1.3, "carbs": 27, "fat": 0.4, "price": 6000}
         ]),

    # Protein
    Meal(name="Ức gà", calories=165, protein=31, carbs=0, fat=3.6, price=80000, component_type="protein", food_type="poultry",
         cooking_methods=[
             {"method": "grilled", "portion": "1 breast (150g)", "calories": 248, "protein": 46.5, "carbs": 0, "fat": 5.4, "price": 120000},
             {"method": "boiled", "portion": "1 breast (150g)", "calories": 248, "protein": 46.5, "carbs": 0, "fat": 5.4, "price": 120000},
             {"method": "baked", "portion": "1 breast (150g)", "calories": 248, "protein": 46.5, "carbs": 0, "fat": 5.4, "price": 120000}
         ]),
    Meal(name="Trứng gà", calories=155, protein=13, carbs=1.1, fat=11, price=3000, component_type="protein", food_type="eggs",
         cooking_methods=[
             {"method": "boiled", "portion": "2 eggs", "calories": 155, "protein": 13, "carbs": 1.1, "fat": 11, "price": 6000},
             {"method": "fried", "portion": "2 eggs", "calories": 184, "protein": 13, "carbs": 1.1, "fat": 14, "price": 6000},
             {"method": "scrambled", "portion": "2 eggs", "calories": 170, "protein": 13, "carbs": 1.1, "fat": 12, "price": 6000}
         ]),
    Meal(name="Cá hồi", calories=208, protein=22, carbs=0, fat=13, price=120000, component_type="protein", food_type="fish",
         cooking_methods=[
             {"method": "baked", "portion": "1 fillet (150g)", "calories": 312, "protein": 33, "carbs": 0, "fat": 19.5, "price": 180000},
             {"method": "grilled", "portion": "1 fillet (150g)", "calories": 312, "protein": 33, "carbs": 0, "fat": 19.5, "price": 180000}
         ]),
    Meal(name="Sữa chua", calories=61, protein=3.5, carbs=4.7, fat=3.3, price=15000, component_type="protein", food_type="dairy",
         cooking_methods=[
             {"method": "plain", "portion": "1 cup (200g)", "calories": 122, "protein": 7, "carbs": 9.4, "fat": 6.6, "price": 30000}
         ]),

    # Good Fat
    Meal(name="Hạnh nhân", calories=579, protein=21.2, carbs=21.6, fat=49.9, price=35000, component_type="good_fat", food_type="nuts",
         cooking_methods=[
             {"method": "raw", "portion": "1 handful (30g)", "calories": 173, "protein": 6.4, "carbs": 6.5, "fat": 15, "price": 10500}
         ]),
    Meal(name="Bơ", calories=717, protein=2.5, carbs=4.4, fat=81.1, price=45000, component_type="good_fat", food_type="dairy",
         cooking_methods=[
             {"method": "spread", "portion": "1 tbsp (15g)", "calories": 107, "protein": 0.4, "carbs": 0.7, "fat": 12.2, "price": 6750}
         ]),
    Meal(name="Dầu ô liu", calories=884, protein=0, carbs=0, fat=100, price=25000, component_type="good_fat", food_type="oils",
         cooking_methods=[
             {"method": "drizzled", "portion": "1 tbsp (15g)", "calories": 132, "protein": 0, "carbs": 0, "fat": 15, "price": 3750}
         ]),

    # Fiber
    Meal(name="Bông cải", calories=34, protein=2.8, carbs=6.6, fat=0.4, price=15000, component_type="fiber", food_type="vegetables",
         cooking_methods=[
             {"method": "steamed", "portion": "1 cup (150g)", "calories": 51, "protein": 4.2, "carbs": 9.9, "fat": 0.6, "price": 22500},
             {"method": "boiled", "portion": "1 cup (150g)", "calories": 51, "protein": 4.2, "carbs": 9.9, "fat": 0.6, "price": 22500},
             {"method": "raw", "portion": "1 cup (150g)", "calories": 51, "protein": 4.2, "carbs": 9.9, "fat": 0.6, "price": 22500}
         ]),
    Meal(name="Cà chua", calories=18, protein=0.9, carbs=3.9, fat=0.2, price=10000, component_type="fiber", food_type="vegetables",
         cooking_methods=[
             {"method": "raw", "portion": "2 medium (200g)", "calories": 36, "protein": 1.8, "carbs": 7.8, "fat": 0.4, "price": 20000}
         ]),
    Meal(name="Cải xoăn", calories=49, protein=4.3, carbs=8.8, fat=0.9, price=12000, component_type="fiber", food_type="vegetables",
         cooking_methods=[
             {"method": "steamed", "portion": "2 cups (200g)", "calories": 98, "protein": 8.6, "carbs": 17.6, "fat": 1.8, "price": 24000},
             {"method": "sautéed", "portion": "2 cups (200g)", "calories": 98, "protein": 8.6, "carbs": 17.6, "fat": 1.8, "price": 24000},
             {"method": "raw", "portion": "2 cups (200g)", "calories": 98, "protein": 8.6, "carbs": 17.6, "fat": 1.8, "price": 24000}
         ]),
    Meal(name="Táo", calories=52, protein=0.3, carbs=13.8, fat=0.2, price=8000, component_type="fiber", food_type="fruits",
         cooking_methods=[
             {"method": "raw", "portion": "1 medium (180g)", "calories": 95, "protein": 0.5, "carbs": 25.1, "fat": 0.3, "price": 14400}
         ]),
]