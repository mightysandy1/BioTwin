import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import dash_cytoscape as cyto
import numpy as np
import pandas as pd
from sklearn.metrics import auc

# Initialize the app
app = dash.Dash(__name__)

# Simulated results for demonstration (replace with your actual simulation logic)
def simulate_drug_response(potency, time_points=48):
    drug_concentration = [1.0 * np.exp(-0.1 * t / 10.0) for t in range(time_points)]
    viability = [1.0 - (potency * 0.1 * t) for t in range(time_points)]
    viability = [max(0, v) for v in viability]  # Ensure no negative values
    resistance = [0.05 * t for t in range(time_points)]
    return {
        'viability': viability,
        'resistance': resistance,
        'drug_concentration': drug_concentration
    }

# Initial data for plotting
initial_potency = 0.85
results = simulate_drug_response(initial_potency)
time_points = list(range(len(results['viability'])))

# Layout for 3D scatter plot
fig_3d = go.Figure(data=[go.Scatter3d(
    x=results['drug_concentration'],
    y=results['viability'],
    z=results['resistance'],
    mode='markers',
    marker=dict(
        size=5,
        color=results['viability'],  # Color by viability
        colorscale='Viridis',
        opacity=0.8
    )
)])
fig_3d.update_layout(
    title="3D Visualization of Drug Response",
    scene=dict(
        xaxis_title="Drug Concentration",
        yaxis_title="Cell Viability",
        zaxis_title="Resistance Factor"
    )
)

# Cytoscape layout for biological interactions
elements = [
    {'data': {'id': 'H1R', 'label': 'Histamine Receptor'}, 'position': {'x': 50, 'y': 50}},
    {'data': {'id': 'Drug', 'label': 'Levocetirizine'}, 'position': {'x': 200, 'y': 50}},
    {'data': {'source': 'Drug', 'target': 'H1R', 'label': 'Targets'}}
]
cytoscape_layout = cyto.Cytoscape(
    id='cytoscape-example',
    elements=elements,
    layout={'name': 'preset'},
    style={'width': '100%', 'height': '400px'}
)

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Drug Response Simulation Dashboard", style={'textAlign': 'center'}),

    # Slider for adjusting drug potency
    html.Div([
        html.Label("Adjust Drug Potency:"),
        dcc.Slider(
            id='potency-slider',
            min=0.1,
            max=1.0,
            step=0.01,
            value=initial_potency,
            marks={i: str(i) for i in [0.1, 0.5, 1.0]},
            tooltip={"placement": "bottom", "always_visible": True},
        )
    ], style={'margin': '20px'}),

    # Graphs
    html.Div([
        dcc.Graph(id='viability-graph'),
        dcc.Graph(id='resistance-graph')
    ]),

    html.Div([
        dcc.Graph(figure=fig_3d)
    ], style={'marginTop': '20px'}),

    # Cytoscape for biological network visualization
    html.Div([
        html.H3("Biological Interaction Network", style={'textAlign': 'center'}),
        cytoscape_layout
    ], style={'marginTop': '20px'}),

    # Metrics
    html.Div(id='metrics', style={'marginTop': '20px', 'textAlign': 'center'})
])

# Callback to update graphs and metrics
@app.callback(
    [
        Output('viability-graph', 'figure'),
        Output('resistance-graph', 'figure'),
        Output('metrics', 'children')
    ],
    [Input('potency-slider', 'value')]
)
def update_dashboard(potency):
    results = simulate_drug_response(potency)

    # Update viability graph
    viability_fig = go.Figure()
    viability_fig.add_trace(go.Scatter(
        x=time_points, y=results['viability'], mode='lines+markers', name='Viability'
    ))
    viability_fig.update_layout(
        title="Cell Viability Over Time",
        xaxis_title="Time (hours)",
        yaxis_title="Viability",
        template="plotly"
    )

    # Update resistance graph
    resistance_fig = go.Figure()
    resistance_fig.add_trace(go.Scatter(
        x=time_points, y=results['resistance'], mode='lines+markers', name='Resistance'
    ))
    resistance_fig.update_layout(
        title="Resistance Development Over Time",
        xaxis_title="Time (hours)",
        yaxis_title="Resistance Factor",
        template="plotly"
    )

    # Calculate and display metrics
    cumulative_effectiveness = auc(time_points, [1 - v for v in results['viability']])
    metrics = html.Div([
        html.H4(f"Cumulative Drug Effectiveness: {cumulative_effectiveness:.2f}"),
        html.H4(f"Final Cell Viability: {results['viability'][-1]:.2%}"),
        html.H4(f"Final Resistance Level: {results['resistance'][-1]:.3f}")
    ])

    return viability_fig, resistance_fig, metrics

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
