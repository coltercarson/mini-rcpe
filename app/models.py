from sqlalchemy import Column, Integer, String, ForeignKey, Float, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import datetime

class Recipe(Base):
    __tablename__ = "recipes"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    total_time_minutes = Column(Integer)
    base_servings = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    image_filename = Column(String, nullable=True)
    source_url = Column(String, nullable=True)

    steps = relationship("Step", back_populates="recipe", cascade="all, delete-orphan", order_by="Step.step_number")

class Step(Base):
    __tablename__ = "steps"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    step_number = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    time_minutes = Column(Integer)
    tools = Column(JSON, default=[])
    image_filename = Column(String, nullable=True)

    recipe = relationship("Recipe", back_populates="steps")
    ingredients = relationship("StepIngredient", back_populates="step", cascade="all, delete-orphan")

class StepIngredient(Base):
    __tablename__ = "step_ingredients"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(Integer, ForeignKey("steps.id"))
    ingredient_name = Column(String, nullable=False)
    amount = Column(Float)
    unit = Column(String)
    
    step = relationship("Step", back_populates="ingredients")

# Conversion table for future use
class IngredientConversion(Base):
    __tablename__ = "ingredient_conversions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    density_g_per_ml = Column(Float)
    common_units = Column(JSON)
