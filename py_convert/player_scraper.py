#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import requests

url  = 'https://orchestrator.pgatour.com/graphql'

payload = {"operationName":"PlayerDirectory","variables":{"tourCode":"R"},"query":"query PlayerDirectory($tourCode: TourCode!, $active: Boolean) {\n  playerDirectory(tourCode: $tourCode, active: $active) {\n    tourCode\n    players {\n      id\n      isActive\n      firstName\n      lastName\n      shortName\n      displayName\n      alphaSort\n      country\n      countryFlag\n      headshot\n      playerBio {\n        id\n        age\n        education\n        turnedPro\n      }\n    }\n  }\n}"}

response = requests.post(url, json = payload, headers = {'X-Api-Key':
'da2-gsrx5bibzbb4njvhl7t37wqyl4'}
)

results = response.json()

player_name = []
player_id = []
player_nationality = []


for player in results['data']['playerDirectory']['players']:
    player_name.append(player['displayName'])
    player_id.append(player['id'])
    player_nationality.append(player['countryFlag'])


# In[4]:


data = {'player_name': player_name,
        'player_id' : player_id,
        'player_nationality' : player_nationality}

df = pd.DataFrame(data)
df


# In[5]:


df.to_csv('/users/zack burnside/desktop/player_db.csv')


# In[ ]:




