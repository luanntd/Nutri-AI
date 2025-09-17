import streamlit as st
from models import User, Meal, MealSelection, SAMPLE_MEALS, Gender, ActivityLevel, Goal
from calculations import calculate_daily_calories, get_macro_targets
from ai_service import get_meal_recommendation, get_optimized_menu

# Configure page
st.set_page_config(
    page_title="🥗 Nutri AI - Complete",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .meal-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border: 1px solid #e1e5e9;
    }
    .recommendation-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .nutrition-info {
        background: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2E8B57;
    }
    .menu-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🥗 Nutri AI - Complete Version</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-powered healthy food recommendation system</p>', unsafe_allow_html=True)

    # Initialize session state
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = None
    if "meal_selection" not in st.session_state:
        st.session_state.meal_selection = []
    if "recommendation" not in st.session_state:
        st.session_state.recommendation = None
    if "budget_menu" not in st.session_state:
        st.session_state.budget_menu = None

    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "🧭 Choose a section:",
        ["🏠 Home", "👤 User Profile", "🍽️ Meal Selection", "💰 Budget Menu", "📊 Results"]
    )

    if page == "🏠 Home":
        show_home()
    elif page == "👤 User Profile":
        show_user_profile()
    elif page == "🍽️ Meal Selection":
        show_meal_selection()
    elif page == "💰 Budget Menu":
        show_budget_menu()
    elif page == "📊 Results":
        show_results()

def show_home():
    st.header("Welcome to Nutri AI Complete! 🌟")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 What we do:")
        st.markdown("""
        - **Personalized Nutrition**: Calculate your daily calorie and macro needs
        - **AI Meal Recommendations**: Get smart suggestions based on your goals
        - **Budget Optimization**: Create perfect menus within your budget
        - **Health Goals**: Support for weight loss, maintenance, or muscle gain
        - **Cooking Methods**: Different preparation styles for every meal
        - **Vietnamese Cuisine**: Local ingredients and traditional foods
        """)

    with col2:
        st.subheader("🍽️ Meal Categories:")
        st.markdown("""
        - **🍚 Carbs**: Energy sources (gạo lứt, yến mạch, khoai lang)
        - **🥩 Protein**: Building blocks (ức gà, trứng, cá hồi)
        - **🥜 Good Fats**: Healthy fats (hạnh nhân, bơ, dầu ô liu)
        - **🥦 Fiber**: Digestive health (bông cải, cà chua, cải xoăn)
        """)

    st.subheader("🚀 Features:")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.info("**🤖 AI Meal Recommendations**\nSelect your meals and get AI-powered portion adjustments based on your goals and macro targets.")
        
    with feature_col2:
        st.success("**💰 Budget Optimization**\nEnter your daily budget and get a complete 3-meal plan optimized for cost and nutrition.")

    st.warning("💡 **Tip**: Start with the User Profile section to input your information!")

def show_user_profile():
    st.header("👤 Your Profile")
    
    if st.session_state.user_profile:
        user = st.session_state.user_profile
        daily_calories = calculate_daily_calories(user)
        macro_targets = get_macro_targets(user, daily_calories)
        
        st.success(f"✅ Current Profile: {user.name}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Daily Calories", f"{daily_calories:.0f}")
        with col2:
            st.metric("Protein Target", f"{macro_targets['protein']:.0f}g")
        with col3:
            st.metric("Carbs Target", f"{macro_targets['carbs']:.0f}g")
        with col4:
            st.metric("Fat Target", f"{macro_targets['fat']:.0f}g")

    with st.form("user_profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Name", value="Luan Nguyen")
            age = st.number_input("Age", min_value=16, max_value=100, value=25)
            gender = st.selectbox("Gender", options=[g.value for g in Gender])
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)

        with col2:
            weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
            activity = st.selectbox("Activity Level", options=[a.value for a in ActivityLevel])
            goal = st.selectbox("Goal", options=[g.value for g in Goal])

        if st.form_submit_button("💾 Save Profile", type="primary"):
            st.session_state.user_profile = User(
                name=name,
                age=age,
                gender=Gender(gender),
                height=height,
                weight=weight,
                activity=ActivityLevel(activity),
                goal=Goal(goal)
            )
            st.success("✅ Profile saved successfully!")
            st.rerun()

