import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import schemas


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_read_root_empty(self, client):
        """Test root endpoint with no recipes."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"<!DOCTYPE html>" in response.content
    
    def test_read_root_with_recipes(self, client, authenticated_client, sample_recipe_data):
        """Test root endpoint with recipes."""
        # Create a recipe
        recipe_schema = schemas.RecipeCreate(**sample_recipe_data)
        authenticated_client.post("/api/recipes", json=recipe_schema.model_dump())
        
        # Get root page
        response = client.get("/")
        assert response.status_code == 200
        assert b"Test Recipe" in response.content


class TestLoginEndpoint:
    """Tests for login endpoints."""
    
    def test_login_page(self, client):
        """Test login page loads."""
        response = client.get("/login")
        assert response.status_code == 200
        assert b"login" in response.content.lower()
    
    def test_login_success(self, client):
        """Test successful login with default password."""
        # Use default password "secret"
        response = client.post("/login", data={"password": "secret"}, follow_redirects=False)
        assert response.status_code == 303
        # Check that the redirect goes to the root
        assert response.headers["location"] == "/"
    
    def test_login_failure(self, client):
        """Test failed login."""
        response = client.post("/login", data={"password": "wrongpass"}, follow_redirects=False)
        assert response.status_code == 303
        assert "error" in response.headers["location"]
    
    def test_logout(self, client):
        """Test logout."""
        response = client.get("/logout", follow_redirects=False)
        assert response.status_code == 303


class TestRecipeDetailEndpoint:
    """Tests for recipe detail endpoint."""
    
    def test_read_recipe_exists(self, client, authenticated_client, sample_recipe_data):
        """Test viewing an existing recipe."""
        # Create a recipe
        recipe_schema = schemas.RecipeCreate(**sample_recipe_data)
        create_response = authenticated_client.post("/api/recipes", json=recipe_schema.model_dump())
        recipe_id = create_response.json()["id"]
        
        # View the recipe
        response = client.get(f"/recipe/{recipe_id}")
        assert response.status_code == 200
        assert b"Test Recipe" in response.content
    
    def test_read_recipe_not_exists(self, client):
        """Test viewing a non-existent recipe."""
        # This should still return 200 but with None recipe (handled by template)
        response = client.get("/recipe/999")
        assert response.status_code == 200


class TestNewRecipeEndpoint:
    """Tests for new recipe endpoint."""
    
    def test_new_recipe_unauthenticated(self, client):
        """Test accessing new recipe page without authentication."""
        response = client.get("/new", follow_redirects=False)
        assert response.status_code == 303
        assert "/login" in response.headers["location"]
    
    def test_new_recipe_authenticated(self, authenticated_client):
        """Test accessing new recipe page with authentication."""
        response = authenticated_client.get("/new")
        assert response.status_code == 200


class TestEditRecipeEndpoint:
    """Tests for edit recipe endpoint."""
    
    def test_edit_recipe_unauthenticated(self, client, sample_recipe_data):
        """Test accessing edit page without authentication."""
        # First, create a recipe using the API (we'll temporarily set auth)
        client.cookies.set("session_token", "authenticated")
        recipe_schema = schemas.RecipeCreate(**sample_recipe_data)
        create_response = client.post("/api/recipes", json=recipe_schema.model_dump())
        recipe_id = create_response.json()["id"]
        
        # Now clear auth and try to edit
        client.cookies.clear()
        response = client.get(f"/recipe/{recipe_id}/edit", follow_redirects=False)
        assert response.status_code == 303
        assert "/login" in response.headers["location"]
    
    def test_edit_recipe_authenticated(self, authenticated_client, sample_recipe_data):
        """Test accessing edit page with authentication."""
        # Create a recipe
        recipe_schema = schemas.RecipeCreate(**sample_recipe_data)
        create_response = authenticated_client.post("/api/recipes", json=recipe_schema.model_dump())
        recipe_id = create_response.json()["id"]
        
        # Edit with auth
        response = authenticated_client.get(f"/recipe/{recipe_id}/edit")
        assert response.status_code == 200
        assert b"Test Recipe" in response.content
    
    def test_edit_recipe_not_exists(self, authenticated_client):
        """Test editing a non-existent recipe."""
        response = authenticated_client.get("/recipe/999/edit")
        assert response.status_code == 404


class TestRecipeAPIEndpoints:
    """Tests for recipe API endpoints."""
    
    def test_create_recipe_unauthenticated(self, client, sample_recipe_data):
        """Test creating recipe without authentication."""
        recipe_schema = schemas.RecipeCreate(**sample_recipe_data)
        response = client.post("/api/recipes", json=recipe_schema.model_dump())
        assert response.status_code == 401
    
    def test_create_recipe_authenticated(self, authenticated_client, sample_recipe_data):
        """Test creating recipe with authentication."""
        recipe_schema = schemas.RecipeCreate(**sample_recipe_data)
        response = authenticated_client.post("/api/recipes", json=recipe_schema.model_dump())
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Test Recipe"
        assert data["id"] is not None
        assert len(data["steps"]) == 2
    
    def test_update_recipe_unauthenticated(self, client, sample_recipe_data):
        """Test updating recipe without authentication."""
        # Create a recipe with auth
        client.cookies.set("session_token", "authenticated")
        recipe_schema = schemas.RecipeCreate(**sample_recipe_data)
        create_response = client.post("/api/recipes", json=recipe_schema.model_dump())
        recipe_id = create_response.json()["id"]
        
        # Try to update without auth
        client.cookies.clear()
        updated_data = sample_recipe_data.copy()
        updated_data["title"] = "Updated Title"
        response = client.put(f"/api/recipes/{recipe_id}", json=updated_data)
        assert response.status_code == 401
    
    def test_update_recipe_authenticated(self, authenticated_client, sample_recipe_data):
        """Test updating recipe with authentication."""
        # Create a recipe
        recipe_schema = schemas.RecipeCreate(**sample_recipe_data)
        create_response = authenticated_client.post("/api/recipes", json=recipe_schema.model_dump())
        recipe_id = create_response.json()["id"]
        
        # Update it
        updated_data = sample_recipe_data.copy()
        updated_data["title"] = "Updated Title"
        response = authenticated_client.put(f"/api/recipes/{recipe_id}", json=updated_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Updated Title"
    
    def test_update_recipe_not_exists(self, authenticated_client, sample_recipe_data):
        """Test updating a non-existent recipe."""
        response = authenticated_client.put("/api/recipes/999", json=sample_recipe_data)
        assert response.status_code == 404
    
    def test_delete_recipe_unauthenticated(self, client, sample_recipe_data):
        """Test deleting recipe without authentication."""
        # Create a recipe with auth
        client.cookies.set("session_token", "authenticated")
        recipe_schema = schemas.RecipeCreate(**sample_recipe_data)
        create_response = client.post("/api/recipes", json=recipe_schema.model_dump())
        recipe_id = create_response.json()["id"]
        
        # Try to delete without auth
        client.cookies.clear()
        response = client.delete(f"/api/recipes/{recipe_id}")
        assert response.status_code == 401
    
    def test_delete_recipe_authenticated(self, authenticated_client, sample_recipe_data):
        """Test deleting recipe with authentication."""
        # Create a recipe
        recipe_schema = schemas.RecipeCreate(**sample_recipe_data)
        create_response = authenticated_client.post("/api/recipes", json=recipe_schema.model_dump())
        recipe_id = create_response.json()["id"]
        
        # Delete it
        response = authenticated_client.delete(f"/api/recipes/{recipe_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "success"
    
    def test_delete_recipe_not_exists(self, authenticated_client):
        """Test deleting a non-existent recipe."""
        response = authenticated_client.delete("/api/recipes/999")
        assert response.status_code == 404


class TestScrapeAPIEndpoint:
    """Tests for scrape API endpoint."""
    
    @patch('main.scraper.scrape_recipe')
    def test_scrape_url_valid(self, mock_scrape, client):
        """Test scraping a valid URL."""
        mock_scrape.return_value = {
            "title": "Scraped Recipe",
            "total_time_minutes": 20,
            "base_servings": 4,
            "steps": []
        }
        
        response = client.post("/api/scrape", json={"url": "http://example.com/recipe"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Scraped Recipe"
        assert data["total_time_minutes"] == 20
    
    def test_scrape_url_missing(self, client):
        """Test scraping without URL."""
        response = client.post("/api/scrape", json={})
        assert response.status_code == 400
        assert "URL is required" in response.json()["detail"]
    
    @patch('main.scraper.scrape_recipe')
    def test_scrape_url_error(self, mock_scrape, client):
        """Test scraping with an error."""
        mock_scrape.side_effect = Exception("Scraping failed")
        
        response = client.post("/api/scrape", json={"url": "http://example.com/invalid"})
        assert response.status_code == 400
        assert "Scraping failed" in response.json()["detail"]


class TestUploadAPIEndpoint:
    """Tests for upload API endpoint."""
    
    def test_upload_image(self, client):
        """Test image upload."""
        files = {"file": ("test.jpg", b"fake image content", "image/jpeg")}
        response = client.post("/api/upload", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert "filename" in data
        assert data["filename"].endswith(".jpg")


class TestConversionsEndpoint:
    """Tests for conversions endpoint."""
    
    def test_get_conversions(self, client):
        """Test getting ingredient conversions."""
        response = client.get("/api/conversions")
        assert response.status_code == 200
        
        # After startup event, should have conversion data
        # Note: startup events may not run in tests without special handling
