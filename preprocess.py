import pandas as pd
import re

SCHEDULE_COLS = ["DAY", "VISIT_COUNTS", "TOTAL_COMPLETED_ADLS","TOTAL_ADLS","ADL_COMPLETION_PERCENTAGE","CANCELLATION_COUNTS","CANCELLATION_REASON_AND_COUNTS","HAS_PAIN_MENTION","PAIN_DETAILS","FALL_COUNT","FALL_DETAILS","HOSPITALIZATION_COUNT","HOSPITALIZATION_DETAILS"]

def table1_header():
    
    columns=[
        {"name": "Name", "id": "Name"},
        {"name": "Completed ADLS (%)", "id": "Completed ADLS"},
        {"name": "Completed visits (%)", "id": "Completed visits"}
    ]
    
    
    return columns

def table2_header():
    
    columns=[
        {"name": "Monday", "id": "Monday"},
        {"name": "Tuesday", "id": "Tuesday"},
        {"name": "Wednesday", "id": "Wednesday"},
        {"name": "Thursday", "id": "Thursday"},
        {"name": "Friday", "id": "Friday"},
        {"name": "Saturday", "id": "Saturday"},
        {"name": "Sunday", "id": "Sunday"},
        
    ]
    return columns
    
def id_extract(df):

    # Extract unique values from the column
    unique_values = df['PATIENT_ID'].unique()

    # Create a new dataframe with unique values and split them into first name and last name
    df_unique = pd.DataFrame(unique_values, columns=['PATIENT_ID'])
    df_unique[['First Name', 'Last Name']] = df_unique['PATIENT_ID'].str.split(' ', expand=True)

    # Select only the 'First Name' and 'Last Name' columns
    df_names = df_unique[['First Name', 'Last Name']]
    
    return df_names

def completed_adls_visit(df):
    # Create an empty DataFrame with the desired columns
    empty_df = pd.DataFrame(columns=['Completed ADLS', 'Completed visits'])

    grouped_df1 = df.groupby('PATIENT_ID', sort=False).agg({
        'TOTAL_COMPLETED_ADLS': 'sum',
        'TOTAL_ADLS': 'sum'
    })
    
    # Calculate the ratio
    grouped_df1['Ratio'] = grouped_df1['TOTAL_COMPLETED_ADLS'] / grouped_df1['TOTAL_ADLS']
    
    grouped_df2 = df.groupby('PATIENT_ID', sort=False).agg({
        'VISIT_COUNTS': 'sum',
        'CANCELLATION_COUNTS': 'sum'
    })
    
    # Calculate the ratio
    grouped_df2['Ratio1'] = grouped_df2['VISIT_COUNTS'] / (grouped_df2['VISIT_COUNTS']+grouped_df2['CANCELLATION_COUNTS'])
    
    empty_df['Completed ADLS'] = grouped_df1['Ratio'].round(2)*100
    empty_df['Completed visits'] = grouped_df2['Ratio1'].round(2)*100
    
    return empty_df

def get_global_data(df):
    # Group by 'PATIENT_ID' and sum the numeric columns
    aggregated = df.groupby('PATIENT_ID').agg({
        'VISIT_COUNTS': 'sum',
        'TOTAL_COMPLETED_ADLS': 'sum',
        'TOTAL_ADLS': 'sum',
        'CANCELLATION_COUNTS': 'sum',
        'FALL_COUNT': 'sum',
        'HOSPITALIZATION_COUNT': 'sum',
        'HAS_PAIN_MENTION': 'sum'
    })

    # Adding 'ADL_COMPLETION_PERCENTAGE' column
    aggregated['ADL_COMPLETION_PERCENTAGE'] = (aggregated['TOTAL_COMPLETED_ADLS'] / aggregated['TOTAL_ADLS']) * 100
    aggregated['UNCOMPLETED_ADLS_PERCENTAGE'] = 100 - aggregated['ADL_COMPLETION_PERCENTAGE']
    return aggregated


def get_notes(notes, PATIENT_ID):

    filtered_df = notes[notes['PATIENT_ID'] == PATIENT_ID]
    filtered_df = filtered_df.drop(columns='PATIENT_ID')

    filtered_df["DAY"] = pd.to_datetime(filtered_df["DAY"])  # Convert "DAY" column to datetime

    return filtered_df  # columns DAY NOTE_TYPE NOTE

