import os
import json
from google import genai
from dotenv import load_dotenv
from models import User, MealSelection, Recommendation, Menu, SAMPLE_MEALS
from calculations import calculate_daily_calories, get_macro_targets

# Load environment variables
load_dotenv()

def get_meal_recommendation(user: User, selection: MealSelection) -> Recommendation:
    """AI-powered meal recommendations using Gemini"""
    
    daily_calories = calculate_daily_calories(user)
    macro_targets = get_macro_targets(user, daily_calories)

    # Calculate current totals - handle both cooking method and legacy data
    current_calories = 0
    current_protein = 0
    current_carbs = 0
    current_fat = 0

    meal_descriptions = []

    for i, (meal, qty) in enumerate(zip(selection.meals, selection.quantities)):
        print(f"DEBUG: Meal {i}: {meal.name}, qty: {qty}, type: {type(qty)}")
        print(f"DEBUG: Meal calories: {meal.calories}, type: {type(meal.calories)}")

        if hasattr(meal, 'cooking_methods') and meal.cooking_methods:
            # New cooking method data - use first cooking method as default
            method_data = meal.cooking_methods[0]
            current_calories += method_data["calories"] * qty
            current_protein += method_data["protein"] * qty
            current_carbs += method_data["carbs"] * qty
            current_fat += method_data["fat"] * qty
            meal_descriptions.append(f"{meal.name} ({method_data['method']}, {qty} portions)")
        else:
            # Legacy gram-based data
            current_calories += (float(meal.calories) * float(qty)) / 100
            current_protein += (float(meal.protein) * float(qty)) / 100
            current_carbs += (float(meal.carbs) * float(qty)) / 100
            current_fat += (float(meal.fat) * float(qty)) / 100
            meal_descriptions.append(f"{meal.name} ({qty}g)")

    print(f"DEBUG: Current totals calculated: {current_calories}, {current_protein}, {current_carbs}, {current_fat}")

    prompt = f"""
    You are a nutrition expert providing meal portion adjustments for optimal health.
    
    User profile:
    - Age: {user.age}, Gender: {user.gender}
    - Height: {user.height}cm, Weight: {user.weight}kg
    - Activity: {user.activity}, Goal: {user.goal}
    - Target daily calories: {daily_calories:.0f}
    - Target protein: {macro_targets['protein']:.1f}g
    - Target carbs: {macro_targets['carbs']:.1f}g
    - Target fat: {macro_targets['fat']:.1f}g

    Current meal plan:
    {', '.join(meal_descriptions)}

    Current nutrition totals:
    - Calories: {current_calories:.1f} (target: {daily_calories:.0f})
    - Protein: {current_protein:.1f}g (target: {macro_targets['protein']:.1f}g)
    - Carbs: {current_carbs:.1f}g (target: {macro_targets['carbs']:.1f}g)
    - Fat: {current_fat:.1f}g (target: {macro_targets['fat']:.1f}g)

    Analyze the current meal plan and suggest portion adjustments to better align with the user's {user.goal} goal and macro targets. 
    
    IMPORTANT INSTRUCTIONS:
    1. Always provide exactly {len(selection.quantities)} adjusted quantities (one for each meal)
    2. For cooking method meals (portions): adjust between 0.5-3.0 portions
    3. For gram-based meals: adjust between 50-300 grams
    4. Make meaningful adjustments (at least 15% change) when nutrition is significantly off target
    5. If current plan is already good (within 10% of targets), make minor adjustments (5-10%)
    
    Focus on:
    - Calorie alignment for {user.goal} goal
    - Protein adequacy (especially important for muscle goals)
    - Balanced macronutrient distribution
    - Practical portion sizes
    
    Return ONLY valid JSON with:
    {{
        "adjusted_quantities": [list of {len(selection.quantities)} float values],
        "explanation": "Clear explanation of why adjustments were made based on nutrition gaps and user goal"
    }}
    """

    print("DEBUG: About to call Gemini API")
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )

        print(f"DEBUG: Gemini API response received: {response.text[:200]}...")

        # Parse the JSON response
        try:
            result = json.loads(response.text)
            print(f"DEBUG: Parsed result: {result}")
            # Ensure adjusted_quantities are floats
            raw_quantities = result.get("adjusted_quantities", selection.quantities)
            adjusted_quantities = [float(qty) for qty in raw_quantities]
            explanation = result.get("explanation", "AI recommendation generated")
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            # Fallback if JSON parsing fails
            result = {"adjusted_quantities": selection.quantities, "explanation": "Unable to parse AI response"}
            adjusted_quantities = [float(qty) for qty in selection.quantities]
            explanation = "Unable to parse AI response"

    except Exception as e:
        print(f"Error calling AI service: {e}")
        # Fallback: simple scaling based on calorie target
        scale_factor = daily_calories / max(current_calories, 1)
        adjusted_quantities = [float(qty * scale_factor) for qty in selection.quantities]
        explanation = f"Simple scaling: {scale_factor:.2f}x to reach {daily_calories} calories"

    # Recalculate with adjusted quantities
    print(f"DEBUG: About to recalculate with adjusted_quantities: {adjusted_quantities}")
    print(f"DEBUG: Meals: {[meal.name for meal in selection.meals]}")
    
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0

    for meal, qty in zip(selection.meals, adjusted_quantities):
        if hasattr(meal, 'cooking_methods') and meal.cooking_methods:
            # New cooking method data
            method_data = meal.cooking_methods[0]
            total_calories += method_data["calories"] * qty
            total_protein += method_data["protein"] * qty
            total_carbs += method_data["carbs"] * qty
            total_fat += method_data["fat"] * qty
        else:
            # Legacy gram-based data
            total_calories += (float(meal.calories) * float(qty)) / 100
            total_protein += (float(meal.protein) * float(qty)) / 100
            total_carbs += (float(meal.carbs) * float(qty)) / 100
            total_fat += (float(meal.fat) * float(qty)) / 100

    print(f"DEBUG: Final totals: {total_calories}, {total_protein}, {total_carbs}, {total_fat}")

    return Recommendation(
        adjusted_meals=selection.meals,
        adjusted_quantities=adjusted_quantities,
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fat=total_fat,
        explanation=explanation
    )

