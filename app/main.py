from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.recommendation import recommend_posts, recommend_for_new_user
from sqlalchemy.orm import Session
from app.db.database import get_db

app = FastAPI()

class RecommendationRequest(BaseModel):
    user_id: Optional[int] = None
    top_n: int = 5

class RecommendationResponse(BaseModel):
    recommendations: List[dict]

@app.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest, db: Session = Depends(get_db)):
    try:
        if request.user_id:
            recommendations = recommend_posts(request.user_id, db, top_n=request.top_n)
        else:
            recommendations = recommend_for_new_user(db, top_n=request.top_n)
        
        return RecommendationResponse(recommendations=[
            {"post_id": post_id, "score": score} for post_id, score in recommendations
        ])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)