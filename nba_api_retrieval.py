from nba_api.stats.endpoints import playercareerstats
import sqlite3
import time

def get_player_season_stats(player_id):
    try:
        print(f"Fetching stats for player ID: {player_id}")
        
        # Fetch career stats for the player
        stats = playercareerstats.PlayerCareerStats(player_id=player_id)
        df = stats.get_data_frames()[0]
        
        # Debug: Print the raw dataframe to check its contents
        print(f"Raw stats for player {player_id}:\n{df.head()}")  # Print top 5 rows of the dataframe
        
        # Check if dataframe is empty
        if df.empty:
            print(f"No data found for player ID {player_id}")
            return []

        # Loop through each season's stats and calculate the average points, rebounds, and assists
        season_data = []
        for _, row in df.iterrows():
            season_id = row['SEASON_ID']

            # Debug: Print individual stats for each row
            print(f"Processing season: {season_id} - PTS: {row['PTS']}, AST: {row['AST']}, REB: {row['REB']}, GP: {row['GP']}")

            # Ensure 'PTS', 'AST', 'REB', and 'GP' are numeric and check for missing data
            try:
                games_played = int(row['GP']) if 'GP' in row else 0
                points = float(row['PTS']) if 'PTS' in row else 0
                assists = float(row['AST']) if 'AST' in row else 0
                rebounds = float(row['REB']) if 'REB' in row else 0
            except ValueError:
                print(f"Error converting stats for player {player_id}, season {season_id}")
                continue  # Skip this season if there's a data conversion issue

            # Calculate averages (only if GP > 0)
            if games_played > 0:
                ppg = points / games_played  # Points per game
                apg = assists / games_played  # Assists per game
                rpg = rebounds / games_played  # Rebounds per game
            else:
                ppg = apg = rpg = 0  # If no games played, set stats to 0

            # Store the results for each season
            season_data.append({
                'season_id': season_id,
                'ppg': ppg,
                'apg': apg,
                'rpg': rpg
            })
        
        return season_data
    
    except Exception as e:
        print(f"Error fetching stats for {player_id}: {e}")
        return []

# 🔗 Connect to your SQLite database
conn = sqlite3.connect('nba.sqlite')
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

# ✅ Fetch player IDs from your existing `players` table
cursor.execute("SELECT id FROM player")  # LIMIT for testing
player_ids = cursor.fetchall()

# Debugging: Print out the player IDs
print(f"Player IDs fetched: {player_ids}")

# 🔁 Loop through and process each player
for (player_id,) in player_ids:
    # Check if this player already has stats in the table
    cursor.execute('SELECT 1 FROM player_stats_simple WHERE player_id = ? LIMIT 1', (player_id,))
    if cursor.fetchone():
        print(f"Skipping player ID {player_id}: Data already exists.")
        continue

    print(f"Processing player with ID: {player_id}")
    season_data = get_player_season_stats(player_id)

    if season_data:
        for season in season_data:
            print(f"Inserting data for player ID {player_id}, season {season['season_id']}")
            cursor.execute('''
                INSERT OR REPLACE INTO player_stats_simple (player_id, season_id, points_per_game, assists_per_game, rebounds_per_game)
                VALUES (?, ?, ?, ?, ?)
            ''', (player_id, season['season_id'], season['ppg'], season['apg'], season['rpg']))
        conn.commit()
    else:
        print(f"Skipping player ID {player_id}: No valid stats returned.")
    
    time.sleep(0.6)

# ✅ Clean up
conn.close()
