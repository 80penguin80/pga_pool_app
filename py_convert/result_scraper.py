#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import requests
import psycopg2


ids = {'WM Phoenix Open': 'R2024003','The Genesis Invitational': 'R2024007',
       'Mexico Open at Vidanta':'R2024540','Cognizant Classic':'R2024010',
       'Arnold Palmer Invitational':'R2024009', 
       'THE PLAYERS Championship':'R2024011', "Texas Children's Houston Open": 'R2024020',
       'Valspar Championship':'R2024475', 'The Valero Texas Open': 'R2023041',
       'RBC Heritage' : 'R2024012', 'THE CJ CUP Byron Nelson': 'R2024019',
       'Wells Fargo Championship': 'R2024480', 'Charles Schwab Challenge': 'R2024021',
        'RBC Canadian Open' : 'R2024032', 'the Memorial Tournament presented by Workday': 'R2024023',
         'Travelers Championship' : 'R2024034', 'Rocket Mortgage Classic' : 'R2024524',
         'John Deere Classic' : 'R2024030', 'Genesis Scottish Open' : 'R2024541', '3M Open' : 'R2024525',
         'Wyndham Championship' : 'R2024013', 'FedEx St. Jude Championship' : 'R2024027'}

r1 = []
r2 = []
r3 = []
r4 = []
player_name = []
fedex_cup_points = []
official_money = []
position = []
score = []
tournament_name = []
tournament_id = []

for i,j in ids.items():
    payload = {"operationName":"TournamentPastResults","variables":{"tournamentPastResultsId":j,"year":None},"query":"query TournamentPastResults($tournamentPastResultsId: ID!, $year: Int) {\n  tournamentPastResults(id: $tournamentPastResultsId, year: $year) {\n    id\n    teams {\n      teamId\n      position\n      players {\n        id\n        firstName\n        lastName\n        shortName\n        displayName\n        abbreviations\n        abbreviationsAccessibilityText\n        amateur\n        country\n        countryFlag\n        lineColor\n        seed\n        status\n      }\n      rounds {\n        score\n        parRelativeScore\n      }\n      additionalData\n      total\n      parRelativeScore\n    }\n    rounds\n    additionalDataHeaders\n    availableSeasons {\n      year\n      displaySeason\n    }\n    winner {\n      id\n      firstName\n      lastName\n      totalStrokes\n      totalScore\n      countryFlag\n      countryName\n      purse\n      points\n      seed\n      displayPoints\n      displayPurse\n    }\n    winningTeam {\n      id\n      firstName\n      lastName\n      totalStrokes\n      totalScore\n      countryFlag\n      countryName\n      purse\n      points\n      seed\n      displayPoints\n      displayPurse\n    }\n    players {\n      id\n      position\n      player {\n        id\n        firstName\n        lastName\n        shortName\n        displayName\n        abbreviations\n        abbreviationsAccessibilityText\n        amateur\n        country\n        countryFlag\n        lineColor\n        seed\n        status\n      }\n      rounds {\n        score\n        parRelativeScore\n      }\n      additionalData\n      total\n      parRelativeScore\n    }\n  }\n}"}

    url = 'https://orchestrator.pgatour.com/graphql'

    response = requests.post(url, json = payload, headers = {'X-Api-Key':
    'da2-gsrx5bibzbb4njvhl7t37wqyl4'})

    results = response.json()


    for player in results['data']['tournamentPastResults']['players']:
        try:
            r3.append(player['rounds'][2]['score'])
            r4.append(player['rounds'][3]['score'])
            player_name.append(player['player']['displayName'])
            fedex_cup_points.append(player['additionalData'][0])
            official_money.append(player['additionalData'][1])
            position.append(player['position'])
            score.append(player['parRelativeScore'])
            tournament_name.append(j) 
            tournament_id.append(i) 
            r1.append(player['rounds'][0]['score'])
            r2.append(player['rounds'][1]['score'])
            
        except:
            break

data = {'tournament_name': tournament_id,
        'tournament_id' : tournament_name,
        'player_name' : player_name,
        'position' : position,
        'score' : score,
        'r1' : r1,
        'r2' : r2,
        'r3' : r3,
        'r4' : r4,
        'fedex_cup_points' : fedex_cup_points,
        'official_money' : official_money,
        }

df = pd.DataFrame(data)
cleaned = []

for a in df['official_money']:
    cleaned.append(a.split('$')[1].replace(',',''))

