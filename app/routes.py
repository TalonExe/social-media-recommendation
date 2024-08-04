from fastapi import APIRouter
from .recommendation import recommend_posts
from .models import UserInteraction
from requests import request as requests

router = APIRouter()

@router.get("/fetch-data")
def fetch_data():
    response = requests.get("https://api.example.com/data")
    return response.json()

@router.post("/recommend")
def get_recommendations(user_interaction: UserInteraction):
    recommendations = recommend_posts(user_interaction.user_id)
    return {"recommendations": recommendations}
