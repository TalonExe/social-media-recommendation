from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from pydantic import HttpUrl
from app.db.database import Base

class PostTag(Base):
    __tablename__ = "PostTags"

    postId = Column(Integer, ForeignKey("Posts.id"), primary_key=True, index=True)
    name = Column(String, primary_key=True)

    # Relationships
    post = relationship("Post", back_populates="post_tags")