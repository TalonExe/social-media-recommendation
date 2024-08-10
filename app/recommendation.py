import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.preprocessing import MinMaxScaler

# Example Data
ratings_dict = {
    "item_id": [1, 1, 1, 2, 2, 2, 3, 3],
    "user_id": ["A", "B", "C", "A", "B", "C", "A", "B"],
    "rating": [5, 4, 3, 4, 5, 3, 2, 5],
}
items_dict = {
    "item_id": [1, 2, 3],
    "title": ["Item 1", "Item 2", "Item 3"],
    "metadata": ["Action Adventure", "Action Sci-Fi", "Romance"],
}

ratings_df = pd.DataFrame(ratings_dict)
items_df = pd.DataFrame(items_dict)

# Collaborative Filtering using SVD
reader = Reader(rating_scale=(1, 5))
data = Dataset.load_from_df(ratings_df[["user_id", "item_id", "rating"]], reader)
trainset, testset = train_test_split(data, test_size=0.25)

algo = SVD()
algo.fit(trainset)

# Content-Based Filtering using TF-IDF
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(items_df["metadata"])

# Similarity Matrix
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Function to get content-based recommendations
def content_based_recommendations(title, cosine_sim=cosine_sim):
    idx = items_df.index[items_df['title'] == title][0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:4]
    item_indices = [i[0] for i in sim_scores]
    return items_df['title'].iloc[item_indices]

# Example Hybrid Recommendation for a user
user_id = "A"
user_rated_items = ratings_df[ratings_df["user_id"] == user_id]["item_id"]

# Content-Based Scores
content_scores = {item: content_based_recommendations(items_df[items_df["item_id"] == item]["title"].values[0]) for item in user_rated_items}

# Collaborative Filtering Prediction for All Items
collab_scores = {}
for item in items_df["item_id"]:
    collab_scores[item] = algo.predict(user_id, item).est

# Combine Scores with a Weighted Average
combined_scores = {}
alpha = 0.7  # Weight for collaborative filtering
for item in items_df["item_id"]:
    content_score = 0
    for recommended_items in content_scores.values():
        if items_df[items_df["title"].isin(recommended_items)]["item_id"].values[0] == item:
            content_score = 1  # Simple binary match, can be replaced with more sophisticated logic
    combined_scores[item] = alpha * collab_scores[item] + (1 - alpha) * content_score

# Normalize Scores for Final Recommendations
scaler = MinMaxScaler()
normalized_scores = scaler.fit_transform([[score] for score in combined_scores.values()])
final_recommendations = sorted(zip(combined_scores.keys(), normalized_scores), key=lambda x: x[1], reverse=True)

# Display the Top Recommendations
print("Top Recommendations for User {}: ".format(user_id))
for item_id, score in final_recommendations:
    print(f"Item {item_id} - Score: {score[0]:.2f}")

def recommend_posts(data):

