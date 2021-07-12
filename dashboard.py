# Libraries for computing and working with data
import pandas as pd
import numpy as np
import math

# Map libraries
import folium
from folium import Choropleth, Circle, Marker

# Chart libraries
import plotly
import plotly.express as px
import plotly.graph_objects as go

# Dashboard/Web application libraries
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table as dt


# Retrieve the latest data from databases

# https://github.com/CSSEGISandData/COVID-19
cases_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
deaths_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
recovered_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")

# https://github.com/CSSEGISandData/COVID-19/tree/web-data
countries_df = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv")


# Process the data

# Column names are converted to lowercase
cases_df.columns = map(str.lower, cases_df.columns)
deaths_df.columns = map(str.lower, deaths_df.columns)
recovered_df.columns = map(str.lower, recovered_df.columns)
countries_df.columns = map(str.lower, countries_df.columns)

# Column names are simplified
cases_df = cases_df.rename(columns={'province/state': 'state', 'country/region': 'country'})
deaths_df = deaths_df.rename(columns={'province/state': 'state', 'country/region': 'country'})
recovered_df = recovered_df.rename(columns={'province/state': 'state', 'country/region': 'country'})
countries_df = countries_df.rename(columns={'long_': 'long', 'country_region': 'country'})

# 'countries_df' is sorted so that countries would descend according to cases
sorted_countries_df = countries_df.sort_values('confirmed', ascending=False)

# NaN is changed to ""
cases_df.state.fillna("", inplace=True)
deaths_df.fillna("", inplace=True)
recovered_df.fillna("", inplace=True)
sorted_countries_df.fillna("", inplace=True)

sorted_countries_df = sorted_countries_df.iloc[:, [0, 4, 5, 6, 7]]


# Calculations

# Calculating total cases, deaths, recoveries and their change from their last update
total_cases = (np.sum(np.asarray(cases_df.iloc[:, 5:]), axis=0))[-1]
change_cases = total_cases - ((np.sum(np.asarray(cases_df.iloc[:, 5:]), axis=0))[-2])

total_deaths = (np.sum(np.asarray(deaths_df.iloc[:, 5:]), axis=0))[-1]
change_deaths = total_deaths - ((np.sum(np.asarray(deaths_df.iloc[:, 5:]), axis=0))[-2])

total_recovered = (np.sum(np.asarray(recovered_df.iloc[:, 5:]), axis=0))[-1]
change_recovered = total_recovered - ((np.sum(np.asarray(recovered_df.iloc[:, 5:]), axis=0))[-2])

total_active = total_cases - total_deaths - total_recovered
change_active = change_cases - change_deaths - change_recovered

# Check if the change is positive or negative and format commas 
def with_plus_or_minus(df):
    if df > 0:
        operator_df = "+"
    elif df < 0 or df == 0:
        operator_df = ""

    df = "{:,}".format(df)
    return (operator_df + df)

change_cases = with_plus_or_minus(change_cases)
change_deaths = with_plus_or_minus(change_deaths)
change_recovered = with_plus_or_minus(change_recovered)
change_active = with_plus_or_minus(change_active)

# Death and recovery ratios are calculated and rounded

# Death (Case Fatality) Ratio calculated according to WHO:
# https://www.who.int/news-room/commentaries/detail/estimating-mortality-from-covid-19
death_ratio = round(total_deaths*100/(total_deaths+total_recovered), 2) 
recovery_ratio = round((total_recovered/total_cases)*100, 2)

# Formatting commas so it'd be easier to see the numbers
total_cases = '{:,}'.format(total_cases)
total_deaths = '{:,}'.format(total_deaths)
total_recovered = '{:,}'.format(total_recovered)
total_active = '{:,}'.format(total_active)


# Creating charts

# Chart 1 - First 15 countries according to the magnitude of COVID-19 cases. Chart type - Bar chart
chart1 = px.bar(sorted_countries_df.head(15), x='confirmed', y='country', color='country',
                     hover_name='country', orientation='h', text='confirmed')

