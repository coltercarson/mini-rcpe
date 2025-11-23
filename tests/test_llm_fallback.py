import pytest
from unittest.mock import patch, MagicMock
import json
import requests

from llm_fallback import (
    clean_html_to_text,
    extract_recipe_with_llm,
    parse_llm_response,
    get_llm_config
)


class TestCleanHtmlToText:
    """Tests for clean_html_to_text function."""
    
    def test_remove_scripts(self):
        """Test that script tags are removed."""
        html = '<html><script>alert("test");</script><p>Content</p></html>'
        result = clean_html_to_text(html)
        assert 'alert' not in result
        assert 'Content' in result
    
    def test_remove_styles(self):
        """Test that style tags are removed."""
        html = '<html><style>.class { color: red; }</style><p>Content</p></html>'
        result = clean_html_to_text(html)
        assert 'color:' not in result
        assert 'Content' in result
    
    def test_remove_html_tags(self):
        """Test that HTML tags are removed."""
        html = '<div><p>Hello <strong>world</strong></p></div>'
        result = clean_html_to_text(html)
        assert '<' not in result
        assert '>' not in result
        assert 'Hello world' in result
    
    def test_decode_html_entities(self):
        """Test that HTML entities are decoded."""
        html = '<p>Tom&amp;Jerry&nbsp;5&lt;10</p>'
        result = clean_html_to_text(html)
        assert 'Tom&Jerry' in result
        assert '5<10' in result
    
    def test_clean_whitespace(self):
        """Test that excessive whitespace is cleaned up."""
        html = '<p>Word1    \n\n   Word2</p>'
        result = clean_html_to_text(html)
        assert '    ' not in result
        assert 'Word1 Word2' in result.replace('\n', ' ')


class TestParseLlmResponse:
    """Tests for parse_llm_response function."""
    
    def test_parse_valid_json(self):
        """Test parsing a valid JSON response."""
        llm_output = json.dumps({
            "title": "Test Recipe",
            "total_time_minutes": 30,
            "base_servings": 4,
            "ingredients": ["2 cups flour", "1 cup water"],
            "instructions": "Step 1. Mix ingredients.\nStep 2. Bake."
        })
        
        result = parse_llm_response(llm_output)
        
        assert result is not None
        assert result["title"] == "Test Recipe"
        assert result["total_time_minutes"] == 30
        assert result["base_servings"] == 4
        assert len(result["steps"]) == 2
        assert result["steps"][0]["step_number"] == 1
        assert "Mix ingredients" in result["steps"][0]["action"]
    
    def test_parse_json_with_extra_text(self):
        """Test parsing JSON when LLM adds extra text."""
        llm_output = 'Here is the recipe:\n{"title": "Test", "total_time_minutes": 20, "base_servings": 2, "ingredients": ["salt"], "instructions": "Cook it."}\nDone!'
        
        result = parse_llm_response(llm_output)
        
        assert result is not None
        assert result["title"] == "Test"
    
    def test_parse_null_response(self):
        """Test parsing when LLM returns null."""
        llm_output = "null"
        result = parse_llm_response(llm_output)
        assert result is None
    
    def test_parse_invalid_json(self):
        """Test parsing invalid JSON."""
        llm_output = "This is not JSON"
        result = parse_llm_response(llm_output)
        assert result is None
    
    def test_remove_step_numbers(self):
        """Test that step numbers are removed from instructions."""
        llm_output = json.dumps({
            "title": "Test",
            "total_time_minutes": 10,
            "base_servings": 1,
            "ingredients": ["flour"],
            "instructions": "1. First step\n2) Second step\nStep 3: Third step"
        })
        
        result = parse_llm_response(llm_output)
        
        assert result is not None
        assert "First step" in result["steps"][0]["action"]
        assert "Second step" in result["steps"][1]["action"]
        assert "Third step" in result["steps"][2]["action"]
        # Ensure step numbers are removed
        assert not result["steps"][0]["action"].startswith("1.")
    
    def test_ingredient_distribution(self):
        """Test that ingredients are distributed to steps."""
        llm_output = json.dumps({
            "title": "Pancakes",
            "total_time_minutes": 20,
            "base_servings": 4,
            "ingredients": ["2 cups flour", "2 eggs", "1 cup milk"],
            "instructions": "Mix flour and eggs.\nAdd milk and stir."
        })
        
        result = parse_llm_response(llm_output)
        
        assert result is not None
        # Step 1 should have flour and eggs
        step1_names = [ing["ingredient_name"] for ing in result["steps"][0]["ingredients"]]
        assert any("flour" in name.lower() for name in step1_names)
        assert any("eggs" in name.lower() for name in step1_names)
        
        # Step 2 should have milk
        step2_names = [ing["ingredient_name"] for ing in result["steps"][1]["ingredients"]]
        assert any("milk" in name.lower() for name in step2_names)


