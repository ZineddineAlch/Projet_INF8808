
import pandas as pd
from dash import html

def get_summary(schedule_df: pd.DataFrame):
    pain = schedule_df['HAS_PAIN_MENTION'].sum()
    hospitalization = schedule_df['HOSPITALIZATION_COUNT'].sum()
    fall = schedule_df['FALL_COUNT'].sum()
    completed_visits = schedule_df['VISIT_COUNTS'].sum()
    cancelled_visits = schedule_df['CANCELLATION_COUNTS'].sum()
    completed_adls = schedule_df['TOTAL_COMPLETED_ADLS'].sum()
    total_adls = schedule_df['TOTAL_ADLS'].sum()
    
    visits_ratio = completed_visits / (completed_visits + cancelled_visits) * 100
    adls_ratio = completed_adls/total_adls * 100
    
    return create_summary_div(adls_ratio, visits_ratio, pain, fall, hospitalization)
    
def create_summary_div(adls_ratio, visits_ratio, pain, fall, hospitalization):
    return html.Div(
        id="summary-div",
        children=[
            html.H3("Summary of the last 28 days"),
            html.P(f"{adls_ratio:.1f}% of ADLS were completed"),
            html.P(f"{visits_ratio:.1f}% of visits were done"),
            html.P(f"{pain} reported cases of pain"),
            html.P(f"{fall} reported falls"),
            html.P(f"{hospitalization} hospitalizations"),
        ]
    )