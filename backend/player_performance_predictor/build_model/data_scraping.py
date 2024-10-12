import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_position(season_data):
    max_games = season_data['G'].max()
    position = season_data[season_data['G'] == max_games]['Pos']
    return position.iloc[0] if not position.empty else None

# pulling data from bball ref from select seasons
def scrape_player_stats(seasons):
    df = []

    for season in seasons:
        url = f"https://www.basketball-reference.com/leagues/NBA_{season}_per_game.html"
        data = requests.get(url)

        if data.status_code != 200:
            print(f"Failed to retrieve data for season {season}. Status code: {data.status_code}")
            continue

        soup = BeautifulSoup(data.content, 'html.parser')
        table = soup.find(id='per_game_stats')
        seasonal_data = pd.read_html(str(table))[0]
        seasonal_data['Season'] = season
        df.append(seasonal_data)
    
    per_game_stats = pd.concat(df, ignore_index=True)
    columns_to_keep = ['Player', 'Season', 'Age', 'Team', 'Pos', 'G', 'MP', 'PTS', 'TRB', 'AST', 'STL', 'BLK', 'TOV', '3P', '3PA', '2P', '2PA', 'FT', 'FTA']
    seasonal_data = per_game_stats[columns_to_keep]

    filter_data = seasonal_data.groupby(['Player', 'Season']).agg({
        'G': 'sum',
        'Age': 'mean',
        'MP': 'mean',
        'PTS': 'mean',
        'AST': 'mean',
        'TRB': 'mean',
        'STL': 'mean',
        'BLK': 'mean',
        'TOV': 'mean',
        '3P': 'mean',
        '3PA': 'mean',
        '2P': 'mean',
        '2PA': 'mean',
        'FT': 'mean',
        'FTA': 'mean',
    }).reset_index()

    filter_data['Pos'] = (seasonal_data.groupby(['Player', 'Season']).apply(get_position).reset_index(drop=True))

    return filter_data

# saving data to the csv file
if __name__ == "__main__":
    seasons = [str(year) for year in range(2006, 2025)]
    player_stats = scrape_player_stats(seasons)

    player_stats = player_stats[player_stats['Player'] != 'League Average']

    if not player_stats.empty:
        player_stats.to_csv('data/player_stats.csv', index=False)
    else:
        print("No player stats to save.")
