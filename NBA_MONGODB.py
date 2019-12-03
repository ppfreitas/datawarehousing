#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 18:43:04 2019
@author: pedro
"""
import pymongo
from urllib.request import urlopen
from bs4 import BeautifulSoup, Comment
import pandas as pd
import numpy as np

def get_months(season):
    year = str(season)
    url = "https://www.basketball-reference.com/leagues/NBA_" + year + "_games.html"
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')
    
    links = [a['href'] for a in soup.find_all('a', href=True)]
    link_months = [link for link in links if ('NBA_'+year+'_games-' in link) and ('html' in link)]
    return link_months

def get_list_of_games(urlarg):
    url = "https://www.basketball-reference.com"+urlarg
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')

    links = [a['href'] for a in soup.find_all('a', href=True)]
    link_bs = [link for link in links if ('boxscore' in link) and ('html' in link)]
    return link_bs

def get_players_score(team):
    id_str = "box-"+str(team)+"-game-basic"
    soup2 = soup.find_all(id=id_str)
    player_stats = [[td.getText() for td in soup2[0].find_all('tr')[i:][0].find_all('td')]
                for i in range(2,len(soup2[0].find_all('tr'))-1)]
    player_names = [[td.getText() for td in soup2[i].find_all('a')]
                for i in range(len(soup2))]
    player_names = [name.replace('.','') for name in player_names[0]]
    player_stats = [player for player in player_stats if len(player) > 0]
    headers = [th.getText() for th in soup.findAll('tr')[1].findAll('th')]
    box_score = pd.DataFrame(player_stats, columns=headers[1:], index = player_names)
    
    return box_score

def get_game_score(soup):
    
    for tr in soup.find_all(id='all_line_score'):
        comment = tr.find(text=lambda text:isinstance(text, Comment))
        commentsoup = BeautifulSoup(comment ,'html.parser')
        
    rows = commentsoup.findAll('tr')
    game_score = [[td.getText() for td in rows[i].findAll('td')]
                for i in range(len(rows))]
    game_score = [score for score in game_score if len(score) > 0]

    header = [[td.getText() for td in rows[i].findAll('th')]
                for i in range(1,len(rows))]
    header = [head for head in header if len(head) > 0]
    header = header[0]
    teamA = game_score[0][0]
    teamH = game_score[1][0]
    
    return pd.DataFrame(game_score, columns=header).set_index('\xa0'), teamA, teamH

client = pymongo.MongoClient("localhost", 27017)

db = client['nba_official2']
cursor = db.games.find({},{"game_id":1,"_id":False})
old_games = ['/boxscores/' + doc['game_id'] + '.html' for doc in cursor]

season = 2020
link_months = get_months(season)

games = [] #list for the url for all games of the season
for i in link_months:
    games = games + get_list_of_games(i)

games = [game for game in games if game not in old_games]

games_dict_list = []

if len(games) != 0:
    for i in range(len(games)):
        url = "https://www.basketball-reference.com" + games[i]
        html = urlopen(url)
        soup = BeautifulSoup(html, 'html.parser')
        game_df, teamA, teamH = get_game_score(soup)
        teamA_stats = get_players_score(teamA)
        teamH_stats = get_players_score(teamH)
        game_id = url[-17:-5]
        game_date = url[-17:-9]
        
        game_dict = {'game_id':game_id, 'game_date':game_date, 'teamA':teamA,
                     'teamH':teamH, 'game_score':game_df.to_dict(orient='index'),
                    'teamA_stats':teamA_stats.to_dict(orient='index'),
                    'teamH_stats':teamH_stats.to_dict(orient='index')}
        games_dict_list.append(game_dict)

print("Done!")
db.people.count_documents({})

#
#test = db.nbastats.find_one({'firstname': 'Maria'})
#
#test = db.list_collection_names()
#db.people
#
#db.count_collections()
#
#
#result = db.people.insert_many(testando)
#
#testando = [{'nome':'Pedro', 'idade':12}, {'nome': 'Jul', 'idade':23}]
#
#
#result.inserted_ids
#
#db.people.count_documents({})
