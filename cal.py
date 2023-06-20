import dash_bootstrap_components as dbc
from dash import html
import pandas as pd

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def get_day(row):
    children = [html.Div(row["DAY"].strftime("%d/%m"))]

    adl_completion = float(row["ADL_COMPLETION_PERCENTAGE"])
    children.append(dbc.Progress(label=f"ADLS: {adl_completion}%", value=adl_completion))

    children = html.Div(children, style=dict(width="7em", height="7em"))
    return dbc.Col(html.Div(children=children, style={"border":"2px black solid"}), width=1)

def get_gray_day():
    child = html.Div(style={"width":"7em", "height":"7em"})
    return dbc.Col(html.Div(child,style={"border":"2px black solid"}), width=1)

def get_cal(schedule_df: pd.DataFrame):
    week_days = [dbc.Row([dbc.Col(html.Div(day, ), width=1) for day in DAYS], className="g-0")]
    
    all_days = []
    first_day = schedule_df.iloc[0]["DAY"].weekday()
    for _ in range(0, first_day):
        all_days.append(get_gray_day())

    for idx, row in schedule_df.iterrows():
        # Generate days
        all_days.append(get_day(row))

    if first_day != 0:
        for _ in range(first_day, 7):
            all_days.append(get_gray_day())

    # Create rows
    cal = []
    for i in range(0, len(all_days), 7):
        cal.append(dbc.Row(all_days[i: i+7], className="g-0"))

    return dbc.Container(week_days + cal,)
