import scraper
import json

urls = [
    "https://www.allrecipes.com/recipe/20268/pancakes-i/",
    "https://www.foodnetwork.com/recipes/food-network-kitchen/pancakes-recipe-1913971",
    "https://www.bbcgoodfood.com/recipes/classic-pancakes"
]

for url in urls:
    print(f"Testing {url}...")
    try:
        data = scraper.scrape_recipe(url)
        print(f"Success: {data['title']}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)
