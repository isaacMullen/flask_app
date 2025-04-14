from rapidfuzz import fuzz, process
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__) 

DATABASE = "nba.sqlite" # defining the path to the database file

def get_conn():
    conn = sqlite3.connect(DATABASE) # connecting to the database
    conn.row_factory = sqlite3.Row  # allowing for indexing rows by column name
    return conn

# home page route
@app.route("/") 
def home():
    return redirect(url_for('players')) # redirects the user to the player search when the visit home

# player search route
@app.route('/players', methods=['GET']) 
def players():
    connection = get_conn() # establish connection to database
    cursor = connection.cursor() # initialize a cursor to execute queries
    
    search_query = request.args.get('player_name', '') # get the query parameter from the URL (if there is one)
    players = [] # will store the players returned by the query
    
    cursor.execute('SELECT rowid, first_name, last_name, full_name, school, birthdate, country FROM common_player_info_fts')
    all_players = cursor.fetchall()
    
    # ----------------------------------Blackbox Begin----------------------------------
    if search_query:
        player_names = [(player['full_name'], player) for player in all_players]
        
        results = process.extract(
            search_query,   
            [name for name, _ in player_names], 
            scorer = fuzz.WRatio, 
            score_cutoff = 65, 
            limit = None
        )
        
        players = [next(player for name, player in player_names if name == match[0]) for match in results]
    # ----------------------------------Blackbox End----------------------------------
        if not players:
            cursor.execute('SELECT * FROM common_player_info_fts WHERE full_name LIKE ?', ('%' + search_query + '%',))
            players = cursor.fetchall() # storing the results inside players[]


    connection.close()

    # display the data retrieved by the query
    return render_template("players.html", players=players)

@app.route("/player/<int:fts_rowid>", methods=["GET"])
def player_details(fts_rowid):
    connection = get_conn()
    cursor = connection.cursor()

    # Get the player info from the FTS table
    cursor.execute('SELECT * FROM common_player_info_fts WHERE rowid = ?', (fts_rowid,))
    player = cursor.fetchone()

    if player:
        # Get the actual player.id using full name (or better, store a mapping if possible)
        cursor.execute('SELECT id FROM player WHERE full_name = ?', (player['full_name'],))
        player_id_row = cursor.fetchone()
        player_id = player_id_row['id'] if player_id_row else None

        # Fetch season stats using the correct player_id
        if player_id:
            cursor.execute('''
                SELECT season_id, points_per_game, assists_per_game, rebounds_per_game
                FROM player_stats_simple
                WHERE player_id = ?
                ORDER BY season_id DESC
            ''', (player_id,))
            season_stats = cursor.fetchall()
        else:
            season_stats = []

        connection.close()

        return render_template("player_details.html", player=player, season_stats=season_stats)
    else:
        connection.close()
        return "Player not found", 404





if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)
