import pandas as pd

SCHEDULE_COLS = ["DAY", "VISIT_COUNTS", "TOTAL_COMPLETED_ADLS","TOTAL_ADLS","ADL_COMPLETION_PERCENTAGE","CANCELLATION_COUNTS","CANCELLATION_REASON_AND_COUNTS","HAS_PAIN_MENTION","PAIN_DETAILS","FALL_COUNT","FALL_DETAILS","HOSPITALIZATION_COUNT","HOSPITALIZATION_DETAILS"]

def table1_header():
    
    columns=[
        {"name": "First Name", "id": "First Name"},
        {"name": "Last Name", "id": "Last Name"},
        {"name": "Completed ADLS (%)", "id": "Completed ADLS"},
        {"name": "Completed visits (%)", "id": "Completed visits"},
        {"name": "Stats", "id": "Stats", "presentation": "markdown"}
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


def get_schedule_for_patient(df, patient_id):
    schedule = pd.DataFrame()
    schedule[SCHEDULE_COLS] = df[df["PATIENT_ID"] == patient_id][SCHEDULE_COLS]

    # TODO Parse JSON for hospitalization and fall details
    for r in schedule["HOSPITALIZATION_DETAILS"]:
        ...
    
    schedule["DAY"] = pd.to_datetime(schedule["DAY"])
    schedule = schedule.sort_values("DAY")

    return schedule
