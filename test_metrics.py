"""
Script de test pour vérifier le calcul des métriques
"""

import pickle
from pathlib import Path
from rl_logic.metrics import ModelMetrics

# Charger un modèle récent
models_dir = Path("models")
model_files = list(models_dir.glob("model_*ep_*.pkl"))

if not model_files:
    print("❌ Aucun modèle trouvé")
    exit(1)

# Prendre le plus récent
latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
print(f"📊 Test du modèle: {latest_model.name}\n")

# Charger le modèle
with open(latest_model, 'rb') as f:
    model_data = pickle.load(f)

print("=== Contenu du modèle ===")
print(f"Clés: {model_data.keys()}\n")

print("=== Métadonnées ===")
metadata = model_data.get('metadata', {})
for key, value in metadata.items():
    print(f"  {key}: {value}")

print("\n=== Stats ===")
stats = model_data.get('stats', {})
for key, value in stats.items():
    print(f"  {key}: {value}")

print("\n=== Hyperparamètres ===")
hyperparams = model_data.get('hyperparameters', {})
for key, value in hyperparams.items():
    print(f"  {key}: {value}")

# Tester le calcul des métriques
print("\n" + "="*70)
print("CALCUL DES MÉTRIQUES")
print("="*70)

try:
    # Préparer les données comme dans le code
    test_data = {
        'states': stats.get('total_states', 0),
        'epsilon': stats.get('epsilon', 1.0),
        'metadata': metadata
    }
    
    print(f"\nDonnées pour le calcul:")
    print(f"  states: {test_data['states']}")
    print(f"  epsilon: {test_data['epsilon']}")
    print(f"  metadata keys: {list(test_data['metadata'].keys())}")
    
    metrics = ModelMetrics.compute_all_metrics(test_data)
    
    print("\n✅ MÉTRIQUES CALCULÉES:")
    print(f"  🏆 Composite Score: {metrics.get('composite_score', 'N/A'):.2f}")
    print(f"  📊 Performance Score: {metrics.get('performance_score', 'N/A'):.2f}")
    print(f"  ⚡ Efficiency Score: {metrics.get('efficiency_score', 'N/A'):.2f}")
    print(f"  💪 Robustness Score: {metrics.get('robustness_score', 'N/A'):.2f}")
    print(f"  🚀 Learning Speed: {metrics.get('learning_speed', 'N/A'):.2f}")
    
    print(f"\n  Win Rate: {metrics.get('win_rate', 'N/A'):.2f}%")
    print(f"  Draw Rate: {metrics.get('draw_rate', 'N/A'):.2f}%")
    print(f"  Loss Rate: {metrics.get('loss_rate', 'N/A'):.2f}%")
    print(f"  États appris: {metrics.get('states_learned', 'N/A')}")
    print(f"  Épisodes: {metrics.get('total_episodes', 'N/A')}")
    
except Exception as e:
    print(f"\n❌ ERREUR lors du calcul:")
    print(f"  {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
