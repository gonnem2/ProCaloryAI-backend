from datetime import datetime

import strawberry


@strawberry.type
class UserGQL:
    id: int
    username: str
    email: str
    role: str


@strawberry.type
class AuthPayload:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


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


@strawberry.type
class NutritionGQL:
    calories: float
    protein: float
    fat: float
    carbs: float


@strawberry.type
class DishGQL:
    id: int
    name: str
    nutrition_per_100g: NutritionGQL


@strawberry.type
class MealLogGQL:
    id: int
    dish: DishGQL
    weight_grams: float
    nutrition_total: NutritionGQL
    eaten_at: datetime


@strawberry.type
class DailyStatsGQL:
    date: str
    total: NutritionGQL
    meals: list[MealLogGQL]


@strawberry.type
class AnalysisRequestGQL:
    request_id: int
    status: str = "pending"


@strawberry.input
class AnalyzePhotoInput:
    photo_base64: str  # base64 encoded image


@strawberry.input
class AddMealLogInput:
    dish_id: int
    weight_grams: float
