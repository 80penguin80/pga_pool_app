#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_leaderboard():
    results = requests.get('https://www.espn.com/golf/leaderboard', headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'})

    soup = BeautifulSoup(results.text, 'html.parser')

    rank = []
    player_name = []
    player_country = []
    score_to_par = []
    round1_score = []
    round2_score = []
    round3_score = []
    round4_score = []
    total_score = []

    for player in soup.find_all('tr', class_='PlayerRow__Overview PlayerRow__Overview--expandable Table__TR Table__even'):
        rank.append(player.select_one('td:nth-of-type(2)').text)
        player_name.append(player.select_one('td:nth-of-type(3) a').text)
        player_country.append(player.select_one('td:nth-of-type(3) img')['alt'])
        score_to_par.append(player.select_one('td:nth-of-type(4)').text)
        round1_score.append(player.select_one('td:nth-of-type(5)').text)
        round2_score.append(player.select_one('td:nth-of-type(6)').text)
        round3_score.append(player.select_one('td:nth-of-type(7)').text)
        round4_score.append(player.select_one('td:nth-of-type(8)').text)
        total_score.append(player.select_one('td:nth-of-type(9)').text)
    
    data = {
        'Rank': rank,
        'Player Name': player_name,
        'Country': player_country,
        'Score to Par': score_to_par,
        'Round 1 Score': round1_score,
        'Round 2 Score': round2_score,
        'Round 3 Score': round3_score,
        'Round 4 Score': round4_score,
        'Total Score': total_score
    }

    df = pd.DataFrame(data)
    
    return df

scrape_leaderboard()

