#!/usr/bin/env python3
"""
Manual test script for LLM fallback functionality.
Run this to test the LLM extraction without needing Ollama installed.
"""

import sys
import os

# Add parent directory to path so we can import app module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.llm_fallback import clean_html_to_text, parse_llm_response
import json

def test_html_cleaning():
    """Test HTML cleaning functionality."""
    print("Testing HTML cleaning...")
    
    html = """
    <html>
    <head>
        <script>alert('test');</script>
        <style>.test { color: red; }</style>
    </head>
    <body>
        <h1>Chocolate Chip Cookies</h1>
        <p>Prep time: 15 minutes | Cook time: 10 minutes | Serves: 24 cookies</p>
        <h2>Ingredients:</h2>
        <ul>
            <li>2 1/4 cups all-purpose flour</li>
            <li>1 tsp baking soda</li>
            <li>1 cup butter, softened</li>
            <li>3/4 cup granulated sugar</li>
            <li>2 large eggs</li>
            <li>2 cups chocolate chips</li>
        </ul>
        <h2>Instructions:</h2>
        <ol>
            <li>Preheat oven to 375°F.</li>
            <li>Mix flour and baking soda in a bowl.</li>
            <li>In another bowl, beat butter and sugar until creamy.</li>
            <li>Add eggs to butter mixture and beat well.</li>
            <li>Gradually mix in flour mixture.</li>
            <li>Stir in chocolate chips.</li>
            <li>Drop spoonfuls onto baking sheet.</li>
            <li>Bake for 9-11 minutes until golden.</li>
        </ol>
    </body>
    </html>
    """
    
    clean_text = clean_html_to_text(html)
    
    # Verify cleaning worked
    assert 'alert' not in clean_text
    assert 'style' not in clean_text
    assert 'Chocolate Chip Cookies' in clean_text
    assert 'flour' in clean_text
    
    print("✓ HTML cleaning works correctly")
    print(f"  Clean text length: {len(clean_text)} characters")
    print(f"  Sample: {clean_text[:100]}...")
    print()

def test_llm_response_parsing():
    """Test LLM response parsing."""
    print("Testing LLM response parsing...")
    
    # Simulate an LLM response
    llm_response = {
        "title": "Chocolate Chip Cookies",
        "total_time_minutes": 25,
        "base_servings": 24,
        "ingredients": [
            "2 1/4 cups all-purpose flour",
            "1 tsp baking soda",
            "1 cup butter, softened",
            "3/4 cup granulated sugar",
            "2 large eggs",
            "2 cups chocolate chips"
        ],
        "instructions": """1. Preheat oven to 375°F.
2. Mix flour and baking soda in a bowl.
3. In another bowl, beat butter and sugar until creamy.
4. Add eggs to butter mixture and beat well.
5. Gradually mix in flour mixture.
6. Stir in chocolate chips.
7. Drop spoonfuls onto baking sheet.
8. Bake for 9-11 minutes until golden."""
    }
    
    llm_output = json.dumps(llm_response)
    result = parse_llm_response(llm_output)
    
    # Verify parsing worked
    assert result is not None
    assert result["title"] == "Chocolate Chip Cookies"
    assert result["total_time_minutes"] == 25
    assert result["base_servings"] == 24
    assert len(result["steps"]) == 8
    
    # Check first step
    first_step = result["steps"][0]
    assert first_step["step_number"] == 1
    assert "Preheat oven" in first_step["action"]
    assert not first_step["action"].startswith("1.")  # Step number should be removed
    
    # Check that ingredients were parsed
    total_ingredients = sum(len(step["ingredients"]) for step in result["steps"])
    assert total_ingredients == 6  # All ingredients should be distributed
    
    print("✓ LLM response parsing works correctly")
    print(f"  Recipe: {result['title']}")
    print(f"  Steps: {len(result['steps'])}")
    print(f"  Total ingredients: {total_ingredients}")
    
    # Show first step with ingredients
    first_step_with_ingredients = next((s for s in result["steps"] if s["ingredients"]), None)
    if first_step_with_ingredients:
        print(f"  Example step with ingredients:")
        print(f"    Step {first_step_with_ingredients['step_number']}: {first_step_with_ingredients['action'][:50]}...")
        for ing in first_step_with_ingredients["ingredients"][:2]:
            print(f"      - {ing['ingredient_name']} ({ing['amount']} {ing['unit'] or ''})")
    print()

def test_edge_cases():
    """Test edge cases in response parsing."""
    print("Testing edge cases...")
    
    # Test null response (recipe not found)
    result = parse_llm_response("null")
    assert result is None
    print("✓ Handles null response correctly")
    
    # Test invalid JSON
    result = parse_llm_response("This is not JSON")
    assert result is None
    print("✓ Handles invalid JSON correctly")
    
    # Test JSON with extra text
    llm_output = 'Here is the recipe: {"title": "Test", "total_time_minutes": 10, "base_servings": 1, "ingredients": ["salt"], "instructions": "Cook it."} Hope that helps!'
    result = parse_llm_response(llm_output)
    assert result is not None
    assert result["title"] == "Test"
    print("✓ Extracts JSON from text with extra content")
    
    # Test recipe with no instructions
    llm_output = json.dumps({
        "title": "Simple Recipe",
        "total_time_minutes": None,
        "base_servings": 1,
        "ingredients": ["1 cup water"],
        "instructions": ""
    })
    result = parse_llm_response(llm_output)
    assert result is not None
    assert result["title"] == "Simple Recipe"
    print("✓ Handles recipe with no instructions")
    print()

def main():
    """Run all tests."""
    print("=" * 60)
    print("Manual Test Suite for LLM Fallback")
    print("=" * 60)
    print()
    
    try:
        test_html_cleaning()
        test_llm_response_parsing()
        test_edge_cases()
        
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        print()
        print("Note: This tests the LLM response parsing logic.")
        print("To test the full LLM integration:")
        print("  1. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print("  2. Pull a model: ollama pull llama3.2")
        print("  3. Start Ollama: ollama serve")
        print("  4. Set LLM_ENABLED=true in your .env file")
        print("  5. Test with an unsupported recipe URL in the app")
        print()
        
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
