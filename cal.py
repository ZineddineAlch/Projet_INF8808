import dash_bootstrap_components as dbc
from dash import html
import pandas as pd
from dash.dcc import Loading
import app
notes_content = []
DAYS = ["Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"]


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

def get_image_note(note_path):
    get_image_note.counter = getattr(get_image_note, 'counter', 0) + 1
    note_id = f"image_{get_image_note.counter}"
    note = html.Img(
        src=note_path, 
        style={"width": "35px"}, 
        id=note_id,
    )
    button = html.Button(
        children=note,  # Place the image inside the button
        style={"background": "none", "border": "none", "padding": "0"},
        id={'type':'button_image', 'index':f"{get_image_note.counter%35}"},  # Set the button's ID
    )
    return button


def insert_image(row,children):
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

def insert_image_note(row,children,note_df):
    # Placeholder for image/icon based on different types of data
    images = []
    # Check if there are notes for the current day
    note_date = row["DAY"].strftime("%Y-%m-%d")
    notes_for_day = note_df.loc[note_df["DAY"].dt.strftime("%Y-%m-%d") == note_date, "NOTE"].values
    if len(notes_for_day) > 0:
        bookmark_image = get_image_note("assets/note.png")
        images.append(bookmark_image)
        save_content(get_image_note.counter%35, notes_for_day)
    return children.append(html.Div(images, style={"display": "flex"}))

def get_day(row,note_df):
    children = [
        html.Div(row["DAY"].strftime("%d/%m"), style={"font-size": "0.7em"})
    ]
    if row["TOTAL_ADLS"] == 0:
        children.append(html.Div("NO SCHEDULED ADLS", style={"height": "15px", "width": "100%", "position": "absolute", "bottom": "0", "border-radius": "0px", "font-size": "10px", "border": "1px black solid", "line-height": "15px"}))
    else:
        adl_completion = round(float(row["ADL_COMPLETION_PERCENTAGE"]))
        children.append(
            dbc.Progress(
                label=f"ADLS: {adl_completion}%",
                value=adl_completion,
                color="success",
                striped=True,
                animated=True,
                style={"height": "15px", "width": "100%", "position": "absolute", "bottom": "0", "border-radius": "0px"},
            )
        )
    insert_image(row,children)
    insert_image_note(row,children,note_df)
    children = html.Div(
        children=children,
        style={"width": "7em", "height": "7em", "position": "relative", "cursor": "pointer"},
    )
    return dbc.Col(html.Div(children=children, style={"border": "1px black solid"}), width="auto")
    

def get_gray_day():
    child = html.Div(
        style={"width": "7em", "height": "7em", "background": "repeating-linear-gradient(45deg,#FFF,#FFF 5px,#e9ecef 5px,#e9ecef 10px)"})
    return dbc.Col(html.Div(child, style={"border": "1px black solid"}), width="auto")


def get_cal(schedule_df: pd.DataFrame,note_df: pd.DataFrame):
    note_df["DAY"] = pd.to_datetime(note_df["DAY"])  # Convert "DAY" column to datetime
    # create week days header row, with each day in a column of width 7em + 2px border
    week_days = [dbc.Row([dbc.Col(html.Div(html.Div(
        day, style={"width": "calc(7em + 2px)", "text-align": "center", "margin": "auto"})), width="auto") for day in DAYS], className="g-0")]

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

def save_content(index:int,content):
    notes_content.insert(index,content)
    
def retrieve_saved_content_note(index:int):
    return notes_content[index-1]
def default_content():
    return "Click on note to show content"
                    
                
     
    