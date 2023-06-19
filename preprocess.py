import pandas as pd



def table1_header():
    
    columns=[
        {"name": "First Name", "id": "First Name"},
        {"name": "Last Name", "id": "Last Name"},
        {"name": "Completed ADLS", "id": "Completed ADLS"},
        {"name": "Completed visits", "id": "Completed visits"},
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
    df_unique[['First Name', 'Last Name']] = df_unique['PATIENT_ID'].str.split(' ', 1, expand=True)

    # Select only the 'First Name' and 'Last Name' columns
    df_names = df_unique[['First Name', 'Last Name']]
    
    print(df_names)
    return df_names

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
    aggregated['UNCOMPLETED_ADLS'] = 100 - aggregated['ADL_COMPLETION_PERCENTAGE']
    return aggregated
