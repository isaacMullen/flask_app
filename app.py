from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "nba.sqlite"

def get_conn():
    conn = sqlite3.connect(DATABASE) # connecting to predefined database
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return redirect(url_for('players'))

@app.route('/players', methods=['GET'])
def players():
    connection = get_conn()
    cursor = connection.cursor()
    
    search_query = request.args.get('player_name', '')

    players = []
    if search_query:
        cursor.execute('SELECT * FROM player WHERE full_name LIKE ?', ('%' + search_query + '%',))
        players = cursor.fetchall()

    connection.close()

    return render_template("players.html", players=players)

@app.route('/teams', methods=['GET'])
def teams():
    connection = get_conn()
    cursor = connection.cursor()
    
    search_query = request.args.get('team_name', '') # gets the query parameter from URL (users search)
    search_query_two = request.args.get('team_abbreviation', '') 

    teams = []
    if search_query:
        query = '''select team.id, team.full_name, team_details.city, team_details.abbreviation, team_details.team_id
                from team 
                join team_details on team.id = team_details.team_id where team.full_name LIKE ?'''
        params = ['%' + search_query + '%']        
        
        if search_query_two:
            query += '''and team_details.abbreviation like ?'''
            params.append('%' + search_query_two + '%')
    
        cursor.execute(query, params)
        teams = cursor.fetchall()
    
    connection.close()

    return render_template("teams.html", teams=teams) 

if __name__ == "__main__":
    app.run(debug=True)
