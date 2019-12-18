import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from datetime import datetime as dt
import pymongo
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from dash.dependencies import Input, Output


client = pymongo.MongoClient("localhost", 27017)

db = client['season2020']
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
    stat_mean = np.array(num_values).mean().round(2)
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
        total_players = total_players.append(pd.DataFrame({'Players':name_players, 'teams':team_list}),ignore_index=True)
        total_players1 = total_players.drop_duplicates(subset ="Players", keep = 'first', inplace = False)
    return total_players1

def get_avgs_dataframe():
    stats = ['PTS','FG','FGA','FG%','3P','3PA','3P%','FT','FTA','FT%','ORB','DRB','TRB','AST','STL','BLK','TOV','PF','+/-']
    names = list(total_players['Players'])
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

def get_team_totals():
    cursor3 = db.games.find({})
    list_games = [i for i in cursor3]
    store_df = pd.DataFrame()
    for match in list_games:
        
        game_id = match['game_id']
        date = match['game_date']
        team_a =  match['teamA']
        team_b =  match['teamH']
    
        df_a = pd.DataFrame.from_dict(match['teamA_stats'], orient='index')
        df_a.dropna(inplace=True)
        df_b = pd.DataFrame.from_dict(match['teamH_stats'], orient='index')
        df_b.dropna(inplace=True)
        df_a['Away'] = 1
        df_b['Away'] = 0
    
        col_stats = ['PTS','FG','FGA','3P','3PA', 'FT', 'FTA',
                     'TRB','ORB','DRB', 'AST', 'STL', 'BLK', 'TOV', 'PF' ]
    
        df_a = pd.DataFrame(df_a[col_stats].astype('int32').sum())
        df_a.columns = [team_a]
        # df_a['Away'] = 1
        df_b = pd.DataFrame(df_b[col_stats].astype('int32').sum())
        df_b.columns = [team_b]
        # df_b['Away'] = 0
        df_a.loc['Opp',:]=team_b
        df_b.loc['Opp',:]=team_a
    
        totals = pd.concat([df_a, df_b], axis=1, sort=False)
        totals = totals.transpose()
    
        store_df = pd.concat([store_df,totals])
    return store_df

def get_avg_team_totals():
    mean_df = pd.DataFrame()
    team_list = teams
    stats = col_stats
    for team in team_list:
        for stat in stats:
            label = 'Avg_'+ stat 
            mean_df.loc[team,label] = team_totals.loc[team,stat].sum()/team_totals.loc[team,stat].count()
    return mean_df

def get_opp_avg_team_totals():
    mean_df = pd.DataFrame()
    store_df = team_totals.set_index('Opp', inplace=True)
    team_list = teams
    stats = col_stats
    for team in team_list:
        for stat in stats:
            label = 'Opp_Avg_'+ stat 
            mean_df.loc[team,label] = team_totals.loc[team,stat].sum()/team_totals.loc[team,stat].count()
    return mean_df

col_stats = ['PTS','FG','FGA','3P','3PA', 'FT', 'FTA',
             'TRB','ORB','DRB', 'AST', 'STL', 'BLK', 'TOV', 'PF']

team_totals = get_team_totals()
total_players = list_of_names()
df_avg_stats = get_avgs_dataframe()
teams = total_players['teams'].unique()
new_df = total_players.merge(df_avg_stats, on='Players')
teams_avg = get_avg_team_totals()
opp_teams_avg = get_opp_avg_team_totals()
graph_10 = df_avg_stats.head(10)

###########################################################################################################################

app = dash.Dash('nba')


