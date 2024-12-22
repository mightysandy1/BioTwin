from flask import Flask, request, jsonify, render_template
import numpy as np
from dataclasses import dataclass
from typing import Dict
from sklearn.metrics import auc

app = Flask(__name__)

@dataclass
class Cell:
    viability: float = 1.0
    metabolic_rate: float = 1.2
    membrane_permeability: float = 0.7
    resistance_factor: float = 0.05
    protein_expression: Dict[str, float] = None

    def __post_init__(self):
        if self.protein_expression is None:
            self.protein_expression = {
                'TNF_alpha': 0.8,
                'CD14': 0.7,
                'MDR1': 0.3,
                'IL6': 0.6,
            }

@dataclass
class Drug:
    name: str
    potency: float
    specificity: float
    toxicity: float
    half_life: float
    protein_targets: Dict[str, float]

class CellSimulation:
    def __init__(self, num_cells: int = 1000):
        self.cells = self._initialize_cells(num_cells)

    def _initialize_cells(self, num_cells: int):
        cells = []
        for _ in range(num_cells):
            cell = Cell(
                viability=np.random.normal(1.0, 0.1),
                metabolic_rate=np.random.normal(1.2, 0.1),
                membrane_permeability=np.random.normal(0.7, 0.1),
                resistance_factor=np.random.normal(0.05, 0.03)
            )
            for protein in cell.protein_expression:
                cell.protein_expression[protein] *= np.random.normal(1.0, 0.1)
            cells.append(cell)
        return cells

    def simulate_drug_response(self, drug: Drug, time_points: int = 48):
        results = {'viability': [], 'resistance': [], 'drug_concentration': []}
        current_drug_concentration = 1.0
        for _ in range(time_points):
            current_drug_concentration *= np.exp(-0.1 / drug.half_life)
            viable_cells = 0
            total_resistance = 0
            for cell in self.cells:
                if cell.viability <= 0:
                    continue
                drug_effect = self._calculate_drug_effect(cell, drug, current_drug_concentration)
                cell.viability -= drug_effect
                if cell.viability > 0:
                    cell.resistance_factor += drug_effect * 0.1
                    viable_cells += 1
                    total_resistance += cell.resistance_factor
            survival_rate = viable_cells / len(self.cells)
            avg_resistance = total_resistance / viable_cells if viable_cells > 0 else 0
            results['viability'].append(survival_rate)
            results['resistance'].append(avg_resistance)
            results['drug_concentration'].append(current_drug_concentration)
        return results

    def _calculate_drug_effect(self, cell, drug, concentration):
        effect = drug.potency * concentration * cell.membrane_permeability
        protein_effect = 0
        for protein, affinity in drug.protein_targets.items():
            protein_effect += affinity * cell.protein_expression[protein]
        protein_effect /= len(drug.protein_targets)
        total_effect = (effect * protein_effect * (1 - cell.resistance_factor) -
                        (1 - drug.specificity) * drug.toxicity)
        return max(0, total_effect * cell.metabolic_rate)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.json
    drug = Drug(
        name=data['name'],
        potency=float(data['potency']),
        specificity=float(data['specificity']),
        toxicity=float(data['toxicity']),
        half_life=float(data['half_life']),
        protein_targets={
            'TNF_alpha': 0.6,
            'CD14': 0.8,
            'MDR1': 0.2,
            'IL6': 0.7
        }
    )
    simulation = CellSimulation(num_cells=int(data['num_cells']))
    results = simulation.simulate_drug_response(drug, time_points=48)
    auc_viability = auc(range(48), results['viability'])
    final_viability = results['viability'][-1]
    final_resistance = results['resistance'][-1]
    results.update({
        'auc': auc_viability,
        'final_viability': final_viability,
        'final_resistance': final_resistance
    })
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)