def get_optimized_menu(user: User, budget: float) -> Menu:
    """Use Gemini to create an optimized menu within budget"""

    daily_calories = calculate_daily_calories(user)
    macro_targets = get_macro_targets(user, daily_calories)

    meals_str = "\n".join([
        f"- {meal.name}: {meal.calories} cal, {meal.protein}g protein, {meal.price} VND" +
        (f" (cooking methods: {', '.join([method['method'] for method in meal.cooking_methods])})" 
         if hasattr(meal, 'cooking_methods') and meal.cooking_methods else "/100g")
        for meal in SAMPLE_MEALS
    ])

    prompt = f"""
    User profile:
    - Age: {user.age}, Gender: {user.gender}, Goal: {user.goal}
    - Target daily calories: {daily_calories}
    - Target protein: {macro_targets['protein']:.1f}g
    - Target carbs: {macro_targets['carbs']:.1f}g
    - Target fat: {macro_targets['fat']:.1f}g
    - Daily budget: {budget} VND

    Available meals:
    {meals_str}

    Create an optimized daily menu (breakfast, lunch, dinner) that:
    1. Stays within budget: {budget} VND
    2. Meets calorie target: ~{daily_calories} calories
    3. Matches macro targets based on goal ({user.goal})
    4. Uses appropriate cooking methods and portions

    Return JSON format:
    {{
        "breakfast": [
            {{"name": "meal_name", "method": "cooking_method", "portions": 1.0, "calories": 100, "protein": 10, "carbs": 20, "fat": 5, "price": 10000}}
        ],
        "lunch": [...],
        "dinner": [...],
        "total_cost": 90000,
        "total_calories": 1500,
        "explanation": "Menu designed for weight loss with high protein..."
    }}
    """

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )

        result = json.loads(response.text)
        
        # Convert to Menu object
        breakfast_meals = []
        lunch_meals = []
        dinner_meals = []
        
        # Create meal objects from the AI response
        for meal_data in result.get("breakfast", []):
            breakfast_meals.append(create_meal_from_response(meal_data))
        
        for meal_data in result.get("lunch", []):
            lunch_meals.append(create_meal_from_response(meal_data))
            
        for meal_data in result.get("dinner", []):
            dinner_meals.append(create_meal_from_response(meal_data))

        return Menu(
            breakfast=breakfast_meals,
            lunch=lunch_meals,
            dinner=dinner_meals,
            total_cost=result.get("total_cost", budget),
            total_calories=result.get("total_calories", daily_calories),
            explanation=result.get("explanation", "AI-generated optimized menu")
        )

    except Exception as e:
        print(f"Error creating optimized menu: {e}")
        # Fallback: create a simple balanced menu
        return create_fallback_menu(user, budget, daily_calories)

def create_meal_from_response(meal_data: dict):
    """Create a meal object from AI response data"""
    from models import Meal
    
    return Meal(
        name=meal_data.get("name", "Unknown"),
        calories=meal_data.get("calories", 0),
        protein=meal_data.get("protein", 0),
        carbs=meal_data.get("carbs", 0),
        fat=meal_data.get("fat", 0),
        price=meal_data.get("price", 0),
        component_type="mixed",
        food_type="prepared",
        cooking_methods=[{
            "method": meal_data.get("method", "prepared"),
            "portion": f"{meal_data.get('portions', 1)} portion",
            "calories": meal_data.get("calories", 0),
            "protein": meal_data.get("protein", 0),
            "carbs": meal_data.get("carbs", 0),
            "fat": meal_data.get("fat", 0),
            "price": meal_data.get("price", 0)
        }]
    )

def create_fallback_menu(user: User, budget: float, daily_calories: float) -> Menu:
    """Create a simple fallback menu when AI fails"""
    # Simple budget distribution: 30% breakfast, 40% lunch, 30% dinner
    breakfast_budget = budget * 0.3
    lunch_budget = budget * 0.4
    dinner_budget = budget * 0.3
    
    # Simple calorie distribution
    breakfast_calories = daily_calories * 0.25
    lunch_calories = daily_calories * 0.45
    dinner_calories = daily_calories * 0.30
    
    # Create simple meals (this is a very basic fallback)
    breakfast_meal = SAMPLE_MEALS[1]  # Yến mạch
    lunch_meal = SAMPLE_MEALS[4]      # Ức gà
    dinner_meal = SAMPLE_MEALS[9]     # Bông cải
    
    return Menu(
        breakfast=[breakfast_meal],
        lunch=[lunch_meal],
        dinner=[dinner_meal],
        total_cost=breakfast_budget + lunch_budget + dinner_budget,
        total_calories=breakfast_calories + lunch_calories + dinner_calories,
        explanation="Fallback menu - AI optimization unavailable"
    )