def get_note_counts(notes, PATIENT_ID):

    patient_notes = notes[notes['PATIENT_ID'] == PATIENT_ID] 
    note_counts = patient_notes.groupby('DAY').agg({
        'NOTE': 'count',
        'NOTE_TYPE': [lambda x: (x == 'Progress Notes').sum(),
                      lambda x: (x == 'Overview Notes').sum()]
    })
    
    note_counts.columns = ['NOTES_COUNT', 'PROGRESS_NOTES_COUNT', 'OVERVIEW_NOTES_COUNT']
    
    return note_counts.reset_index() # columns 	NOTES_COUNT PROGRESS_NOTES_COUNT OVERVIEW_NOTES_COUNT


def get_hospitalization_details(df, PATIENT_ID):

    patient_data = df.loc[(df['PATIENT_ID'] == PATIENT_ID) & df['HOSPITALIZATION_COUNT']!=0 ].copy()
    patient_data['HOSPITALIZATION_SOURCE'] = patient_data['HOSPITALIZATION_DETAILS'].apply(lambda x: re.search(r"'source': '([^']*)'", x).group(1) if re.search(r"'source': '([^']*)'", x) else None)
    patient_data = patient_data[['DAY', 'HOSPITALIZATION_SOURCE']]

    return patient_data #'DAY' and 'HOSPITALIZATION_SOURCE' columns

def get_pain_details(df, PATIENT_ID):

    patient_data = df.loc[(df['PATIENT_ID'] == PATIENT_ID) & (df['HAS_PAIN_MENTION'] == True)].copy()
    patient_data['PAIN_SOURCE'] = patient_data['PAIN_DETAILS'].apply(lambda x: x.split("'source': '")[1].split("'")[0] if x else None)
    patient_data = patient_data[['DAY', 'PAIN_SOURCE']]

    return patient_data #'DAY' and 'PAIN_SOURCE' columns

def get_fall_details(df, PATIENT_ID):
  
    patient_data = df.loc[(df['PATIENT_ID'] == PATIENT_ID) & df['FALL_COUNT']!=0 ].copy()
    patient_data['FALL_SOURCE'] = patient_data['FALL_DETAILS'].apply(lambda x: re.search(r"'source': '([^']*)'", x).group(1) if re.search(r"'source': '([^']*)'", x) else None)
    patient_data = patient_data[['DAY', 'FALL_SOURCE']]

    return patient_data #'DAY' and 'FALL_SOURCE' columns

def get_schedule_for_patient(df, patient_id):
    schedule = pd.DataFrame()
    schedule[SCHEDULE_COLS] = df[df["PATIENT_ID"] == patient_id][SCHEDULE_COLS]

    schedule['HOSPITALIZATION_SOURCE'] = schedule['HOSPITALIZATION_DETAILS'].apply(lambda x: re.search(r"'source': '([^']*)'", x).group(1) if re.search(r"'source': '([^']*)'", x) else None)
    schedule['PAIN_SOURCE'] = schedule['PAIN_DETAILS'].apply(lambda x: re.search(r"'source': '([^']*)'", x).group(1) if re.search(r"'source': '([^']*)'", x) else None)
    schedule['FALL_SOURCE'] = schedule['FALL_DETAILS'].apply(lambda x: re.search(r"'source': '([^']*)'", x).group(1) if re.search(r"'source': '([^']*)'", x) else None)

    schedule["DAY"] = pd.to_datetime(schedule["DAY"])
    schedule = schedule.sort_values("DAY")
    return schedule

def polar_to_cartesian(r, theta):
    return [r * np.cos(theta), r * np.sin(theta)]

def calculate_area(values, thetas):
    coordinates = [polar_to_cartesian(r, theta) for r, theta in zip(values, thetas)]
    coordinates.append(coordinates[0])
    xs, ys = zip(*coordinates) 
    area = 0.5 * abs(sum(xs[i-1]*ys[i] - xs[i]*ys[i-1] for i in range(len(xs))))
    return area

def calculate_areas(df): #input timeline_dataset.csv
    df = = get_global_data(df)
    thetas = [i * 2 * np.pi / df.shape[1] for i in range(df.shape[1])]
    areas = []
    for index, row in df.iterrows():
        values = row.values.tolist()
        area = calculate_area(values, thetas)
        areas.append([index, area])
    df_areas = pd.DataFrame(areas, columns=['PATIENT_ID', 'AREA'])
    df_areas = df_areas.sort_values(by='AREA', ascending=False)

    return df_areas
