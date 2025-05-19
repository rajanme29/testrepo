# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Get all unique launch sites
launch_sites = sorted(spacex_df['Launch Site'].unique())
all_sites_option = 'ALL'
min_value, max_value = 0.0, 16000.0

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)

                                dcc.Dropdown(id='site-dropdown', options=[{'label': 'All Sites', 'value': 'ALL'},
                                                               {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                               {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                               {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                               {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                               ], value='ALL', 
                                             placeholder="Select a Launch Site here", searchable=True
                                             ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider', min=0, max=16000, step=500, marks={0: '0', 100: '100'},
                                                value=[min_value, max_value]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == all_sites_option:
        # For ALL sites, show success count for each site
        success_by_site = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        success_by_site.columns = ['Launch Site', 'Success Count']
        
        fig = px.pie(
            success_by_site, 
            values='Success Count', 
            names='Launch Site',
            title='Total Success Launches by Site',
            color='Launch Site'
        )
    else:
        # For specific site, show success vs failure
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        outcome_counts = filtered_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['class', 'count']
        
        fig = px.pie(
            outcome_counts, 
            values='count', 
            names='class', 
            title=f'Success vs Failure Launches for {selected_site}',
            labels={'class': 'Launch Outcome'},
            color='class',
            color_discrete_map={0: 'red', 1: 'green'}
        )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=True)
    return fig
    
# Helper function to filter data based on inputs
def get_filtered_data(selected_site, payload_range):
    # Filter by payload range first
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                    (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    
    # Then filter by site if needed
    if selected_site != all_sites_option:
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    return filtered_df

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# Callback for the payload vs outcome scatter plots
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    Input('site-dropdown', 'value'),
    Input('payload-slider', 'value')
)
def update_scatter_plot(selected_site, payload_range):
    filtered_df = get_filtered_data(selected_site, payload_range)
    
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Payload Mass vs Launch Outcome ({payload_range[0]}-{payload_range[1]} Kg)',
        labels={'class': 'Launch Outcome (1=Success, 0=Failure)'},
        hover_data=['Booster Version', 'Launch Site']
    )
    
    # Customize the scatter plot appearance
    fig.update_traces(marker=dict(size=16, opacity=0.8))
    fig.update_layout(
        yaxis=dict(tickvals=[0, 1], ticktext=['Failure', 'Success']),
        hovermode='closest'
    )
    return fig


# Run the app
if __name__ == '__main__':
    app.run()