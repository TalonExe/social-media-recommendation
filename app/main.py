from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from app.recommendation import recommend_posts, recommend_for_new_user
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.User import User
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class RecommendationRequest(BaseModel):
    username: Optional[str] = None

class RecommendationResponse(BaseModel):
    recommendations: List[dict]

@app.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    username: Optional[str] = Query(None, description="Username for personalized recommendations"),
    db: Session = Depends(get_db)
):
    try:
        if username:
            user = db.query(User).filter(User.username == username).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            recommendations = recommend_posts(user.id, db)
        else:
            recommendations = recommend_for_new_user(db)
        
        return RecommendationResponse(recommendations=[
            {"post_id": post_id, "score": score} for post_id, score in recommendations
        ])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)