from pydantic import BaseModel

class UserInteraction(BaseModel):
    user_id: int
