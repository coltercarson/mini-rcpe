import pytest
from unittest.mock import patch, MagicMock

from app.scraper import parse_ingredient, scrape_recipe, validate_url


class TestValidateUrl:
    """Tests for validate_url function."""
    
    def test_valid_http_url(self):
        """Test that valid HTTP URLs pass validation."""
        validate_url("http://example.com/recipe")
        # Should not raise exception
    
    def test_valid_https_url(self):
        """Test that valid HTTPS URLs pass validation."""
        validate_url("https://example.com/recipe")
        # Should not raise exception
    
    def test_invalid_scheme(self):
        """Test that non-HTTP(S) schemes are rejected."""
        with pytest.raises(Exception) as exc_info:
            validate_url("file:///etc/passwd")
        assert "HTTP and HTTPS" in str(exc_info.value)
    
    def test_localhost_blocked(self):
        """Test that localhost URLs are blocked."""
        with pytest.raises(Exception) as exc_info:
            validate_url("http://localhost:8080/recipe")
        assert "localhost" in str(exc_info.value).lower()
    
    def test_private_ip_blocked(self):
        """Test that private IP addresses are blocked."""
        with pytest.raises(Exception) as exc_info:
            validate_url("http://192.168.1.1/recipe")
        assert "private" in str(exc_info.value).lower()
    
    def test_loopback_ip_blocked(self):
        """Test that loopback IP addresses are blocked."""
        with pytest.raises(Exception) as exc_info:
            validate_url("http://127.0.0.1/recipe")
        assert "private" in str(exc_info.value).lower()
    
    def test_no_hostname(self):
        """Test that URLs without hostname are rejected."""
        with pytest.raises(Exception) as exc_info:
            validate_url("http:///recipe")
        assert "hostname" in str(exc_info.value).lower()


class TestParseIngredient:
    """Tests for parse_ingredient function."""
    
    def test_parse_ingredient_with_amount_and_unit(self):
        """Test parsing ingredient with amount and unit."""
        result = parse_ingredient("2 cups flour")
        assert result["ingredient_name"] == "flour"
        assert result["amount"] == 2.0
        assert result["unit"] == "cups"
    
    def test_parse_ingredient_with_fraction(self):
        """Test parsing ingredient with fraction."""
        result = parse_ingredient("1/2 teaspoon salt")
        assert result["ingredient_name"] == "salt"
        assert result["amount"] == 0.5
        assert result["unit"] == "teaspoon"
    
    def test_parse_ingredient_without_unit(self):
        """Test parsing ingredient without unit."""
        result = parse_ingredient("3 eggs")
        assert result["ingredient_name"] == "eggs"
        assert result["amount"] == 3.0
        assert result["unit"] is None
    
    def test_parse_ingredient_without_amount(self):
        """Test parsing ingredient without amount."""
        result = parse_ingredient("salt to taste")
        assert result["ingredient_name"] == "salt to taste"
        assert result["amount"] is None
        assert result["unit"] is None
    
    def test_parse_ingredient_with_tablespoon(self):
        """Test parsing ingredient with tablespoon."""
        result = parse_ingredient("3 tablespoons butter")
        assert result["ingredient_name"] == "butter"
        assert result["amount"] == 3.0
        assert result["unit"] == "tablespoons"
    
    def test_parse_ingredient_with_tbsp_abbreviation(self):
        """Test parsing ingredient with tbsp abbreviation."""
        result = parse_ingredient("2 tbsp olive oil")
        assert result["ingredient_name"] == "olive oil"
        assert result["amount"] == 2.0
        assert result["unit"] == "tbsp"
    
    def test_parse_ingredient_with_grams(self):
        """Test parsing ingredient with grams."""
        result = parse_ingredient("500g sugar")
        assert result["ingredient_name"] == "sugar"
        assert result["amount"] == 500.0
        assert result["unit"] == "g"
    
    def test_parse_ingredient_complex_name(self):
        """Test parsing ingredient with complex name."""
        result = parse_ingredient("2 cups all-purpose flour")
        assert result["ingredient_name"] == "all-purpose flour"
        assert result["amount"] == 2.0
        assert result["unit"] == "cups"
    
    def test_parse_ingredient_with_decimal(self):
        """Test parsing ingredient with decimal amount."""
        result = parse_ingredient("1.5 cups milk")
        assert result["ingredient_name"] == "milk"
        assert result["amount"] == 1.5
        assert result["unit"] == "cups"
    
    def test_parse_ingredient_plain_text(self):
        """Test parsing plain ingredient text without measurements."""
        result = parse_ingredient("fresh parsley for garnish")
        assert result["ingredient_name"] == "fresh parsley for garnish"
        assert result["amount"] is None
        assert result["unit"] is None


