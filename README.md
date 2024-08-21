# Recommendation System for Rock Paper Radar

## Installation

1. Clone this repository
2. Install the requirements: 
``` bash
pip install -r requirements.txt
```
3. Create a .env file with the following variables:
``` bash
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=your_database_name
```

## Running the application

To run the application, use the following command:
``` bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.