chart1.update_xaxes(title_text="Cases")
chart1.update_yaxes(title_text='Country')
chart1.update_layout(title="First 15 countries according to the magnitude of COVID-19 cases")


# Chart 2 - Number of cases, deaths and recovered over time. Chart type - Linear graph with dots
def country_cases_chart(country):
    text = ['cases', 'deaths', "recovered"]
    name = ['Cases', 'Deaths', "Recovered"]
    colors = ['orange', 'crimson', "forestgreen"]
    list_ = [cases_df, deaths_df, recovered_df]

    chart_temp = go.Figure()

    for i, df in enumerate(list_):
        if country == 'World':
            x_data = df.iloc[:, 5:].columns
            y_data = np.sum(np.asarray(df.iloc[:, 5:]), axis=0)

        else:
            x_data = df.iloc[:, 5:].columns
            y_data = np.sum(np.asarray(df[df['country']==country].iloc[:, 5:]), axis=0)

        chart_temp.add_trace(go.Scatter(x=x_data,
                                       y=y_data,
                                       mode='lines+markers',
                                       name=name[i],
                                       line=dict(color=colors[i], width=4),
                                       connectgaps=True,
                                       text="Total " + str(text[i]) + ": " + str(y_data[-1])
                                      ))
    return chart_temp


chart2 = country_cases_chart('World')
chart2.update_layout(title="Number of cases, deaths and recovered over time", yaxis_type='linear')
chart2.update_xaxes(title_text='Date')
chart2.update_yaxes(title_text='Quantity')


# Chart 3 - Daily cases. Chart type - Bar chart
cases_list = (np.sum(np.asarray(cases_df.iloc[:, 5:]), axis=0))
x_data = []
y_data = []

for i in range(len(cases_list)):
    if i+1 < len(cases_list):
        x_data.append(np.asarray(cases_df.iloc[:, 5:].columns[i+1])),
        y_data.append(np.asarray(cases_list[i+1] - cases_list[i]))


chart3_df = pd.DataFrame({"Date": x_data, 'Cases': y_data})

chart3 = px.bar(chart3_df, x='Date', y='Cases')

chart3.update_xaxes(title_text='Date')
chart3.update_yaxes(title_text='Cases')
chart3.update_layout(title="Daily increase of cases")
chart3.update_traces(marker_color='orange');


# Creating the map

def map_creation(df, name):
    map_temp = folium.Map(location=[54.687157, 25.279652], tiles='cartodbpositron', zoom_start=5, min_zoom=2)
    for i in range(len(df)):
        if name == "cases_df" or name == "deaths_df" or name == "recovered_df":
            radius = 2 * math.pi * math.sqrt(int(df.iloc[i, -1]))
        elif name == "countries_df":
            radius = 2 * math.pi * math.sqrt(int(df.iloc[i]['confirmed']))

        if 'state' not in df.columns or df.iloc[i]['state'] == "":
            state_country = df.iloc[i]['country']
        else:
            state_country = df.iloc[i]['state'] + ", " + df.iloc[i]['country']

        if name == "cases_df":
            tooltip = state_country + "<br> Confirmed: " + str(df.iloc[i, -1])
            fill_color = 'orange'
            color = 'orange'
        elif name == "deaths_df":
            tooltip = state_country + "<br> Deaths: " + str(df.iloc[i, -1])
            fill_color = 'crimson'
            color = 'crimson'
        elif name == "recovered_df":
            tooltip = state_country + "<br> Recovered: " + str(df.iloc[i, -1])
            fill_color = 'forestgreen'
            color = 'forestgreen'
        elif name == "countries_df" and pd.isnull(df.iloc[i]['recovered']):
            tooltip = state_country + "<br> Confirmed: " + str(int(df.iloc[i]['confirmed'])) +            "<br> Deaths: " + str(int(df.iloc[i]['deaths'])) +            "<br> Recovered: " + str(0) +            "<br> Active: " + str(int(int(df.iloc[i]['confirmed'])-int(df.iloc[i]['deaths'])))
            fill_color = 'deepskyblue'
            color = 'deepskyblue'
        elif name == "countries_df":
            tooltip = state_country + "<br> Confirmed: " + str(int(df.iloc[i]['confirmed'])) +            "<br> Deaths: " + str(int(df.iloc[i]['deaths'])) +            "<br> Recovered: " + str(int(df.iloc[i]['recovered'])) +            "<br> Active: " + str(int(int(df.iloc[i]['confirmed'])-int(df.iloc[i]['deaths']))-int(df.iloc[i]['recovered']))
            fill_color = 'deepskyblue'
            color = 'deepskyblue'

        if pd.isnull(df.iloc[i]['lat']) or pd.isnull(df.iloc[i]['long']):
            pass
        else:
            location = [df.iloc[i]['lat'], df.iloc[i]['long']]

        folium.Circle(
        location=location,
        fill=True,
        radius=radius,
        fill_color=color,
        color=color,
        tooltip=tooltip
        ).add_to(map_temp)

    return map_temp


