import dash_bootstrap_components as dbc
from dash import html
import pandas as pd
import note,icons


DAYS = ["Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"]
sz = 7.5


def get_cal(schedule_df: pd.DataFrame,note_df: pd.DataFrame):
    note_df["DAY"] = pd.to_datetime(note_df["DAY"])  

    week_days = create_week_days_header()
    all_days = generate_all_days(schedule_df, note_df)
    cal = create_calendar_rows(all_days)

    return dbc.Container(week_days + cal, id='calendar')

def get_day(row,note_df):
    children = [
        html.Div(row["DAY"].strftime("%d/%m"), style={"font-size": "0.9em","font-weight":"600"})
    ]
    if row["TOTAL_ADLS"] == 0:
        children.append(create_no_scheduled_adls_div())

    else:
        adl_completion = round(float(row["ADL_COMPLETION_PERCENTAGE"]))
        children.append(create_progress_bar(adl_completion))
        children.append(create_adls_div(row['TOTAL_COMPLETED_ADLS'], row['TOTAL_ADLS']))

    icons.insert_image(row,children)
    note.insert_image_note(row,children,note_df)
    children = html.Div(children, style={"width": f"{sz}em", "height": f"{sz}em", "position": "relative"})
    return dbc.Col(html.Div(children=children, style={"border": "1px rgb(211, 211, 211) solid"}), width="auto")

def create_no_scheduled_adls_div():
    return html.Div("NO SCHEDULED ADLS", style={"height": "11%", "width": "100%", "color": "rgb(17, 60, 202)", "position": "absolute", "bottom": "0", "border-radius": "0px", "font-size": "65%", "text-align": "center", "font-weight": "bold"})

def create_progress_bar(adl_completion):
    
    return dbc.Progress(
        value=adl_completion,
        color="rgb(255, 170, 5)",
        striped=True,
        animated=True,
        style={"height": "15px", "width": "100%", "position": "absolute", "bottom": "0", "border-radius": "0px", "progress-bar-color": "#fff", "overflow": "hidden"},
    )

def create_adls_div(completed_adls, total_adls):
    return html.Div(
        f"ADLS: {completed_adls}/{total_adls}",
        style={
            "height": "11%", "width": "100%", "position": "absolute",
            "bottom": "1px", "border-radius": "0px", "color": "rgb(17, 60, 202)",
            "text-align": "center", "font-weight": "bold", "font-size": "75%", "font-variant-numeric": "lining-nums"
        },
    )

def get_gray_day():
    
    child = html.Div(
        style={"width": f"{sz}em", "height": f"{sz}em", "background": "repeating-linear-gradient(45deg,#FFF,#FFF 5px,#F370211A 5px,#F370211A 6px)"})
    
    return dbc.Col(html.Div(child, style={"border": "1px #fafcff solid"}), width="auto")

def create_week_days_header():
    
    return [dbc.Row([
        dbc.Col(
            html.Div(
                html.Div(day, style={"width": f"calc({sz}em + 2px)", "text-align": "center", "margin": "auto",
                                     "font-weight": "600"})
            ),
            width="auto"
        ) for day in DAYS], className="g-0")
    ]

def generate_all_days(schedule_df, note_df):
    
    all_days = []
    first_day = schedule_df.iloc[0]["DAY"].weekday()

    for _ in range(0, first_day):
        all_days.append(get_gray_day())

    for idx, row in schedule_df.iterrows():
        all_days.append(get_day(row, note_df))

    if first_day != 0:
        for _ in range(first_day, 7):
            all_days.append(get_gray_day())

    return all_days

def create_calendar_rows(all_days):
    
    cal_rows = []
    for i in range(0, len(all_days), 7):
        cal_rows.append(dbc.Row(all_days[i: i + 7], className="g-0"))
        
    return cal_rows
