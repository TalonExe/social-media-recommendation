import numpy as np
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer

# Example Data
ratings_dict = {
    "post_id": [1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 4, 5, 5, 5],
    "user_id": ["A", "B", "C", "A", "B", "C", "A", "B", "A", "B", "C", "A", "B", "C",],
    "isLiked": [1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
}

posts_dict = {
    "post_id": [1, 2, 3, 4, 5],
    "user_id": ["A", "B", "C", "D", "E"],
    "title": ["Hainanese Chicken Here is amazing!!!", "The Child King of Cambodia", "The wonders of Universal Studios in Japan", "The beauties of the rivers of Paris", "Into the wildlife of the jungle"],
    "Food": [1, 1, 1, 0, 0],
    "Historical": [1, 1, 0, 1, 0],
    "Entertainment": [0, 1, 1, 1, 1],
    "Scenery": [0, 0, 0, 1, 1],
    "Adventure": [1, 0, 1, 1, 1],
    "location": ["Hong Kong", "Cambodia", "Japan", "France", "Nigeria"],
    "likes": [1, 2, 2, 3, 3]
}

ratings_df = pd.DataFrame(ratings_dict)
items_df = pd.DataFrame(posts_dict)

# Collaborative Filtering using SVD
reader = Reader(rating_scale=(0, 1))
data = Dataset.load_from_df(ratings_df[["user_id", "post_id", "isLiked"]], reader)
trainset, testset = train_test_split(data, test_size=0.25)

algo = SVD()
algo.fit(trainset)

# Content-Based Filtering using Item Features (e.g., Food, Historical, etc.)
item_features = items_df.drop(columns=["post_id", "user_id", "title", "location", "likes"])
cosine_sim = cosine_similarity(item_features)

# Function to get content-based recommendations
def content_based_recommendations(title, cosine_sim=cosine_sim):
    idx = items_df.index[items_df['title'] == title][0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:4]
    item_indices = [i[0] for i in sim_scores]
    return items_df['title'].iloc[item_indices]

def recommend_posts(user_id, alpha=0.7, top_n=5):
    user_rated_items = ratings_df[ratings_df["user_id"] == user_id]["post_id"].tolist()
    
    # Content-Based Scores
    content_scores = defaultdict(float)
    for item in user_rated_items:
        recommendations = content_based_recommendations(items_df[items_df["post_id"] == item]["title"].values[0])
        for rec in recommendations:
            content_scores[items_df[items_df["title"] == rec]["post_id"].values[0]] += 1
    
    # Normalize content scores
    max_content_score = max(content_scores.values()) if content_scores else 1
    content_scores = {k: v / max_content_score for k, v in content_scores.items()}

    # Collaborative Filtering Prediction for All Items
    collab_scores = {}
    for item in items_df["post_id"]:
        collab_scores[item] = algo.predict(user_id, item).est

    # Combine Scores with a Weighted Average
    combined_scores = {}
    for item in items_df["post_id"]:
        combined_scores[item] = alpha * collab_scores[item] + (1 - alpha) * content_scores.get(item, 0)

    # Add popularity factor
    popularity = items_df.set_index('post_id')['likes'].to_dict()
    max_likes = max(popularity.values())
    for item in combined_scores:
        combined_scores[item] += 0.1 * (popularity[item] / max_likes)  # Small boost based on popularity

    # Sort and return top N recommendations
    final_recommendations = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]

    print(f"Top {top_n} Recommendations for User {user_id}:")
    for item_id, score in final_recommendations:
        print(f"{items_df[items_df['post_id'] == item_id]['title'].values[0]} - Score: {score:.2f}")

    return final_recommendations

# Example Usage
recommend_posts("E", top_n=3)

# Add function to handle cold start for new users
def recommend_for_new_user(top_n=5):
    # Use popularity and diversity for new users
    popular_items = items_df.sort_values('likes', ascending=False)['post_id'].tolist()[:top_n]
    
    print(f"Top {top_n} Recommendations for New User:")
    for item_id in popular_items:
        print(f"{items_df[items_df['post_id'] == item_id]['title'].values[0]}")

    return popular_items

# Example Usage for new user
recommend_for_new_user(top_n=3)