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


def get_day(row):
    children = [
        html.Div(row["DAY"].strftime("%d/%m"), style={"font-size": "0.7em"})
    ]

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

    children.append(html.Div(images, style={"display": "flex"}))

    children = html.Div(children, style={"width": "7em", "height": "7em", "position": "relative"})
    return dbc.Col(html.Div(children=children, style={"border": "1px black solid"}), width="auto")

def get_gray_day():
    child = html.Div(
        style={"width": "7em", "height": "7em", "background-color": "#E0E0E0"})
    return dbc.Col(html.Div(child, style={"border": "1px black solid"}), width="auto")


def get_cal(schedule_df: pd.DataFrame):
    # create week days header row, with each day in a column of width 7em + 2px border
    week_days = [dbc.Row([dbc.Col(html.Div(html.Div(
        day, style={"width": "calc(7em + 2px)"})), width="auto") for day in DAYS], className="g-0")]

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