class TestScrapeRecipe:
    """Tests for scrape_recipe function."""
    
    @patch('app.scraper.requests.get')
    @patch('app.scraper.scrape_html')
    def test_scrape_recipe_basic(self, mock_scrape_html, mock_requests_get):
        """Test basic recipe scraping."""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.text = "<html>Recipe HTML</html>"
        mock_requests_get.return_value = mock_response
        
        # Mock the recipe scraper
        mock_scraper = MagicMock()
        mock_scraper.title.return_value = "Test Recipe"
        mock_scraper.total_time.return_value = 30
        mock_scraper.yields.return_value = "4 servings"
        mock_scraper.image.return_value = "http://example.com/image.jpg"
        mock_scraper.ingredients.return_value = [
            "2 cups flour",
            "1 cup water"
        ]
        mock_scraper.instructions.return_value = "Mix ingredients.\nBake for 20 minutes."
        mock_scrape_html.return_value = mock_scraper
        
        result = scrape_recipe("http://example.com/recipe")
        
        assert result["title"] == "Test Recipe"
        assert result["total_time_minutes"] == 30
        assert result["base_servings"] == 4
        assert result["source_url"] == "http://example.com/recipe"
        assert len(result["steps"]) == 2
        assert result["steps"][0]["step_number"] == 1
        assert result["steps"][0]["action"] == "Mix ingredients."
    
    @patch('app.scraper.requests.get')
    @patch('app.scraper.scrape_html')
    def test_scrape_recipe_with_ingredient_distribution(self, mock_scrape_html, mock_requests_get):
        """Test recipe scraping with ingredient distribution to steps."""
        mock_response = MagicMock()
        mock_response.text = "<html>Recipe HTML</html>"
        mock_requests_get.return_value = mock_response
        
        mock_scraper = MagicMock()
        mock_scraper.title.return_value = "Pancakes"
        mock_scraper.total_time.return_value = 20
        mock_scraper.yields.return_value = "6"
        mock_scraper.image.return_value = None
        mock_scraper.ingredients.return_value = [
            "2 cups flour",
            "2 eggs",
            "1 cup milk"
        ]
        mock_scraper.instructions.return_value = "Mix flour and eggs.\nAdd milk and stir.\nCook on griddle."
        mock_scrape_html.return_value = mock_scraper
        
        result = scrape_recipe("http://example.com/pancakes")
        
        assert result["title"] == "Pancakes"
        assert result["base_servings"] == 6
        assert len(result["steps"]) == 3
        
        # Check ingredient distribution
        # Step 1 should have flour and eggs (mentioned in "Mix flour and eggs")
        step1_ingredient_names = [ing["ingredient_name"] for ing in result["steps"][0]["ingredients"]]
        assert "flour" in step1_ingredient_names
        assert "eggs" in step1_ingredient_names
        
        # Step 2 should have milk (mentioned in "Add milk")
        step2_ingredient_names = [ing["ingredient_name"] for ing in result["steps"][1]["ingredients"]]
        assert "milk" in step2_ingredient_names
    
    @patch('app.scraper.requests.get')
    @patch('app.scraper.scrape_html')
    def test_scrape_recipe_no_steps(self, mock_scrape_html, mock_requests_get):
        """Test recipe scraping when no instructions are provided."""
        mock_response = MagicMock()
        mock_response.text = "<html>Recipe HTML</html>"
        mock_requests_get.return_value = mock_response
        
        mock_scraper = MagicMock()
        mock_scraper.title.return_value = "Simple Recipe"
        mock_scraper.total_time.return_value = 10
        mock_scraper.yields.return_value = "2"
        mock_scraper.image.return_value = None
        mock_scraper.ingredients.return_value = ["1 cup sugar"]
        mock_scraper.instructions.return_value = ""
        mock_scrape_html.return_value = mock_scraper
        
        result = scrape_recipe("http://example.com/simple")
        
        # Should create a dummy step with all ingredients
        assert len(result["steps"]) == 1
        assert result["steps"][0]["action"] == "Prepare ingredients"
        assert len(result["steps"][0]["ingredients"]) == 1
    
    @patch('app.scraper.requests.get')
    @patch('app.scraper.scrape_html')
    def test_scrape_recipe_yields_parsing(self, mock_scrape_html, mock_requests_get):
        """Test parsing different yield formats."""
        mock_response = MagicMock()
        mock_response.text = "<html>Recipe HTML</html>"
        mock_requests_get.return_value = mock_response
        
        mock_scraper = MagicMock()
        mock_scraper.title.return_value = "Test"
        mock_scraper.total_time.return_value = 10
        mock_scraper.image.return_value = None
        mock_scraper.ingredients.return_value = []
        mock_scraper.instructions.return_value = "Cook."
        mock_scrape_html.return_value = mock_scraper
        
        # Test different yield formats
        test_cases = [
            ("Makes 12 servings", 12),
            ("8 portions", 8),
            ("Serves 4-6", 4),
            (None, 1),  # Default case
        ]
        
        for yields_text, expected_servings in test_cases:
            mock_scraper.yields.return_value = yields_text
            result = scrape_recipe("http://example.com/test")
            assert result["base_servings"] == expected_servings
    
    @patch.dict('os.environ', {'LLM_ENABLED': 'true'})
    @patch('app.scraper.LLM_AVAILABLE', True)
    @patch('app.scraper.extract_recipe_with_llm')
    @patch('app.scraper.requests.get')
    @patch('app.scraper.scrape_html')
    def test_llm_fallback_on_scraper_failure(self, mock_scrape_html, mock_requests_get, mock_llm):
        """Test that LLM fallback is used when recipe-scrapers fails."""
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.text = "<html>Recipe content</html>"
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response
        
        # Mock recipe-scrapers to fail
        mock_scrape_html.side_effect = Exception("Unsupported website")
        
        # Mock LLM to succeed
        mock_llm.return_value = {
            "title": "LLM Extracted Recipe",
            "total_time_minutes": 45,
            "base_servings": 6,
            "image_filename": None,
            "steps": [{"step_number": 1, "action": "Test", "time_minutes": None, "ingredients": []}]
        }
        
        result = scrape_recipe("http://example.com/unsupported")
        
        # Verify LLM was called
        assert mock_llm.called
        assert result["title"] == "LLM Extracted Recipe"
        assert result["base_servings"] == 6
    
    @patch.dict('os.environ', {'LLM_ENABLED': 'false'})
    @patch('app.scraper.requests.get')
    @patch('app.scraper.scrape_html')
    def test_no_llm_fallback_when_disabled(self, mock_scrape_html, mock_requests_get):
        """Test that LLM fallback is not used when disabled."""
        mock_response = MagicMock()
        mock_response.text = "<html>Recipe content</html>"
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response
        
        # Mock recipe-scrapers to fail
        mock_scrape_html.side_effect = Exception("Unsupported website")
        
        # Should raise exception without trying LLM
        with pytest.raises(Exception) as exc_info:
            scrape_recipe("http://example.com/unsupported")
        
        assert "Recipe extraction failed" in str(exc_info.value)
