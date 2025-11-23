# Mini-RCPE: Complete Project Overview

## Design Philosophy
**Ultra-minimal, content-first recipe manager inspired by gibney.org/writer aesthetic**
- Monospace font for ALL text (uniform size)
- Slightly grey background (`#f4f4f4`)
- Clean typography, no bold headers (or very subtle)
- Generous whitespace
- No images (for now)
- Mobile-first responsive design
- Hideable navigation with NO title
- Fast, zero-bloat loading

---

## UI/UX Structure

### **Navigation (Hideable Sidebar)**
- **Desktop**: Left sidebar (200px), toggle button in top-left
- **Mobile**: Hamburger menu, full-screen overlay when open
- Recipe list: title only, sorted alphabetically
- No application title in sidebar
- Hover states: simple underline
- Active recipe: bold or underline

### **Recipe View (Main Content)**
```
  SOURDOUGH BREAD                  ← Title (monospace, bold, uppercase)
  3h 30m • 1 loaf • Serves 8       ← Metadata (monospace, small, gray)

  Scale: [1x]                      ← Simple text input/select

  Ingredients Summary:
  500g bread flour
  350g water
  100g starter
  10g salt

  1. Mix the dough                 ← Step number (bold)
     500g bread flour
     350g water
     100g sourdough starter

     Combine in large bowl
     and mix until shaggy.
     Rest 30 minutes.

     30m  Bowl, spoon              ← Meta (gray)

  2. Add salt...
```

### **Typography & Spacing**
- **Font**: Monospace (SFMono-Regular, Consolas, etc.) for EVERYTHING
- **Size**: Uniform small size (e.g., 13px) for body, headers, and meta
- **Colors**: 
  - Text: `#000000`
  - Meta/secondary: `#555555`
  - Background: `#f4f4f4`
  - Borders: Minimal or none
- **Spacing**: Liberal use of margins, but tighter vertical rhythm due to small font

### **Entry Form**
- Single-page form, clean layout
- Auto-save to localStorage (while editing)
- Fields:
  ```
  Title: [________________]
  Total Time: [___] minutes
  Servings: [___]
  
  Steps:
  ┌─────────────────────────────┐
  │ Step 1                      │
  │ Action: [________________]  │
  │ Time: [___] minutes         │
  │ Tools: [________________]   │
  │                             │
  │ Ingredients:                │
  │ [+ Add Ingredient]          │
  │   └ 500g bread flour  [x]   │
  │   └ 350ml water      [x]   │
  │                             │
  │ [+ Add Step]                │
  └─────────────────────────────┘
  
  [Save Recipe]
  ```

---

## Technical Architecture

### **Tech Stack**

**Frontend:**
- **Vanilla HTML/CSS/JS** or **Alpine.js** (minimal JS framework, 15kb)
- **Tailwind CSS** (utility-first, purge unused CSS for tiny bundle)
- OR pure CSS with CSS Grid/Flexbox
- No build step needed (or minimal Vite setup)

**Backend:**
- **FastAPI** (Python) - lightweight, modern, excellent docs
  - OR **Go** with stdlib/Gin - ultimate performance
- **PostgreSQL** - JSON support for flexible recipe storage
  - OR **SQLite** - simpler, single-file database (fine for personal use)

**Authentication:**
- Environment variable password for editing
- No auth for reading (public)
- Simple session cookie when authenticated

**Deployment:**
- Docker + Docker Compose
- Nginx reverse proxy (optional but recommended)
- Caddy as alternative (auto-HTTPS)

### **Database Schema**

```sql
-- Recipes table
CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    total_time_minutes INTEGER,
    base_servings INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Steps table (ordered)
CREATE TABLE steps (
    id SERIAL PRIMARY KEY,
    recipe_id INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    action TEXT NOT NULL,
    time_minutes INTEGER,
    tools TEXT[], -- array of tool names
    UNIQUE(recipe_id, step_number)
);

-- Ingredients per step
CREATE TABLE step_ingredients (
    id SERIAL PRIMARY KEY,
    step_id INTEGER REFERENCES steps(id) ON DELETE CASCADE,
    ingredient_name VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2),
    unit VARCHAR(20), -- g, ml, tsp, tbsp, cup, etc
    ingredient_id INTEGER REFERENCES ingredient_conversions(id)
);

-- Conversion database
CREATE TABLE ingredient_conversions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    density_g_per_ml DECIMAL(10,4), -- for volume->weight conversion
    common_units JSONB -- {"cup": 240, "tbsp": 15, "tsp": 5}
);
```

### **API Endpoints**

