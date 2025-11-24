// Sample recipes for the demo
const recipes = [
    {
        id: 1,
        title: "Chocolate Chip Cookies",
        base_servings: 24,
        total_time_minutes: 30,
        recipe_mode: "standard",
        source_url: "https://example.com",
        steps: [
            {
                step_number: 1,
                action: "Preheat oven to 375°F (190°C). Line baking sheets with parchment paper.",
                ingredients: [],
                time_minutes: 5
            },
            {
                step_number: 2,
                action: "In a large bowl, cream together the butter and sugars until light and fluffy.",
                ingredients: [
                    { amount: 1, unit: "cup", ingredient_name: "butter, softened" },
                    { amount: 0.75, unit: "cup", ingredient_name: "granulated sugar" },
                    { amount: 0.75, unit: "cup", ingredient_name: "brown sugar" }
                ],
                time_minutes: 3
            },
            {
                step_number: 3,
                action: "Beat in the eggs and vanilla extract until well combined.",
                ingredients: [
                    { amount: 2, unit: "", ingredient_name: "large eggs" },
                    { amount: 2, unit: "tsp", ingredient_name: "vanilla extract" }
                ],
                time_minutes: 2
            },
            {
                step_number: 4,
                action: "In a separate bowl, whisk together the flour, baking soda, and salt.",
                ingredients: [
                    { amount: 2.25, unit: "cups", ingredient_name: "all-purpose flour" },
                    { amount: 1, unit: "tsp", ingredient_name: "baking soda" },
                    { amount: 1, unit: "tsp", ingredient_name: "salt" }
                ],
                time_minutes: 2
            },
            {
                step_number: 5,
                action: "Gradually stir the dry ingredients into the wet ingredients until just combined. Fold in the chocolate chips.",
                ingredients: [
                    { amount: 2, unit: "cups", ingredient_name: "chocolate chips" }
                ],
                time_minutes: 3
            },
            {
                step_number: 6,
                action: "Drop rounded tablespoons of dough onto prepared baking sheets, spacing them 2 inches apart.",
                ingredients: [],
                time_minutes: 5
            },
            {
                step_number: 7,
                action: "Bake for 9-11 minutes, until edges are golden but centers are still soft. Cool on baking sheet for 5 minutes before transferring to a wire rack.",
                ingredients: [],
                time_minutes: 15
            }
        ]
    },
    {
        id: 2,
        title: "Classic Sourdough Bread",
        base_servings: 1,
        total_time_minutes: 1440,
        recipe_mode: "bread",
        source_url: null,
        steps: [
            {
                step_number: 1,
                action: "Mix the flour and water together in a large bowl until no dry flour remains. Cover and let rest (autolyse) for 30-60 minutes.",
                ingredients: [
                    { amount: 500, unit: "g", ingredient_name: "bread flour" },
                    { amount: 350, unit: "g", ingredient_name: "water" }
                ],
                time_minutes: 60
            },
            {
                step_number: 2,
                action: "Add the sourdough starter and salt to the dough. Mix thoroughly by hand, squeezing and folding until fully incorporated.",
                ingredients: [
                    { amount: 100, unit: "g", ingredient_name: "active sourdough starter" },
                    { amount: 10, unit: "g", ingredient_name: "salt" }
                ],
                time_minutes: 10
            },
            {
                step_number: 3,
                action: "Perform a series of stretch and folds every 30 minutes for the next 2-3 hours. Cover bowl between folds.",
                ingredients: [],
                time_minutes: 180
            },
            {
                step_number: 4,
                action: "Shape the dough into a round and place in a floured banneton basket, seam side up. Cover with a damp towel.",
                ingredients: [],
                time_minutes: 10
            },
            {
                step_number: 5,
                action: "Refrigerate for 12-18 hours for cold fermentation. This develops flavor and makes scoring easier.",
                ingredients: [],
                time_minutes: 900
            },
            {
                step_number: 6,
                action: "Preheat oven to 450°F (230°C) with a Dutch oven inside for at least 30 minutes.",
                ingredients: [],
                time_minutes: 30
            },
            {
                step_number: 7,
                action: "Turn out dough onto parchment paper, score the top, and carefully transfer to the hot Dutch oven. Cover with lid.",
                ingredients: [],
                time_minutes: 5
            },
            {
                step_number: 8,
                action: "Bake covered for 20 minutes, then remove lid and bake for another 25-30 minutes until deep golden brown.",
                ingredients: [],
                time_minutes: 50
            },
            {
                step_number: 9,
                action: "Remove from oven and cool completely on a wire rack before slicing (at least 1 hour).",
                ingredients: [],
                time_minutes: 60
            }
        ]
    },
    {
        id: 3,
        title: "Simple Tomato Pasta",
        base_servings: 4,
        total_time_minutes: 25,
        recipe_mode: "standard",
        source_url: null,
        steps: [
            {
                step_number: 1,
                action: "Bring a large pot of salted water to a boil. Add pasta and cook according to package directions until al dente.",
                ingredients: [
                    { amount: 400, unit: "g", ingredient_name: "spaghetti or pasta" }
                ],
                time_minutes: 10
            },
            {
                step_number: 2,
                action: "While pasta cooks, heat olive oil in a large skillet over medium heat. Add garlic and red pepper flakes, cook until fragrant (about 1 minute).",
                ingredients: [
                    { amount: 3, unit: "tbsp", ingredient_name: "olive oil" },
                    { amount: 4, unit: "", ingredient_name: "garlic cloves, minced" },
                    { amount: 0.5, unit: "tsp", ingredient_name: "red pepper flakes" }
                ],
                time_minutes: 2
            },
            {
                step_number: 3,
                action: "Add the crushed tomatoes, salt, and sugar. Bring to a simmer and cook for 10 minutes, stirring occasionally.",
                ingredients: [
                    { amount: 800, unit: "g", ingredient_name: "crushed tomatoes (canned)" },
                    { amount: 1, unit: "tsp", ingredient_name: "salt" },
                    { amount: 1, unit: "tsp", ingredient_name: "sugar" }
                ],
                time_minutes: 10
            },
            {
                step_number: 4,
                action: "Reserve 1 cup of pasta water, then drain the pasta. Add pasta to the sauce along with fresh basil. Toss to combine, adding pasta water as needed to reach desired consistency.",
                ingredients: [
                    { amount: 0.25, unit: "cup", ingredient_name: "fresh basil, torn" }
                ],
                time_minutes: 3
            },
            {
                step_number: 5,
                action: "Serve immediately with grated Parmesan cheese and extra basil if desired.",
                ingredients: [
                    { amount: null, unit: "", ingredient_name: "Parmesan cheese, for serving" }
                ],
                time_minutes: 0
            }
        ]
    }
];
