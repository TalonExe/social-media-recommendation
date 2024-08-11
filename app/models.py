from pydantic import BaseModel
from typing import List

#posts that user interact with 
class UserInteraction(BaseModel):
    user_id: int
    post_id: int
    isLiked: int # 0 or 1 for no like/like

#other posts

class Posts(BaseModel):
    user_id: int
    post_id: int
    metadata: List[str]
    location: str
    likes: int