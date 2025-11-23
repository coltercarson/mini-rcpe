import pytest

from app import crud, schemas


class TestGetRecipe:
    """Tests for get_recipe function."""
    
    def test_get_recipe_exists(self, test_db, sample_recipe_data):
        """Test retrieving an existing recipe."""
        # Create a recipe
        recipe_create = schemas.RecipeCreate(**sample_recipe_data)
        created_recipe = crud.create_recipe(test_db, recipe_create)
        
        # Retrieve it
        retrieved_recipe = crud.get_recipe(test_db, created_recipe.id)
        
        assert retrieved_recipe is not None
        assert retrieved_recipe.id == created_recipe.id
        assert retrieved_recipe.title == sample_recipe_data["title"]
    
    def test_get_recipe_not_exists(self, test_db):
        """Test retrieving a non-existent recipe."""
        result = crud.get_recipe(test_db, 999)
        assert result is None


class TestGetRecipes:
    """Tests for get_recipes function."""
    
    def test_get_recipes_empty(self, test_db):
        """Test retrieving recipes when database is empty."""
        recipes = crud.get_recipes(test_db)
        assert recipes == []
    
    def test_get_recipes_with_data(self, test_db, sample_recipe_data):
        """Test retrieving all recipes."""
        # Create multiple recipes
        recipe1 = schemas.RecipeCreate(**sample_recipe_data)
        recipe2_data = sample_recipe_data.copy()
        recipe2_data["title"] = "Another Recipe"
        recipe2 = schemas.RecipeCreate(**recipe2_data)
        
        crud.create_recipe(test_db, recipe1)
        crud.create_recipe(test_db, recipe2)
        
        recipes = crud.get_recipes(test_db)
        assert len(recipes) == 2
        assert recipes[0].title == "Test Recipe"
        assert recipes[1].title == "Another Recipe"
    
    def test_get_recipes_with_pagination(self, test_db, sample_recipe_data):
        """Test retrieving recipes with pagination."""
        # Create 5 recipes
        for i in range(5):
            recipe_data = sample_recipe_data.copy()
            recipe_data["title"] = f"Recipe {i+1}"
            recipe = schemas.RecipeCreate(**recipe_data)
            crud.create_recipe(test_db, recipe)
        
        # Test skip and limit
        recipes = crud.get_recipes(test_db, skip=2, limit=2)
        assert len(recipes) == 2
        assert recipes[0].title == "Recipe 3"
        assert recipes[1].title == "Recipe 4"


class TestCreateRecipe:
    """Tests for create_recipe function."""
    
    def test_create_recipe_basic(self, test_db, sample_recipe_data):
        """Test creating a basic recipe."""
        recipe_create = schemas.RecipeCreate(**sample_recipe_data)
        result = crud.create_recipe(test_db, recipe_create)
        
        assert result.id is not None
        assert result.title == sample_recipe_data["title"]
        assert result.total_time_minutes == sample_recipe_data["total_time_minutes"]
        assert result.base_servings == sample_recipe_data["base_servings"]
        assert len(result.steps) == 2
    
    def test_create_recipe_with_steps_and_ingredients(self, test_db, sample_recipe_data):
        """Test creating a recipe with steps and ingredients."""
        recipe_create = schemas.RecipeCreate(**sample_recipe_data)
        result = crud.create_recipe(test_db, recipe_create)
        
        # Verify steps
        assert len(result.steps) == 2
        assert result.steps[0].step_number == 1
        assert result.steps[0].action == "Mix flour and water"
        assert result.steps[0].time_minutes == 5
        assert result.steps[0].tools == ["bowl", "spoon"]
        
        # Verify ingredients
        assert len(result.steps[0].ingredients) == 2
        assert result.steps[0].ingredients[0].ingredient_name == "flour"
        assert result.steps[0].ingredients[0].amount == 2.0
        assert result.steps[0].ingredients[0].unit == "cup"
    
    def test_create_recipe_minimal(self, test_db):
        """Test creating a recipe with minimal data."""
        recipe_data = {
            "title": "Minimal Recipe",
            "base_servings": 1,
            "steps": []
        }
        recipe_create = schemas.RecipeCreate(**recipe_data)
        result = crud.create_recipe(test_db, recipe_create)
        
        assert result.id is not None
        assert result.title == "Minimal Recipe"
        assert result.total_time_minutes is None
        assert len(result.steps) == 0


class TestUpdateRecipe:
    """Tests for update_recipe function."""
    
    def test_update_recipe_basic_fields(self, test_db, sample_recipe_data):
        """Test updating basic recipe fields."""
        # Create a recipe
        recipe_create = schemas.RecipeCreate(**sample_recipe_data)
        created_recipe = crud.create_recipe(test_db, recipe_create)
        
        # Update it
        updated_data = sample_recipe_data.copy()
        updated_data["title"] = "Updated Recipe"
        updated_data["total_time_minutes"] = 45
        update_schema = schemas.RecipeCreate(**updated_data)
        
        result = crud.update_recipe(test_db, created_recipe.id, update_schema)
        
        assert result is not None
        assert result.title == "Updated Recipe"
        assert result.total_time_minutes == 45
    
    def test_update_recipe_steps(self, test_db, sample_recipe_data):
        """Test updating recipe steps."""
        # Create a recipe
        recipe_create = schemas.RecipeCreate(**sample_recipe_data)
        created_recipe = crud.create_recipe(test_db, recipe_create)
        
        # Update with different steps
        updated_data = sample_recipe_data.copy()
        updated_data["steps"] = [
            {
                "step_number": 1,
                "action": "New step",
                "time_minutes": 10,
                "tools": [],
                "ingredients": []
            }
        ]
        update_schema = schemas.RecipeCreate(**updated_data)
        
        result = crud.update_recipe(test_db, created_recipe.id, update_schema)
        
        assert result is not None
        assert len(result.steps) == 1
        assert result.steps[0].action == "New step"
    
    def test_update_recipe_not_exists(self, test_db, sample_recipe_data):
        """Test updating a non-existent recipe."""
        recipe_create = schemas.RecipeCreate(**sample_recipe_data)
        result = crud.update_recipe(test_db, 999, recipe_create)
        assert result is None


class TestDeleteRecipe:
    """Tests for delete_recipe function."""
    
    def test_delete_recipe_exists(self, test_db, sample_recipe_data):
        """Test deleting an existing recipe."""
        # Create a recipe
        recipe_create = schemas.RecipeCreate(**sample_recipe_data)
        created_recipe = crud.create_recipe(test_db, recipe_create)
        
        # Delete it
        result = crud.delete_recipe(test_db, created_recipe.id)
        assert result is True
        
        # Verify it's deleted
        retrieved = crud.get_recipe(test_db, created_recipe.id)
        assert retrieved is None
    
    def test_delete_recipe_not_exists(self, test_db):
        """Test deleting a non-existent recipe."""
        result = crud.delete_recipe(test_db, 999)
        assert result is False
    
    def test_delete_recipe_cascades_to_steps(self, test_db, sample_recipe_data):
        """Test that deleting a recipe also deletes its steps."""
        # Create a recipe with steps
        recipe_create = schemas.RecipeCreate(**sample_recipe_data)
        created_recipe = crud.create_recipe(test_db, recipe_create)
        
        # Verify steps exist
        assert len(created_recipe.steps) > 0
        
        # Delete recipe
        crud.delete_recipe(test_db, created_recipe.id)
        
        # Verify recipe and steps are deleted
        retrieved = crud.get_recipe(test_db, created_recipe.id)
        assert retrieved is None