def show_meal_selection():
    st.header("🍽️ Meal Selection & AI Recommendations")
    
    if not st.session_state.user_profile:
        st.warning("⚠️ Please complete your profile first!")
        return

    # Initialize session state for meal plans
    if "daily_meals" not in st.session_state:
        st.session_state.daily_meals = {
            "breakfast": {"meals": [], "quantities": [], "methods": []},
            "lunch": {"meals": [], "quantities": [], "methods": []},
            "dinner": {"meals": [], "quantities": [], "methods": []}
        }

    # Group meals by category
    categories = {
        "carb": {"name": "🍚 Carbs", "meals": []},
        "protein": {"name": "🥩 Protein", "meals": []},
        "good_fat": {"name": "🥜 Good Fats", "meals": []},
        "fiber": {"name": "🥦 Fiber", "meals": []}
    }

    for meal in SAMPLE_MEALS:
        if meal.component_type in categories:
            categories[meal.component_type]["meals"].append(meal)

    # Meal time selection
    meal_times = ["🌅 Breakfast", "☀️ Lunch", "🌙 Dinner"]
    meal_keys = ["breakfast", "lunch", "dinner"]
    
    for meal_time, meal_key in zip(meal_times, meal_keys):
        with st.expander(f"{meal_time}", expanded=True):
            st.subheader(f"Select meals for {meal_time.split()[1].lower()}")
            
            # Create temporary lists for this meal time
            temp_meals = []
            temp_quantities = []
            temp_methods = []
            
            for category, data in categories.items():
                st.markdown(f"**{data['name']}**")
                
                for meal in data["meals"]:
                    # Create a unique key for each meal and meal time
                    meal_checkbox_key = f"{meal_key}_{meal.name.replace(' ', '_')}"
                    
                    if st.checkbox(f"{meal.name}", key=meal_checkbox_key):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            # Cooking method selection
                            if meal.cooking_methods:
                                method_options = [f"{method['method']} - {method['portion']}" 
                                                for method in meal.cooking_methods]
                                selected_method_idx = st.selectbox(
                                    "Cooking Method",
                                    range(len(method_options)),
                                    format_func=lambda x: method_options[x],
                                    key=f"method_{meal_checkbox_key}"
                                )
                                selected_method = meal.cooking_methods[selected_method_idx]
                                temp_methods.append(selected_method)
                            else:
                                st.write("Per 100g")
                                temp_methods.append(None)
                        
                        with col2:
                            if meal.cooking_methods:
                                qty = st.number_input(
                                    "Portions", 
                                    min_value=0.1, 
                                    max_value=10.0, 
                                    value=1.0, 
                                    step=0.1,
                                    key=f"qty_{meal_checkbox_key}"
                                )
                            else:
                                qty = st.number_input(
                                    "Grams", 
                                    min_value=10, 
                                    max_value=1000, 
                                    value=100,
                                    key=f"qty_{meal_checkbox_key}"
                                )
                            temp_quantities.append(qty)
                        
                        with col3:
                            if meal.cooking_methods and len(temp_methods) > 0 and temp_methods[-1]:
                                method_data = temp_methods[-1]
                                calories = method_data["calories"] * qty
                                price = method_data["price"] * qty
                            else:
                                calories = meal.calories * qty / 100
                                price = meal.price * qty / 100
                            
                            st.metric("Calories", f"{calories:.0f}")
                            st.caption(f"💰 {price:.0f} VND")
                        
                        temp_meals.append(meal)
            
            # Update session state for this meal time
            st.session_state.daily_meals[meal_key] = {
                "meals": temp_meals,
                "quantities": temp_quantities,
                "methods": temp_methods
            }

    # Show daily summary
    st.subheader("📋 Daily Meal Summary")
    
    # Collect all meals from all meal times
    all_selected_meals = []
    all_quantities = []
    all_cooking_methods = []
    
    daily_calories = 0
    daily_protein = 0
    daily_carbs = 0
    daily_fat = 0
    daily_cost = 0
    
    # Display summary for each meal time
    meal_time_names = ["🌅 Breakfast", "☀️ Lunch", "🌙 Dinner"]
    meal_time_keys = ["breakfast", "lunch", "dinner"]
    
    for meal_time_name, meal_time_key in zip(meal_time_names, meal_time_keys):
        meal_data = st.session_state.daily_meals[meal_time_key]
        
        if meal_data["meals"]:
            with st.expander(f"{meal_time_name} Summary", expanded=False):
                meal_calories = 0
                meal_protein = 0
                meal_carbs = 0
                meal_fat = 0
                meal_cost = 0
                
                for meal, qty, method in zip(meal_data["meals"], meal_data["quantities"], meal_data["methods"]):
                    if method:
                        cal = method["calories"] * qty
                        prot = method["protein"] * qty
                        carb = method["carbs"] * qty
                        fat = method["fat"] * qty
                        cost = method["price"] * qty
                    else:
                        cal = meal.calories * qty / 100
                        prot = meal.protein * qty / 100
                        carb = meal.carbs * qty / 100
                        fat = meal.fat * qty / 100
                        cost = meal.price * qty / 100
                    
                    meal_calories += cal
                    meal_protein += prot
                    meal_carbs += carb
                    meal_fat += fat
                    meal_cost += cost
                    
                    # Add to overall lists for AI processing
                    all_selected_meals.append(meal)
                    all_quantities.append(qty)
                    all_cooking_methods.append(method)
                    
                    # Display individual meal
                    st.write(f"- **{meal.name}**: {cal:.0f} cal, {prot:.1f}g protein, {cost:.0f} VND")
                
                # Meal time totals
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Calories", f"{meal_calories:.0f}")
                with col2:
                    st.metric("Protein", f"{meal_protein:.1f}g")
                with col3:
                    st.metric("Carbs", f"{meal_carbs:.1f}g")
                with col4:
                    st.metric("Cost", f"{meal_cost:.0f} VND")
                
                daily_calories += meal_calories
                daily_protein += meal_protein
                daily_carbs += meal_carbs
                daily_fat += meal_fat
                daily_cost += meal_cost

    # Show overall daily totals
    if all_selected_meals:
        st.subheader("🎯 Daily Totals")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Calories", f"{daily_calories:.0f}")
        with col2:
            st.metric("Total Protein", f"{daily_protein:.1f}g")
        with col3:
            st.metric("Total Carbs", f"{daily_carbs:.1f}g")
        with col4:
            st.metric("Total Fat", f"{daily_fat:.1f}g")
        with col5:
            st.metric("Total Cost", f"{daily_cost:.0f} VND")

        # Progress towards daily goals
        user = st.session_state.user_profile
        target_calories = calculate_daily_calories(user)
        macro_targets = get_macro_targets(user, target_calories)
        
        progress_col1, progress_col2, progress_col3 = st.columns(3)
        
        with progress_col1:
            calorie_progress = min(daily_calories / target_calories, 1.0)
            st.progress(calorie_progress, text=f"Calories: {calorie_progress * 100:.0f}% of target")
        
        with progress_col2:
            protein_progress = min(daily_protein / macro_targets['protein'], 1.0)
            st.progress(protein_progress, text=f"Protein: {protein_progress * 100:.0f}% of target")
            
        with progress_col3:
            carb_progress = min(daily_carbs / macro_targets['carbs'], 1.0)
            st.progress(carb_progress, text=f"Carbs: {carb_progress * 100:.0f}% of target")

        # Get AI recommendation for the full day
        if st.button("🤖 Get AI Recommendation for Full Day", type="primary"):
            with st.spinner("Getting AI recommendation for your daily meal plan..."):
                # Create meal objects with cooking method data
                processed_meals = []
                processed_quantities = []
                
                for meal, qty, method in zip(all_selected_meals, all_quantities, all_cooking_methods):
                    if method:
                        # Create meal object with cooking method data
                        meal_obj = Meal(
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
                        processed_meals.append(meal_obj)
                        processed_quantities.append(qty)
                    else:
                        # Legacy data
                        processed_meals.append(meal)
                        processed_quantities.append(qty)

                selection = MealSelection(meals=processed_meals, quantities=processed_quantities)
                recommendation = get_meal_recommendation(user, selection)
                st.session_state.recommendation = recommendation
                st.success("✅ AI recommendations generated for your full day!")
                st.rerun()
    
    else:
        st.info("👆 Select meals for breakfast, lunch, and dinner to see your daily nutrition summary and get AI recommendations!")

def show_budget_menu():
    st.header("💰 Budget-Based Menu Optimization")

    if not st.session_state.user_profile:
        st.warning("⚠️ Please complete your profile first!")
        return

    user = st.session_state.user_profile
    daily_calories = calculate_daily_calories(user)

    st.info(f"🎯 Your daily calorie target: {daily_calories:.0f} calories")

    with st.form("budget_form"):
        budget = st.number_input(
            "Daily Budget (VND)", 
            min_value=50000, 
            max_value=500000, 
            value=100000, 
            step=10000
        )
        
        if st.form_submit_button("🎯 Generate Optimized Menu", type="primary"):
            with st.spinner("Creating your optimized menu..."):
                menu = get_optimized_menu(user, budget)
                st.session_state.budget_menu = menu
                st.success("✅ Optimized menu created!")
                st.rerun()

    # Show generated menu
    if st.session_state.budget_menu:
        menu = st.session_state.budget_menu
        
        st.subheader("🍽️ Your Optimized Daily Menu")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cost", f"{menu.total_cost:.0f} VND", f"{menu.total_cost - budget:+.0f}")
        with col2:
            st.metric("Total Calories", f"{menu.total_calories:.0f}")
        with col3:
            st.metric("Budget Used", f"{(menu.total_cost/budget)*100:.1f}%")

        # Menu breakdown
        meals_by_time = [
            ("🌅 Breakfast", menu.breakfast),
            ("☀️ Lunch", menu.lunch),
            ("🌙 Dinner", menu.dinner)
        ]

        for meal_time, meals in meals_by_time:
            with st.expander(f"{meal_time} ({len(meals)} items)", expanded=True):
                if meals:
                    for meal in meals:
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        with col1:
                            st.write(f"**{meal.name}**")
                            if meal.cooking_methods:
                                st.caption(f"Method: {meal.cooking_methods[0]['method']}")
                        with col2:
                            st.write(f"{meal.calories:.0f} cal")
                        with col3:
                            st.write(f"{meal.protein:.1f}g protein")
                        with col4:
                            st.write(f"{meal.price:.0f} VND")
                else:
                    st.write("No meals planned for this time")

        # Explanation
        st.info(f"💡 **AI Explanation**: {menu.explanation}")

def show_results():
    st.header("📊 Results & Analysis")

    if not st.session_state.user_profile:
        st.warning("⚠️ Please complete your profile first!")
        return

    user = st.session_state.user_profile
    daily_calories = calculate_daily_calories(user)
    macro_targets = get_macro_targets(user, daily_calories)

    # Show user summary
    st.subheader("👤 User Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Name**: {user.name}")
        st.write(f"**Age**: {user.age}")
        st.write(f"**Goal**: {user.goal.title()}")
        st.write(f"**Activity**: {user.activity.title()}")
    
    with col2:
        st.metric("Daily Calories", f"{daily_calories:.0f}")
        st.metric("Protein Target", f"{macro_targets['protein']:.0f}g")
        st.metric("Carbs Target", f"{macro_targets['carbs']:.0f}g") 
        st.metric("Fat Target", f"{macro_targets['fat']:.0f}g")

    # Show meal recommendations if available
    if st.session_state.recommendation:
        st.subheader("🤖 AI Meal Recommendations")
        rec = st.session_state.recommendation
        
        with st.container():
            st.success("✨ Here's your optimized meal plan:")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Optimized Calories", f"{rec.total_calories:.0f}")
            with col2:
                st.metric("Protein", f"{rec.total_protein:.1f}g")
            with col3:
                st.metric("Carbs", f"{rec.total_carbs:.1f}g")
            with col4:
                st.metric("Fat", f"{rec.total_fat:.1f}g")
            
            st.info(f"💡 {rec.explanation}")
            
            # Show adjusted portions
            if len(rec.adjusted_meals) > 0:
                st.subheader("🔧 Portion Adjustments")
                for i, (meal, old_qty, new_qty) in enumerate(zip(rec.adjusted_meals, [1]*len(rec.adjusted_meals), rec.adjusted_quantities)):
                    if abs(new_qty - old_qty) > 0.1:  # Only show significant changes
                        change = ((new_qty - old_qty) / old_qty) * 100 if old_qty > 0 else 0
                        direction = "📈" if change > 0 else "📉"
                        st.write(f"{direction} **{meal.name}**: {old_qty:.1f} → {new_qty:.1f} "
                               f"({change:+.0f}%)")

    # Show budget menu if available
    if st.session_state.budget_menu:
        st.subheader("💰 Budget Menu Analysis")
        menu = st.session_state.budget_menu
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Menu Cost", f"{menu.total_cost:.0f} VND")
            st.metric("Menu Calories", f"{menu.total_calories:.0f}")
        
        with col2:
            # Calculate efficiency metrics
            cost_per_calorie = menu.total_cost / menu.total_calories if menu.total_calories > 0 else 0
            st.metric("Cost per Calorie", f"{cost_per_calorie:.1f} VND/cal")
            
            calorie_efficiency = (menu.total_calories / daily_calories) * 100
            st.metric("Calorie Efficiency", f"{calorie_efficiency:.1f}%")

        st.info(f"📝 **Menu Strategy**: {menu.explanation}")

    if not st.session_state.recommendation and not st.session_state.budget_menu:
        st.info("🔍 No results yet. Try the Meal Selection or Budget Menu sections!")

if __name__ == "__main__":
    main()