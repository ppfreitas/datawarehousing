#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 19:14:07 2019

@author: pedro
"""
import pymongo
import pandas as pd
import numpy as np

client = pymongo.MongoClient("localhost", 27017)

db = client['nba_teste4']
test = db.games.find()

def player_avg_stat(player, stat):
    player = str(player)
    stat = str(stat)
    cursor = db.games.find({"teamA_stats."+player:{"$exists":True}},{"teamA_stats."+player+"."+stat:1,"_id":False})
    value = [doc['teamA_stats'][player][stat] for doc in cursor]
    cursor1 = db.games.find({"teamH_stats."+player:{"$exists":True}},{"teamH_stats."+player+"."+stat:1,"_id":False})
    value1 = [doc['teamH_stats'][player][stat] for doc in cursor1]
    values = value + value1
    num_values = [float(num) for num in values if (num is not None) and (num is not '')]
    stat_mean = np.array(num_values).mean()
    return player, stat, stat_mean

def list_of_names():
    cursor2 = db.games.find({},{"teamA":1,"teamA_stats":1,"_id":False})
    c = pd.DataFrame(cursor2)
    total_players = pd.DataFrame()
    for j in range(len(c)):
        players = c.to_dict(orient='split')['data'][j][1]
        team = c.to_dict(orient='split')['data'][j][0]
        name_players = [name for name in pd.DataFrame(players).columns]
        team_list = [team for i in range(len(pd.DataFrame(players).columns))]
        total_players = total_players.append(pd.DataFrame({'teams':team_list, 'players':name_players}),ignore_index=True)
        total_players1 = total_players.drop_duplicates(subset ="players", keep = 'first', inplace = False)
    return total_players1

def get_avgs_dataframe():
    stats = ['FG','FGA','FG%','3P','3PA','3P%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF','PTS','+/-']
    names = list(total_players['players'])
    store = []
    final_list = []
    avg_stats = pd.DataFrame()
    for name in names:
        store = [name]
        for stat in stats:
            foo = player_avg_stat(name, stat)
            store = store + [foo[2]]
        final_list.append(store)
    return pd.DataFrame(final_list, columns=(['Players'] +stats)).sort_values('PTS', ascending=False)

total_players = list_of_names()
df_avg_stats = get_avgs_dataframe()

#db.games.insert_many(games_dict_list)
#db.games.count_documents({})
