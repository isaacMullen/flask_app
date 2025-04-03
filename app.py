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

    player = cursor.fetchall()
    connection.close()

    return render_template("players.html", players=players)

@app.route('/teams', methods=['GET'])
def teams():
    connection = get_conn()
    cursor = connection.cursor()
    
    search_query = request.args.get('team_name', '')

    teams = []
    if search_query:
        cursor.execute('SELECT * FROM team WHERE full_name LIKE ?', ('%' + search_query + '%',))
        teams = cursor.fetchall()

    team = cursor.fetchall()
    connection.close()

    return render_template("teams.html", teams=teams)

if __name__ == "__main__":
    app.run(debug=True)
