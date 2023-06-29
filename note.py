from dash import html

notes_content = [None]*35

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


def save_content(index:int, content):
    date, notes = content
    ret = [html.H3(f"Notes for {date}")]
    children = []
    for note_type, notes_ in notes.items():
        if len(notes_) > 0:
            sub_children = [html.H5(note_type)]
            for n in notes_:
                sub_children.append(html.Li(n))
            children.append(html.Ul(sub_children))
    notes_div = html.Div(children, style={"display":"flex", "flex-direction": "column", "text-align": "left"})
    ret.append(notes_div)

    notes_content[index] = ret

def retrieve_saved_content_note(index:int):
    return notes_content[index-1]

def default_content():
    return "Click on note to show content"