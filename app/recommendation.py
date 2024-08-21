import numpy as np
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from app.repositories.PostRepository import PostRepository
from app.db.database import get_db
from app.models.User import User
from app.models.Post import Post
from app.models.UserLike import UserLike
from app.models.PostTag import PostTag
from sqlalchemy.orm import Session
from sqlalchemy import func

def fetch_data_from_db(db: Session):
    # Fetch ratings data
    ratings = db.query(UserLike.userId, UserLike.postId, func.count(UserLike.postId).label('isLiked')) \
        .group_by(UserLike.userId, UserLike.postId).all()
    
    # Fetch posts data
    posts = db.query(Post).all()
    
    # Fetch post tags
    post_tags = db.query(PostTag).all()
    
    return ratings, posts, post_tags

def recommend_posts(user_id: int, db: Session, alpha=0.7, top_n=5):
    ratings, posts, post_tags = fetch_data_from_db(db)
    
    # Create DataFrames
    ratings_df = pd.DataFrame([(r.userId, r.postId, r.isLiked) for r in ratings], 
                              columns=['userId', 'postId', 'isLiked'])
    posts_df = pd.DataFrame([(p.id, p.userId, p.postTitle, p.location, p.postLikes) for p in posts],
                            columns=['postId', 'userId', 'title', 'location', 'likes'])
    
    # Create tag columns
    tag_columns = set(pt.name for pt in post_tags)
    for tag in tag_columns:
        posts_df[tag] = posts_df['postId'].apply(lambda x: 1 if any(pt.postId == x and pt.name == tag for pt in post_tags) else 0)
    
    # Collaborative Filtering
    reader = Reader(rating_scale=(0, 1))
    data = Dataset.load_from_df(ratings_df[["userId", "postId", "isLiked"]], reader)
    trainset = data.build_full_trainset()
    
    algo = SVD()
    algo.fit(trainset)
    
    # Content-Based Filtering
    item_features = posts_df.drop(columns=["postId", "userId", "title", "location", "likes"])
    cosine_sim = cosine_similarity(item_features)
    
    # Function to get content-based recommendations
    def content_based_recommendations(title, cosine_sim=cosine_sim):
        idx = posts_df.index[posts_df['title'] == title][0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:4]
        item_indices = [i[0] for i in sim_scores]
        return posts_df['title'].iloc[item_indices]
    
    # Content-Based Scores
    content_scores = defaultdict(float)
    for item in ratings_df[ratings_df["userId"] == user_id]["postId"].tolist():
        recommendations = content_based_recommendations(posts_df[posts_df["postId"] == item]["title"].values[0])
        for rec in recommendations:
            content_scores[posts_df[posts_df["title"] == rec]["postId"].values[0]] += 1
    
    # Normalize content scores
    max_content_score = max(content_scores.values()) if content_scores else 1
    content_scores = {k: v / max_content_score for k, v in content_scores.items()}

    # Collaborative Filtering Prediction for All Items
    collab_scores = {}
    for item in posts_df["postId"]:
        collab_scores[item] = algo.predict(user_id, item).est

    # Combine Scores with a Weighted Average
    combined_scores = {}
    for item in posts_df["postId"]:
        combined_scores[item] = alpha * collab_scores[item] + (1 - alpha) * content_scores.get(item, 0)

    # Add popularity factor
    popularity = posts_df.set_index('postId')['likes'].to_dict()
    max_likes = max(popularity.values())
    for item in combined_scores:
        combined_scores[item] += 0.1 * (popularity[item] / max_likes)  # Small boost based on popularity

    # Sort and return top N recommendations
    final_recommendations = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return final_recommendations

def recommend_for_new_user(db: Session, top_n=5):
    posts = db.query(Post).all()
    popular_items = sorted(posts, key=lambda p: p.postLikes, reverse=True)[:top_n]
    return [(p.id, 1.0) for p in popular_items]