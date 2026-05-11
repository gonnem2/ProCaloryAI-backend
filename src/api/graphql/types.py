# src/api/graphql/types.py
import strawberry
from datetime import datetime
from typing import Optional


@strawberry.type
class UserGQL:
    id: int
    username: str
    email: str
    role: str
    created_at: datetime
    days_in_app: int
    total_records: int


@strawberry.type
class AnalysisResultGQL:
    dish_name: str
    calories: float
    protein: float
    fat: float
    carbs: float


@strawberry.type
class AnalysisStatusGQL:
    request_id: int
    status: str
    result: Optional[AnalysisResultGQL] = None


@strawberry.type
class AuthPayload:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@strawberry.type
class NutritionGQL:
    calories: float
    protein: float
    fat: float
    carbs: float


@strawberry.type
class MealLogGQL:
    id: int
    name: str
    nutrition: NutritionGQL
    meal_type: str
    source: str
    eaten_at: datetime
    s3_key: Optional[str]


@strawberry.type
class GoalGQL:
    id: int
    goal_type: str
    target_kg: float
    current_weight_kg: float
    daily_calories: float
    progress_percent: float
    total_calorie_deficit: float
    created_at: datetime


@strawberry.type
class PreferencesGQL:
    diet_type: str
    meals_per_day: int
    water_goal_ml: int
    notifications_enabled: bool


@strawberry.type
class PrivacySettingsGQL:
    analytics_enabled: bool
    crash_reports_enabled: bool
    personalization_enabled: bool


@strawberry.type
class AchievementsGQL:
    streak_days: int
    goal_created: bool
    photos_added: int
    days_in_app: int
    total_records: int


@strawberry.type
class UploadUrlGQL:
    request_id: int
    upload_url: str
    s3_key: str
    expires_in: int


# --- Inputs ---


@strawberry.input
class RegisterInput:
    username: str
    email: str
    password: str


@strawberry.input
class LoginInput:
    email: str
    password: str


@strawberry.input
class RefreshInput:
    refresh_token: str


@strawberry.input
class AddMealLogInput:
    name: str
    calories: float
    protein: float
    fat: float
    carbs: float
    meal_type: str
    eaten_at: Optional[datetime] = None
    source: str = "manual"  # ← добавить


@strawberry.input
class GoalInput:
    goal_type: str
    target_kg: float
    current_weight_kg: float
    daily_calories: float


@strawberry.input
class PreferencesInput:
    diet_type: Optional[str] = None
    meals_per_day: Optional[int] = None
    water_goal_ml: Optional[int] = None
    notifications_enabled: Optional[bool] = None


@strawberry.input
class PrivacySettingsInput:
    analytics_enabled: Optional[bool] = None
    crash_reports_enabled: Optional[bool] = None
    personalization_enabled: Optional[bool] = None
