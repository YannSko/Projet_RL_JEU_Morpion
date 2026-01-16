"""
Script de test pour vérifier le système de tri des modèles
"""
from pathlib import Path
from rl_logic.model_manager import ModelManager
from rl_logic.agent import QLearningAgent
from engine.environment import TicTacToeEnvironment

def test_sort_system():
    """Teste le système de tri par différents critères"""
    print("\n" + "="*70)
    print("🔍 TEST DU SYSTÈME DE TRI DES MODÈLES")
    print("="*70)
    
    # Initialiser le gestionnaire
    manager = ModelManager()
    agent = QLearningAgent()
    env = TicTacToeEnvironment()
    
    # Charger les modèles
    models = manager.list_models()
    print(f"\n📦 Nombre de modèles: {len(models)}")
    
    if len(models) == 0:
        print("❌ Aucun modèle trouvé!")
        return
    
    # Calculer les métriques pour les 5 premiers modèles
    print("\n📊 Calcul des métriques pour les premiers modèles...\n")
    
    from gui.view_models import ModelsView
    from gui.assets import Assets
    import pygame
    
    # Initialiser pygame minimalement pour Assets
    pygame.init()
    screen = pygame.display.set_mode((100, 100))
    assets = Assets(window_size=100)
    
    # Créer une vue (sans affichage)
    view = ModelsView(screen, assets, agent, env, manager)
    
    # Tester les 3 critères de tri
    criteria = ['composite_score', 'sample_efficiency', 'bellman_error']
    
    for criterion in criteria:
        print(f"\n{'='*70}")
        print(f"🎯 TRI PAR: {criterion.upper()}")
        print('='*70)
        
        # Trouver l'index du critère
        try:
            view.current_sort_index = view.sort_criteria.index(criterion)
        except ValueError:
            print(f"❌ Critère '{criterion}' non trouvé!")
            continue
        
        # Trier
        view._sort_models()
        
        # Afficher le top 5
        print(f"\n🏆 TOP 5 MODÈLES PAR {criterion}:\n")
        for i, model in enumerate(view.models[:5]):
            name = model['name']
            metrics = model.get('metrics', {})
            
            if metrics:
                comp_score = metrics.get('composite_score', 0)
                sample_eff = metrics.get('sample_efficiency', 0)
                bellman = metrics.get('bellman_error', 999)
                
                print(f"{i+1}. {name}")
                print(f"   Score: {comp_score:.1f} | Sample Eff: {sample_eff:.2f} | Bellman: {bellman:.4f}")
            else:
                print(f"{i+1}. {name} (pas de métriques)")
            print()
    
    # Test du meilleur modèle
    print(f"\n{'='*70}")
    print("🏆 MEILLEUR MODÈLE (composite_score)")
    print('='*70)
    
    best_path = manager.get_best_model('composite_score')
    if best_path:
        print(f"\n📁 Chemin: {best_path}")
        
        # Charger et afficher ses métriques
        success = manager.load_best_model(agent, metric='composite_score')
        if success:
            print("✅ Modèle chargé avec succès!")
            
            # Trouver dans la liste triée
            for model in view.models:
                if model['path'] == best_path:
                    metrics = model.get('metrics', {})
                    if metrics:
                        print(f"\n📊 Métriques du meilleur modèle:")
                        print(f"   • Score Composite: {metrics.get('composite_score', 0):.1f}/100")
                        print(f"   • Sample Efficiency: {metrics.get('sample_efficiency', 0):.2f}")
                        print(f"   • Bellman Error: {metrics.get('bellman_error', 999):.4f}")
                        print(f"   • Return Variance: {metrics.get('return_variance', 0):.3f}")
                        print(f"   • Policy Entropy: {metrics.get('policy_entropy', 0):.3f}")
                    break
        else:
            print("❌ Échec du chargement")
    else:
        print("❌ Aucun meilleur modèle trouvé")
    
    print("\n" + "="*70)
    print("✅ TEST TERMINÉ")
    print("="*70 + "\n")
    
    pygame.quit()

if __name__ == "__main__":
    test_sort_system()
