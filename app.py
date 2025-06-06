from rapidfuzz import fuzz, process
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

app = Flask(__name__) 

DATABASE = "nba.sqlite" # defining the path to the database file

import sqlite3

def get_top_youtube_videos(player_id, player_name, category="", limit=10):
    # Establish a connection to the database
    connection = get_conn()
    cursor = connection.cursor()

    # Check if there are already videos for the player in this category
    cursor.execute(
        'SELECT video_id, title FROM player_videos WHERE player_id = ? AND category = ?',
        (player_id, category)
    )
    existing_videos = cursor.fetchall()

    if existing_videos:
        # Return existing videos
        print(f"Videos already exist for player ID {player_id} and category '{category}'. Skipping scraping.")
        return [{'video_id': video['video_id'], 'title': video['title']} for video in existing_videos]

    # If no videos exist for the player/category, scrape YouTube
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    search_query = f"{player_name} {category}".strip()
    driver.get(f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}")

    time.sleep(3)

    video_elements = driver.find_elements(By.ID, "video-title")
    videos = []

    for video in video_elements:
        url = video.get_attribute("href")
        title = video.get_attribute("title")

        if url and "watch?v=" in url:
            video_id = url.split("watch?v=")[-1].split("&")[0]
            videos.append({
                'title': title,
                'video_id': video_id,
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'category': category
            })

        if len(videos) >= limit:
            break

    # Insert the new videos into the database
    for video in videos:
        cursor.execute('''
            INSERT INTO player_videos (player_id, video_id, title, url, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (player_id, video['video_id'], video['title'], video['url'], video['category']))
    
    connection.commit()
    driver.quit()
    connection.close()

    return videos




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
            cursor.execute('SELECT rowid, * FROM common_player_info_fts WHERE full_name LIKE ?', ('%' + search_query + '%',))
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
        # Get the actual player.id using full name
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

        # Get the selected category from query params (e.g., ?category=Highlights)
        category = request.args.get("category", "").strip()

        # Fetch YouTube videos based on player and category
        videos = get_top_youtube_videos(player_id, player['full_name'], category=category)

        connection.close()

        return render_template(
            "player_details.html",
            player=player,
            season_stats=season_stats,
            videos=videos,
            selected_category=category  # so you can keep track of the selected one in the template
        )
    else:
        connection.close()
        return "Player not found", 404






if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=True)
