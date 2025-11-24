#!/usr/bin/env python3
"""
Integration tests for Ollama LLM functionality.
These tests require Ollama to be running locally with a model installed.

Run with: pytest tests/test_ollama_integration.py -v -s
Or directly: python3 tests/test_ollama_integration.py
"""

import requests
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.llm_fallback import extract_recipe_with_llm, get_llm_config

# Import pytest only if available (for pytest-based test runs)
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Create a dummy pytest.skip for standalone execution
    class pytest:
        @staticmethod
        def skip(msg):
            pass
        class fixture:
            def __init__(self, *args, **kwargs):
                pass
            def __call__(self, func):
                return func


def check_ollama_available():
    """Check if Ollama service is running and has models."""
    try:
        config = get_llm_config()
        response = requests.get(f"{config['base_url']}/api/tags", timeout=5)
        if response.status_code != 200:
            return False, "Ollama service not responding"
        
        data = response.json()
        models = data.get("models", [])
        if not models:
            return False, "No models installed in Ollama"
        
        # Check if configured model is available
        model_names = [m["name"] for m in models]
        configured_model = config["model"]
        # Check for exact match or with :latest suffix
        if configured_model not in model_names and f"{configured_model}:latest" not in model_names:
            return False, f"Configured model '{configured_model}' not found. Available: {', '.join(model_names)}"
        
        return True, "Ollama is ready"
    except Exception as e:
        return False, f"Error connecting to Ollama: {e}"


