function displayResults(data, containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container not found: ${containerId}`);
        return;
    }
    
    console.log('Displaying results for container:', containerId);
    console.log('Data received:', data);
    
    container.innerHTML = ''; // Clear previous content

    if (data.error) {
        showError(data.error);
        return;
    }

    // Nutrition Tips
    if (data.tips) {
        const tipsSection = document.createElement('div');
        tipsSection.className = 'nutrition-tips';
        tipsSection.innerHTML = `
            <h3><i class="fas fa-lightbulb"></i> Nutrition Tips</h3>
            <ul>${data.tips.map(tip => `<li>${tip}</li>`).join('')}</ul>
        `;
        container.appendChild(tipsSection);
    }

    // Recipes (for both regular recipes and leftover recipes)
    if (Array.isArray(data.recipes) && data.recipes.length > 0) {
        const recipesGrid = document.createElement('div');
        recipesGrid.className = 'recipe-grid';

        data.recipes.forEach(recipe => {
            const card = document.createElement('div');
            card.className = 'recipe-card';

            // Ensure all numeric values are properly handled
            const calories = Math.round(parseFloat(recipe.Calories || 0));
            const protein = Math.round(parseFloat(recipe.ProteinContent || 0));
            const carbs = Math.round(parseFloat(recipe.CarbohydrateContent || 0));
            const fat = Math.round(parseFloat(recipe.FatContent || 0));

            // Clean up image URL if it exists
            const imageUrl = recipe.Images ? recipe.Images.replace(/["\\]/g, '') : '';

            card.innerHTML = `
                <h3>${recipe.Name || recipe.name || 'Untitled Recipe'}</h3>
                ${imageUrl ? `
                    <img src="${imageUrl}" 
                         alt="${recipe.Name || recipe.name || 'Recipe Image'}" 
                         onerror="this.style.display='none'" 
                         class="recipe-image">
                ` : ''}
                <div class="recipe-metadata">
                    ${recipe.RecipeCategory ? `
                        <span class="metadata-item"><i class="fas fa-tag"></i> ${recipe.RecipeCategory}</span>
                    ` : ''}
                    ${recipe.TotalTime ? `
                        <span class="metadata-item"><i class="fas fa-clock"></i> ${formatTime(recipe.TotalTime)}</span>
                    ` : ''}
                    ${recipe.RecipeServings ? `
                        <span class="metadata-item"><i class="fas fa-users"></i> Serves ${recipe.RecipeServings}</span>
                    ` : ''}
                </div>
                <div class="nutrition-info">
                    <span><i class="fas fa-fire"></i> ${calories} calories</span>
                    <span><i class="fas fa-drumstick-bite"></i> ${protein}g protein</span>
                    <span><i class="fas fa-bread-slice"></i> ${carbs}g carbs</span>
                    <span><i class="fas fa-cheese"></i> ${fat}g fat</span>
                </div>
                <details>
                    <summary>View Details</summary>
                    <div class="meal-details">
                        <p><strong>Ingredients:</strong><br>${formatIngredients(recipe.RecipeIngredientParts || recipe.ingredients)}</p>
                        <p><strong>Instructions:</strong><br>${formatInstructions(recipe.RecipeInstructions || recipe.instructions)}</p>
                    </div>
                </details>
            `;

            recipesGrid.appendChild(card);
        });

        container.appendChild(recipesGrid);
    } else if (Array.isArray(data.recipes) && data.recipes.length === 0) {
        container.innerHTML = '<p class="no-results">No recipes found matching your criteria.</p>';
    }

    // BMI result
    if (data.bmi !== undefined) {
        const bmiResult = document.createElement('div');
        bmiResult.className = 'bmi-result';
        bmiResult.innerHTML = `
            <h3>Your BMI Result</h3>
            <p class="bmi-value">${data.bmi}</p>
            <p class="bmi-category">${getBMICategory(data.bmi)}</p>
        `;
        container.appendChild(bmiResult);
        localStorage.setItem('currentBMI', data.bmi);
    }

    // Weekly Meal Plan
    if (data.meal_plan) {
        const mealPlanDiv = document.createElement('div');
        mealPlanDiv.className = 'meal-plan';
        let mealPlanHtml = '<h3>Your Weekly Meal Plan</h3>';
        
        for (const [day, meals] of Object.entries(data.meal_plan)) {
            mealPlanHtml += `
                <div class="day-plan">
                    <h4>${day}</h4>
                    <div class="meals">
                        ${Object.entries(meals).map(([mealType, recipe]) => `
                            <div class="meal">
                                <h5>${mealType}</h5>
                                <p>${recipe.Name || recipe.name || 'Recipe name not available'}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        mealPlanDiv.innerHTML = mealPlanHtml;
        container.appendChild(mealPlanDiv);
    }

    // Smooth scroll to result
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}