app.layout = html.Div(className = 'layout', children = [

                    html.Div(className = 'firstbox', children = [
                        html.Img(className= 'logo', src=app.get_asset_url('nba_logo.jpg')),           
                        html.H2(className = 'stats_font',children = 'Team Stats')
                        ]),
        
                    html.Div(className= 'secondbox', children = [
        
                        html.Div(className = 'firstteam', children = [
                            html.H3('Choose your team', className = 'Home_Team'),
                            dcc.Dropdown(
                                id='select_home',
                                className="select_home",
                                options=[{'label': i, 'value': i} for i in teams],
                                value='LAL')])
        
                        # html.Div(className = 'datebox', children = [
                        #     dcc.DatePickerSingle(
                        #         id='date-selection')]),
        
                        # html.Div(className = 'secondteam', children = [
                        #     html.H3('Away Team', className = 'Away_Team'),
                        #     dcc.Dropdown(
                        #         id='select_away',
                        #         className="select_away",
                        #         options=[{'label': i, 'value': i} for i in teams],
                        #         value='Choose second team')])
                        ]),
                                        
                    html.Div(className = 'onevsrest', children = [
                            dcc.Graph(
                                id='graph2',
                                figure={'data':[
                                        {'x': teams_avg.columns, 'y': teams_avg.loc['MIL',:], 'type':'bar', 'name':'My team'},
                                        {'x': teams_avg.columns, 'y': opp_teams_avg.loc['MIL',:], 'type':'bar', 'name':'Opponent teams'},
                                        {'orientation':'h'}                                    
                                        ],
                                'layout': {
                                'title': 'One VS The Rest'}})
                                    ]),
    
    				html.Div(className = 'secondbox', children = [        
                        html.H2(className = 'player_stats_font',children = 'Player Stats')
                        ]),
    
                    html.Div(className = 'data_frame', children = [
                            dash_table.DataTable(
                                id='table',
                                columns=[{"name": i, "id": i, "selectable": True} for i in new_df.columns],
                                data=new_df.to_dict('records'),
                                page_current=0,
                                page_size=17,
                                page_action='native',
                                filter_action="native",
                                sort_action="native",
                                sort_mode="multi",
                                style_header={'backgroundColor': 'rgb(211, 211, 211)',
                                			  'fontWeight': 'bold'},
                                style_cell_conditional=[
                                        {
                                        'if': {'column_id': c},
                                        'textAlign': 'left'
                                        } for c in ['Players', 'teams']],
#                                fixed_columns={'headers': True, 'data': 1},
                                style_table={'overflowX': 'scroll'#,
                                             #'minWidth': '1550px'
                                             },
                                style_cell={
                                        'minWidth': '0px',
                                        'maxWidth': '120px',
                                        'overflow': 'hidden',
                                        'textOverflow': 'ellipsis'})
                                    ]),
                                    
                    html.Div(className = 'graph', children = [
                            
                            html.H3('Choose a stat', className = 'choose_stat'),

                            dcc.Dropdown(
                                id='select_stats',
                                className="dropdown2",
                                options=[{'label': i, 'value': i} for i in new_df.columns[2:]],
                                value='PTS'),
    
                            dcc.Graph(
                                id='graph',
                                className="hbarplayers",
                                figure={'data':[go.Bar(x = graph_10.PTS,
                                y = graph_10.Players,
                                orientation = 'h')],
                                'layout': {
                                'title': 'Player Comparison'}})
                                ])

    ])


@app.callback(
    [Output('table', 'data'),
     Output('graph', 'figure')],
    [Input('select_home', 'value'),
     Input('select_stats', 'value')]
)
def df_filter(team_dd, stat):
    if team_dd == '':
        df = new_df
    else:
        mask = new_df['teams'] == team_dd
        df = new_df[mask]
    
    df1 = df.sort_values(stat, ascending=True)
    df2 = df1.tail(20)
    
    figure={'data':[go.Bar(x = df2[stat],
                               y = df2.Players,
                                orientation = 'h')],
                                'layout': {
                                        'title': 'Player Comparison'}}
    return df.to_dict('records'), figure
    
@app.callback(
    Output('graph2', 'figure'),
    [Input('select_home', 'value')]
)
def update_graph(team_dd):
       
    figure={'data':[
            {'x': teams_avg.columns, 'y': teams_avg.loc[team_dd,:], 'type':'bar', 'name':'My team'},
            {'x': teams_avg.columns, 'y': opp_teams_avg.loc[team_dd,:], 'type':'bar', 'name':'Opponent teams'}                                     
            ],
    'layout': {
    'title': 'One VS The Rest'}}
    return figure


app.run_server(debug=True)
