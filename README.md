# Player Performance Predictor

## Overview
This application was mostly designed to predict a player's performance for an upcoming season based on historical data.

## Technologies Used
- **Backend**: Django
- **Frontend**: Next.js, React, Material-UI
- **Machine Learning**: TensorFlow, scikit-learn
- **Database**: MongoDB
- **Styling**: Tailwind CSS

## Installation
To run this project:

1. Clone the repository
    git clone https://github.com/yourusername/player-performance-predictor.git

2. Activate virtual environment
    cd player-performance-predictor/backend
    python -m venv venv
For windows:
    venv\Scripts\activate
For Mac/Linux:
    source venv/bin/activate

3. Install dependencies
    pip install -r requirements.txt

4. Install packages for frontend
    cd ../frontend
    npm install

5. In order to save the data to the database run this once
    cd ..
    python nba-player-performance-predictor\backend\player_performance_predictor\build_model\data_processing.py

6. To run the database and API
    python manage.py migrate
    python manage.py runserver

7. In a new terminal
    cd ../frontend
    npm run dev