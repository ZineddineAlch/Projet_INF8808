import dash_bootstrap_components as dbc
from dash import html

def get_image(image_path, tooltip_text):
    
    update_image_counter()
    tooltip_id = f"tooltip_{get_image.counter}"
    image_id = f"image_{get_image.counter}"
    image = create_image(image_path, image_id)
    tooltip = dbc.Tooltip(tooltip_text, target=image_id, id=tooltip_id, placement="top")
    
    return html.Div([image, tooltip], style={"position": "relative"})

def create_image(image_path, image_id):
    
    return html.Img(
        src=image_path, 
        style={"width": "35px"}, 
        id=image_id
    )
    
def update_image_counter():
    get_image.counter = getattr(get_image, 'counter', 0) + 1


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
    first_row = images[:2]
    second_row = images[2:]

    first_row_div = html.Div(first_row, style={"display": "flex", "justify-content": "space-around","margin-top": "13%"})
    second_row_div = html.Div(second_row, style={"display": "flex", "justify-content": "space-around"})
    
    return children.append(html.Div([first_row_div, second_row_div], style={"display": "flex", "flex-direction": "column"}))