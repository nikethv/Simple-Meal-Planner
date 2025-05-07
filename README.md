# Simple-Meal-Planner
# 🍽️ Nutrition-Aware Recipe Recommendation System

This project is a Flask-based web application designed to help users plan meals intelligently by offering:

- ✅ **Nutrition-Aware Recipe Recommendations**
- 💪 **BMI Calculation and Personalized Suggestions**
- 📅 **Weekly Meal Planner**
- 🥦 **Leftover Ingredient-Based Meal Suggestions**

---

## 🧰 Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Data**: CSV and Parquet files (recipes, reviews, BMI dataset)
- **Templates**: Jinja2 with Flask

---

## 📁 Project Structure

Meal Planner/
├── dataset/
│ ├── Indian_Recipe_Search_Dataset.csv
│ ├── Indian_Recipes_BMI.csv
│ ├── recipes.csv
│ ├── recipes.parquet
│ ├── reviews.csv
│ └── reviews.parquet
├── static/
│ ├── favicon.ico
│ ├── script.js
│ └── style.css
├── templates/
│ ├── index.html
│ └── plan.html
├── app.py
├── requirements.txt
└── .gitignore


---

## 🚀 Features

### 🔍 Recipe Recommendation
- Search recipes based on ingredients.
- Filter by nutrition and user preferences.

### 📏 BMI Calculator
- Input your weight and height.
- Get personalized diet and meal recommendations.

### 🗓️ Weekly Meal Planner
- Plan breakfast, lunch, and dinner for the week.
- Save and review the meal plan dynamically.

### 🥘 Leftover Ingredient Suggestions
- Input leftover ingredients.
- Get suggested meals that can be made with them.

---

## ▶️ Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd "Meal Planner"
Create a virtual environment

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

pip install -r requirements.txt
Run the app

python app.py
Open your browser and navigate to http://127.0.0.1:5000/
