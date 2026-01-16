"""
Test simple du système de tri sans interface graphique
"""
from pathlib import Path
from rl_logic.model_manager import ModelManager
from rl_logic.agent import QLearningAgent
from engine.environment import TicTacToeEnvironment
from rl_logic.metrics import ModelMetrics

def test_sort_logic():
    """Teste la logique de tri sans GUI"""
    print("\n" + "="*70)
    print("🔍 TEST DE LA LOGIQUE DE TRI (sans GUI)")
    print("="*70)
    
    # Initialiser
    manager = ModelManager()
    agent = QLearningAgent()
    
    # Charger les modèles
    models = manager.list_models()
    print(f"\n📦 Nombre de modèles: {len(models)}")
    
    if len(models) == 0:
        print("❌ Aucun modèle trouvé!")
        return
    
    # Meilleur modèle selon chaque critère
    print(f"\n{'='*70}")
    print("🏆 MEILLEUR MODÈLE PAR CRITÈRE")
    print('='*70)
    
    criteria = ['composite_score', 'sample_efficiency', 'bellman_error']
    
    for criterion in criteria:
        best_path = manager.get_best_model(criterion)
        if best_path:
            print(f"\n📊 Meilleur selon {criterion}:")
            print(f"   {Path(best_path).name}")
        else:
            print(f"\n❌ Pas de meilleur modèle pour {criterion}")
    
    # Charger et afficher le meilleur composite
    print(f"\n{'='*70}")
    print("🏆 CHARGEMENT DU MEILLEUR MODÈLE GLOBAL")
    print('='*70)
    
    best_path = manager.get_best_model('composite_score')
    if best_path:
        print(f"\n📁 Chemin: {Path(best_path).name}")
        
        # Charger
        success = manager.load_model(agent, best_path)
        if success:
            print("✅ Chargé avec succès!")
            print(f"   États: {len(agent.q_table)}")
            print(f"   Epsilon: {agent.epsilon:.6f}")
            print(f"   Gamma: {agent.gamma}")
        else:
            print("❌ Échec du chargement")
    
    print("\n" + "="*70)
    print("✅ TEST TERMINÉ")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_sort_logic()
