from dash import html

notes_content = [None]*35

def get_image_note(note_path):
    get_image_note.counter = getattr(get_image_note, 'counter', 0) + 1
    note_id = f"image_{get_image_note.counter}"
    note = create_image(note_path, note_id)
    button = create_button_with_image(note)
    return button

def create_image(note_path, note_id):
    return html.Img(
        src=note_path,
        style={"width": "35px"},
        id=note_id,
    )

def create_button_with_image(image_element):
    button = html.Button(
        children=image_element,
        style={"background": "none", "border": "none", "padding": "0", "position": "absolute", "top": "2px", "right": "2px"},
        id={'type': 'button_image', 'index': f"{get_image_note.counter % 35}"},
    )
    return button

def insert_image_note(row,children,note_df):
    images = []
    note_date = get_formatted_date(row["DAY"])
    notes_for_day = get_notes_for_date(note_df, note_date)
    
    if notes_for_day:
        notes = group_notes_by_type(notes_for_day)
        bookmark_image = get_image_note("assets/note.jpeg")
        images.append(bookmark_image)
        save_content((get_image_note.counter-1)%35, (note_date, notes))

    return children.append(html.Div(images, style={"display": "flex"}))

def get_formatted_date(day):
    return day.strftime("%Y-%m-%d")

def get_notes_for_date(note_df, note_date):
    return note_df.loc[note_df["DAY"].dt.strftime("%Y-%m-%d") == note_date, ["NOTE_TYPE", "NOTE"]].values.tolist()

def group_notes_by_type(notes_for_day):
    notes = {"Progress Notes": [], "Overview Notes": []}
    for note_type, note in notes_for_day:
        notes[note_type].append(note)
    return notes


def save_content(index:int, content):
    date, notes = content
    ret = create_notes_header(date)
    children = create_note_children(notes)
    notes_div = create_notes_div(children)
    ret.append(notes_div)
    notes_content[index] = ret
    
def create_notes_header(date):
    return [html.H3(f"Notes for {date}")]

def create_note_children(notes):
    children = []
    for note_type, notes_ in notes.items():
        if notes_:
            sub_children = [html.H5(note_type)]
            for n in notes_:
                sub_children.append(html.Li(n))
            children.append(html.Ul(sub_children))
    return children

def create_notes_div(children):
    return html.Div(children, style={"display": "flex", "flex-direction": "column", "text-align": "left"})

def retrieve_saved_content_note(index:int):
    return notes_content[index-1]

def default_content():
    return "Click on note to show content"