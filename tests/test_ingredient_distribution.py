from app import scraper
import json

# Test with BBC Good Food pancakes recipe
url = "https://www.bbcgoodfood.com/recipes/classic-pancakes"

print(f"Testing ingredient distribution for: {url}\n")
print("=" * 60)

try:
    data = scraper.scrape_recipe(url)
    
    print(f"Recipe: {data['title']}")
    print(f"Total Time: {data['total_time_minutes']} minutes")
    print(f"Servings: {data['base_servings']}")
    print(f"\nNumber of steps: {len(data['steps'])}\n")
    
    for step in data['steps']:
        print(f"Step {step['step_number']}: {step['action']}")
        if step['ingredients']:
            print(f"  Ingredients ({len(step['ingredients'])}):")
            for ing in step['ingredients']:
                amount_str = f"{ing['amount']} " if ing['amount'] else ""
                unit_str = f"{ing['unit']} " if ing['unit'] else ""
                print(f"    - {amount_str}{unit_str}{ing['ingredient_name']}")
        else:
            print("  Ingredients: None")
        print()
    
    # Print full JSON for inspection
    print("\n" + "=" * 60)
    print("Full JSON output:")
    print(json.dumps(data, indent=2))
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