```
Public (no auth):
  GET  /api/recipes          - List all recipes
  GET  /api/recipes/:id      - Get single recipe with steps

Authenticated:
  POST   /api/recipes        - Create recipe
  PUT    /api/recipes/:id    - Update recipe
  DELETE /api/recipes/:id    - Delete recipe
  
Utility:
  POST /api/scale            - Scale recipe ingredients
  GET  /api/ingredients      - Autocomplete ingredient names
  POST /api/auth/login       - Authenticate for editing
  POST /api/auth/logout      - Clear session
```

---

## Mobile Responsiveness

### **Breakpoints**
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### **Mobile Adaptations**
- Navigation becomes hamburger menu
- Single column layout
- Slightly larger touch targets (48px minimum)
- Sticky scaling widget at top
- Collapsible ingredient summary
- Steps remain full-width, generous spacing

### **CSS Approach**
```css
/* Mobile first */
.sidebar {
  position: fixed;
  left: -100%;
  transition: left 0.3s;
  width: 100%;
}

.sidebar.open {
  left: 0;
}

/* Desktop */
@media (min-width: 768px) {
  .sidebar {
    position: static;
    width: 280px;
  }
  
  .main-content {
    margin-left: 280px;
  }
}
```

---

## Ingredient Scaling System

### **Base Conversion Data**
Populate with common ingredients:
```json
{
  "all-purpose flour": {"density": 0.593, "cup_ml": 240},
  "water": {"density": 1.0, "cup_ml": 240},
  "butter": {"density": 0.911, "cup_ml": 240},
  "sugar": {"density": 0.845, "cup_ml": 240},
  "milk": {"density": 1.03, "cup_ml": 240}
}
```

### **Scaling Logic**
1. Store all amounts in grams/ml (metric base)
2. Calculate scale factor: `new_servings / base_servings`
3. Multiply all ingredient amounts
4. Convert to user's preferred unit system
5. Round sensibly (5g increments for flour, 1g for salt, etc)

### **UI Widget**
```
Scale: [1x ▼]
       0.5x
       1x   ✓
       1.5x
       2x
       3x
       Custom: [___]
```

---

## Docker Setup

### **docker-compose.yml**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://rcpe:rcpe@db:5432/rcpe
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./data:/app/data
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=rcpe
      - POSTGRES_USER=rcpe
      - POSTGRES_PASSWORD=rcpe
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### **Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Differentiation from Existing Tools

| Feature | Mealie/Tandoor | Mini-RCPE |
|---------|---------------|-----------|
| Design | Feature-rich UI | Minimal, gibney.org aesthetic |
| Focus | All-in-one | Recipes only, zero bloat |
| Steps | Paragraph format | Ingredient-per-step breakdown |
| Performance | Good | Lightning fast (<100kb page) |
| Complexity | Many features | One thing, done perfectly |

---

## Similar Existing Tools

- **Mealie** - Most mature self-hosted option with RestAPI backend and Vue frontend, automatic recipe import from URLs
- **Tandoor Recipes** - Complete meal planning application with shopping lists and meal planning
- **KitchenOwl** - Smart grocery list and recipe manager with cross-platform support
- **RecipeSage** - Collaborative recipe keeper with meal planning features
- **Groceri.es** - Simpler Flask-based recipe and meal planning app

---

## Next Steps / Development Phases

### **Phase 1: MVP** (Weekend project)
- Basic CRUD for recipes
- Simple list + detail view
- No scaling yet
- SQLite database
- Basic auth

### **Phase 2: Core Features** (Week 2)
- Ingredient scaling
- Conversion database
- Hideable navigation
- Mobile responsive

### **Phase 3: Polish** (Week 3)
- Import/export recipes (JSON)
- Print stylesheet
- Keyboard shortcuts
- Search/filter

### **Phase 4: Nice-to-haves**
- Recipe duplication
- Tags/categories
- Recipe notes/variations
- Multi-user (if needed)

---

## Key Design Principles

1. **Content First**: Every design decision serves the recipe content
2. **Zero Bloat**: No unnecessary features, text, or UI elements
3. **Fast**: Sub-second page loads, minimal JavaScript
4. **Readable**: Typography and spacing optimized for scanning recipes while cooking
5. **Mobile-Friendly**: Works perfectly on phone propped up in kitchen
6. **Self-Hostable**: Full control over your data, Docker-based deployment

---

## Implementation Notes

- Use semantic HTML for accessibility
- Progressive enhancement: works without JS for basic viewing
- Consider prefers-color-scheme for optional dark mode
- Test on actual mobile devices in kitchen environment
- Keep bundle size < 100kb total (HTML + CSS + JS)
- Server-side rendering for instant page loads
- Consider static site generation for read-only recipes if scaling becomes issue