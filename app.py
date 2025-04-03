from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

items = ["Isaac", "Mike", "Jack", "Adam", "Joey"]

@app.route("/")
def index():
    return render_template("index.html", items=items)


if __name__ == "__main__":
    app.run(debug=True)