df['official_money'] = cleaned

whole_number = []

for i in df['official_money']:
    try:
        whole_number.append(int(float(i)))  # Convert to float first, then to int to strip cents
    except:
        pass

df['official_money'] = whole_number


df


# In[6]:


import pandas as pd
import psycopg2

# Load database credentials
db_creds = pd.read_csv('/users/zack burnside/desktop/database_creds.csv')

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname=db_creds['dbname'][0],
    user=db_creds['user'][0],
    password=db_creds['password'][0],
    host=db_creds['host'][0],
    port="5433"
)

# Create a cursor
cur = conn.cursor()

# Define the insert query
insert_query = """
    INSERT INTO public.tournaments_results (tournament_name, tournament_id, player_name, position, score, 
                                            r1, r2, r3, r4, fedex_cup_points, official_money)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
"""

# Execute the insert query for each row of data
for index, row in df.iterrows():  # Iterate over DataFrame rows
    cur.execute(insert_query, row.tolist())

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()

print('Data Inserted Into Table, Duplicates Ignored')


# In[7]:


import pandas as pd
import psycopg2

# updating the weekly results0
db_creds = pd.read_csv('/users/zack burnside/desktop/database_creds.csv')

def update_weekly_results():
    conn = psycopg2.connect(
    dbname=db_creds['dbname'][0],
    user=db_creds['user'][0],
    password=db_creds['password'][0],
    host=db_creds['host'][0],
    port=db_creds['port'][0]  # Use 'port' from db_creds file
)
    try:
        # Create a cursor
        cursor = conn.cursor()
        
        # SQL query to truncate the weekly_tournament_results table
        cursor.execute("TRUNCATE TABLE public.weekly_tournament_results")
        
        # SQL query to insert new data into weekly_results
        sql_query = '''
           INSERT INTO public.weekly_tournament_results (tournament_name, user_name, player_pick, prize_money)
            SELECT DISTINCT
                TRIM(up.tournament_name) AS tournament_name, 
                TRIM(up.user_name) AS user_name, 
                TRIM(up.player_pick) AS player_pick,
                CAST(FLOOR(tr.official_money::numeric) AS int) AS prize_money
            FROM 
                public.user_picks up
            JOIN 
                public.tournaments_results tr 
            ON 
                TRIM(up.tournament_name) = TRIM(tr.tournament_name)
                AND TRIM(up.player_pick) = TRIM(tr.player_name)
            WHERE NOT EXISTS (
                SELECT 1 
                FROM public.weekly_tournament_results wr
                WHERE TRIM(wr.tournament_name) = TRIM(up.tournament_name)
                AND TRIM(wr.user_name) = TRIM(up.user_name)
                AND TRIM(wr.player_pick) = TRIM(up.player_pick)
            );
        '''

        # Execute the SQL query
        cursor.execute(sql_query)
        
        # Commit the transaction
        conn.commit()
        print("Weekly results table updated successfully.")
        
    except psycopg2.Error as e:
        print(f"Error updating weekly results table: {e}")
        
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()

update_weekly_results()


# In[8]:


import pandas as pd
import psycopg2
from psycopg2 import sql

def update_user_picks():
    # File path
    file_path = 'C:/Users/zack burnside/Desktop/user_picks.csv'

    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    
    # Database connection
    conn = psycopg2.connect(
        dbname=db_creds['dbname'][0],
        user=db_creds['user'][0],
        password=db_creds['password'][0],
        host=db_creds['host'][0],
        port="5433"
    )
    cur = conn.cursor()
    
    # Drop table if it exists
    cur.execute("DROP TABLE IF EXISTS public.user_picks")
    
    # Create the table again
    create_table_query = """
    CREATE TABLE public.user_picks (
        tournament_name TEXT,
        user_name TEXT,
        date DATE,
        player_pick TEXT
    )
    """
    cur.execute(create_table_query)
    
    # Iterate through the DataFrame and update the database
    for index, row in df.iterrows():
        insert_query = sql.SQL("""
            INSERT INTO public.user_picks (tournament_name, user_name, date, player_pick)
            VALUES (%s, %s, %s, %s)
        """)
        cur.execute(insert_query, (row['tournament_name'], row['user_name'], row['date'], row['player_pick']))

    # Commit the transaction and close the connection
    conn.commit()
    cur.close()
    conn.close()

# Call the function
update_user_picks()


# In[ ]:




