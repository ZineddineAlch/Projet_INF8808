import dash_bootstrap_components as dbc
from dash import html
import pandas as pd
import note


DAYS = ["Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"]
sz = 7.5

def get_image(image_path, tooltip_text):
    get_image.counter = getattr(get_image, 'counter', 0) + 1
    tooltip_id = f"tooltip_{get_image.counter}"
    image_id = f"image_{get_image.counter}"
    image = html.Img(
        src=image_path, 
        style={"width": "35px"}, 
        id=image_id
    )
    
    tooltip = dbc.Tooltip(tooltip_text, target=image_id, id=tooltip_id, placement="top")
    return html.Div([image, tooltip], style={"position": "relative"})


def insert_image(row,children):
    images = []
    if row["FALL_COUNT"] > 0:
        image = get_image("assets/fall1.png", f"Falls: {row['FALL_COUNT']}, , {row['FALL_SOURCE']}")
        images.append(image)

    if row["HAS_PAIN_MENTION"] == True:
        image = get_image("assets/pain.png", f"{row['PAIN_SOURCE']}")
        images.append(image)

    if row["HOSPITALIZATION_COUNT"] > 0:
        image = get_image("assets/hospital.png", f"Hospitalizations: {row['HOSPITALIZATION_COUNT']}, {row['HOSPITALIZATION_SOURCE']}")
        images.append(image)

    if row["CANCELLATION_COUNTS"] > 0:
        image = get_image("assets/cancelled.png", f"Cancellations: {row['CANCELLATION_COUNTS']}")
        images.append(image)
    # Divide the images into two rows
    first_row = images[:2]
    second_row = images[2:]

    # Create divs for each row
    first_row_div = html.Div(first_row, style={"display": "flex", "justify-content": "space-around","margin-top": "13%"})
    second_row_div = html.Div(second_row, style={"display": "flex", "justify-content": "space-around"})
    
    return children.append(html.Div([first_row_div, second_row_div], style={"display": "flex", "flex-direction": "column"}))

def get_day(row,note_df):
    children = [
        html.Div(row["DAY"].strftime("%d/%m"), style={"font-size": "0.9em","font-weight":"600"})
    ]
    if row["TOTAL_ADLS"] == 0:
        children.append(html.Div("NO SCHEDULED ADLS", style={"height": "11%", "width": "100%","color":"rgb(17, 60, 202)", "position": "absolute", "bottom": "0", "border-radius": "0px", "font-size": "65%","text-align": "center","font-weight": "bold"}))

    else:
        adl_completion = round(float(row["ADL_COMPLETION_PERCENTAGE"]))
        children.append(
            dbc.Progress(
                value=adl_completion,
                color="rgb(255, 170, 5)",
                
                striped=True,
                animated=True,
                style={"height": "15px", "width": "100%", "position": "absolute",
                       "bottom": "0", "border-radius": "0px","progress-bar-color":"#fff", "overflow": "hidden"},
            )
        )
        children.append(
            html.Div(
                f"ADLS: {row['TOTAL_COMPLETED_ADLS']}/{row['TOTAL_ADLS']}",
                style={
                    "height": "11%", "width": "100%", "position": "absolute",
                    "bottom": "1px", "border-radius": "0px","color":"rgb(17, 60, 202)",
                    "text-align": "center","font-weight": "bold","font-size": "75%", "font-variant-numeric": "lining-nums"
                },
            ),
        )
    insert_image(row,children)
    note.insert_image_note(row,children,note_df)
    children = html.Div(children, style={"width": f"{sz}em", "height": f"{sz}em", "position": "relative"})
    return dbc.Col(html.Div(children=children, style={"border": "1px rgb(211, 211, 211) solid"}), width="auto")

def get_gray_day():
    child = html.Div(
        style={"width": f"{sz}em", "height": f"{sz}em", "background": "repeating-linear-gradient(45deg,#FFF,#FFF 5px,#F370211A 5px,#F370211A 6px)"})
    return dbc.Col(html.Div(child, style={"border": "1px #fafcff solid"}), width="auto")

def get_cal(schedule_df: pd.DataFrame,note_df: pd.DataFrame):
    note_df["DAY"] = pd.to_datetime(note_df["DAY"])  # Convert "DAY" column to datetime
    # create week days header row, with each day in a column of width 8em + 2px border
    week_days = [dbc.Row([dbc.Col(html.Div(html.Div(
        day, style={"width": f"calc({sz}em + 2px)", "text-align": "center", "margin": "auto",
                    "font-weight": "600"})), width="auto") for day in DAYS], className="g-0")]

    all_days = []
    first_day = schedule_df.iloc[0]["DAY"].weekday()
    for _ in range(0, first_day):
        all_days.append(get_gray_day())

    for idx, row in schedule_df.iterrows():
        # Generate days
        all_days.append(get_day(row,note_df))

    if first_day != 0:
        for _ in range(first_day, 7):
            all_days.append(get_gray_day())

    # Create rows
    cal = []
    for i in range(0, len(all_days), 7):
        cal.append(dbc.Row(all_days[i: i+7], className="g-0"))
    return dbc.Container(week_days + cal,id='calendar')

def get_summary(schedule_df: pd.DataFrame):
    pain = schedule_df['HAS_PAIN_MENTION'].sum()
    hospitalization = schedule_df['HOSPITALIZATION_COUNT'].sum()
    fall = schedule_df['FALL_COUNT'].sum()
    completed_visits = schedule_df['VISIT_COUNTS'].sum()
    cancelled_visits = schedule_df['CANCELLATION_COUNTS'].sum()
    visits_ratio = completed_visits / (completed_visits + cancelled_visits) * 100

    completed_adls = schedule_df['TOTAL_COMPLETED_ADLS'].sum()
    total_adls = schedule_df['TOTAL_ADLS'].sum()

    adls_ratio = completed_adls/total_adls * 100

    return html.Div(
        id="summary-div",
        children=[
            html.H3("Summary of the last 28 days"),
            html.P(f"{adls_ratio:.1f}% of ADLS were completed"),
            html.P(f"{visits_ratio:.1f}% of visits were done"),
            html.P(f"{pain} reported cases of pain"),
            html.P(f"{fall} reported falls"),
            html.P(f"{hospitalization} hospitalizations"),
        ])
