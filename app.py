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
    
    cursor.execute('SELECT full_name, * FROM common_player_info_fts')
    all_players = cursor.fetchall()
    
    # ----------------------------------Blackbox Begin----------------------------------
    if search_query:
        player_names = [(player['full_name'], player) for player in all_players]
        
        results = process.extract(
            search_query,   
            [name for name, _ in player_names], 
            scorer=fuzz.WRatio, 
            score_cutoff=65, 
            limit=10
        )
        
        players = [next(player for name, player in player_names if name == match[0]) for match in results]
    # ----------------------------------Blackbox End----------------------------------
        if not players:
            cursor.execute('SELECT * FROM common_player_info_fts WHERE full_name LIKE ?', ('%' + search_query + '%',))
            players = cursor.fetchall() # storing the results inside players[]


    connection.close()

    # display the data retrieved by the query
    return render_template("players.html", players=players)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)
