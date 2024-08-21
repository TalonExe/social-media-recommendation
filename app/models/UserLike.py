from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class UserLike(Base):
    __tablename__ = "UserLikes"

    userId = Column(Integer, ForeignKey("Users.id"), primary_key=True, nullable=False)
    postId = Column(Integer, ForeignKey("Posts.id"), primary_key=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="user_likes")
    post = relationship("Post", back_populates="user_likes")