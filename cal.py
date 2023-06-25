import dash_bootstrap_components as dbc
from dash import html
import pandas as pd
from dash.dcc import Loading
import app

notes_content = [None]*35

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
        style={"background": "none", "border": "none", "padding": "0", "position": "absolute", "top": "2px", "right": "2px"},
        id={'type':'button_image', 'index':f"{get_image_note.counter%35}"},  # Set the button's ID
    )
    return button


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
    return children.append(html.Div(images, style={"display": "flex"}))

def insert_image_note(row,children,note_df):
    # Placeholder for image/icon based on different types of data
    images = []
    # Check if there are notes for the current day
    note_date = row["DAY"].strftime("%Y-%m-%d")
    notes_for_day = note_df.loc[note_df["DAY"].dt.strftime("%Y-%m-%d") == note_date, ["NOTE_TYPE", "NOTE"]].values.tolist()
    if len(notes_for_day) > 0:
        notes = {"Progress Notes": [], "Overview Notes": []}

        for note_type, note in notes_for_day:
            notes[note_type].append(note)

        bookmark_image = get_image_note("assets/note.jpeg")
        images.append(bookmark_image)

        save_content((get_image_note.counter-1)%35, (note_date, notes))

    return children.append(html.Div(images, style={"display": "flex"}))

def get_day(row,note_df):
    children = [
        html.Div(row["DAY"].strftime("%d/%m"), style={"font-size": "0.9em","font-weight":"600"})
    ]
    if row["TOTAL_ADLS"] == 0:
        children.append(html.Div("NO SCHEDULED ADLS", style={"height": "15px", "width": "100%","color":"rgb(255, 170, 5)", "position": "absolute", "bottom": "0", "border-radius": "0px", "font-size": "9px", "border-top": "0.5px rgba(239,239,240) solid", "line-height": "15px", "text-align": "center","font-weight": "bold"}))

    else:
        adl_completion = round(float(row["ADL_COMPLETION_PERCENTAGE"]))
        children.append(
            dbc.Progress(
                label=f"ADLS: {adl_completion}%",
                value=adl_completion,
                color="rgb(17, 60, 202)",
                striped=True,
                animated=True,
                style={"height": "15px", "width": "100%", "position": "absolute",
                       "bottom": "0", "border-radius": "0px","progress-bar-color":"#fff"},
            )
        )
    insert_image(row,children)
    insert_image_note(row,children,note_df)
    children = html.Div(children, style={"width": "8em", "height": "8em", "position": "relative"})
    return dbc.Col(html.Div(children=children, style={"border": "1px rgb(211, 211, 211) solid"}), width="auto")

def get_gray_day():
    child = html.Div(
        style={"width": "8em", "height": "8em", "background": "repeating-linear-gradient(45deg,#FFF,#FFF 5px,#F370211A 5px,#F370211A 6px)"})
    return dbc.Col(html.Div(child, style={"border": "1px #fafcff solid"}), width="auto")


def get_cal(schedule_df: pd.DataFrame,note_df: pd.DataFrame):
    note_df["DAY"] = pd.to_datetime(note_df["DAY"])  # Convert "DAY" column to datetime
    # create week days header row, with each day in a column of width 8em + 2px border
    week_days = [dbc.Row([dbc.Col(html.Div(html.Div(
        day, style={"width": "calc(8em + 2px)", "text-align": "center", "margin": "auto",
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

def save_content(index:int, content):
    notes_content[index] = content

def retrieve_saved_content_note(index:int):
    global notes_content
    date, notes = notes_content[index-1]
    ret = [html.H3(f"Notes for {date}")]
    children = []
    for note_type, notes_ in notes.items():
        if len(notes_) > 0:
            sub_children = [html.H5(note_type)]
            for n in notes_:
                sub_children.append(html.Li(n))
            children.append(html.Ul(sub_children, style={"width": "50%"}))
    notes_div = html.Div(children, style={"display":"flex", "flex-direction": "row", "text-align": "left"})
    ret.append(notes_div)
    return ret

def default_content():
    return "Click on note to show content"

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
