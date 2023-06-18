import dash_bootstrap_components as dbc
from dash import html

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def get_square(text, progress=None):
    children = [html.Div(text)]

    if progress is not None:
        children.append(dbc.Progress(label=f"{progress}%", value=progress))

    return html.Div(children, style={"width": "7em", "height": "7em"})

def get_cal():
    days = [dbc.Row([dbc.Col(html.Div(day, ))
                for day in DAYS])]
    
    sq = [
        dbc.Row([dbc.Col(html.Div(children=get_square("yo", 35), style={"border":"2px black solid"}))
                for _ in range(7)],
                className="g-0",)
        for _ in range(5)
    ]

    return dbc.Container(days + sq)
