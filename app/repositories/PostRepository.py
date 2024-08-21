from sqlalchemy.orm import Session
from app.models.Post import Post

class PostRepository:
    @staticmethod
    def get_all_posts(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Post).offset(skip).limit(limit).all()