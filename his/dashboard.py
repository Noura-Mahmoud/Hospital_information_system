from typing import Counter
import dash
import dash_core_components as dcc
from dash_core_components.Markdown import Markdown
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_table
import pandas as pd
from his.models import *

APP_ID = 'dash_app_1'
URL_BASE = '/dash/'
MIN_HEIGHT = 200


def add_dash(server):

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(
        server=server,
        url_base_pathname=URL_BASE,
        suppress_callback_exceptions=True,
        external_stylesheets=external_stylesheets
    )

    app.layout = html.Div([
        html.H1(
            children='Statistical Analysis',
            style={
                'textAlign': 'center',
            }
        ),
        html.Div([dcc.Graph(id='gender-pie', figure=get_gender_pie()),
                  dcc.Graph(id='sunburst', figure=get_sunburst_pie())], style={'display': 'grid', 'grid-template-columns': "1fr 1fr"}),

        html.H2(
            children='Top 5 Doctors with appointments',
            style={
                'textAlign': 'center',
            }
        ),

        html.Div([generate_dash_table()], style={'width':"75%", "margin-left":"12%"}),
    ])

    return server


def get_gender_pie():
    ct_gender = Counter([x[0]
                         for x in User.query.with_entities(User.role).all()])
    return px.pie(names=ct_gender.keys(), values=ct_gender.values())


def get_sunburst_pie():
    sun_data = [(x[0], x[1]) for x in User.query.with_entities(
        User.gender, User.role).all() if x[1] != 'admin']
    df = pd.DataFrame(sun_data)
    df.columns = ['gender', 'role']
    return go.Figure(px.sunburst(df,
                                 path=['role', 'gender']
                                 ))


def generate_table():
    drs = Counter([x[0] for x in Appointment.query.with_entities(
        Appointment.doctor_id).all() if len(x) and x[0] != None])
    dr_names = [User.query.get(x).username for x in drs.keys()]
    dr_values = list(drs.values())

    return html.Table([
        html.Thead(
            html.Tr([html.Td("Doctor Name"), html.Td("Appointments Count")])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dr_names[i]), html.Td(dr_values[i])]) for i in range(min(len(dr_names), 5))
        ])
    ])


def generate_dash_table():
    drs = Counter([x[0] for x in Appointment.query.with_entities(
        Appointment.doctor_id).all() if len(x) and x[0] != None])
    dr_names = [User.query.get(x).username for x in drs.keys()]
    dr_values = list(drs.values())
    table = dash_table.DataTable(
        id='table',
        columns=[{"name": "Doctor Name", "id": "Doctor Name"}, {
            "name": "Appointments Count", "id": "Appointments Count"}],
        data=[{"Doctor Name": key, "Appointments Count": val}
              for key, val in zip(dr_names, dr_values)],
    )
    return table
