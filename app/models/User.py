from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    country = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)

    # Relationships
    posts = relationship("Post", back_populates="user")
    user_likes = relationship("UserLike", back_populates="user")