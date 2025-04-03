from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

DATABASE = "test.db"

def get_conn():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    connection = get_conn()
    cursor = connection.cursor()
    
    try:
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        print(f"Users fetched: {users}")  # Log the fetched data
    except sqlite3.Error as e:
        print(f"Database error: {e}")  # Catch any database errors and log them
        users = []
    finally:
        connection.close()

    return render_template("index.html", items=users)

if __name__ == "__main__":
    app.run(debug=True)