class TestExtractRecipeWithLlm:
    """Tests for extract_recipe_with_llm function."""
    
    @patch.dict('os.environ', {'LLM_BASE_URL': 'http://test:11434', 'LLM_MODEL': 'test-model'})
    @patch('llm_fallback.requests.post')
    def test_successful_extraction(self, mock_post):
        """Test successful recipe extraction."""
        # Mock Ollama API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": json.dumps({
                "title": "LLM Recipe",
                "total_time_minutes": 25,
                "base_servings": 3,
                "ingredients": ["1 cup sugar"],
                "instructions": "Make it sweet."
            })
        }
        mock_post.return_value = mock_response
        
        result = extract_recipe_with_llm("<html><p>Recipe content</p></html>", "http://example.com")
        
        assert result is not None
        assert result["title"] == "LLM Recipe"
        assert result["total_time_minutes"] == 25
        assert mock_post.called
    
    @patch.dict('os.environ', {'LLM_BASE_URL': 'http://test:11434'})
    @patch('llm_fallback.requests.post')
    def test_api_error(self, mock_post):
        """Test handling of API errors."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        result = extract_recipe_with_llm("<html>Content</html>", "http://example.com")
        
        assert result is None
    
    @patch.dict('os.environ', {'LLM_BASE_URL': 'http://test:11434'})
    @patch('llm_fallback.requests.post')
    def test_request_timeout(self, mock_post):
        """Test handling of request timeout."""
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        result = extract_recipe_with_llm("<html>Content</html>", "http://example.com")
        
        assert result is None
    
    @patch.dict('os.environ', {'LLM_BASE_URL': 'http://test:11434'})
    @patch('llm_fallback.requests.post')
    def test_html_cleaning(self, mock_post):
        """Test that HTML is cleaned before sending to LLM."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": json.dumps({
                "title": "Test",
                "total_time_minutes": 10,
                "base_servings": 1,
                "ingredients": [],
                "instructions": "Do it."
            })
        }
        mock_post.return_value = mock_response
        
        html = '<html><script>alert("test");</script><p>Recipe here</p></html>'
        result = extract_recipe_with_llm(html, "http://example.com")
        
        # Check that the prompt sent doesn't contain script tags
        call_args = mock_post.call_args
        prompt = call_args[1]['json']['prompt']
        assert 'alert' not in prompt
        assert 'Recipe here' in prompt


class TestGetLlmConfig:
    """Tests for get_llm_config function."""
    
    @patch.dict('os.environ', {})
    def test_default_config(self):
        """Test default configuration values."""
        config = get_llm_config()
        assert config["base_url"] == "http://localhost:11434"
        assert config["model"] == "llama3.2"
        assert config["timeout"] == 120
    
    @patch.dict('os.environ', {
        'LLM_BASE_URL': 'http://custom:8080',
        'LLM_MODEL': 'custom-model',
        'LLM_TIMEOUT': '60'
    })
    def test_custom_config(self):
        """Test custom configuration from environment."""
        config = get_llm_config()
        assert config["base_url"] == "http://custom:8080"
        assert config["model"] == "custom-model"
        assert config["timeout"] == 60
