import os
import json
from google import genai
from dotenv import load_dotenv
from backend.models import Meal, User, MealSelection, Recommendation, Menu, SAMPLE_MEALS
from backend.calculations import calculate_daily_calories, get_macro_targets

# Load environment variables
load_dotenv()

def get_meal_recommendation(user: User, selection: MealSelection) -> Recommendation:
    """AI-powered meal recommendations using Gemini"""
    
    daily_calories = calculate_daily_calories(user)
    macro_targets = get_macro_targets(user, daily_calories)

    # Calculate current totals - always use gram-based approach
    current_calories = 0
    current_protein = 0
    current_carbs = 0
    current_fat = 0
    current_fiber = 0
    current_cost = 0

    meal_descriptions = []

    for i, (meal, qty) in enumerate(zip(selection.meals, selection.quantities)):
        print(f"DEBUG: Meal {i}: {meal.name}, qty: {qty}, type: {type(qty)}")
        print(f"DEBUG: Meal calories: {meal.calories}, type: {type(meal.calories)}")

        # Always use gram-based calculation (qty is in grams)
        # Use first cooking method nutrition values if available, otherwise use base values
        if hasattr(meal, 'cooking_methods') and meal.cooking_methods:
            # Use first cooking method nutrition per 100g
            method_data = meal.cooking_methods[0]
            calories_per_100g = method_data["calories"]
            protein_per_100g = method_data["protein"]
            carbs_per_100g = method_data["carbs"]
            fat_per_100g = method_data["fat"]
            fiber_per_100g = method_data.get("fiber", 0)
            method_name = method_data['method']
        else:
            # Use base meal nutrition per 100g
            calories_per_100g = float(meal.calories)
            protein_per_100g = float(meal.protein)
            carbs_per_100g = float(meal.carbs)
            fat_per_100g = float(meal.fat)
            fiber_per_100g = float(getattr(meal, 'fiber', 0))
            method_name = "cơ bản"
        
        # Calculate nutrition and cost based on grams
        current_calories += (calories_per_100g * float(qty) / 100)
        current_protein += (protein_per_100g * float(qty) / 100)
        current_carbs += (carbs_per_100g * float(qty) / 100)
        current_fat += (fat_per_100g * float(qty) / 100)
        current_fiber += (fiber_per_100g * float(qty) / 100)
        current_cost += (float(meal.price) * float(qty) / 100)  # Price per 100g
        meal_descriptions.append(f"{meal.name} ({method_name}, {qty}g)")

    print(f"DEBUG: Current totals calculated: {current_calories}, {current_protein}, {current_carbs}, {current_fat}, {current_fiber}")

    prompt = f"""
    Bạn là một chuyên gia dinh dưỡng AI chuyên nghiệp. Hãy phân tích kế hoạch bữa ăn hiện tại và đề xuất điều chỉnh khẩu phần để phù hợp với mục tiêu và nhu cầu dinh dưỡng của người dùng.

    Hồ sơ người dùng:
    - Tuổi: {user.age}, Giới tính: {user.gender}
    - Chiều cao: {user.height}cm, Cân nặng: {user.weight}kg
    - Mức độ vận động: {user.activity}, Mục tiêu: {user.goal}
    - Calo mục tiêu hàng ngày: {daily_calories:.0f}
    - Protein mục tiêu: {macro_targets['protein']:.1f}g
    - Carb mục tiêu: {macro_targets['carbs']:.1f}g
    - Chất béo mục tiêu: {macro_targets['fat']:.1f}g
    - Chất xơ mục tiêu: {macro_targets['fiber']:.1f}g

    Kế hoạch bữa ăn hiện tại:
    {', '.join(meal_descriptions)}

    Tổng dinh dưỡng hiện tại:
    - Calo: {current_calories:.1f} (mục tiêu: {daily_calories:.0f})
    - Protein: {current_protein:.1f}g (mục tiêu: {macro_targets['protein']:.1f}g)
    - Carb: {current_carbs:.1f}g (mục tiêu: {macro_targets['carbs']:.1f}g)
    - Chất béo: {current_fat:.1f}g (mục tiêu: {macro_targets['fat']:.1f}g)
    - Chất xơ: {current_fiber:.1f}g (mục tiêu: {macro_targets['fiber']:.1f}g)

    Lưu ý:
    - Có 4 calo trên mỗi gram protein và carb, 9 calo trên mỗi gram fat, 2 calo trên mỗi gram fiber.

    Hãy phân tích kế hoạch bữa ăn hiện tại và đề xuất điều chỉnh khẩu phần để phù hợp hơn với mục tiêu {user.goal} và các chỉ số dinh dưỡng của người dùng:
    - Nếu mục tiêu người dùng là "lose", hãy ưu tiên giảm tổng calo thấp hơn calo hằng ngày và đảm bảo đủ protein.
    - Nếu mục tiêu người dùng là "gain", hãy ưu tiên tăng tổng calo cao hơn calo hằng ngày và tăng cường protein.
    - Nếu mục tiêu người dùng là "maintain", hãy giữ calo ổn định và cân bằng các chất dinh dưỡng.
    
    HƯỚNG DẪN QUAN TRỌNG:
    1. Luôn cung cấp chính xác {len(selection.quantities)} lượng điều chỉnh (một cho mỗi món ăn)
    2. TẤT CẢ món ăn đều tính theo GRAM, điều chỉnh từ 25-400 gram
    3. MỖI lượng gram phải chia hết cho 25 (ví dụ: 25g, 50g, 75g, 100g, 125g, 150g...)
    4. Thực hiện điều chỉnh có ý nghĩa (ít nhất 25g thay đổi) khi dinh dưỡng lệch khá nhiều so với mục tiêu
    5. Nếu kế hoạch hiện tại đã tốt (trong vòng 10% mục tiêu), chỉ điều chỉnh ±25g hoặc ±50g
    6. Giá trị dinh dưỡng của mỗi món ăn được tính theo cal/100g
    
    Tập trung vào:
    - Cân bằng calo cho mục tiêu {user.goal}
    - Đủ protein (đặc biệt quan trọng cho mục tiêu cơ bắp)
    - Phân bố cân bằng các chất dinh dưỡng macro
    - Khẩu phần thực tế (25g là bước nhỏ nhất)
    
    Vui lòng trả về bằng tiếng Việt và chỉ trả về JSON hợp lệ với:
    {{
        "adjusted_grams": [danh sách {len(selection.quantities)} giá trị gram (phải chia hết cho 25)],
        "explanation": "Giải thích rõ ràng về lý do điều chỉnh dựa trên thiếu hụt dinh dưỡng và mục tiêu của người dùng"
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
            # Get gram values and ensure they are multiples of 25
            raw_grams = result.get("adjusted_grams", result.get("adjusted_quantities", selection.quantities))
            adjusted_quantities = []
            for gram_qty in raw_grams:
                # Round to nearest 25g increment
                rounded_grams = round(float(gram_qty) / 25) * 25
                # Ensure minimum 25g
                rounded_grams = max(25, rounded_grams)
                adjusted_quantities.append(float(rounded_grams))
            explanation = result.get("explanation", "AI recommendation generated")
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            # Fallback if JSON parsing fails - round current quantities to 25g increments
            adjusted_quantities = []
            for qty in selection.quantities:
                rounded_grams = round(float(qty) / 25) * 25
                rounded_grams = max(25, rounded_grams)
                adjusted_quantities.append(float(rounded_grams))
            explanation = "Unable to parse AI response - using rounded current quantities"

    except Exception as e:
        print(f"Error calling AI service: {e}")
        # Fallback: simple scaling based on calorie target with 25g rounding
        scale_factor = daily_calories / max(current_calories, 1)
        adjusted_quantities = []
        for qty in selection.quantities:
            scaled_qty = qty * scale_factor
            # Round to nearest 25g increment
            rounded_grams = round(scaled_qty / 25) * 25
            rounded_grams = max(25, rounded_grams)
            adjusted_quantities.append(float(rounded_grams))
        explanation = f"Simple scaling: {scale_factor:.2f}x to reach {daily_calories} calories (rounded to 25g increments)"

    # Recalculate with adjusted quantities
    print(f"DEBUG: About to recalculate with adjusted_quantities: {adjusted_quantities}")
    print(f"DEBUG: Meals: {[meal.name for meal in selection.meals]}")
    
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    total_fiber = 0
    total_cost = 0

    for meal, qty in zip(selection.meals, adjusted_quantities):
        # Always use gram-based calculation (qty is in grams)
        # Use first cooking method nutrition values if available, otherwise use base values
        if hasattr(meal, 'cooking_methods') and meal.cooking_methods:
            # Use first cooking method nutrition per 100g
            method_data = meal.cooking_methods[0]
            calories_per_100g = method_data["calories"]
            protein_per_100g = method_data["protein"]
            carbs_per_100g = method_data["carbs"]
            fat_per_100g = method_data["fat"]
            fiber_per_100g = method_data.get("fiber", 0)
        else:
            # Use base meal nutrition per 100g
            calories_per_100g = float(meal.calories)
            protein_per_100g = float(meal.protein)
            carbs_per_100g = float(meal.carbs)
            fat_per_100g = float(meal.fat)
            fiber_per_100g = float(getattr(meal, 'fiber', 0))
        
        # Calculate nutrition and cost based on grams
        total_calories += (calories_per_100g * float(qty) / 100)
        total_protein += (protein_per_100g * float(qty) / 100)
        total_carbs += (carbs_per_100g * float(qty) / 100)
        total_fat += (fat_per_100g * float(qty) / 100)
        total_fiber += (fiber_per_100g * float(qty) / 100)
        total_cost += (float(meal.price) * float(qty) / 100)  # Price per 100g

    print(f"DEBUG: Final totals: {total_calories}, {total_protein}, {total_carbs}, {total_fat}, {total_fiber}, {total_cost}")

    return Recommendation(
        adjusted_meals=selection.meals,
        adjusted_quantities=adjusted_quantities,
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fat=total_fat,
        total_fiber=total_fiber,
        total_cost=total_cost,
        explanation=explanation
    )

def get_optimized_menu(user: User, budget: float) -> Menu:
    """Use Gemini to create an optimized menu within budget"""

    daily_calories = calculate_daily_calories(user)
    macro_targets = get_macro_targets(user, daily_calories)

    meals_str = "\n".join([
        f"- {meal.name} " +
        (f"\n  Cooking methods: " + 
         ", ".join([f"{method['method']} ({method['calories']} cal, {method['protein']}g protein, {method['carbs']}g carbs, {method['fat']}g fat, {method['fiber']}g fiber, {method['price']} VND/100g)" 
                   for method in meal.cooking_methods]) 
         if hasattr(meal, 'cooking_methods') and meal.cooking_methods else "")
        for meal in SAMPLE_MEALS
    ])

    prompt = f"""
    Hồ sơ người dùng:
    - Tuổi: {user.age}, Giới tính: {user.gender}, Mục tiêu: {user.goal}
    - Calo mục tiêu hàng ngày: {daily_calories}
    - Protein mục tiêu: {macro_targets['protein']:.1f}g
    - Carb mục tiêu: {macro_targets['carbs']:.1f}g
    - Chất béo mục tiêu: {macro_targets['fat']:.1f}g
    - Ngân sách hàng ngày: {budget} VND

    Các món ăn có sẵn:
    {meals_str}

    Tạo thực đơn tối ưu cho cả ngày (sáng, trưa, tối) sao cho:
    1. Nằm trong ngân sách: {budget} VND
    2. Đạt mục tiêu calo hằng ngày: ~{daily_calories}
    3. Phù hợp với các chỉ số dinh dưỡng dựa trên mục tiêu ({user.goal}):
    - Nếu mục tiêu người dùng là "lose", hãy ưu tiên giảm tổng calo thấp hơn calo hằng ngày và đảm bảo đủ protein.
    - Nếu mục tiêu người dùng là "gain", hãy ưu tiên tăng tổng calo cao hơn calo hằng ngày và tăng cường protein.
    - Nếu mục tiêu người dùng là "maintain", hãy giữ calo ổn định và cân bằng các chất dinh dưỡng.
    4. Chỉ sử dụng phương pháp nấu và khối lượng tính bằng gram (PHẢI chia hết cho 25g, tối thiểu 25g)
    5. Chỉ chọn từ danh sách món ăn có sẵn ở trên

    HƯỚNG DẪN TÍNH GIÁ:
    - Tất cả giá trên được tính theo VND/100g
    - Để tính giá cho số gram cụ thể: (giá/100g) × (số gram) / 100
    - Ví dụ: Ức gà nướng 200g = (60000 VND/100g) × 200g / 100 = 120,000 VND
    - Hãy tính toán cẩn thận để đảm bảo tổng chi phí không vượt quá ngân sách {budget} VND

    Vui lòng trả về bằng tiếng Việt với định dạng JSON:
    {{
        "breakfast": [
            {{"name": "tên_món_ăn", "method": "phương_pháp_nấu", "grams": 100, "calories": 100, "protein": 10, "carbs": 20, "fat": 5, "fiber": 3}}
        ],
        "lunch": [...],
        "dinner": [...],
        "explanation": "Thực đơn được thiết kế cho mục tiêu giảm cân với protein cao..."
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
        print(f"DEBUG: parsed result: {result}")
        
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

        # Recalculate totals based on corrected meal data
        all_meals = breakfast_meals + lunch_meals + dinner_meals
        corrected_total_cost = sum(meal.price for meal in all_meals)
        corrected_total_calories = sum(meal.calories for meal in all_meals)

        return Menu(
            breakfast=breakfast_meals,
            lunch=lunch_meals,
            dinner=dinner_meals,
            total_cost=corrected_total_cost,
            total_calories=corrected_total_calories,
            explanation=result.get("explanation", "AI-generated optimized menu")
        )

    except Exception as e:
        print(f"Error creating optimized menu: {e}")
        # Fallback: create a simple balanced menu
        return create_fallback_menu(user, budget, daily_calories)

def create_meal_from_response(meal_data: dict):
    """Create a meal object from AI response data"""
    
    # Extract gram/quantity information and round to 25g increments
    grams = meal_data.get("grams", meal_data.get("portions", 100))  # Fallback for old format
    # Round to 25g increments
    rounded_grams = round(float(grams) / 25) * 25
    rounded_grams = max(25, rounded_grams)  # Minimum 25g
    
    method = meal_data.get("method", "")
    meal_name = meal_data.get("name", "Unknown")
    
    # Find the actual meal from SAMPLE_MEALS to get correct price
    actual_meal = None
    for sample_meal in SAMPLE_MEALS:
        if sample_meal.name.lower() == meal_name.lower():
            actual_meal = sample_meal
            break
    
    if actual_meal:
        # Calculate correct price based on actual meal data and quantity
        correct_price = (float(actual_meal.price) * rounded_grams / 100)
        
        # Use actual meal nutrition or cooking method nutrition
        if method and hasattr(actual_meal, 'cooking_methods') and actual_meal.cooking_methods:
            # Find the matching cooking method
            method_data = None
            for cook_method in actual_meal.cooking_methods:
                if cook_method['method'].lower() == method.lower():
                    method_data = cook_method
                    break
            
            if method_data:
                # Use cooking method nutrition per 100g, calculate for actual grams
                calories = method_data["calories"] * rounded_grams / 100
                protein = method_data["protein"] * rounded_grams / 100
                carbs = method_data["carbs"] * rounded_grams / 100
                fat = method_data["fat"] * rounded_grams / 100
                fiber = method_data.get("fiber", 0) * rounded_grams / 100
                # Use cooking method price if available, otherwise base meal price
                if "price" in method_data:
                    correct_price = method_data["price"] * rounded_grams / 100
            else:
                # Fallback to base meal nutrition
                calories = actual_meal.calories * rounded_grams / 100
                protein = actual_meal.protein * rounded_grams / 100
                carbs = actual_meal.carbs * rounded_grams / 100
                fat = actual_meal.fat * rounded_grams / 100
                fiber = getattr(actual_meal, 'fiber', 0) * rounded_grams / 100
        else:
            # Use base meal nutrition
            calories = actual_meal.calories * rounded_grams / 100
            protein = actual_meal.protein * rounded_grams / 100
            carbs = actual_meal.carbs * rounded_grams / 100
            fat = actual_meal.fat * rounded_grams / 100
            fiber = getattr(actual_meal, 'fiber', 0) * rounded_grams / 100
    else:
        # Fallback: use AI provided values if meal not found
        calories = meal_data.get("calories", 0) * rounded_grams / 100
        protein = meal_data.get("protein", 0) * rounded_grams / 100
        carbs = meal_data.get("carbs", 0) * rounded_grams / 100
        fat = meal_data.get("fat", 0) * rounded_grams / 100
        fiber = meal_data.get("fiber", 0) * rounded_grams / 100
        correct_price = meal_data.get("price", 0) * rounded_grams / 100
    
    # Create meal object with corrected data
    meal = Meal(
        name=meal_name,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat,
        fiber=fiber,
        price=correct_price,
        component_type="mixed",
        food_type="prepared",
        cooking_methods=[{
            "method": method,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
            "fiber": fiber,
            "price": correct_price,
            "grams": rounded_grams
        }] if method else []
    )
    
    # Add additional attributes for frontend display
    meal.method = method
    meal.quantity = rounded_grams  # Use rounded grams for all calculations
    
    return meal

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