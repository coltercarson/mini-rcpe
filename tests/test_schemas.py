import pytest
from pydantic import ValidationError
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import schemas


class TestStepIngredientBase:
    """Tests for StepIngredient schema."""
    
    def test_step_ingredient_valid(self):
        """Test creating a valid step ingredient."""
        ingredient = schemas.StepIngredientCreate(
            ingredient_name="flour",
            amount=2.0,
            unit="cup"
        )
        assert ingredient.ingredient_name == "flour"
        assert ingredient.amount == 2.0
        assert ingredient.unit == "cup"
    
    def test_step_ingredient_optional_fields(self):
        """Test step ingredient with optional fields."""
        ingredient = schemas.StepIngredientCreate(
            ingredient_name="salt"
        )
        assert ingredient.ingredient_name == "salt"
        assert ingredient.amount is None
        assert ingredient.unit is None
    
    def test_step_ingredient_missing_required_field(self):
        """Test that ingredient_name is required."""
        with pytest.raises(ValidationError):
            schemas.StepIngredientCreate()


class TestStepBase:
    """Tests for Step schema."""
    
    def test_step_valid(self):
        """Test creating a valid step."""
        step = schemas.StepCreate(
            step_number=1,
            action="Mix ingredients",
            time_minutes=5,
            tools=["bowl", "spoon"],
            ingredients=[
                schemas.StepIngredientCreate(
                    ingredient_name="flour",
                    amount=2.0,
                    unit="cup"
                )
            ]
        )
        assert step.step_number == 1
        assert step.action == "Mix ingredients"
        assert step.time_minutes == 5
        assert len(step.tools) == 2
        assert len(step.ingredients) == 1
    
    def test_step_optional_fields(self):
        """Test step with optional fields as defaults."""
        step = schemas.StepCreate(
            step_number=1,
            action="Stir"
        )
        assert step.step_number == 1
        assert step.action == "Stir"
        assert step.time_minutes is None
        assert step.tools == []
        assert step.ingredients == []
    
    def test_step_missing_required_fields(self):
        """Test that required fields must be provided."""
        with pytest.raises(ValidationError):
            schemas.StepCreate()
        
        with pytest.raises(ValidationError):
            schemas.StepCreate(step_number=1)
        
        with pytest.raises(ValidationError):
            schemas.StepCreate(action="Mix")


class TestRecipeBase:
    """Tests for Recipe schema."""
    
    def test_recipe_valid(self):
        """Test creating a valid recipe."""
        recipe = schemas.RecipeCreate(
            title="Test Recipe",
            total_time_minutes=30,
            base_servings=4,
            steps=[
                schemas.StepCreate(
                    step_number=1,
                    action="Mix",
                    ingredients=[]
                )
            ]
        )
        assert recipe.title == "Test Recipe"
        assert recipe.total_time_minutes == 30
        assert recipe.base_servings == 4
        assert len(recipe.steps) == 1
    
    def test_recipe_optional_fields(self):
        """Test recipe with optional fields as defaults."""
        recipe = schemas.RecipeCreate(
            title="Minimal Recipe"
        )
        assert recipe.title == "Minimal Recipe"
        assert recipe.total_time_minutes is None
        assert recipe.base_servings == 1
        assert recipe.image_filename is None
        assert recipe.steps == []
    
    def test_recipe_missing_required_field(self):
        """Test that title is required."""
        with pytest.raises(ValidationError):
            schemas.RecipeCreate()
    
    def test_recipe_with_image(self):
        """Test recipe with image filename."""
        recipe = schemas.RecipeCreate(
            title="Recipe with Image",
            image_filename="test.jpg"
        )
        assert recipe.image_filename == "test.jpg"


class TestRecipeNested:
    """Tests for nested recipe structures."""
    
    def test_recipe_with_multiple_steps(self):
        """Test recipe with multiple steps."""
        recipe = schemas.RecipeCreate(
            title="Multi-Step Recipe",
            steps=[
                schemas.StepCreate(step_number=1, action="Step 1"),
                schemas.StepCreate(step_number=2, action="Step 2"),
                schemas.StepCreate(step_number=3, action="Step 3")
            ]
        )
        assert len(recipe.steps) == 3
        assert recipe.steps[1].step_number == 2
    
    def test_recipe_with_nested_ingredients(self):
        """Test recipe with steps containing ingredients."""
        recipe = schemas.RecipeCreate(
            title="Complex Recipe",
            steps=[
                schemas.StepCreate(
                    step_number=1,
                    action="Mix dry ingredients",
                    ingredients=[
                        schemas.StepIngredientCreate(
                            ingredient_name="flour",
                            amount=2.0,
                            unit="cup"
                        ),
                        schemas.StepIngredientCreate(
                            ingredient_name="salt",
                            amount=1.0,
                            unit="tsp"
                        )
                    ]
                ),
                schemas.StepCreate(
                    step_number=2,
                    action="Add wet ingredients",
                    ingredients=[
                        schemas.StepIngredientCreate(
                            ingredient_name="eggs",
                            amount=2.0,
                            unit=None
                        )
                    ]
                )
            ]
        )
        assert len(recipe.steps) == 2
        assert len(recipe.steps[0].ingredients) == 2
        assert len(recipe.steps[1].ingredients) == 1
        assert recipe.steps[0].ingredients[0].ingredient_name == "flour"


class TestSchemaValidation:
    """Tests for schema validation rules."""
    
    def test_invalid_data_types(self):
        """Test that invalid data types are rejected."""
        with pytest.raises(ValidationError):
            schemas.RecipeCreate(
                title=123,  # Should be string
                base_servings="four"  # Should be int
            )
    
    def test_negative_values(self):
        """Test handling of negative values."""
        # Negative values are technically allowed by the schema
        # but may not make sense in practice
        recipe = schemas.RecipeCreate(
            title="Test",
            total_time_minutes=-5,
            base_servings=-1
        )
        assert recipe.total_time_minutes == -5
        assert recipe.base_servings == -1
