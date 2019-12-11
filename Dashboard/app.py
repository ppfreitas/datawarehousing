import dash
import dash_html_components as html
import dash_core_components as dcc
from datetime import datetime as dt





app = dash.Dash('nba')


app.layout = html.Div(className = 'layout', children = [

            html.Div(className = 'firstbox', children = [
                html.Img(className= 'logo', src=app.get_asset_url('nba_logo.jpg')),           
                html.H2(className = 'stats_font',children = 'Stats')
                ]),

            html.Div(className= 'secondbox', children = [

                html.Div(className = 'firstteam', children = [
                    html.H2('Home Team', className = 'Home_Team'),
                    dcc.Dropdown(
                        id='select_home',
                        className="select_home",
                        options=[{'label': i, 'value': i} for i in ['Los Angeles', 'New York Knicks', 'Miami Heat']],
                        value='LA')]),

                html.Div(className = 'datebox', children = [
                    dcc.DatePickerSingle(
                        id='date-selection')]),

                html.Div(className = 'secondteam', children = [
                    html.H2('Away Team', className = 'Away_Team'),
                    dcc.Dropdown(
                        id='select_away',
                        className="select_away",
                        options=[{'label': i, 'value': i} for i in ['Los Angeles', 'New York Knicks', 'Miami Heat']],
                        value='LA')])
                ])
    ])
app.run_server(debug=True)



