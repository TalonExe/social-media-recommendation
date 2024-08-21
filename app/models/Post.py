from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Post(Base):
    __tablename__ = "Posts"

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, ForeignKey("Users.id"), nullable=False)
    pictureUrl = Column(String, nullable=False)
    postTitle = Column(String, nullable=False)
    postContent = Column(String, nullable=False)
    location = Column(String, nullable=False)
    postLikes = Column(Integer, nullable=False, default=0)

    # Relationships
    user = relationship("User", back_populates="posts")
    user_likes = relationship("UserLike", back_populates="post")
    post_tags = relationship("PostTag", back_populates="post")