# COVID-19 Dashboard

# Creating elements, their actions and organizing them to create a layout
# https://medium.com/@shachiakyaagba_41915/integrating-folium-with-dash-5338604e7c56
# Stylesheet from https://www.bootstrapcdn.com/bootswatch/

external_stylesheets = 'https://stackpath.bootstrapcdn.com/bootswatch/4.5.0/cosmo/bootstrap.min.css'

app = dash.Dash(__name__, external_stylesheets=[external_stylesheets])

app.title = "COVID-19 Dashboard"

app.config.suppress_callback_exceptions = True

header_element = html.H1("COVID-19 Dashboard")

def create_card1(name1, df1, name2, df2, color):
    return dbc.Card(
        dbc.CardBody([
            html.H5(name1, className='card-subtitle', style={'font-size': '28px', 'font-family': 'Lato'}),
            html.P(df1, className="card-subtitle", style={'font-size': '20px', 'font-weight': 'bold', 'font-family': 'Lato'}),
            html.H5(name2 + ": " + str(df2), className='card-subtitle', style={'font-size': '28px', 'font-family': 'Lato'}),
        ],
            className="text-center",
            style={"color": color}
        ))

cases_card = create_card1("Total confirmed", total_cases, "Change", change_cases, 'orange')
active_card = create_card1("Total active", total_active, "Change", change_active, 'peru')

def create_card2(name1, df1, name2, df2, color, ratio):
    return dbc.Card(
        dbc.CardBody([
            html.H5(name1, className='card-subtitle', style={'font-size': '28px', 'font-family': 'Lato'}),
            html.P(str(df1) + " / " + str(ratio) + "%", className="card-subtitle", style={'font-size': '20px', 'font-weight': 'bold', 'font-family': 'Lato'}),
            html.H5(name2 + ": " + str(df2), className='card-subtitle', style={'font-size': '28px', 'font-family': 'Lato'}),
        ],
            className="text-center",
            style={"color": color}
        ))

deaths_card = create_card2("Total deaths", total_deaths, "Change", change_deaths, 'crimson', death_ratio)
recovered_card = create_card2("Total recovered", total_recovered, "Change", change_recovered, 'forestgreen', recovery_ratio)

cards_element =    dbc.CardDeck([
        cases_card,
        deaths_card,
        recovered_card,
        active_card
    ],
    className="mb-4")

tabs_element =    dbc.Tabs(id="tabs", active_tab="all-tab", children=[
            dbc.Tab(label="All", tab_id="all-tab"),
            dbc.Tab(label="Cases", tab_id="cases-tab"),
            dbc.Tab(label="Deaths", tab_id="deaths-tab"),
            dbc.Tab(label="Recovered", tab_id="recovered-tab")
            ]
        )

map_with_tabs =    html.Div([tabs_element, html.Div(id="map-tab")])

search_element =    dcc.Input(
        id="country-input",
        placeholder='Enter a country... (or type "World")',
        type='text',
        value='Lithuania',
        size='30',
    )

selection_element =    dcc.RadioItems(
        id="type-choice",
        options=[{'label': k, 'value': k} for k in ['Linear', 'Logarithmic']],
        value='Linear',
        labelStyle={'display': 'inline-block'}
    )

