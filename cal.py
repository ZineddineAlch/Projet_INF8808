import dash_bootstrap_components as dbc
from dash import html
import pandas as pd

DAYS = ["Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"]

def get_image(image_path, tooltip_text):
    get_image.counter = getattr(get_image, 'counter', 0) + 1
    tooltip_id = f"tooltip_{get_image.counter}"
    image_id = f"image_{get_image.counter}"
    image = html.Img(src=image_path, style={"width": "35px"}, id=image_id)
    tooltip = dbc.Tooltip(tooltip_text, target=image_id, id=tooltip_id, placement="top")
    
    return html.Div([image, tooltip], style={"position": "relative"})

def insert_image(row,children):
    # Placeholder for image/icon based on different types of data
    images = []

    if row["FALL_COUNT"] > 0:
        image = get_image("assets/fall.png", f"Falls: {row['FALL_COUNT']}, , {row['FALL_SOURCE']}")
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
    return children.append(html.Div(images, style={"display": "flex"}))

def get_note_section(note_content):
    note_div = html.Div(
        note_content,
        id="note-content",
        className="note-content",
        style={"background-color": "brown", "padding": "5px"},
    )
    return note_div



def get_day(row):
    children = [
        html.Div(row["DAY"].strftime("%d/%m"), style={"font-size": "0.9em","font-weight":"600"})
    ]

    if row["TOTAL_ADLS"] == 0:
        
        children.append(html.Div("NO SCHEDULED ADLS", style={"height": "15px", "width": "100%", "position": "absolute", "bottom": "0", "border-radius": "0px", "font-size": "10px", "border-top": "0.5px rgba(239,239,240) solid", "line-height": "15px"}))
    else:
        adl_completion = round(float(row["ADL_COMPLETION_PERCENTAGE"]))
        children.append(
            dbc.Progress(
                label=f"ADLS: {adl_completion}%",
                value=adl_completion,
                color="success",
                striped=True,
                animated=True,
                style={"height": "15px", "width": "100%", "position": "absolute",
                       "bottom": "0", "border-radius": "0px","progress-bar-color":"#fff"},
            )
        )

    insert_image(row,children)
    children = html.Div(children, style={"width": "7em", "height": "7em", "position": "relative"})
    return dbc.Col(html.Div(children=children, style={"border": "1px black solid"}), width="auto")

def get_gray_day():
    child = html.Div(
        style={"width": "7em", "height": "7em", "background": "repeating-linear-gradient(45deg,#FFF,#FFF 5px,#F370211A 5px,#F370211A 6px)"})
    return dbc.Col(html.Div(child, style={"border": "1px black solid"}), width="auto")


def get_cal(schedule_df: pd.DataFrame):
    # create week days header row, with each day in a column of width 7em + 2px border
    week_days = [dbc.Row([dbc.Col(html.Div(html.Div(
        day, style={"width": "calc(7em + 2px)", "text-align": "center", "margin": "auto",
                    "font-weight": "600"})), width="auto") for day in DAYS], className="g-0")]

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

def get_summary(schedule_df: pd.DataFrame):
    pain = schedule_df['HAS_PAIN_MENTION'].values.sum()
    hospitalization = schedule_df['HOSPITALIZATION_COUNT'].values.sum()
    fall = schedule_df['FALL_COUNT'].values.sum()
    completed_visits = schedule_df['VISIT_COUNTS'].values.sum()
    cancelled_visits = schedule_df['CANCELLATION_COUNTS'].values.sum()
    visits_ratio = completed_visits / (completed_visits + cancelled_visits) * 100

    completed_adls = schedule_df['TOTAL_COMPLETED_ADLS'].values.sum()
    total_adls = schedule_df['TOTAL_ADLS'].values.sum()

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
