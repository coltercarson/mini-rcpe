from fastapi import FastAPI, Depends, Request, Form, HTTPException, status, Response, UploadFile, File, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.database import engine, get_db, SessionLocal
from app import models, crud, schemas, scraper
import os
import shutil
import uuid

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "secret")

@app.post("/api/scrape")
def scrape_url(payload: dict = Body(...)):
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    try:
        data = scraper.scrape_recipe(url)
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return JSONResponse({"filename": unique_filename})

def get_current_user(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token == "authenticated":
        return True
    return None

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(response: Response, password: str = Form(...)):
    if password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="session_token", value="authenticated")
        return response
    else:
        return RedirectResponse(url="/login?error=Invalid password", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("session_token")
    return response

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    all_recipes = crud.get_recipes(db)
    user = get_current_user(request)
    return templates.TemplateResponse("index.html", {"request": request, "all_recipes": all_recipes, "user": user})

@app.get("/recipe/{recipe_id}", response_class=HTMLResponse)
def read_recipe(request: Request, recipe_id: int, db: Session = Depends(get_db)):
    recipe = crud.get_recipe(db, recipe_id)
    all_recipes = crud.get_recipes(db)
    user = get_current_user(request)
    return templates.TemplateResponse("detail.html", {"request": request, "recipe": recipe, "all_recipes": all_recipes, "user": user})

@app.get("/new", response_class=HTMLResponse)
def new_recipe(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    all_recipes = crud.get_recipes(db)
    return templates.TemplateResponse("form.html", {"request": request, "all_recipes": all_recipes, "user": user})

from fastapi.encoders import jsonable_encoder

@app.get("/recipe/{recipe_id}/edit", response_class=HTMLResponse)
def edit_recipe(request: Request, recipe_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    db_recipe = crud.get_recipe(db, recipe_id)
    if not db_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    # Convert to Pydantic model then to dict (handling datetimes etc)
    recipe = jsonable_encoder(schemas.Recipe.from_orm(db_recipe))
    all_recipes = crud.get_recipes(db)
    return templates.TemplateResponse("form.html", {"request": request, "recipe": recipe, "all_recipes": all_recipes, "user": user})

@app.post("/api/recipes", response_model=schemas.Recipe)
def create_recipe(request: Request, recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return crud.create_recipe(db=db, recipe=recipe)

@app.put("/api/recipes/{recipe_id}", response_model=schemas.Recipe)
def update_recipe(request: Request, recipe_id: int, recipe: schemas.RecipeCreate, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    updated_recipe = crud.update_recipe(db, recipe_id, recipe)
    if not updated_recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return updated_recipe

@app.delete("/api/recipes/{recipe_id}")
def delete_recipe(request: Request, recipe_id: int, db: Session = Depends(get_db)):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    success = crud.delete_recipe(db, recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"status": "success"}

@app.get("/api/conversions")
def get_conversions(db: Session = Depends(get_db)):
    return db.query(models.IngredientConversion).all()

# Seed initial conversion data
@app.on_event("startup")
def seed_conversions():
    db = SessionLocal()
    if db.query(models.IngredientConversion).count() == 0:
        initial_data = [
            {"name": "all-purpose flour", "density_g_per_ml": 0.593, "common_units": {"cup": 240, "tbsp": 15, "tsp": 5}},
            {"name": "water", "density_g_per_ml": 1.0, "common_units": {"cup": 240, "tbsp": 15, "tsp": 5}},
            {"name": "butter", "density_g_per_ml": 0.911, "common_units": {"cup": 240, "tbsp": 15, "tsp": 5}},
            {"name": "sugar", "density_g_per_ml": 0.845, "common_units": {"cup": 240, "tbsp": 15, "tsp": 5}},
            {"name": "milk", "density_g_per_ml": 1.03, "common_units": {"cup": 240, "tbsp": 15, "tsp": 5}},
            {"name": "salt", "density_g_per_ml": 1.2, "common_units": {"tsp": 5, "tbsp": 15}}
        ]
        for item in initial_data:
            db.add(models.IngredientConversion(**item))
        db.commit()
    db.close()
