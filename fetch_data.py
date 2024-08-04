import requests

def fetch_data():
    response = requests.get("http://127.0.0.1:8000/fetch-data")
    data = response.json()
    return data

def get_recommendations(user_id):
    response = requests.post("http://127.0.0.1:8000/recommend", json={"user_id": user_id})
    data = response.json()
    return data["recommendations"]

if __name__ == "__main__":
    data = fetch_data()
    print("Fetched data:", data)
    
    recommendations = get_recommendations(0)
    print("Recommendations for User0:", recommendations)