charts_element =    html.Div([
        search_element,
        selection_element,
        dbc.Row([
            dbc.Col(html.Div([
                dcc.Graph(
                    id='chart2',
                    figure=chart2)])),
            dbc.Col(html.Div(
                dcc.Graph(
                    id='chart3',
                    figure=chart3)))
        ], className='mb-2'),

        dbc.Row([
            dbc.Col(html.Div(
                dcc.Graph(
                    id='chart1',
                    figure=chart1)))

        ]),
    ],
        className='mb-4'
    )

table_element =    html.Div([
        dt.DataTable(
        id='lentele',
        columns=[{"name": i, "id": i} for i in sorted_countries_df.columns],
        data=sorted_countries_df.to_dict('records'),
            sort_action="native",
            fixed_rows={"headers": True, "data": 0},
            style_as_list_view=True,
            style_cell={"font_family": "Lato"},
            style_table={
                "maxHeight": "800px",
                "height": "645px",
                "width": "600px"
            },
            style_header={
                "fontWeight": "bold",
                "padding": "15px"
            },
            style_cell_conditional=[
                {"if": {"column_id": "country"}, "width": "15%"},
                {"if": {"column_id": "confirmed"}, "width": "20%"},
                {"if": {"column_id": "recovered"}, "width": "20%"},
                {"if": {"column_id": "deaths"}, "width": "20%"},
                {"if": {"column_id": "active"}, "width": "25%"},
                {"if": {"column_id": "confirmed"}, "color": "orange"},
                {"if": {"column_id": "recovered"}, "color": "forestgreen"},
                {"if": {"column_id": "deaths"}, "color": "crimson"},
                {"if": {"column_id": "active"}, "color": "peru"},
                {"textAlign": "center"},
            ],
        )
    ])

footer_element =    html.Div([
        html.Hr(),
        html.P("Dashboard written by Rytis Markevičius",
                style={"textAlign": "center", "margin": "auto"}),
        html.Hr()
    ])

@app.callback(
    Output('chart2', 'figure'),
    [Input('country-input', 'value'),
     Input('type-choice', 'value')]
)
def change_country(country, choice):
    chart_temp = country_cases_chart(country)
    if choice == 'Logarithmic':
        chart_temp.update_layout(title="Number of cases, deaths and recovered over time", yaxis_type='log')
        chart_temp.update_xaxes(title_text='Date')
        chart_temp.update_yaxes(title_text='Quantity')
    elif choice == 'Linear':
        chart_temp.update_layout(title="Number of cases, deaths and recovered over time", yaxis_type='linear')
        chart_temp.update_xaxes(title_text='Date')
        chart_temp.update_yaxes(title_text='Quantity')

    return chart_temp

@app.callback(
    Output('map-tab', 'children'),
    [Input('tabs', 'active_tab')]
)
def map_tabs(active_tab):
    if active_tab == "all-tab":
        map = map_creation(countries_df, "countries_df")
        map.save("map.html")

    elif active_tab == "cases-tab":
        map = map_creation(cases_df, "cases_df")
        map.save("map.html")

    elif active_tab == "deaths-tab":
        map = map_creation(deaths_df, "deaths_df")
        map.save("map.html")

    elif active_tab == "recovered-tab":
        map = map_creation(recovered_df, "recovered_df")
        map.save("map.html")

    return html.Div([html.Iframe(id='map',
                        srcDoc = open('map.html', 'r').read(),
                        width='100%',
                        height='600',
                        style={'border': 'none'},
                        className='mb-4')])


def create_layout():
    return dbc.Container([html.Div([header_element, html.Hr()]),
                          cards_element,
                          html.Div([
                              dbc.Row([
                                  dbc.Col([table_element], width=4),
                                  dbc.Col([map_with_tabs], width=8)
                              ])
                          ]),
                          charts_element,
                          footer_element
                         ],
                         fluid=True, style={'backgroundColor': '#f0f2f2'})


app.layout = create_layout

if __name__ == '__main__':
    app.run_server(debug=True)
