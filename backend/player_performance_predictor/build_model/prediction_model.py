import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from lightgbm import LGBMRegressor
from data_processing import get_recent_seasons

# load data from the data base
def load_data_from_mongo(db_name, collection_name):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    collection = db[collection_name]
    
    data = pd.DataFrame(list(collection.find()))
    return data

# using mse to evaluate the model and getting a % for a more clear understanding
def evaluate_model(y_true, y_pred):    
    mse = mean_squared_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    mse_percent = []
    for i in range(y_true.shape[1]):
        non_zero_mask = (y_true[:, i] != 0)
        if non_zero_mask.any():
            mse_col = mean_squared_error(y_true[non_zero_mask, i], y_pred[non_zero_mask, i])
            mean_y_true_col = np.mean(y_true[non_zero_mask, i])
            if mean_y_true_col != 0:
                mse_percent.append((mse_col / mean_y_true_col) * 100)
            else:
                mse_percent.append(np.nan)
        else:
            mse_percent.append(np.nan)
    
    return mse, r2, np.nanmean(mse_percent)

# building the model
if __name__ == "__main__":
    db_name = "player_stats"
    player_per_game_data = load_data_from_mongo(db_name, "player_stats_table")

    player_per_game_df = pd.DataFrame(player_per_game_data)

    player_per_game_df.drop(columns=['_id'], errors='ignore', inplace=True)

    player_per_game_df = get_recent_seasons(player_per_game_df)

    player_stats = player_per_game_df.sort_values(by=['Player', 'Season'])

    non_numeric_cols = ['Age_Category', 'Pos']
    numeric_feature_cols = [
        'Season', 'Age',
        'pl_avg_PTS', 'pl_avg_AST', 'pl_avg_TRB', 'pl_avg_STL', 'pl_avg_BLK'
    ]

    feature_cols = numeric_feature_cols + non_numeric_cols
    target_cols = ['PTS', 'AST', 'TRB', 'STL', 'BLK']

    X = player_stats[feature_cols]
    y = player_stats[target_cols]

    X = pd.get_dummies(X, columns=non_numeric_cols, drop_first=True).astype(int)

    X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=0.4, random_state=42)
    X_train, X_valid, y_train, y_valid = train_test_split(X_train_val, y_train_val, test_size=0.5, random_state=42)


    # found these params to be realistic
    lgbm_params = {
        'objective': 'regression',
        'metric': 'mse',
        'boosting_type': 'gbdt',
        'learning_rate': 0.01,
        'n_estimators': 10000,
        'num_leaves': 50,
        'max_depth': 7,
        'random_state': 42
    }

    models = {}
    y_preds = []

    # separately training the model for each stat
    for target in target_cols:
        model = LGBMRegressor(**lgbm_params)
        
        model.fit(
            X_train, 
            y_train[target],
            eval_set=[(X_valid, y_valid[target])],
            eval_metric='mse'
        )
        
        y_pred = model.predict(X_test)
        
        y_preds.append(y_pred)
        
        models[target] = model

    y_preds = np.vstack(y_preds).T

    mse, r2, mse_percent = evaluate_model(y_test.to_numpy(), y_preds)

    print("Individual Models Mean Squared Error (Percentage):", mse_percent)
    print("Individual Models R2 Score:", r2)

    # saving all models
    for target in target_cols:
        joblib.dump(models[target], f'saved_models/best_model_{target}.pkl')
