import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Example Data
users = ['User1', 'User2', 'User3']
posts = ['Post1', 'Post2', 'Post3', 'Post4']
tags = ['TagA', 'TagB', 'TagC', 'TagD']

# User-Tag Interaction Matrix (example values)
user_tag_matrix = np.array([
    [3, 1, 0, 2],  # User1
    [0, 2, 3, 1],  # User2
    [1, 0, 4, 0]   # User3
])

# Post-Tag Matrix (example values)
post_tag_matrix = np.array([
    [1, 1, 0, 1],  # Post1
    [0, 1, 3, 0],  # Post2
    [2, 0, 1, 1],  # Post3
    [1, 1, 2, 1]   # Post4
])

def recommend_posts(user_id, top_n=2):
    # Get user profile
    user_profile = user_tag_matrix[user_id]
    
    # Calculate similarity scores
    similarity_scores = cosine_similarity([user_profile], post_tag_matrix)[0]
    
    # Get top N post indices
    top_post_indices = similarity_scores.argsort()[-top_n:][::-1]
    
    return [posts[i] for i in top_post_indices]
