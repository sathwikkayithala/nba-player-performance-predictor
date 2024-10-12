import pandas as pd
from pymongo import MongoClient
import numpy as np

# ensure csv data is clean
def save_clean_data_csv(data_path):
    df = pd.read_csv(data_path)

    cleaned_df = clean_data(df)
    cleaned_df = get_age_cat(cleaned_df)

    cleaned_df.to_csv(data_path, index=False)

    return cleaned_df

# cleans data, filling in null values
def clean_data(df):
    mode_pos = df['Pos'].mode()[0]
    df['Pos'].fillna(mode_pos, inplace=True)

    stat_columns = ['MP', 'PTS', 'AST', 'TRB', 'STL', 'BLK', 'TOV', '3P', '3PA', '2P', '2PA', 'FT', 'FTA']
    df[stat_columns] = df[stat_columns].fillna(0)

    df['Age'].fillna(df['Age'].median(), inplace=True)

    df['G'] = df['G'].astype('int64')
    df['Age'] = df['Age'].astype('int64')

    for col in stat_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df

# group players by ages of their performance and athletic primes
def get_age_cat(df):
    bins = [0, 20, 25, 31, 35, 40]
    labels = ['Premature', 'Young', 'Prime', 'Veteran', 'Old']
    df['Age_Category'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
    return df

# get the std of players by their position
def calculate_std(df):
    stats = ['G', 'MP', 'PTS', 'AST', 'TRB', 'STL', 'BLK', 'TOV', '3P', '3PA', '2P', '2PA', 'FT', 'FTA']

    for col in stats:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    std_features = df.groupby(['Pos', 'Age'])[stats].std().reset_index()
    std_features.columns = ['Pos', 'Age'] + [f'{m}_std' for m in stats]

    for col in stats:
        std_features[f'{col}_std'].fillna(0, inplace=True)

    return std_features

# get league averages by position and ages
def calculate_league_averages(df):
    stats = ['G', 'MP', 'PTS', 'AST', 'TRB', 'STL', 'BLK', 'TOV', '3P', '3PA', '2P', '2PA', 'FT', 'FTA']
    
    for col in stats:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    league_avg = df.groupby(['Pos', 'Age']).mean(numeric_only=True).reset_index()

    league_avg = league_avg.drop(['Season'], axis=1)

    league_avg.columns = ['Pos', 'Age'] + [f'lg_{m}_avg' for m in stats]

    for col in stats:
        league_avg[f'lg_{col}_avg'].fillna(0, inplace=True)

    return league_avg

# initializing new player based on mandatory params
def get_new_player_init(name, age, pos, season):
    new_player_data = {
        'Player': [name],
        'Age': [age],
        'Pos': [pos],
        'Season': [season],
        'MP': [0],
        'PTS': [0],
        'AST': [0],
        'TRB': [0],
        'STL': [0],
        'BLK': [0],
        'TOV': [0],
        '3P': [0],
        '3PA': [0],
        '2P': [0],
        '2PA': [0],
        'FT': [0],
        'FTA': [0]
    }
    
    return pd.DataFrame(new_player_data)

# gets last 3 seasons to predict their performance
def get_recent_seasons(df, n=3):
    recent_stats = []
    averages = []

    grouped = df.groupby('Player')
    for player, group in grouped:
        group = pd.DataFrame(group)
        group = group.sort_values(by='Season', ascending=False)

        if len(group) == 0:
            empty_stats = pd.DataFrame([[0] * (len(group.columns) - 1)], columns=group.columns.drop('Player'))
            empty_stats['Player'] = player
            recent_stats.append(empty_stats)

            empty_avg = pd.DataFrame([[0] * (len(group.columns) - 1)], columns=[f'pl_avg_{col}' for col in group.columns.drop('Player')])
            empty_avg['Player'] = player
            averages.append(empty_avg)
        else:
            if len(group) < n:
                stats = group.tail(len(group))
            else:
                stats = group.tail(n)

            recent_stats.append(stats)
            numeric_stats = stats.select_dtypes(include=[np.number])
            averaged_stats = numeric_stats.mean().to_frame().T
            averaged_stats.columns = [f"pl_avg_{col}" for col in averaged_stats.columns]
            averaged_stats['Player'] = player
            averages.append(averaged_stats)

    recent_stats_df = pd.concat(recent_stats, ignore_index=True)
    averages_df = pd.concat(averages, ignore_index=True)
    final_df = recent_stats_df.merge(averages_df, on='Player')
    final_df = final_df.drop(['pl_avg_Season', 'pl_avg_Age'], axis=1)
    return final_df

# function to save data
def upload_to_mongo(df, db_name, collection_name):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    collection = db[collection_name]

    data_dict = df.to_dict('records')
    collection.insert_many(data_dict)

    print(f"Data successfully saved to {db_name}.{collection_name}")

# savin csv data to mongodb
if __name__ == "__main__":
    data_path = "data/player_stats.csv"
    db_name = "player_stats"

    cleaned_df = save_clean_data_csv(data_path)
    upload_to_mongo(cleaned_df, db_name, "player_stats_table")