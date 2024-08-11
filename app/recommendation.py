import numpy as np
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

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

# General Recommendation Function for Any User
def recommend_posts(user_id, alpha=0.7):
    user_rated_items = ratings_df[ratings_df["user_id"] == user_id]["post_id"]

    # Content-Based Scores
    content_scores = {item: content_based_recommendations(items_df[items_df["post_id"] == item]["title"].values[0]) for item in user_rated_items}

    # Collaborative Filtering Prediction for All Items
    collab_scores = {}
    for item in items_df["post_id"]: 
        collab_scores[item] = algo.predict(user_id, item).est

    # Combine Scores with a Weighted Average
    combined_scores = {}
    for item in items_df["post_id"]:
        content_score = 0
        for recommended_items in content_scores.values():
            if items_df[items_df["title"].isin(recommended_items)]["post_id"].values[0] == item:
                content_score = 1  # Simple binary match, can be replaced with more sophisticated logic
        combined_scores[item] = alpha * collab_scores[item] + (1 - alpha) * content_score

    # Normalize Scores for Final Recommendations
    scaler = MinMaxScaler()
    normalized_scores = scaler.fit_transform([[score] for score in combined_scores.values()])
    final_recommendations = sorted(zip(combined_scores.keys(), normalized_scores), key=lambda x: x[1], reverse=True)

    # Display the Top Recommendations
    print(f"Top Recommendations for User {user_id}:")
    for item_id, score in final_recommendations:
        print(f"{posts_dict['title'][item_id - 1]} - Score: {score[0]:.2f}")

# Example Usage for a specific user
recommend_posts("E")
