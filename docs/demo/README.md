# Mini-RCPE Demo

This is a static demo of the mini-rcpe recipe manager, hosted on GitHub Pages.

## What is this?

This demo showcases the user interface and basic functionality of mini-rcpe with sample recipes. It's a client-side only version that doesn't require a backend server.

## Features in this demo

- ✅ Browse sample recipes
- ✅ View recipe details with ingredients and preparation steps
- ✅ Scale recipes (0.5x, 1x, 2x, 3x)
- ✅ Customize font size and background color
- ✅ Responsive sidebar navigation
- ✅ Bread mode display (see the Sourdough Bread recipe)

## What's NOT included

This is a static demo, so the following features from the full application are not available:

- ❌ Recipe scraping from websites
- ❌ Creating, editing, or deleting recipes
- ❌ LLM fallback for unsupported sites
- ❌ Image uploads
- ❌ Database storage
- ❌ Authentication

## Running the full application

For the complete experience with all features, including recipe scraping and editing:

1. Clone the repository: `git clone https://github.com/coltercarson/mini-rcpe.git`
2. Follow the setup instructions in the [main README](https://github.com/coltercarson/mini-rcpe#readme)
3. Or deploy with Docker: See [Docker documentation](https://github.com/coltercarson/mini-rcpe/tree/main/docs/docker.md)

## Technical details

This demo consists of:
- `index.html` - Main demo page
- `style.css` - Styling (copied from the main application)
- `recipes.js` - Sample recipe data embedded in JavaScript

The demo is automatically deployed to GitHub Pages via GitHub Actions whenever changes are pushed to the main branch.
