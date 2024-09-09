#!/usr/bin/env python
# coding: utf-8

# In[6]:


from flask import Flask, request, render_template_string, redirect, url_for, render_template
from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime
import bcrypt
import os
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import random
import string
import nbimporter
import current_tournament_leaderboard
import current_tournament_information
import logging
import seaborn as sns
import os
from dotenv import load_dotenv


# In[9]:


app = Flask(__name__, template_folder='c:\\Users\\Zack Burnside\\Desktop\\pga_pool\\templates')

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'penguin123crazy1--')
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

load_dotenv()


logging.basicConfig(level=logging.ERROR)
# Functions
def authenticate_user(username, password):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            SELECT password
            FROM public.user_logins
            WHERE username = %s
        """
        cur.execute(query, (username,))
        result = cur.fetchone()

        if result:
            stored_password = result[0]
            if stored_password == password:
                return True
            else:
                print("Password does not match.")
                return False
        else:
            print("Username not found.")
            return False

    except psycopg2.Error as e:
        print(f"Database error during authentication: {e}")
        return False
    except Exception as e:
        print(f"Error during authentication: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn

def fetch_user_results(username=None):
    conn = get_db_connection()
    cur = conn.cursor()
    if username:
        cur.execute("SELECT user_name, player_pick, prize_money, tournament_name FROM public.weekly_tournament_results WHERE user_name = %s", (username,))
    else:
        cur.execute("SELECT user_name, player_pick, prize_money, tournament_name FROM public.weekly_tournament_results")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def fetch_tournament_info(tournament_name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT index, tournament_name, dates, 
        to_char(purse::numeric, 'FM$999,999,999,999.00') 
        FROM public.tournament_info
        WHERE tournament_name = %s
    """, (tournament_name,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def fetch_tournament_results(tournament_name):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_name, player_pick, prize_money 
        FROM public.weekly_tournament_results 
        WHERE tournament_name = %s
    """, (tournament_name,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def fetch_stats_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT player_pick, COUNT(*) as pick_count FROM public.user_picks GROUP BY player_pick ORDER BY pick_count DESC")
    data = cursor.fetchall()
    conn.close()
    return data

def fetch_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT username FROM public.user_logins")
    data = cursor.fetchall()
    conn.close()
    return data

def fetch_accuracy_data():
    query = """
    WITH picked_weeks AS (
        SELECT
            p.player_pick AS golfer_name,
            p.date AS pick_date,
            p.tournament_name
        FROM user_picks p
    ),
    earned_weeks AS (
        SELECT
            r.player_name AS golfer_name,
            r.tournament_name
        FROM tournaments_results r
        WHERE r.official_money > 0
    ),
    combined AS (
        SELECT
            pw.golfer_name,
            pw.tournament_name,
            CASE
                WHEN ew.tournament_name IS NOT NULL THEN 1
                ELSE 0
            END AS earned
        FROM picked_weeks pw
        LEFT JOIN earned_weeks ew
        ON pw.golfer_name = ew.golfer_name AND pw.tournament_name = ew.tournament_name
    )
    SELECT
        golfer_name,
        COUNT(DISTINCT tournament_name) AS weeks_picked,
        SUM(earned) AS weeks_with_earnings,
        ROUND(
            (SUM(earned)::numeric / COUNT(DISTINCT tournament_name)) * 100,
            2
        ) AS pick_accuracy_rate
    FROM combined
    GROUP BY golfer_name
    ORDER BY pick_accuracy_rate DESC;
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]  # Get column names
    conn.close()
    
    return pd.DataFrame(data, columns=columns)

def plot_accuracy_data(df):
    plt.figure(figsize=(10, 6))
    sns.barplot(x='golfer_name', y='pick_accuracy_rate', data=df)
    plt.xticks(rotation=90)
    plt.title('Pick Accuracy Rate by Golfer')
    plt.xlabel('Golfer Name')
    plt.ylabel('Pick Accuracy Rate (%)')
    plt.tight_layout()  # Adjust layout to prevent clipping
    plt.show()

