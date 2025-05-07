from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import  json
import random

app = Flask(__name__)


# Load and clean the dataset
try:
    df = pd.read_csv('dataset/recipes.csv')
    # Replace NaN values with appropriate defaults
    df = df.fillna({
        'Name': '',
        'Calories': 0,
        'ProteinContent': 0,
        'CarbohydrateContent': 0,
        'FatContent': 0,
        'RecipeCategory': '',
        'TotalTime': '',
        'PrepTime': '',
        'CookTime': '',
        'RecipeServings': 0,
        'RecipeIngredientParts': '',
        'RecipeInstructions': '',
        'Images': '',
        'Description': '',
        'SodiumContent': 0,
        'SugarContent': 0
    })
except Exception as e:
    print(f"Error loading dataset: {e}")
    df = pd.DataFrame()
except Exception as e:
    print(f"Error loading dataset: {e}")
    df = pd.DataFrame()  # Create empty DataFrame if file not found

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/meal_plan')
def meal_plan():
    return render_template('plan.html')  # Render plan.html when '/meal_plan' is accessed

@app.route('/calculate_bmi', methods=['POST'])
def calculate_bmi():
    try:
        height = float(request.form.get('height', 0)) / 100
        weight = float(request.form.get('weight', 0))
        
        if height <= 0 or weight <= 0:
            return jsonify({'error': 'Please enter valid height and weight'}), 400
            
        bmi = weight / (height * height)
        return jsonify({'bmi': round(bmi, 2)})
    except Exception as e:
        print(f"BMI calculation error: {str(e)}")
        return jsonify({'error': 'Error calculating BMI'}), 400

@app.route('/get_recipes', methods=['POST'])
def get_recipes():
    try:
        ingredients = request.form.get('ingredients', '').lower()
        bmi = float(request.form.get('bmi', 22))  # Default BMI if not provided
        
        # Define calorie ranges based on BMI
        if bmi < 18.5:  # Underweight
            min_cal, max_cal = 300, 800
        elif bmi < 25:  # Normal weight
            min_cal, max_cal = 200, 600
        elif bmi < 30:  # Overweight
            min_cal, max_cal = 200, 500
        else:  # Obese
            min_cal, max_cal = 200, 400

        # Filter recipes
        filtered_df = df[
            (df['Calories'].between(min_cal, max_cal)) &
            (df['RecipeIngredientParts'].str.lower().str.contains(ingredients, na=False))
        ]

        if filtered_df.empty:
            return jsonify({'error': 'No recipes found matching your criteria'}), 404

        # Clean and prepare the data
        recipes = []
        for _, recipe in filtered_df.sample(n=min(5, len(filtered_df))).iterrows():
            clean_recipe = {
                'Name': str(recipe['Name']),
                'Calories': float(recipe['Calories']) if pd.notnull(recipe['Calories']) else 0,
                'ProteinContent': float(recipe['ProteinContent']) if pd.notnull(recipe['ProteinContent']) else 0,
                'CarbohydrateContent': float(recipe['CarbohydrateContent']) if pd.notnull(recipe['CarbohydrateContent']) else 0,
                'FatContent': float(recipe['FatContent']) if pd.notnull(recipe['FatContent']) else 0,
                'RecipeCategory': str(recipe['RecipeCategory']) if pd.notnull(recipe['RecipeCategory']) else '',
                'TotalTime': str(recipe['TotalTime']) if pd.notnull(recipe['TotalTime']) else '',
                'RecipeServings': float(recipe['RecipeServings']) if pd.notnull(recipe['RecipeServings']) else 0,
                'RecipeIngredientParts': str(recipe['RecipeIngredientParts']).replace("'", "").replace('"', '').replace('c(', '').replace(')', ''),
                'RecipeInstructions': str(recipe['RecipeInstructions']).replace("'", "").replace('"', '').replace('c(', '').replace(')', '')
            }
            
            # Clean up the Images field if it exists
            if 'Images' in recipe and pd.notnull(recipe['Images']):
                clean_recipe['Images'] = str(recipe['Images']).replace('"', '').replace('c(', '').replace(')', '')
            else:
                clean_recipe['Images'] = ''

            recipes.append(clean_recipe)

        return jsonify({'recipes': recipes})
    except Exception as e:
        print(f"Recipe search error: {str(e)}")
        return jsonify({'error': f'Error finding recipes: {str(e)}'}), 500

