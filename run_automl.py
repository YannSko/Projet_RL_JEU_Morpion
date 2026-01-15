"""
Script pour lancer l'AutoML - Hyperparameter Tuning
"""

from rl_logic.automl import AutoMLTuner
from engine.environment import TicTacToeEnvironment

def main():
    print("🤖 AUTOML - Optimisation Automatique des Hyperparamètres")
    print("=" * 70 + "\n")
    
    env = TicTacToeEnvironment()
    tuner = AutoMLTuner(env)
    
    print("Choisissez le type de recherche:")
    print("  1. Grid Search (test toutes les combinaisons)")
    print("  2. Random Search (échantillonnage aléatoire)")
    print("  3. Grid Search rapide (configurations réduites)")
    
    choice = input("\nVotre choix (1-3): ").strip()
    
    episodes = int(input("Épisodes d'entraînement par config (défaut: 10000): ") or "10000")
    eval_games = int(input("Parties d'évaluation (défaut: 100): ") or "100")
    
    if choice == "1":
        # Grid Search complet
        param_grid = {
            'alpha': [0.1, 0.15, 0.2, 0.25, 0.3],
            'gamma': [0.90, 0.92, 0.95, 0.97, 0.99],
            'epsilon_decay': [0.990, 0.995, 0.997, 0.999]
        }
        
        total = 5 * 5 * 4  # 100 configurations
        print(f"\n⚠️  Cela va tester {total} configurations!")
        print(f"⏱️  Temps estimé: ~{total * episodes / 2000:.0f} minutes")
        
        if input("Continuer? (o/n): ").lower() == 'o':
            result = tuner.grid_search(param_grid, episodes, eval_games)
    
    elif choice == "2":
        # Random Search
        param_distributions = {
            'alpha': (0.05, 0.5),
            'gamma': (0.85, 0.99),
            'epsilon_decay': (0.98, 0.9999),
            'epsilon_min': (0.001, 0.1)
        }
        
        n_iter = int(input("Nombre d'itérations (défaut: 20): ") or "20")
        
        print(f"\n⚠️  Cela va tester {n_iter} configurations aléatoires")
        print(f"⏱️  Temps estimé: ~{n_iter * episodes / 2000:.0f} minutes")
        
        if input("Continuer? (o/n): ").lower() == 'o':
            result = tuner.random_search(param_distributions, n_iter, episodes, eval_games)
    
    else:
        # Grid Search rapide
        param_grid = {
            'alpha': [0.15, 0.2, 0.25],
            'gamma': [0.92, 0.95, 0.99],
            'epsilon_decay': [0.995, 0.997]
        }
        
        total = 3 * 3 * 2  # 18 configurations
        print(f"\n⚠️  Cela va tester {total} configurations")
        print(f"⏱️  Temps estimé: ~{total * episodes / 2000:.0f} minutes")
        
        if input("Continuer? (o/n): ").lower() == 'o':
            result = tuner.grid_search(param_grid, episodes, eval_games)
    
    print("\n✅ AutoML terminé!")
    print(f"📊 Résultats détaillés dans: models/automl_results.csv")
    print("\n💡 Utilisez la meilleure configuration pour votre prochain entraînement!")

if __name__ == "__main__":
    main()