class TestOllamaIntegration:
    """Integration tests for Ollama LLM service."""
    
    @pytest.fixture(autouse=True)
    def check_ollama(self):
        """Skip tests if Ollama is not available."""
        available, message = check_ollama_available()
        if not available:
            pytest.skip(f"Ollama not available: {message}")
    
    def test_ollama_connection(self):
        """Test that we can connect to Ollama."""
        config = get_llm_config()
        response = requests.get(f"{config['base_url']}/api/tags")
        assert response.status_code == 200
        
        data = response.json()
        assert "models" in data
        assert len(data["models"]) > 0
        print(f"\n✓ Connected to Ollama at {config['base_url']}")
        print(f"  Available models: {[m['name'] for m in data['models']]}")
    
    def test_simple_recipe_extraction(self):
        """Test extracting a simple recipe with Ollama."""
        html = """
        <html>
        <body>
            <h1>Simple Pasta</h1>
            <p>Total time: 20 minutes | Serves: 2</p>
            <h2>Ingredients:</h2>
            <ul>
                <li>200g pasta</li>
                <li>2 tablespoons olive oil</li>
                <li>2 cloves garlic</li>
                <li>Salt to taste</li>
            </ul>
            <h2>Instructions:</h2>
            <ol>
                <li>Boil water and cook pasta for 10 minutes.</li>
                <li>Heat olive oil and sauté garlic for 2 minutes.</li>
                <li>Drain pasta and toss with garlic oil.</li>
                <li>Season with salt and serve.</li>
            </ol>
        </body>
        </html>
        """
        
        result = extract_recipe_with_llm(html, "http://example.com/pasta")
        
        assert result is not None, "Failed to extract recipe"
        assert result["title"], "No title extracted"
        assert result["steps"], "No steps extracted"
        
        print(f"\n✓ Extracted recipe: {result['title']}")
        print(f"  Total time: {result['total_time_minutes']} minutes")
        print(f"  Servings: {result['base_servings']}")
        print(f"  Steps: {len(result['steps'])}")
        
        # Verify steps have ingredients
        total_ingredients = sum(len(step["ingredients"]) for step in result["steps"])
        print(f"  Total ingredients distributed: {total_ingredients}")
    
    def test_complex_recipe_extraction(self):
        """Test extracting a more complex recipe."""
        html = """
        <html>
        <body>
            <article>
                <h1>Chocolate Chip Cookies</h1>
                <div class="recipe-meta">
                    <span>Prep: 15 min</span>
                    <span>Cook: 12 min</span>
                    <span>Total: 27 min</span>
                    <span>Yield: 24 cookies</span>
                </div>
                
                <div class="ingredients">
                    <h2>What You'll Need:</h2>
                    <ul>
                        <li>2 1/4 cups all-purpose flour</li>
                        <li>1 teaspoon baking soda</li>
                        <li>1 teaspoon salt</li>
                        <li>1 cup (2 sticks) butter, softened</li>
                        <li>3/4 cup granulated sugar</li>
                        <li>3/4 cup packed brown sugar</li>
                        <li>2 large eggs</li>
                        <li>2 teaspoons vanilla extract</li>
                        <li>2 cups chocolate chips</li>
                    </ul>
                </div>
                
                <div class="instructions">
                    <h2>How to Make It:</h2>
                    <ol>
                        <li>Preheat your oven to 375°F (190°C).</li>
                        <li>In a small bowl, combine flour, baking soda, and salt. Set aside.</li>
                        <li>In a large bowl, beat butter, granulated sugar, and brown sugar until creamy.</li>
                        <li>Add eggs and vanilla extract to the butter mixture. Beat well.</li>
                        <li>Gradually blend in the flour mixture.</li>
                        <li>Stir in chocolate chips.</li>
                        <li>Drop rounded tablespoons of dough onto ungreased baking sheets.</li>
                        <li>Bake for 9 to 11 minutes or until golden brown.</li>
                        <li>Cool on baking sheets for 2 minutes, then transfer to wire racks.</li>
                    </ol>
                </div>
            </article>
        </body>
        </html>
        """
        
        result = extract_recipe_with_llm(html, "http://example.com/cookies")
        
        assert result is not None, "Failed to extract recipe"
        assert result["title"], "No title extracted"
        assert "cookie" in result["title"].lower() or "chocolate" in result["title"].lower(), \
            f"Title doesn't match recipe: {result['title']}"
        
        print(f"\n✓ Extracted complex recipe: {result['title']}")
        print(f"  Total time: {result['total_time_minutes']} minutes")
        print(f"  Servings: {result['base_servings']}")
        print(f"  Steps: {len(result['steps'])}")
        
        # Print step details
        for i, step in enumerate(result["steps"][:3], 1):
            print(f"  Step {i}: {step['action'][:60]}...")
            print(f"    Ingredients: {len(step['ingredients'])}")
    
    def test_recipe_with_mixed_format(self):
        """Test recipe with non-standard format."""
        html = """
        <html>
        <body>
            <h1>Quick Guacamole</h1>
            <p>This takes just 5 minutes to make and serves 4 people.</p>
            
            <p><strong>You will need:</strong> 3 ripe avocados, 1 lime (juiced), 
            1/2 teaspoon salt, 1/2 cup diced onion, 3 tablespoons chopped cilantro, 
            2 roma tomatoes (diced), 1 teaspoon minced garlic, and a pinch of cayenne pepper.</p>
            
            <p><strong>Directions:</strong> Mash the avocados in a bowl. Mix in lime juice 
            and salt. Add onion, cilantro, tomatoes, and garlic. Stir well. 
            Add cayenne pepper to taste. Serve immediately.</p>
        </body>
        </html>
        """
        
        result = extract_recipe_with_llm(html, "http://example.com/guacamole")
        
        assert result is not None, "Failed to extract recipe"
        assert result["title"], "No title extracted"
        assert result["steps"], "No steps extracted"
        
        print(f"\n✓ Extracted non-standard recipe: {result['title']}")
        print(f"  Total time: {result['total_time_minutes']} minutes")
        print(f"  Servings: {result['base_servings']}")
        print(f"  Steps: {len(result['steps'])}")
    
    def test_recipe_not_found(self):
        """Test handling of non-recipe content."""
        html = """
        <html>
        <body>
            <h1>About Our Kitchen</h1>
            <p>Welcome to our cooking blog! We share recipes every week.</p>
            <p>Subscribe to our newsletter for updates.</p>
            <p>Contact us at info@example.com</p>
        </body>
        </html>
        """
        
        result = extract_recipe_with_llm(html, "http://example.com/about")
        
        # The LLM might return None or a minimal result
        # We just want to ensure it doesn't crash
        print(f"\n✓ Handled non-recipe content: {result}")
    
    def test_extraction_timeout(self):
        """Test that extraction respects timeout settings."""
        import time
        
        # Very large HTML to potentially trigger timeout
        html = "<html><body>" + ("Lorem ipsum dolor sit amet. " * 10000) + "</body></html>"
        
        start_time = time.time()
        result = extract_recipe_with_llm(html, "http://example.com/long")
        elapsed_time = time.time() - start_time
        
        config = get_llm_config()
        timeout = config["timeout"]
        
        # Should complete within timeout + buffer
        assert elapsed_time < timeout + 10, f"Took too long: {elapsed_time}s (timeout: {timeout}s)"
        print(f"\n✓ Extraction completed in {elapsed_time:.2f}s (timeout: {timeout}s)")
    
    def test_real_website_extraction(self):
        """Test extracting a recipe from a real website that's not in recipe-scrapers."""
        # Use a simple recipe site that's unlikely to be in recipe-scrapers
        test_url = "https://nadialim.com/corn-bread/"
        
        try:
            print(f"\n  Fetching real webpage: {test_url}")
            response = requests.get(test_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; RecipeBot/1.0)'
            })
            response.raise_for_status()
            html = response.text
            
            print(f"  Downloaded {len(html)} bytes")
            print("  Extracting with LLM...")
            
            result = extract_recipe_with_llm(html, test_url)
            
            assert result is not None, "Failed to extract recipe from real website"
            assert result["title"], "No title extracted"
            assert len(result["steps"]) > 0, "No steps extracted"
            
            print(f"\n✓ Successfully extracted real recipe: {result['title']}")
            print(f"  Total time: {result['total_time_minutes']} minutes")
            print(f"  Servings: {result['base_servings']}")
            print(f"  Steps: {len(result['steps'])}")
            
            # Verify ingredient distribution
            steps_with_ingredients = [s for s in result["steps"] if s["ingredients"]]
            total_ingredients = sum(len(s["ingredients"]) for s in result["steps"])
            print(f"  Steps with ingredients: {len(steps_with_ingredients)}/{len(result['steps'])}")
            print(f"  Total ingredients: {total_ingredients}")
            
            # Verify time extraction
            steps_with_time = [s for s in result["steps"] if s["time_minutes"] is not None]
            print(f"  Steps with time info: {len(steps_with_time)}")
            
            # Print first few steps for verification
            print("\n  First 3 steps:")
            for i, step in enumerate(result["steps"][:3], 1):
                print(f"    {i}. {step['action'][:60]}{'...' if len(step['action']) > 60 else ''}")
                print(f"       Time: {step['time_minutes']} min, Ingredients: {len(step['ingredients'])}")
            
            # Assert basic quality checks
            assert total_ingredients > 0, "No ingredients were distributed to steps"
            
        except requests.RequestException as e:
            pytest.skip(f"Could not fetch real website: {e}")
        except Exception as e:
            print(f"\n  Error details: {e}")
            raise


