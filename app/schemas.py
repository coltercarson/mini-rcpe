from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StepIngredientBase(BaseModel):
    ingredient_name: str
    amount: Optional[float] = None
    unit: Optional[str] = None
    baker_percentage: Optional[float] = None

class StepIngredientCreate(StepIngredientBase):
    pass

class StepIngredient(StepIngredientBase):
    id: int
    step_id: int

    class Config:
        from_attributes = True

class StepBase(BaseModel):
    step_number: int
    action: str
    time_minutes: Optional[int] = None
    tools: Optional[List[str]] = []
    image_filename: Optional[str] = None

class StepCreate(StepBase):
    ingredients: List[StepIngredientCreate] = []

class Step(StepBase):
    id: int
    recipe_id: int
    ingredients: List[StepIngredient] = []

    class Config:
        from_attributes = True

class RecipeBase(BaseModel):
    title: str
    total_time_minutes: Optional[int] = None
    base_servings: int = 1
    recipe_mode: str = "normal"
    dough_weight: Optional[float] = None
    image_filename: Optional[str] = None
    source_url: Optional[str] = None

class RecipeCreate(RecipeBase):
    steps: List[StepCreate] = []

class Recipe(RecipeBase):
    id: int
    created_at: datetime
    updated_at: datetime
    steps: List[Step] = []

    class Config:
        from_attributes = True
