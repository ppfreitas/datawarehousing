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
    stat_mean = np.array(num_values).mean().round(1)
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
    stats = ['PTS','FG','FGA','FG%','3P','3PA','3P%','FT','FTA','FT%','TRB','AST','STL','BLK','TOV','+/-']
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
                     'TRB', 'AST', 'STL', 'BLK', 'TOV' ]
    
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
             'TRB', 'AST', 'STL', 'BLK', 'TOV']

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
                        #         id='select_away',                      #         className="select_away",
                        #         options=[{'label': i, 'value': i} for i in teams],
                        #         value='Choose second team')])
                        ]),
                                        
                    html.Div(className = 'onevsrest', children = [
                            dcc.Graph(
                                id='graph2',
                                figure={'data':[
                                        {'x': teams_avg.columns, 'y': teams_avg.loc['MIL',:], 'type':'bar', 'name':'My team'},
                                        {'x': teams_avg.columns, 'y': opp_teams_avg.loc['MIL',:], 'type':'bar', 'name':'Opponent teams',
                                        'marker':{'color':'rgb(201,8,42)'}}                            
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
                                sort_action="native",
                                sort_mode="multi",
                                style_header={'backgroundColor': 'rgb(169,169,169)',
                                			  'fontWeight': 'bold',
                                			  'border' : '1px solid black'},
                                style_data= { 'border' : '1px solid black'},
                                style_data_conditional=[
                                        {
                                        'if': {'row_index': 'odd'},
                                        'backgroundColor': 'rgb(230,242,255)'}],		  
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
                                		'textAlign': 'center',
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
    color_graph = dict[team_dd]
    color_graph1 = dict1[team_dd]
    figure={'data':[
            {'x': teams_avg.columns, 'y': teams_avg.loc[team_dd,:], 'type':'bar', 'name':team_dd,
            'marker':{'color':color_graph1}},
            {'x': teams_avg.columns, 'y': opp_teams_avg.loc[team_dd,:], 'type':'bar', 'name':'Opponent teams',
            'marker':{'color':color_graph}}
            ],
    'layout': {
    'title': 'One VS The Rest'}}
    return figure




dict = {'ATL':'rgb(225,68,52)',
        'NOP':'rgb(0,22,65)',
        'LAL':'rgb(85,37,130)',
        'CHI':'rgb(206,17,65)',
        'DET':'rgb(200,16,46)',
        'CLE':'rgb(134,0,56)',
        'MIN':'rgb(12,35,64)',
        'MEM':'rgb(93,118,169)',
        'BOS':'rgb(0,122,51)',
        'WAS':'rgb(0,43,92)',
        'NYK':'rgb(245,132,38)',
        'OKC':'rgb(0,125,195)',
        'SAC':'rgb(91,43,130)',
        'DEN':'rgb(13,34,64)',
        'MIL':'rgb(0,71,27)',
        'LAC':'rgb(200,16,46)',
        'TOR':'rgb(206,17,65)',
        'DAL':'rgb(0,83,188)',
        'PHO':'rgb(29,17,96)',
        'POR':'rgb(224,58,62)',
        'UTA':'rgb(0,71,27)',
        'MIA':'rgb(152,0,46)',
        'PHI':'rgb(0,107,182)',
        'ORL':'rgb(0,125,197)',
        'IND':'rgb(253,187,48)',
        'GSW':'rgb(255,199,44)',
        'BRK':'rgb(0,0,0)',
        'CHO':'rgb(0,120,140)',
        'HOU':'rgb(206,17,65)',
        'SAS':'rgb(196,206,211)'
        }

dict1 = {'ATL':'rgb(196,214,0)',
        'NOP':'rgb(225,58,62)',
        'LAL':'rgb(253,185,39)',
        'CHI':'rgb(6,25,34)',
        'DET':'rgb(29,66,138)',
        'CLE':'rgb(4,30,66)',
        'MIN':'rgb(35,97,146)',
        'MEM':'rgb(18,23,63)',
        'BOS':'rgb(139,111,78)',
        'WAS':'rgb(227,24,55)',
        'NYK':'rgb(0,107,182)',
        'OKC':'rgb(239,59,36)',
        'SAC':'rgb(99,113,122)',
        'DEN':'rgb(255,198,39)',
        'MIL':'rgb(240,235,210)',
        'LAC':'rgb(29,66,148)',
        'TOR':'rgb(6,25,34)',
        'DAL':'rgb(0,43,92)',
        'PHO':'rgb(229,95,32)',
        'POR':'rgb(6,25,34)',
        'UTA':'rgb(0,43,92)',
        'MIA':'rgb(249,160,27)',
        'PHI':'rgb(237,23,76)',
        'ORL':'rgb(196,206,211)',
        'IND':'rgb(0,45,98)',
        'GSW':'rgb(29,66,138)',
        'BRK':'rgb(255,255,255)',
        'CHO':'rgb(29,17,96)',
        'HOU':'rgb(6,25,34)',
        'SAS':'rgb(6,25,34)'
}

app.run_server(debug=True)