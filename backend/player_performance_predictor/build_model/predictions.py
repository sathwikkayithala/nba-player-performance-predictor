import joblib
from pymongo import MongoClient
import pandas as pd
import numpy as np
import warnings
import os

warnings.filterwarnings("ignore", category=UserWarning)

base_dir = os.path.dirname(os.path.abspath(__file__))

target_cols = ['PTS', 'AST', 'TRB', 'STL', 'BLK']

# cleaning up data, raised some warnings so did it in a less simpler way
def clean_data(df):
    mode_pos = df['Pos'].mode()[0]
    df.loc[df['Pos'].isna(), 'Pos'] = mode_pos
    median_age = df['Age'].median()
    df.loc[df['Age'].isna(), 'Age'] = median_age
    return df

# loading data
def load_data_from_mongo(db_name, collection_name):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client[db_name]
        collection = db[collection_name]
        data = pd.DataFrame(list(collection.find()))
        return data
    except Exception as e:
        print(f"Error loading data from MongoDB: {e}")
        return pd.DataFrame()

# calculating averages for recent seasons if it exists
def get_recent_seasons(df, target_season, n=3):
    filtered_df = df[df['Season'] < target_season]
    grouped = filtered_df.groupby('Player')
    
    averages = []
    
    for player, group in grouped:
        group = group.sort_values(by='Season', ascending=False)

        recent_stats = group.head(n)
        
        numeric_stats = recent_stats.select_dtypes(include=[np.number])
        averaged_stats = numeric_stats.mean().to_frame().T if not numeric_stats.empty else pd.DataFrame([[0] * len(numeric_stats.columns)], columns=numeric_stats.columns)
        averaged_stats.columns = [f"pl_avg_{col}" for col in averaged_stats.columns]

        non_numeric_stats = recent_stats[['Player', 'Age_Category', 'Pos']].iloc[0]
        
        averaged_stats['Player'] = player
        averaged_stats = averaged_stats.assign(**non_numeric_stats)
        averages.append(averaged_stats)

    final_df = pd.concat(averages, ignore_index=True)
    final_df.drop(columns=['Season', 'Pos'], errors='ignore', inplace=True)
    
    return final_df

# a function to make predictions based on loaded data for previous seasons if it exists using the saved model
def load_predictions(req_season):
    db_name = "player_stats"
    player_per_game_data = load_data_from_mongo(db_name, "player_stats_table")
    player_per_game_df = pd.DataFrame(player_per_game_data)

    player_per_game_df.drop(columns=['_id'], errors='ignore', inplace=True)
    player_prev_year = player_per_game_df[player_per_game_df['Season'] == (req_season - 1)]

    prediction_df = pd.DataFrame({
        'Player': player_prev_year['Player'],
        'Season': req_season,
        'Age': player_prev_year['Age'] + 1,
        'Pos': player_prev_year['Pos'],
    })

    prediction_df = clean_data(prediction_df)
    recent_averages_df = get_recent_seasons(player_per_game_df, req_season)

    prediction_df = prediction_df.merge(recent_averages_df, on='Player', how='left')

    non_numeric_cols = ['Age_Category', 'Pos']
    numeric_feature_cols = [
        'Season', 'Age',
        'pl_avg_PTS', 'pl_avg_AST', 
        'pl_avg_TRB', 'pl_avg_STL', 'pl_avg_BLK'
    ]

    X = prediction_df[['Player'] + numeric_feature_cols + non_numeric_cols]

    X_grouped = X.groupby('Player').agg(
        {
            'Season': 'first',
            'Age': 'first',
            **{col: 'mean' for col in numeric_feature_cols if col in X.columns},
            'Age_Category': 'first',
            'Pos': 'first'
        }
    ).reset_index()

    player_info = X_grouped[['Player', 'Age', 'Season', 'Pos']]

    X_grouped.drop(columns=['Player'], errors='ignore', inplace=True)

    X_grouped = pd.get_dummies(X_grouped, columns=non_numeric_cols, drop_first=True).astype(int)

    models = {}
    for target in target_cols:
        model_path = os.path.join(base_dir, 'saved_models', f'best_model_{target}.pkl')
        if os.path.exists(model_path):
            models[target] = joblib.load(model_path)
        else:
            print(f"Model file not found: {model_path}")
            exit(1)

    predictions_df = pd.DataFrame()

    for target in target_cols:
        target_predictions = models[target].predict(X_grouped.to_numpy())

        predictions_df[target] = target_predictions

    final_predictions_df = pd.concat([player_info.reset_index(drop=True), predictions_df.reset_index(drop=True)], axis=1)

    final_predictions_df['Player'] = final_predictions_df['Player'].astype(str)
    final_predictions_df['Pos'] = final_predictions_df['Pos'].astype(str)
    final_predictions_df['Age'] = final_predictions_df['Age'].astype(int)
    final_predictions_df['Season'] = final_predictions_df['Season'].astype(int)

    final_predictions_df[target_cols] = final_predictions_df[target_cols].round(1)

    return final_predictions_df
