import pandas as pd
import re
from fractions import Fraction
SCHEDULE_COLS = ["DAY", "VISIT_COUNTS", "TOTAL_COMPLETED_ADLS","TOTAL_ADLS","ADL_COMPLETION_PERCENTAGE","CANCELLATION_COUNTS","CANCELLATION_REASON_AND_COUNTS","HAS_PAIN_MENTION","PAIN_DETAILS","FALL_COUNT","FALL_DETAILS","HOSPITALIZATION_COUNT","HOSPITALIZATION_DETAILS"]

def table1_header():
    
    columns=[
        {"name": "Name", "id": "Name"},
        {"name": "ADLS", "id": "ADLS"},
        {"name": "Visits", "id": "Visits"},
        {"name": "Pain", "id": "Pain"},
        {"name": "Fall", "id": "Fall"},
        {"name": "Hospitalization", "id": "Hospitalization"}
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
    
    unique_values = df['PATIENT_ID'].unique()

    df_unique = pd.DataFrame(unique_values, columns=['PATIENT_ID'])
    df_unique[['First Name', 'Last Name']] = df_unique['PATIENT_ID'].str.split(' ', expand=True)

    df_names = df_unique[['First Name', 'Last Name']]
    
    return df_names

def completed_adls_visit(df):
    
    empty_df = pd.DataFrame()

    grouped_df1 = df.groupby('PATIENT_ID', sort=False).agg({
        'TOTAL_COMPLETED_ADLS': 'sum',
        'TOTAL_ADLS': 'sum',
        'HAS_PAIN_MENTION': 'sum',
        'FALL_COUNT': 'sum',
        'HOSPITALIZATION_COUNT':'sum'
    })
    
    grouped_df1['Ratio'] = grouped_df1.apply(lambda row: str(Fraction(row['TOTAL_COMPLETED_ADLS'], row['TOTAL_ADLS'])), axis=1)
    grouped_df2 = df.groupby('PATIENT_ID', sort=False).agg({
        'VISIT_COUNTS': 'sum',
        'CANCELLATION_COUNTS': 'sum',
    })
    
    grouped_df2['Ratio1'] = grouped_df2.apply(lambda row: str(Fraction(row['VISIT_COUNTS'], (row['CANCELLATION_COUNTS']+row['VISIT_COUNTS']))), axis=1)
    
    empty_df['ADLS'] = grouped_df1['Ratio']
    empty_df['Visits'] = grouped_df2['Ratio1']
    empty_df['Pain'] = grouped_df1['HAS_PAIN_MENTION']
    empty_df['Fall'] = grouped_df1['FALL_COUNT']
    empty_df['Hospitalization'] = grouped_df1['HOSPITALIZATION_COUNT']
    
    return empty_df

def get_global_data(df):
    
    aggregated = df.groupby('PATIENT_ID').agg({
        'VISIT_COUNTS': 'sum',
        'TOTAL_COMPLETED_ADLS': 'sum',
        'TOTAL_ADLS': 'sum',
        'CANCELLATION_COUNTS': 'sum',
        'FALL_COUNT': 'sum',
        'HOSPITALIZATION_COUNT': 'sum',
        'HAS_PAIN_MENTION': 'sum'
    })

    aggregated['ADL_COMPLETION_PERCENTAGE'] = (aggregated['TOTAL_COMPLETED_ADLS'] / aggregated['TOTAL_ADLS']) * 100
    aggregated['UNCOMPLETED_ADLS_PERCENTAGE'] = 100 - aggregated['ADL_COMPLETION_PERCENTAGE']
    
    return aggregated


def get_notes(notes, PATIENT_ID):

    filtered_df = notes[notes['PATIENT_ID'] == PATIENT_ID]
    filtered_df = filtered_df.drop(columns='PATIENT_ID')
    
    return filtered_df 

def get_note_counts(notes, PATIENT_ID):

    patient_notes = notes[notes['PATIENT_ID'] == PATIENT_ID] 
    note_counts = patient_notes.groupby('DAY').agg({
        'NOTE': 'count',
        'NOTE_TYPE': [lambda x: (x == 'Progress Notes').sum(),
                      lambda x: (x == 'Overview Notes').sum()]
    })
    
    note_counts.columns = ['NOTES_COUNT', 'PROGRESS_NOTES_COUNT', 'OVERVIEW_NOTES_COUNT']
    
    return note_counts.reset_index() 


def get_hospitalization_details(df, PATIENT_ID):

    patient_data = df.loc[(df['PATIENT_ID'] == PATIENT_ID) & df['HOSPITALIZATION_COUNT']!=0 ].copy()
    patient_data['HOSPITALIZATION_SOURCE'] = patient_data['HOSPITALIZATION_DETAILS'].apply(lambda x: re.search(r"'source': '([^']*)'", x).group(1) if re.search(r"'source': '([^']*)'", x) else None)
    patient_data = patient_data[['DAY', 'HOSPITALIZATION_SOURCE']]

    return patient_data 

def get_pain_details(df, PATIENT_ID):

    patient_data = df.loc[(df['PATIENT_ID'] == PATIENT_ID) & (df['HAS_PAIN_MENTION'] == True)].copy()
    patient_data['PAIN_SOURCE'] = patient_data['PAIN_DETAILS'].apply(lambda x: x.split("'source': '")[1].split("'")[0] if x else None)
    patient_data = patient_data[['DAY', 'PAIN_SOURCE']]

    return patient_data 

def get_fall_details(df, PATIENT_ID):
  
    patient_data = df.loc[(df['PATIENT_ID'] == PATIENT_ID) & df['FALL_COUNT']!=0 ].copy()
    patient_data['FALL_SOURCE'] = patient_data['FALL_DETAILS'].apply(lambda x: re.search(r"'source': '([^']*)'", x).group(1) if re.search(r"'source': '([^']*)'", x) else None)
    patient_data = patient_data[['DAY', 'FALL_SOURCE']]

    return patient_data 

def get_schedule_for_patient(df, patient_id):
    
    schedule = pd.DataFrame()
    schedule[SCHEDULE_COLS] = df[df["PATIENT_ID"] == patient_id][SCHEDULE_COLS]

    schedule['HOSPITALIZATION_SOURCE'] = schedule['HOSPITALIZATION_DETAILS'].apply(lambda x: re.search(r"'source': '([^']*)'", x).group(1) if re.search(r"'source': '([^']*)'", x) else None)
    schedule['PAIN_SOURCE'] = schedule['PAIN_DETAILS'].apply(lambda x: re.search(r"'source': '([^']*)'", x).group(1) if re.search(r"'source': '([^']*)'", x) else None)
    schedule['FALL_SOURCE'] = schedule['FALL_DETAILS'].apply(lambda x: re.search(r"'source': '([^']*)'", x).group(1) if re.search(r"'source': '([^']*)'", x) else None)

    schedule["DAY"] = pd.to_datetime(schedule["DAY"])
    schedule = schedule.sort_values("DAY")
    
    return schedule

def calculate_summary(df):

    required_columns = ['PATIENT_ID', 'FALL_COUNT', 'HOSPITALIZATION_COUNT','CANCELLATION_COUNTS']
    for col in required_columns:
        assert col in df.columns, f"Le DataFrame doit contenir une colonne '{col}'."

    unique_patients = df['PATIENT_ID'].nunique()
    total_falls = df['FALL_COUNT'].sum()
    total_hospitalizations = df['HOSPITALIZATION_COUNT'].sum()
    total_cancelation = df['CANCELLATION_COUNTS'].sum()

    return {
        'Patients': unique_patients,
        'Falls': total_falls,
        'Hospitalizations': total_hospitalizations,
        'Cancelations' : total_cancelation
    }
