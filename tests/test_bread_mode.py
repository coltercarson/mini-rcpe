import pytest
from app import crud, schemas


class TestBreadModeRecipe:
    """Tests for bread mode recipe functionality."""
    
    def test_create_bread_recipe_basic(self, test_db):
        """Test creating a basic bread mode recipe."""
        recipe_data = {
            "title": "Simple Bread",
            "recipe_mode": "bread",
            "dough_weight": 1000.0,
            "base_servings": 1,
            "steps": [
                {
                    "step_number": 1,
                    "action": "Mix all ingredients",
                    "ingredients": [
                        {
                            "ingredient_name": "flour",
                            "amount": 600.0,
                            "unit": "g",
                            "baker_percentage": 60.0
                        },
                        {
                            "ingredient_name": "water",
                            "amount": 400.0,
                            "unit": "g",
                            "baker_percentage": 40.0
                        }
                    ]
                }
            ]
        }
        
        recipe_create = schemas.RecipeCreate(**recipe_data)
        result = crud.create_recipe(test_db, recipe_create)
        
        assert result.id is not None
        assert result.title == "Simple Bread"
        assert result.recipe_mode == "bread"
        assert result.dough_weight == 1000.0
        assert len(result.steps) == 1
        assert len(result.steps[0].ingredients) == 2
        assert result.steps[0].ingredients[0].baker_percentage == 60.0
        assert result.steps[0].ingredients[1].baker_percentage == 40.0
    
    def test_create_normal_recipe_without_bread_fields(self, test_db):
        """Test creating a normal recipe without bread-specific fields."""
        recipe_data = {
            "title": "Normal Recipe",
            "recipe_mode": "normal",
            "base_servings": 4,
            "steps": [
                {
                    "step_number": 1,
                    "action": "Mix ingredients",
                    "ingredients": [
                        {
                            "ingredient_name": "sugar",
                            "amount": 2.0,
                            "unit": "cups"
                        }
                    ]
                }
            ]
        }
        
        recipe_create = schemas.RecipeCreate(**recipe_data)
        result = crud.create_recipe(test_db, recipe_create)
        
        assert result.id is not None
        assert result.title == "Normal Recipe"
        assert result.recipe_mode == "normal"
        assert result.dough_weight is None
        assert len(result.steps) == 1
        assert result.steps[0].ingredients[0].baker_percentage is None
    
    def test_update_recipe_to_bread_mode(self, test_db):
        """Test updating a normal recipe to bread mode."""
        # Create a normal recipe
        recipe_data = {
            "title": "Recipe to Convert",
            "recipe_mode": "normal",
            "base_servings": 1,
            "steps": [
                {
                    "step_number": 1,
                    "action": "Mix",
                    "ingredients": []
                }
            ]
        }
        
        recipe_create = schemas.RecipeCreate(**recipe_data)
        created_recipe = crud.create_recipe(test_db, recipe_create)
        
        # Update to bread mode
        updated_data = {
            "title": "Recipe to Convert",
            "recipe_mode": "bread",
            "dough_weight": 800.0,
            "base_servings": 1,
            "steps": [
                {
                    "step_number": 1,
                    "action": "Mix",
                    "ingredients": [
                        {
                            "ingredient_name": "flour",
                            "amount": 500.0,
                            "unit": "g",
                            "baker_percentage": 62.5
                        },
                        {
                            "ingredient_name": "water",
                            "amount": 300.0,
                            "unit": "g",
                            "baker_percentage": 37.5
                        }
                    ]
                }
            ]
        }
        
        update_schema = schemas.RecipeCreate(**updated_data)
        result = crud.update_recipe(test_db, created_recipe.id, update_schema)
        
        assert result is not None
        assert result.recipe_mode == "bread"
        assert result.dough_weight == 800.0
        assert len(result.steps[0].ingredients) == 2
        assert result.steps[0].ingredients[0].baker_percentage == 62.5
    
    def test_bread_recipe_with_multiple_steps(self, test_db):
        """Test bread recipe with ingredients distributed across multiple steps."""
        recipe_data = {
            "title": "Multi-Step Bread",
            "recipe_mode": "bread",
            "dough_weight": 1500.0,
            "base_servings": 2,
            "steps": [
                {
                    "step_number": 1,
                    "action": "Make preferment",
                    "ingredients": [
                        {
                            "ingredient_name": "flour",
                            "amount": 300.0,
                            "unit": "g",
                            "baker_percentage": 20.0
                        },
                        {
                            "ingredient_name": "water",
                            "amount": 300.0,
                            "unit": "g",
                            "baker_percentage": 20.0
                        }
                    ]
                },
                {
                    "step_number": 2,
                    "action": "Make final dough",
                    "ingredients": [
                        {
                            "ingredient_name": "flour",
                            "amount": 600.0,
                            "unit": "g",
                            "baker_percentage": 40.0
                        },
                        {
                            "ingredient_name": "water",
                            "amount": 300.0,
                            "unit": "g",
                            "baker_percentage": 20.0
                        }
                    ]
                }
            ]
        }
        
        recipe_create = schemas.RecipeCreate(**recipe_data)
        result = crud.create_recipe(test_db, recipe_create)
        
        assert result.id is not None
        assert result.recipe_mode == "bread"
        assert len(result.steps) == 2
        assert len(result.steps[0].ingredients) == 2
        assert len(result.steps[1].ingredients) == 2
        
        # Verify baker percentages are preserved
        assert result.steps[0].ingredients[0].baker_percentage == 20.0
        assert result.steps[1].ingredients[0].baker_percentage == 40.0


class TestBreadModeSchemas:
    """Tests for bread mode schema validation."""
    
    def test_recipe_with_bread_mode_fields(self):
        """Test recipe schema with bread mode fields."""
        recipe_data = {
            "title": "Sourdough",
            "recipe_mode": "bread",
            "dough_weight": 1200.0,
            "base_servings": 1,
            "steps": []
        }
        
        recipe = schemas.RecipeCreate(**recipe_data)
        
        assert recipe.title == "Sourdough"
        assert recipe.recipe_mode == "bread"
        assert recipe.dough_weight == 1200.0
    
    def test_ingredient_with_baker_percentage(self):
        """Test step ingredient with baker percentage."""
        ingredient_data = {
            "ingredient_name": "flour",
            "amount": 500.0,
            "unit": "g",
            "baker_percentage": 100.0
        }
        
        ingredient = schemas.StepIngredientCreate(**ingredient_data)
        
        assert ingredient.ingredient_name == "flour"
        assert ingredient.amount == 500.0
        assert ingredient.unit == "g"
        assert ingredient.baker_percentage == 100.0
    
    def test_recipe_defaults_to_normal_mode(self):
        """Test that recipe mode defaults to 'normal' when not specified."""
        recipe_data = {
            "title": "Default Mode Recipe",
            "base_servings": 1,
            "steps": []
        }
        
        recipe = schemas.RecipeCreate(**recipe_data)
        
        assert recipe.recipe_mode == "normal"
        assert recipe.dough_weight is None
