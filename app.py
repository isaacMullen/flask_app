from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

DATABASE = "test.db"

def get_conn():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

items = ["Isaac", "Mike", "Jack", "Adam", "Joey"]

@app.route("/")
def index():
    connection = get_conn()
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    

    connection.close()

    return render_template("index.html", items=users)

if __name__ == "__main__":
    app.run(debug=True)
