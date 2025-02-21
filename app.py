import dash
import dash_bootstrap_components.themes
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import pandas as pd
import os
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

green = pd.read_csv("https://raw.githubusercontent.com/DuaneIndustries/BCMProjectCashFlow/refs/heads/main/CategoryTotalsv223.csv")
roastlog = pd.read_csv("https://raw.githubusercontent.com/DuaneIndustries/BCMProjectCashFlow/refs/heads/main/BCMCashflowTimelinev15.csv")

#DATA CLEANING

roastlog['Balance'] = roastlog['Balance'].astype('float')
green['Projected'] = green['Projected'].astype('float')
green['Current'] = green['Current'].astype('float')
green['Remaining cost until store opening'] = green['Remaining cost until store opening'].astype('float')
roastlog['Start Date'] = pd.to_datetime(roastlog['Start Date'], format="%m/%d/%y")
roastlog['End Date'] = pd.to_datetime(roastlog['End Date'], format="%m/%d/%y")
roastlog['Start Date'] = roastlog['Start Date'].dt.normalize()
roastlog['End Date'] = roastlog['End Date'].dt.normalize()




color_map = {
    'Construction': 'red',
    'Debt Service': 'blue',
    'Equipment': 'darkred',
    'Occupancy' : 'yellow',
    'Project Management' : 'purple',
    'Revenue' : 'darkgreen',
    'Salary' : 'black',
    'Supplies & Materials' : 'orange',
    "Other" : "Gray"
}



roastlog['HoverText'] = roastlog['Vendor'] + '<br>Amount: ' + roastlog['Amount'].astype(str) +"<br>Notes:" + roastlog["Notes"]
roastlog['Color'] = roastlog['Category'].map(color_map)



dff = roastlog

#for deploying

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.SLATE])
server=app.server

 # app.config.suppress_callback_exceptions=True



# LAYOUT
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1('BCM Project Cost Analysis',
                        style={'textAlign' : 'center','color' : 'Linen'},
                        className='text-m-center mb-m-4'),
                width=12)
    ]),
    dbc.Row([
        dbc.Col([
                    html.Label(['Category Totals'], style={'font-weight': 'bold', 'color':'linen'}),
                    dcc.Dropdown(
                        id='x-axis-dropdown',
                        style={'backgroundColor' : 'linen'},
                        options=[{'label': i, 'value': i} for i in green['Category'].unique()],
                        value='Total'),
    html.Br(),
    ], width={'size' : 4}),
        ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='green-bar',figure={},style={"border" : "2px linen solid"}),
        html.Br(),
        ], width={'size' : 12}),

]),
    dbc.Row([
        dbc.Col([
            html.Label(['Filter by Vendor'], style={'font-weight': 'bold', 'color':'linen'}),
            html.Br(),
            dcc.Checklist(id='my-checklist', value=["Aperion","BCM","Cincinnati Insurance","Decor","ECRS","Embassy","Fresh Ink","Hud Drawdown","KeHe","LEAF","Market Flats","Micro Innovation","Paypal","Payroll (admin)","Payroll (store)","Penn","PPL","SBS","Zepole","Boyle"],
                          inline=False,
                          className="me-1",
                          style={'color': 'linen'},
                          inputStyle={'margin-left': '10px'},
                          options=[{'label': vendor, 'value': vendor} for vendor in dff['Vendor'].unique()]
                          ),
            ], width={'size': 2}),
        dbc.Col([
                html.Br(),
                dcc.Graph(
                     id='balanceline',
                    figure={},
                    style={"border" : "2px linen solid"} )
            ], width={'size' : 10 }),
        html.Br(),



]),
])

# Balance Line

@app.callback(
    Output('balanceline', 'figure'),
    Input('my-checklist', 'value')
)

def update_graph(cat_slctd):

    dff = roastlog[roastlog['Vendor'].isin(cat_slctd)]
    starting_balance = 205035.19 
    dff = dff.sort_values(by='Start Date')
    dff['Cumulative Balance'] = dff['Amount'].cumsum() + starting_balance


    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dff['Start Date'], y=dff['Cumulative Balance'], name='Balance',hovertext=dff['Vendor'], line=dict(color='darkgrey', width=4)))
    fig.add_trace(go.Scatter(x=dff['Start Date'], y=dff['Cumulative Balance'], name='Balance',hovertext=dff['HoverText'], mode='markers',marker=dict(color=dff['Color'],showscale=False)))
    fig.add_shape(
        type="rect",
        xref="x",
        yref="y",
        x0=min(dff['Start Date']),
        y0=min(dff['Balance']),
        x1=max(dff['Start Date']),
        y1=0,
        fillcolor="red",
        opacity=0.2,
        layer="below",
        line_width=0)
    fig.update_layout(title='Projected Operating Balance',
                    title_x=0.45,
                    xaxis_title='Date',
                    yaxis_title='Balance',
                    paper_bgcolor='#353839',
                    plot_bgcolor='linen',
                    font_color='linen',
                    showlegend=False,
                    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(step="month", stepmode="backward", count=1, label="Month"),
                dict(step="month", stepmode="backward", count=3, label="3 Month"),
                dict(step="month", stepmode="backward", count=6, label="6 Month"),
                dict(step="all", label="All")
            ]),
            bgcolor="lightblue",
            activecolor='darkgrey'
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        ),
        yaxis=dict(
            range=[-2_000_000, 1_000_000]  # Set the y-axis range
            )
    )
    return (fig)


# BAR
@app.callback(
    Output('green-bar', 'figure'),
    Input('x-axis-dropdown', 'value')
)

def update_figure(selected_x_value):
    filtered_df = green[green['Category'] == selected_x_value]

    figx = go.Figure(go.Bar(x=filtered_df['subcategory'], y=filtered_df['Projected'], name='Budgeted',offsetgroup=0, marker = dict(color='dimgrey', pattern_shape='-')))
    figx.add_trace(go.Bar(x=filtered_df['subcategory'],y=filtered_df['Current'], name='Paid to Date', opacity=.5, offsetgroup=1, marker = dict(color='darkblue')))
    figx.add_trace(go.Bar(x=filtered_df['subcategory'], y=filtered_df['Remaining cost until store opening'],hovertext=filtered_df['Notes'], name='Projected Cost to Completion',text=filtered_df['Total Cost'],textposition='auto', opacity=.5,offsetgroup=1,base=filtered_df['Current'], marker = dict(color='indianred',pattern_shape='/')))

    figx.update_layout(barmode='overlay',
                       title='Grant Budget v Actuals by Category',
                       title_x=0.5,
                       xaxis_title='Subcategory',
                       yaxis_title='Cost',
                       paper_bgcolor='#353839',
                       plot_bgcolor='linen',
                       font_color='linen')
    return figx



if __name__ == '__main__' :
    app.run_server(debug=True)
