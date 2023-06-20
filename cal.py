import dash_bootstrap_components as dbc
from dash import html
import pandas as pd


DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
def get_day(row):
    children = [html.Div(row["DAY"].strftime("%d/%m"))]

    adl_completion = round(float(row["ADL_COMPLETION_PERCENTAGE"]))
    children.append(
    dbc.Progress(
        label=f"ADLS: {adl_completion}%",
        value=adl_completion,
        color="success",
        striped=True,
        animated=True,
        style={"height": "20px", "margin-bottom": "0px"}
    )
    )
    
    # Placeholder for image/icon based on different types of data
    if row["FALL_COUNT"] > 0:
        children.append(html.Img(src="assets/fall.png", style={"width": "50px"}))
    if row["HAS_PAIN_MENTION"] == True:
        children.append(html.Img(src="assets/pain.png", style={"width": "50px"}))
    if row["HOSPITALIZATION_COUNT"] > 0:
        children.append(html.Img(src="assets/hospital.png", style={"width": "50px"}))
    if row["CANCELLATION_COUNTS"] > 0:
        children.append(html.Img(src="assets/cancelled.png", style={"width": "50px"}))
        
    

    children = html.Div(children, style=dict(width="7em", height="7em"))
    return dbc.Col(html.Div(children=children, style={"border":"2px black solid"}), width="auto")

def get_gray_day():
    child = html.Div(style={"width":"7em", "height":"7em"})
    return dbc.Col(html.Div(child,style={"border":"2px black solid"}), width="auto")

def get_cal(schedule_df: pd.DataFrame):
    week_days = [dbc.Row([dbc.Col(html.Div(html.Div(day, style={"width":"116px"})), width="auto") for day in DAYS], className="g-0")]

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