def manual_test():
    """Run tests manually without pytest."""
    print("=" * 70)
    print("Ollama Integration Tests")
    print("=" * 70)
    print()
    
    # Check Ollama availability
    available, message = check_ollama_available()
    print(f"Checking Ollama service: {message}")
    
    if not available:
        print("\n❌ Cannot run tests - Ollama is not available")
        print("\nTo fix this:")
        print("  1. Start Ollama: ollama serve")
        print("  2. Pull a model: ollama pull llama3.2")
        print("  3. Re-run this test")
        sys.exit(1)
    
    print("✓ Ollama is ready\n")
    print("=" * 70)
    
    # Create test instance
    test = TestOllamaIntegration()
    
    try:
        print("\n1. Testing Ollama Connection")
        print("-" * 70)
        test.test_ollama_connection()
        
        print("\n2. Testing Simple Recipe Extraction")
        print("-" * 70)
        test.test_simple_recipe_extraction()
        
        print("\n3. Testing Complex Recipe Extraction")
        print("-" * 70)
        test.test_complex_recipe_extraction()
        
        print("\n4. Testing Mixed Format Recipe")
        print("-" * 70)
        test.test_recipe_with_mixed_format()
        
        print("\n5. Testing Non-Recipe Content")
        print("-" * 70)
        test.test_recipe_not_found()
        
        print("\n6. Testing Real Website Extraction")
        print("-" * 70)
        test.test_real_website_extraction()
        
        print("\n" + "=" * 70)
        print("All tests passed! ✓")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    manual_test()