def leaderboard_chart():
    # Fetch leaderboard data and convert it to a DataFrame
    df = pd.DataFrame(fetch_leaderboard(), columns=['username', 'prize_money'])
    
    # Create a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(df['username'], df['prize_money'], color='skyblue')
    
    # Add titles and labels
    plt.title('Leaderboard - Total Prize Money by User')
    plt.xlabel('User')
    plt.ylabel('Total Prize Money')
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Add grid for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Display the chart
    plt.tight_layout()
    plt.show()

def create_bar_chart(data):
    golfers = [row[0] for row in data]
    pick_count = [row[1] for row in data]

    fig, ax = plt.subplots(figsize=(20, 12))
    bars = ax.bar(golfers, pick_count, color='skyblue')

    for bar in bars:
        count_value = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(count_value), ha='center', va='bottom', fontsize=8)

    ax.set_title('Most Picked Golfer', fontsize=12)
    ax.set_xlabel('Golfer Name', fontsize=10)
    ax.set_ylabel('Pick Count', fontsize=10)
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.grid(axis='y', linestyle='--')
    plt.tight_layout()

    # Convert plot to PNG image and encode it in base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = buffer.getvalue()
    buffer.close()
    plot_data = base64.b64encode(plot_data).decode('utf-8')
    plt.close()

    return plot_data

def has_already_picked(username, tournament, pick):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT COUNT(*) FROM user_picks 
            WHERE user_name = %s AND tournament_name = %s
            """, (username, tournament))
        tournament_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM user_picks 
            WHERE user_name = %s AND player_pick = %s
            """, (username, pick))
        golfer_count = cursor.fetchone()[0]

        return tournament_count > 0 or golfer_count > 0
    finally:
        cursor.close()
        conn.close()

def insert_pick(username, tournament, pick):
    if has_already_picked(username, tournament, pick):
        raise ValueError("You have already picked this golfer or tournament.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO user_picks (user_name, tournament_name, player_pick) VALUES (%s, %s, %s)",
            (username, tournament, pick)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def fetch_leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_name AS username, SUM(prize_money) AS total_prize_money
        FROM public.weekly_tournament_results
        GROUP BY user_name
        ORDER BY total_prize_money DESC
    """)
    return cursor.fetchall()

def get_player_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT player_name FROM public.players ORDER BY player_name DESC")
    players = cursor.fetchall()
    cursor.close()
    conn.close()
    return [player[0] for player in players]

# App Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()  # Clear the session data
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if authenticate_user(username, password):
            session['username'] = username
            session.permanent = False  # Session expires when the browser is closed
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/results', methods=['GET', 'POST'])
def results():
    selected_user = None
    if request.method == 'POST':
        selected_user = request.form['username']
    
    results_data = fetch_user_results(selected_user)
    usernames = [row[0] for row in fetch_user_results()]  # Fetch usernames for the dropdown
    
    return render_template_string('results.html', results_data=results_data, usernames=set(usernames), selected_user=selected_user)

@app.route('/get_players')
def get_players():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT player_name FROM player_list")  # Adjust query as needed
    players = cursor.fetchall()

    cursor.close()
    conn.close()

    player_names = [player[0] for player in players]
    return jsonify(player_names)

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    logged_in_user = session['username']

    username = ''
    tournament = ''
    pick = ''

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                def total_money_won():
                    cursor.execute("SELECT SUM(prize_money) FROM public.weekly_tournament_results;")
                    total_money_ = cursor.fetchone()
                    return total_money_[0] if total_money_ else 0

                def total_money_left():
                    cursor.execute("SELECT SUM(purse::numeric) AS total_purse FROM public.tournament_info WHERE dates::date > CURRENT_DATE;")
                    total_money = cursor.fetchone()
                    return f"${total_money[0]:,.2f}" if total_money and total_money[0] is not None else "$0.00"

                def fetch_leaderboard():
                    cursor.execute("""
                        SELECT user_name AS username, SUM(prize_money) AS total_prize_money
                        FROM public.weekly_tournament_results
                        GROUP BY user_name
                        ORDER BY total_prize_money DESC
                    """)
                    return cursor.fetchall()

                cursor.execute("SELECT DISTINCT player_name FROM public.players")
                golfers = [row[0] for row in cursor.fetchall()]

                last_winner = 'TBD'
                next_tournament = 'TBD'
                total_moneyWon = total_money_won()
                total_moneyLeft = total_money_left()
                leaderboard_data = fetch_leaderboard()
                
    except Exception as e:
        print(f"Error fetching data: {e}")
        last_winner, next_tournament, total_moneyWon, total_moneyLeft, leaderboard_data, golfers = "N/A", "N/A", 0, "$0.00", [], []

    if request.method == 'POST':
        form_username = request.form.get('username', '').strip()
        tournament = request.form.get('tournament', '').strip()
        pick = request.form.get('pick', '').strip()

        if form_username != logged_in_user:
            return "Error: You are not authorized to make this pick for another user."

        if not form_username or not tournament or not pick:
            print(f"Form data: username={form_username}, tournament={tournament}, pick={pick}")
            return "Error: Missing form fields."

        try:
            insert_pick(form_username, tournament, pick)
            return f'Thank you! Your pick is {pick}.'
        except ValueError as ve:
            print(f"Validation error: {ve}")
            return str(ve)
        except Exception as e:
            print(f"Error inserting pick: {e}")
            return "Error inserting pick."

    return render_template(
        'index.html',
        last_winner=last_winner,
        next_tournament=next_tournament,
        total_moneyWon=total_moneyWon,
        total_moneyLeft=total_moneyLeft,
        usernames=[logged_in_user],
        tournaments=[
            "WM Phoenix Open", "The Genesis Invitational", "Mexico Open at Vidanta", 
            "Cognizant Classic", "Arnold Palmer Invitational", 
            "THE PLAYERS Championship", "Valspar Championship", "Texas Children's Houston Open", 
            "The Valero Texas Open", "Masters Tournament", "RBC Heritage", "THE CJ CUP Byron Nelson", 
            "Wells Fargo Championship", "PGA Championship", "Charles Schwab Challenge", 
            "RBC Canadian Open", "the Memorial Tournament presented by Workday", "U.S. Open", 
            "Travelers Championship", "Rocket Mortgage Classic", "John Deere Classic", 
            "Genesis Scottish Open", "The Open Championship", "3M Open", "Wyndham Championship", 
            "FedEx St. Jude Championship", "BMW Championship", "TOUR Championship"
        ],
        current_tournament_info=current_tournament_information.tournament_information(),
        leaderboard_data=leaderboard_data,
        golfers=golfers
)

@app.route('/tournament_results/<tournament_name>')
def tournament_results(tournament_name):
    results_data = fetch_tournament_results(tournament_name)
    blank_query_data = fetch_tournament_info(tournament_name)  # Use fetch_tournament_info for BLANK QUERY data
    tournaments = [
        "WM Phoenix Open", "The Genesis Invitational", "Mexico Open at Vidanta", 
        "Cognizant Classic", "Arnold Palmer Invitational", 
        "THE PLAYERS Championship", "Valspar Championship", "Texas Children's Houston Open", 
        "The Valero Texas Open", "Masters Tournament", "RBC Heritage", "THE CJ CUP Byron Nelson", 
        "Wells Fargo Championship", "PGA Championship", "Charles Schwab Challenge", 
        "RBC Canadian Open", "the Memorial Tournament presented by Workday", "U.S. Open", 
        "Travelers Championship", "Rocket Mortgage Classic", "John Deere Classic", 
        "Genesis Scottish Open", "The Open Championship", "3M Open", "Wyndham Championship", 
        "FedEx St. Jude Championship", "BMW Championship", "TOUR Championship"
    ]
    return render_template('tournament_results.html', tournament_name=tournament_name, results_data=results_data, blank_query_data=blank_query_data, tournaments=tournaments)

@app.route('/rules')
def rules():
    return render_template('rules.html')

if __name__ == "__main__":
    app.run()


# In[ ]:




