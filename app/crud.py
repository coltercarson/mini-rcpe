from sqlalchemy.orm import Session
from app import models, schemas

def get_recipe(db: Session, recipe_id: int):
    return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()

def get_recipes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Recipe).offset(skip).limit(limit).all()

def create_recipe(db: Session, recipe: schemas.RecipeCreate):
    db_recipe = models.Recipe(
        title=recipe.title,
        total_time_minutes=recipe.total_time_minutes,
        base_servings=recipe.base_servings,
        recipe_mode=recipe.recipe_mode,
        dough_weight=recipe.dough_weight,
        image_filename=recipe.image_filename,
        source_url=recipe.source_url
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)

    for step_data in recipe.steps:
        db_step = models.Step(
            recipe_id=db_recipe.id,
            step_number=step_data.step_number,
            action=step_data.action,
            time_minutes=step_data.time_minutes,
            tools=step_data.tools,
            image_filename=step_data.image_filename
        )
        db.add(db_step)
        db.commit()
        db.refresh(db_step)

        for ing_data in step_data.ingredients:
            db_ing = models.StepIngredient(
                step_id=db_step.id,
                ingredient_name=ing_data.ingredient_name,
                amount=ing_data.amount,
                unit=ing_data.unit,
                baker_percentage=ing_data.baker_percentage
            )
            db.add(db_ing)
    
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def update_recipe(db: Session, recipe_id: int, recipe_data: schemas.RecipeCreate):
    db_recipe = get_recipe(db, recipe_id)
    if not db_recipe:
        return None
    
    # Update basic fields
    db_recipe.title = recipe_data.title
    db_recipe.total_time_minutes = recipe_data.total_time_minutes
    db_recipe.base_servings = recipe_data.base_servings
    db_recipe.recipe_mode = recipe_data.recipe_mode
    db_recipe.dough_weight = recipe_data.dough_weight
    db_recipe.image_filename = recipe_data.image_filename
    db_recipe.source_url = recipe_data.source_url
    
    # Delete existing steps (cascade will handle ingredients)
    # Note: In a more complex app, we might try to diff steps, but for MVP, replacing is safer/easier
    db.query(models.Step).filter(models.Step.recipe_id == recipe_id).delete()
    
    # Re-create steps
    for step_data in recipe_data.steps:
        db_step = models.Step(
            recipe_id=db_recipe.id,
            step_number=step_data.step_number,
            action=step_data.action,
            time_minutes=step_data.time_minutes,
            tools=step_data.tools,
            image_filename=step_data.image_filename
        )
        db.add(db_step)
        db.commit() # Commit to get ID
        db.refresh(db_step)

        for ing_data in step_data.ingredients:
            db_ing = models.StepIngredient(
                step_id=db_step.id,
                ingredient_name=ing_data.ingredient_name,
                amount=ing_data.amount,
                unit=ing_data.unit,
                baker_percentage=ing_data.baker_percentage
            )
            db.add(db_ing)
            
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def delete_recipe(db: Session, recipe_id: int):
    db_recipe = get_recipe(db, recipe_id)
    if db_recipe:
        db.delete(db_recipe)
        db.commit()
        return True
    return False
