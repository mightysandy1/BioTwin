import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import numpy as np
from dataclasses import dataclass
from sklearn.metrics import auc
from typing import List, Dict

# Initialize the app
app = dash.Dash(__name__)



# Define cell and drug profiles using dataclasses
@dataclass
class Cell:
    name: str
    category: str  # Category of the cell (e.g., Respiratory, Immune)
    resistance_factor: float  # Base resistance factor specific to the cell type

@dataclass
class Drug:
    name: str
    category: str  # Category of the drug (e.g., Antihistamine, Corticosteroid)
    potency: float  # Base potency of the drug
    specificity: float  # How specific the drug is to its target
    toxicity: float  # Toxicity factor of the drug
    half_life: float  # Drug half-life in hours
    targets: List[str]  # Biological targets for the drug

# Categorized drugs
antihistamines = {
    "Levocetirizine": Drug(name="Levocetirizine", category="Antihistamine", potency=0.85, specificity=0.9, toxicity=0.1, half_life=10.0, targets=["H1R", "Histamine"]),
    "Diphenhydramine": Drug(name="Diphenhydramine", category="Antihistamine", potency=0.75, specificity=0.8, toxicity=0.2, half_life=6.0, targets=["H1R", "Central Nervous System"]),
    "Cetirizine": Drug(name="Cetirizine", category="Antihistamine", potency=0.85, specificity=0.9, toxicity=0.1, half_life=10.0, targets=["H1R", "Histamine"])
}

corticosteroids = {
    "Dexamethasone": Drug(name="Dexamethasone", category="Corticosteroid", potency=0.9, specificity=0.9, toxicity=0.2, half_life=54.0, targets=["Inflammation", "Immune Suppression"])
}

leukotriene_antagonists = {
    "Montelukast": Drug(name="Montelukast", category="Leukotriene Receptor Antagonist", potency=0.8, specificity=0.85, toxicity=0.15, half_life=8.0, targets=["LTR", "Inflammation"])
}

drugs = {**antihistamines, **corticosteroids, **leukotriene_antagonists}

# Categorized cells
respiratory_cells = {
    "Bronchial": Cell(name="Bronchial", category="Respiratory", resistance_factor=0.05),
    "Alveolar": Cell(name="Alveolar Epithelial", category="Respiratory", resistance_factor=0.06),
    "Ciliated": Cell(name="Ciliated Epithelial", category="Respiratory", resistance_factor=0.05)
}

immune_cells = {
    "Macrophage": Cell(name="Macrophage", category="Immune", resistance_factor=0.07),
    "Lymphocyte": Cell(name="Lymphocyte", category="Immune", resistance_factor=0.04),
    "T-Cell": Cell(name="T-Cell", category="Immune", resistance_factor=0.08),
    "B-Cell": Cell(name="B-Cell", category="Immune", resistance_factor=0.06)
}

cells = {**respiratory_cells, **immune_cells}

# Map cell categories to allowed drugs
cell_drug_map = {
    "Respiratory": list(antihistamines.keys()) + list(leukotriene_antagonists.keys()),
    "Immune": list(corticosteroids.keys())
}

# Function to simulate drug response based on the selected drug and cell type
def simulate_drug_response(drug: Drug, cell: Cell, time_points=48):
    drug_concentration = [1.0 * np.exp(-0.1 * t / drug.half_life) for t in range(time_points)]
    viability = [
        1.0 - (drug.potency * drug.specificity * 0.1 * t) + (cell.resistance_factor * t / 10.0)
        for t in range(time_points)
    ]
    viability = [max(0, v) for v in viability]  # Ensure no negative values
    resistance = [cell.resistance_factor * t for t in range(time_points)]
    return {
        'viability': viability,
        'resistance': resistance,
        'drug_concentration': drug_concentration
    }

# Initial simulation data
initial_drug = drugs["Levocetirizine"]
initial_cell = cells["Bronchial"]
results = simulate_drug_response(initial_drug, initial_cell)
time_points = list(range(len(results['viability'])))

# Layout of the app
app.layout = html.Div([
    html.H1("Enhanced Drug Response Simulation Dashboard", style={'textAlign': 'center'}),

    # Dropdowns for cell types and drugs
    html.Div([
        html.Label("Select Cell Type:"),
        dcc.Dropdown(
            id="cell-type-dropdown",
            options=[{"label": f"{cell.name} ({cell.category})", "value": cell.name} for cell in cells.values()],
            value="Bronchial"
        ),
        html.Label("Select Drug:"),
        dcc.Dropdown(
            id="drug-dropdown",
            options=[{"label": f"{drug.name} ({drug.category})", "value": drug.name} for drug in drugs.values()],
            value="Levocetirizine"
        )
    ], style={"width": "50%", "margin": "auto"}),

    # Slider for adjusting drug potency
    html.Div([
        html.Label("Adjust Drug Potency:"),
        dcc.Slider(
            id='potency-slider',
            min=0.1,
            max=1.0,
            step=0.01,
            value=initial_drug.potency,
            marks={i: str(i) for i in [0.1, 0.5, 1.0]},
            tooltip={"placement": "bottom", "always_visible": True}
        )
    ], style={'margin': '20px'}),

    # Graphs
    html.Div([
        dcc.Graph(id='viability-graph'),
        dcc.Graph(id='resistance-graph')
    ]),

    # Metrics
    html.Div(id='metrics', style={'marginTop': '20px', 'textAlign': 'center'})
])

# Callback to update graphs and metrics
@app.callback(
    [
        Output('drug-dropdown', 'options'),
        Output('viability-graph', 'figure'),
        Output('resistance-graph', 'figure'),
        Output('metrics', 'children')
    ],
    [
        Input('cell-type-dropdown', 'value'),
        Input('drug-dropdown', 'value'),
        Input('potency-slider', 'value')
    ]
)
def update_dashboard(selected_cell, selected_drug, potency):
    # Find the selected cell object by name
    selected_cell_obj = next(cell for cell in cells.values() if cell.name == selected_cell)
    cell_category = selected_cell_obj.category

    # Update drug options based on cell type
    drug_options = [
        {"label": f"{drug} ({drugs[drug].category})", "value": drug}
        for drug in cell_drug_map[cell_category]
    ]

    # Fallback for selected drug if it's not in the filtered options
    if selected_drug not in cell_drug_map[cell_category]:
        selected_drug = cell_drug_map[cell_category][0]

    # Get the selected drug profile
    drug = drugs[selected_drug]

    # Update the drug's potency based on slider input
    drug.potency = potency

    # Simulate the drug response
    results = simulate_drug_response(drug, selected_cell_obj)

    # Update viability graph
    viability_fig = go.Figure()
    viability_fig.add_trace(go.Scatter(
        x=time_points, y=results['viability'], mode='lines+markers', name='Viability'
    ))
    viability_fig.update_layout(
        title=f"Cell Viability Over Time ({selected_cell} with {selected_drug})",
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
        title=f"Resistance Development Over Time ({selected_cell} with {selected_drug})",
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

    return drug_options, viability_fig, resistance_fig, metrics

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
