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
    if search_query:
        # if the user provided a search parameter, execute an SQL query to retrieve the players that match the query
        cursor.execute('SELECT * FROM player WHERE full_name LIKE ?', ('%' + search_query + '%',))
        players = cursor.fetchall() # storing the results inside players[]

    connection.close()

    # display the data retrieved by the query
    return render_template("players.html", players=players)

# team search route
@app.route('/teams', methods=['GET'])
def teams():
    connection = get_conn() # establishing connection
    cursor = connection.cursor() # cursor to execute queries
    
    search_query = request.args.get('team_name', '') # gets the first query parameter if one exists
    search_query_two = request.args.get('team_abbreviation', '') # gets the second query parameter if one exists

    teams = [] # returned data will be stored in a list of objects
    if search_query:
        # if there is at least one query parameter present, search the database using the search query provided by the user
        query = '''select team.id, team.full_name, team_details.city, team_details.abbreviation, team_details.team_id
                from team 
                join team_details on team.id = team_details.team_id where team.full_name LIKE ?'''
        params = ['%' + search_query + '%'] # adding the returned data to a list       
        
        if search_query_two:
            # if there are two search qeuries, modifying the SQL query and add another parameter to search on
            query += '''and team_details.abbreviation like ?'''
            params.append('%' + search_query_two + '%')
    
        cursor.execute(query, params) # exceuting the SQL squery that was built
        teams = cursor.fetchall() # storing all returned data in teams[]
    
    connection.close()

    return render_template("teams.html", teams=teams) 

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)
