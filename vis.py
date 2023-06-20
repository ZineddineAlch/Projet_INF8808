import plotly.graph_objects as go
import plotly.io as pio

# Data for the radar chart
categories = ['FALL_COUNT', 'CANCELLATION_COUNTS', 'HOSPITALIZATION_COUNT', 'HAS_PAIN_MENTION']
values = [5, 3, 2, 1]

# Create a trace for the radar chart
trace = go.Scatterpolar(
    r=values,
    theta=categories,
    fill='toself'
)

# Create the layout for the chart
layout = go.Layout(
    polar=dict(
        radialaxis=dict(visible=True)
    ),
    showlegend=False
)

# Create the figure and add the trace
fig = go.Figure(data=[trace], layout=layout)

# Save the image
pio.write_image(fig, './assets/radar_chart.png')
