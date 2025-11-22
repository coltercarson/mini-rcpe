from app import scraper
import json

# Test with multiple recipes
test_urls = [
    "https://www.bbcgoodfood.com/recipes/classic-pancakes",
    "https://www.bbcgoodfood.com/recipes/spaghetti-bolognese-recipe",
]

for url in test_urls:
    print(f"\n{'=' * 70}")
    print(f"Testing: {url}")
    print('=' * 70)
    
    try:
        data = scraper.scrape_recipe(url)
        
        print(f"\nRecipe: {data['title']}")
        print(f"Steps: {len(data['steps'])}")
        
        total_ingredients = sum(len(step['ingredients']) for step in data['steps'])
        print(f"Total ingredients distributed: {total_ingredients}\n")
        
        for step in data['steps']:
            ing_count = len(step['ingredients'])
            print(f"Step {step['step_number']}: {ing_count} ingredient(s)")
            if step['ingredients']:
                for ing in step['ingredients']:
                    amount_str = f"{ing['amount']} " if ing['amount'] else ""
                    unit_str = f"{ing['unit']} " if ing['unit'] else ""
                    print(f"  • {amount_str}{unit_str}{ing['ingredient_name']}")
        
        print("\n✓ Success")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'=' * 70}")
print("Testing complete!")
print('=' * 70)
