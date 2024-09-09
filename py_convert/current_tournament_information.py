#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import pandas as pd

def tournament_information():
    results = requests.get('https://www.espn.com/golf/leaderboard', headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'})

    soup = BeautifulSoup(results.text, 'html.parser')

    dates = soup.find('span', class_ = 'Leaderboard__Event__Date n7').text
    event_name = soup.find('h1', class_ = 'headline headline__h1 Leaderboard__Event__Title').text
    course_name = soup.find('div', class_ = 'Leaderboard__Course__Location n8 clr-gray-04').text.split(' -')[0]
    location = soup.find('div', class_ = 'Leaderboard__Course__Location n8 clr-gray-04').text.split('- ')[1]
    yardage = soup.find('div', class_ = 'Leaderboard__Courses').text.split('Yards')[-1].split('P')[0]
    purse = soup.find('div', class_ = 'Leaderboard__Courses').text.split('Purse')[-1].split('P')[0]
    previous_winner = soup.find('div', class_ = 'Leaderboard__Courses').text.split('Previous Winner')[-1]

    data = {'Event Name' : event_name,
            'Dates': dates,
            'Course Name' : course_name,
            'Locations' : location,
            'Yardage' : yardage,
            'Purse' : purse,
            'Previous Winner' : previous_winner
                }
    return data

tournament_information()


# In[ ]:




