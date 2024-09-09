
from flask import Flask, request, render_template, redirect, url_for, session
import psycopg2
import bcrypt
import random
import string
import pandas as pd
import psycopg2
import os

db_creds = pd.read_csv('/users/zack burnside/desktop/database_creds.csv')

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

usernames = [
    "Z",
    "Timmy Chips",
    "Goob",
    "C",
    "Steve",
    "Sus",
    "DV3",
    "Jlo",
    "Ty Dolla $$$",
    "Ryan",
    "Mike D",
    "Mando",
    "Eddie Buckets",
    "Garrett",
    "T Sully"
]

user_passwords = {username: generate_random_password() for username in usernames}

def get_db_connection():
    conn = psycopg2.connect(
        dbname=db_creds['dbname'][0],
        user=db_creds['user'][0],
        password=db_creds['password'][0],
        host=db_creds['host'][0],
        port=db_creds['port'][0]
    )
    return conn

def upload_user_logins():
    conn = get_db_connection()
    cur = conn.cursor()

    # Insert query
    insert_query = """
        INSERT INTO public.user_logins (username, password)
        VALUES (%s, %s)
    """
    
    # Insert data
    for username, password in user_passwords.items():
        try:
            cur.execute(insert_query, (username, password))
        except Exception as e:
            print(f"Error inserting {username}: {e}")

    # Commit changes and close connection
    conn.commit()
    cur.close()
    conn.close()
    print("User logins uploaded successfully.")

upload_user_logins()