@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    try:
        selected_recipes = df.sample(n=21)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        meal_types = ['Breakfast', 'Lunch', 'Dinner']
        weekly_plan = []
        recipe_index = 0

        for day in days:
            daily_meals = {'day': day, 'meals': []}
            for meal_type in meal_types:
                if recipe_index < len(selected_recipes):
                    recipe = selected_recipes.iloc[recipe_index]
                    instructions = recipe.get('RecipeInstructions', 'Instructions not available')
                    try:
                        instructions = eval(instructions) if isinstance(instructions, str) else instructions
                    except:
                        instructions = [instructions]
                    daily_meals['meals'].append({
                        'type': meal_type,
                        'name': recipe['Name'],
                        'calories': recipe['Calories'],
                        'protein': recipe.get('ProteinContent', 'N/A'),
                        'ingredients': recipe['RecipeIngredientParts'],
                        'instructions': instructions,
                        'image': recipe.get('ImageURL', '')  # Add image URL if available
                    })
                    recipe_index += 1
            weekly_plan.append(daily_meals)
        return jsonify({'weekly_plan': weekly_plan})
    except Exception as e:
        print(f"Meal plan generation error: {str(e)}")
        return jsonify({'error': f'Error generating meal plan: {str(e)}'}), 500

@app.route('/leftover_ingredients', methods=['POST'])
def leftover_ingredients():
    try:
        ingredients = request.form.get('ingredients', '').lower().split(',')
        ingredients = [i.strip() for i in ingredients if i.strip()]
        
        if not ingredients:
            return jsonify({'error': 'Please enter at least one ingredient'}), 400

        # Filter recipes that contain any of the provided ingredients
        matching_recipes = []
        for _, recipe in df.iterrows():
            recipe_ingredients = str(recipe['RecipeIngredientParts']).lower()
            if any(ingredient in recipe_ingredients for ingredient in ingredients):
                clean_recipe = {
                    'Name': str(recipe['Name']),
                    'Calories': float(recipe['Calories']) if pd.notna(recipe['Calories']) else 0,
                    'ProteinContent': float(recipe['ProteinContent']) if pd.notna(recipe['ProteinContent']) else 0,
                    'CarbohydrateContent': float(recipe['CarbohydrateContent']) if pd.notna(recipe['CarbohydrateContent']) else 0,
                    'FatContent': float(recipe['FatContent']) if pd.notna(recipe['FatContent']) else 0,
                    'RecipeCategory': str(recipe['RecipeCategory']) if pd.notna(recipe['RecipeCategory']) else '',
                    'RecipeServings': float(recipe['RecipeServings']) if pd.notna(recipe['RecipeServings']) else 0,
                    'RecipeIngredientParts': str(recipe['RecipeIngredientParts']).replace("'", "").replace('"', '').replace('c(', '').replace(')', ''),
                    'RecipeInstructions': str(recipe['RecipeInstructions']).replace("'", "").replace('"', '').replace('c(', '').replace(')', '')
                }
                
                # Handle Images field
                if 'Images' in recipe and pd.notna(recipe['Images']):
                    clean_recipe['Images'] = str(recipe['Images']).replace('"', '').replace('c(', '').replace(')', '')
                else:
                    clean_recipe['Images'] = ''

                # Handle TotalTime field
                if 'TotalTime' in recipe and pd.notna(recipe['TotalTime']):
                    clean_recipe['TotalTime'] = str(recipe['TotalTime'])
                else:
                    clean_recipe['TotalTime'] = ''

                matching_recipes.append(clean_recipe)

        if not matching_recipes:
            return jsonify({'error': 'No recipes found with these ingredients'}), 404

        # Return up to 5 random recipes
        selected_recipes = random.sample(matching_recipes, min(5, len(matching_recipes)))
        return jsonify({'recipes': selected_recipes})

    except Exception as e:
        print(f"Leftover ingredients search error: {str(e)}")
        return jsonify({'error': f'Error finding recipes: {str(e)}'}), 500
    
@app.route('/nutrition_advice', methods=['POST'])
def nutrition_advice():
    try:
        # Get user preferences and dietary restrictions
        dietary_preference = request.form.get('dietary-preference', '').lower()
        restrictions = request.form.getlist('restrictions[]')
        health_condition = request.form.get('health-condition', '').lower()
        
        # Start with all recipes
        filtered_df = df.copy()
        
        # Filter based on dietary preference
       # Filter based on dietary preference
        if dietary_preference == 'vegetarian':
            filtered_df = filtered_df[~filtered_df['RecipeIngredientParts'].str.lower().str.contains('chicken|beef|pork|fish|meat', na=False)]
        elif dietary_preference == 'vegan':
            filtered_df = filtered_df[~filtered_df['RecipeIngredientParts'].str.lower().str.contains('chicken|beef|pork|fish|meat|egg|milk|cheese|dairy', na=False)]
        elif dietary_preference == 'non-vegetarian':
    # Filter for recipes containing meat products
            filtered_df = filtered_df[
            filtered_df['RecipeIngredientParts'].str.lower().str.contains(
            'chicken|beef|pork|fish|meat|turkey|lamb|bacon|ham|seafood|shrimp|prawn|crab|lobster', 
            na=False
        )
    ]
        # Apply health condition filters
        if health_condition == 'diabetes':
            filtered_df = filtered_df[filtered_df['Calories'] < 500]
        elif health_condition == 'hypertension':
            if 'SodiumContent' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['SodiumContent'] < 500]
        
        # Apply dietary restrictions
        for restriction in restrictions:
            filtered_df = filtered_df[~filtered_df['RecipeIngredientParts'].str.lower().str.contains(restriction.lower(), na=False)]
        
        if filtered_df.empty:
            return jsonify({
                'error': 'No recipes found matching your dietary requirements'
            }), 404

        # Clean and prepare recipes
        recommended_recipes = []
        for _, recipe in filtered_df.sample(n=min(5, len(filtered_df))).iterrows():
            clean_recipe = {}
            
            # Handle string fields
            string_fields = ['Name', 'RecipeCategory', 'Description']
            for field in string_fields:
                clean_recipe[field] = str(recipe.get(field, '')) if pd.notna(recipe.get(field)) else ''

            # Handle numeric fields
            numeric_fields = ['Calories', 'ProteinContent', 'CarbohydrateContent', 'FatContent', 
                            'RecipeServings', 'SodiumContent', 'SugarContent']
            for field in numeric_fields:
                clean_recipe[field] = float(recipe.get(field, 0)) if pd.notna(recipe.get(field)) else 0

            # Clean ingredient parts
            ingredients = recipe.get('RecipeIngredientParts', '')
            if pd.notna(ingredients):
                if isinstance(ingredients, str):
                    ingredients = ingredients.replace('c(', '').replace(')', '').replace('"', '')
                elif isinstance(ingredients, list):
                    ingredients = ', '.join(ingredients)
                clean_recipe['RecipeIngredientParts'] = ingredients
            else:
                clean_recipe['RecipeIngredientParts'] = ''

            # Clean instructions
            instructions = recipe.get('RecipeInstructions', '')
            if pd.notna(instructions):
                if isinstance(instructions, str):
                    instructions = instructions.replace('c(', '').replace(')', '').replace('"', '')
                elif isinstance(instructions, list):
                    instructions = '. '.join(instructions)
                clean_recipe['RecipeInstructions'] = instructions
            else:
                clean_recipe['RecipeInstructions'] = ''

            # Clean images
            images = recipe.get('Images', '')
            if pd.notna(images):
                if isinstance(images, str):
                    images = images.replace('c(', '').replace(')', '').replace('"', '')
                elif isinstance(images, list):
                    images = images[0] if images else ''
                clean_recipe['Images'] = images
            else:
                clean_recipe['Images'] = ''

            # Handle time fields
            time_fields = ['TotalTime', 'CookTime', 'PrepTime']
            for field in time_fields:
                value = recipe.get(field, '')
                clean_recipe[field] = str(value) if pd.notna(value) else ''

            recommended_recipes.append(clean_recipe)
        
        # Prepare nutrition tips based on health condition
        nutrition_tips = {
            'diabetes': [
                'Choose foods with low glycemic index',
                'Monitor carbohydrate intake',
                'Include fiber-rich foods',
                'Eat at regular intervals'
            ],
            'hypertension': [
                'Reduce sodium intake',
                'Include potassium-rich foods',
                'Limit alcohol consumption',
                'Choose lean proteins'
            ],
            'weight_management': [
                'Control portion sizes',
                'Include protein in every meal',
                'Choose whole grains over refined grains',
                'Increase fiber intake'
            ]
        }
        
        # Get appropriate tips or default tips
        selected_tips = nutrition_tips.get(health_condition, [
            'Maintain a balanced diet',
            'Include variety of fruits and vegetables',
            'Stay hydrated',
            'Control portion sizes'
        ])
        
        return jsonify({
            'recipes': recommended_recipes,
            'tips': selected_tips
        })
    
    except Exception as e:
        print(f"Nutrition advice error: {str(e)}")
        return jsonify({
            'error': f'Error providing nutrition advice: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
