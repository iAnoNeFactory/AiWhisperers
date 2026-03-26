from pydantic import BaseModel
from typing import Optional


# ── Ingredients & Steps (shared sub-models) ──────────────────────────────────

class IngredientIn(BaseModel):
    name: str
    amount: float
    unit: str

class IngredientOut(IngredientIn):
    id: int

class StepIn(BaseModel):
    position: int = 0
    title: Optional[str] = None
    description: Optional[str] = None
    time_min: int = 0
    stage: str = "Dzień 1"

class StepOut(StepIn):
    id: int


# ── Layer ─────────────────────────────────────────────────────────────────────

class LayerIn(BaseModel):
    name: str
    description: Optional[str] = None
    category: str = "inne"
    default_height_cm: float = 2.0
    default_diameter_cm: float = 24.0
    prep_time_min: int = 0
    bake_time_min: int = 0
    ingredients: list[IngredientIn] = []
    steps: list[StepIn] = []

class LayerOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str
    default_height_cm: float
    default_diameter_cm: float
    prep_time_min: int
    bake_time_min: int
    photo_path: Optional[str]
    created_at: str
    updated_at: str
    ingredients: list[IngredientOut] = []
    steps: list[StepOut] = []
    avg_rating: Optional[float] = None
    review_count: int = 0

class LayerSummary(BaseModel):
    id: int
    name: str
    category: str
    default_height_cm: float
    default_diameter_cm: float
    photo_path: Optional[str]
    avg_rating: Optional[float]
    review_count: int


# ── Frosting ──────────────────────────────────────────────────────────────────

class FrostingIngredientIn(BaseModel):
    name: str
    amount: float
    unit: str

class FrostingIngredientOut(FrostingIngredientIn):
    id: int

class FrostingIn(BaseModel):
    name: str
    description: Optional[str] = None
    type: str = "masło"
    ref_diameter_cm: float = 24.0
    ref_height_cm: float = 10.0
    prep_time_min: int = 0
    ingredients: list[FrostingIngredientIn] = []
    steps: list[StepIn] = []

class FrostingOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    type: str
    ref_diameter_cm: float
    ref_height_cm: float
    prep_time_min: int
    photo_path: Optional[str]
    created_at: str
    updated_at: str
    ingredients: list[FrostingIngredientOut] = []
    steps: list[StepOut] = []
    avg_rating: Optional[float] = None
    review_count: int = 0

class FrostingSummary(BaseModel):
    id: int
    name: str
    type: str
    ref_diameter_cm: float
    ref_height_cm: float
    photo_path: Optional[str]
    avg_rating: Optional[float]
    review_count: int


# ── Decoration ────────────────────────────────────────────────────────────────

class DecorationIn(BaseModel):
    name: str
    type: str = "inne"
    description: Optional[str] = None
    unit: str = "szt"

class DecorationOut(DecorationIn):
    id: int
    photo_path: Optional[str]


# ── Cake composition ──────────────────────────────────────────────────────────

class CakeLayerIn(BaseModel):
    layer_id: int
    position: int = 0
    height_cm: Optional[float] = None
    diameter_cm: Optional[float] = None

class CakeLayerOut(BaseModel):
    id: int
    layer_id: int
    layer_name: str
    layer_category: str
    position: int
    height_cm: float
    diameter_cm: float
    ingredients: list[IngredientOut] = []

class CakeFrostingIn(BaseModel):
    frosting_id: int
    apply_top: bool = True
    apply_sides: bool = True

class CakeFrostingOut(BaseModel):
    id: int
    frosting_id: int
    frosting_name: str
    frosting_type: str
    apply_top: bool
    apply_sides: bool
    ingredients: list[FrostingIngredientOut] = []

class CakeDecorationIn(BaseModel):
    decoration_id: int
    quantity: float = 1.0
    note: Optional[str] = None

class CakeDecorationOut(BaseModel):
    id: int
    decoration_id: int
    decoration_name: str
    decoration_type: str
    quantity: float
    note: Optional[str]


# ── Cake ──────────────────────────────────────────────────────────────────────

class CakeIn(BaseModel):
    name: str
    description: Optional[str] = None
    diameter_cm: float = 24.0
    serves: int = 0

class CakeOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    diameter_cm: float
    serves: int
    photo_path: Optional[str]
    created_at: str
    updated_at: str
    layers: list[CakeLayerOut] = []
    frostings: list[CakeFrostingOut] = []
    decorations: list[CakeDecorationOut] = []
    total_height_cm: float = 0.0
    avg_rating: Optional[float] = None
    review_count: int = 0

class CakeSummary(BaseModel):
    id: int
    name: str
    description: Optional[str]
    diameter_cm: float
    serves: int
    total_height_cm: float
    photo_path: Optional[str]
    layer_count: int
    avg_rating: Optional[float]
    review_count: int


# ── Review ────────────────────────────────────────────────────────────────────

class ReviewIn(BaseModel):
    target_type: str   # cake | layer | frosting
    target_id: int
    author: str = "Anonim"
    text: Optional[str] = None
    rating: int        # 1-5

class ReviewOut(ReviewIn):
    id: int
    created_at: str


# ── Calculator ────────────────────────────────────────────────────────────────

class CalcLayerResult(BaseModel):
    layer_id: int
    layer_name: str
    position: int
    orig_height_cm: float
    orig_diameter_cm: float
    new_height_cm: float
    new_diameter_cm: float
    volume_scale: float
    ingredients: list[dict]  # {name, orig_amount, new_amount, unit}

class CalcFrostingResult(BaseModel):
    frosting_id: int
    frosting_name: str
    ref_area_cm2: float
    new_area_cm2: float
    area_scale: float
    ingredients: list[dict]

class CalcResult(BaseModel):
    cake_id: int
    cake_name: str
    orig_diameter_cm: float
    new_diameter_cm: float
    orig_total_height_cm: float
    new_total_height_cm: float
    layers: list[CalcLayerResult]
    frostings: list[CalcFrostingResult]
