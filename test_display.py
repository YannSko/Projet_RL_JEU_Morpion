"""
Test rapide pour vérifier l'affichage des métriques
"""

from rl_logic.model_manager import ModelManager
from rl_logic.metrics import ModelMetrics

print("=" * 70)
print("TEST AFFICHAGE DES MÉTRIQUES")
print("=" * 70 + "\n")

# Créer le manager
manager = ModelManager()

# Lister les modèles
models = manager.list_models()

print(f"📁 {len(models)} modèles trouvés\n")

# Tester les 5 premiers modèles
for i, model in enumerate(models[:5], 1):
    print(f"\n{i}. {model['name']}")
    print(f"   Timestamp: {model.get('timestamp', 'N/A')}")
    print(f"   États: {model.get('states', 0)}")
    print(f"   Win Rate (racine): {model.get('final_win_rate', 'N/A')}")
    
    metadata = model.get('metadata', {})
    print(f"   Win Rate (metadata): {metadata.get('final_win_rate', 'N/A')}")
    print(f"   Total Episodes: {model.get('total_episodes', metadata.get('total_episodes', 'N/A'))}")
    
    # Tester le calcul des métriques (comme dans l'interface)
    try:
        model_data = {
            'states': model.get('states', 0),
            'epsilon': model.get('epsilon', 1.0),
            'metadata': {
                'final_win_rate': model.get('final_win_rate', metadata.get('final_win_rate', 0)),
                'final_draw_rate': model.get('final_draw_rate', metadata.get('final_draw_rate', 0)),
                'final_loss_rate': model.get('final_loss_rate', metadata.get('final_loss_rate', 0)),
                'total_episodes': model.get('total_episodes', metadata.get('total_episodes', 0)),
                **{k: v for k, v in metadata.items() if k not in ['final_win_rate', 'final_draw_rate', 'final_loss_rate', 'total_episodes']}
            },
            'timestamp': model.get('timestamp', '')
        }
        
        metrics = ModelMetrics.compute_all_metrics(model_data)
        
        if metrics and metrics.get('composite_score', 0) > 0:
            print(f"   ✅ MÉTRIQUES CALCULÉES:")
            print(f"      🏆 Score: {metrics.get('composite_score', 0):.1f}")
            print(f"      📊 Perf: {metrics.get('performance_score', 0):.1f}")
            print(f"      ⚡ Eff: {metrics.get('efficiency_score', 0):.1f}")
            print(f"      💪 Rob: {metrics.get('robustness_score', 0):.2f}")
        else:
            print(f"   ❌ Pas de métriques (ancien modèle)")
            
    except Exception as e:
        print(f"   ❌ ERREUR: {e}")

print("\n" + "=" * 70)
print("Résultat: Si vous voyez ✅ au-dessus, les métriques fonctionnent !")
print("=" * 70)
