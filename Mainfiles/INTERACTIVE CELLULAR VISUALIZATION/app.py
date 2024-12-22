import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import numpy as np

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Nicotine Effect on Cell Health"

# Generate sample data for visualization
# Healthy baseline values
cytokine_levels = [10]  # TNF-α, IL-1β, IL-6 levels (aggregate measure)
viability = [100]  # Percentage of live cells
oxidative_stress = [20]  # ROS levels (lower is better)
metabolic_rate = [80]  # ATP production level
apoptosis_markers = [10]  # Caspase levels (lower is better)

# Effects of nicotine (simulation)
nicotine_steps = np.linspace(0, 10, 11)  # Nicotine exposure levels (0 to 10)
cytokine_increase = [10 + 5 * step for step in nicotine_steps]
viability_decrease = [100 - 8 * step for step in nicotine_steps]
oxidative_stress_increase = [20 + 7 * step for step in nicotine_steps]
metabolic_rate_decrease = [80 - 6 * step for step in nicotine_steps]
apoptosis_markers_increase = [10 + 4 * step for step in nicotine_steps]

# Medicine effect (simulation)
medicine_steps = np.linspace(0, 10, 11)  # Medicine response levels (0 to 10)
cytokine_reduction = [cytokine_increase[-1] - 6 * step for step in medicine_steps]
viability_recovery = [viability_decrease[-1] + 7 * step for step in medicine_steps]
oxidative_stress_reduction = [oxidative_stress_increase[-1] - 6 * step for step in medicine_steps]
metabolic_rate_recovery = [metabolic_rate_decrease[-1] + 5 * step for step in medicine_steps]
apoptosis_markers_reduction = [apoptosis_markers_increase[-1] - 3 * step for step in medicine_steps]

# Layout of the app
app.layout = html.Div([
    html.H1("Interactive Visualization: Nicotine's Effect on Cell Health", style={"textAlign": "center"}),

    html.Div([
        html.Label("Nicotine Exposure Level:"),
        dcc.Slider(
            id='nicotine-slider',
            min=0,
            max=10,
            step=1,
            value=0,
            marks={i: str(i) for i in range(11)},
        ),
    ], style={"padding": "20px"}),

    html.Div([
        html.Label("Medicine Response Level:"),
        dcc.Slider(
            id='medicine-slider',
            min=0,
            max=10,
            step=1,
            value=0,
            marks={i: str(i) for i in range(11)},
        ),
    ], style={"padding": "20px"}),

    dcc.Graph(id='cytokine-levels-graph'),
    dcc.Graph(id='cell-health-graph'),

    # Additional graphs for deeper insights
    dcc.Graph(id='trends-graph'),
    dcc.Graph(id='health-radar-graph')
])

# Callbacks for interactivity
@app.callback(
    [
        Output('cytokine-levels-graph', 'figure'),
        Output('cell-health-graph', 'figure'),
        Output('trends-graph', 'figure'),
        Output('health-radar-graph', 'figure')
    ],
    [
        Input('nicotine-slider', 'value'),
        Input('medicine-slider', 'value')
    ]
)
def update_graphs(nicotine_level, medicine_level):
    # Update data based on nicotine and medicine levels
    cytokine = cytokine_increase[nicotine_level] if medicine_level == 0 else cytokine_reduction[medicine_level]
    viability = viability_decrease[nicotine_level] if medicine_level == 0 else viability_recovery[medicine_level]
    oxidative_stress = oxidative_stress_increase[nicotine_level] if medicine_level == 0 else oxidative_stress_reduction[medicine_level]
    metabolic_rate = metabolic_rate_decrease[nicotine_level] if medicine_level == 0 else metabolic_rate_recovery[medicine_level]
    apoptosis_markers = apoptosis_markers_increase[nicotine_level] if medicine_level == 0 else apoptosis_markers_reduction[medicine_level]

    # Cytokine Levels Graph
    cytokine_fig = go.Figure()
    cytokine_fig.add_trace(go.Bar(x=["Cytokine Levels"], y=[cytokine], name="Cytokine Levels"))
    cytokine_fig.update_layout(title="Cytokine Levels (Inflammation Markers)", yaxis_title="Level", xaxis_title="Parameter")

    # Cell Health Graph
    cell_health_fig = go.Figure()
    cell_health_fig.add_trace(go.Bar(x=["Viability"], y=[viability], name="Viability"))
    cell_health_fig.add_trace(go.Bar(x=["Oxidative Stress"], y=[oxidative_stress], name="Oxidative Stress", marker_color='red'))
    cell_health_fig.add_trace(go.Bar(x=["Metabolic Rate"], y=[metabolic_rate], name="Metabolic Rate"))
    cell_health_fig.add_trace(go.Bar(x=["Apoptosis Markers"], y=[apoptosis_markers], name="Apoptosis Markers", marker_color='orange'))
    cell_health_fig.update_layout(
        title="Cell Health Parameters",
        yaxis_title="Level",
        xaxis_title="Parameters",
        barmode="group"
    )

    # Trends Graph (Line chart showing parameter trends)
    trends_fig = go.Figure()
    trends_fig.add_trace(go.Scatter(x=nicotine_steps, y=cytokine_increase, mode='lines+markers', name="Cytokine Increase"))
    trends_fig.add_trace(go.Scatter(x=nicotine_steps, y=viability_decrease, mode='lines+markers', name="Viability Decrease"))
    trends_fig.add_trace(go.Scatter(x=nicotine_steps, y=oxidative_stress_increase, mode='lines+markers', name="Oxidative Stress Increase"))
    trends_fig.add_trace(go.Scatter(x=nicotine_steps, y=metabolic_rate_decrease, mode='lines+markers', name="Metabolic Rate Decrease"))
    trends_fig.add_trace(go.Scatter(x=nicotine_steps, y=apoptosis_markers_increase, mode='lines+markers', name="Apoptosis Markers Increase"))
    trends_fig.update_layout(title="Trends of Parameters Over Nicotine Exposure", xaxis_title="Nicotine Level", yaxis_title="Parameter Level")

    # Health Radar Graph (Spider chart for overall health metrics)
    radar_fig = go.Figure()
    radar_fig.add_trace(go.Scatterpolar(
        r=[viability, oxidative_stress, metabolic_rate, apoptosis_markers],
        theta=["Viability", "Oxidative Stress", "Metabolic Rate", "Apoptosis Markers"],
        fill='toself',
        name="Cell Health Metrics"
    ))
    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 120])
        ),
        title="Cell Health Radar Chart"
    )

    return cytokine_fig, cell_health_fig, trends_fig, radar_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
