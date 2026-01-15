"""
Script pour lancer un tournoi entre modèles
"""

from rl_logic.tournament import Tournament
from rl_logic.elo_system import ELOSystem
from rl_logic.model_manager import ModelManager
from rl_logic.agent import QLearningAgent
from engine.environment import TicTacToeEnvironment

def main():
    print("🏆 SYSTÈME DE TOURNOI - Q-Learning Morpion")
    print("=" * 70 + "\n")
    
    # Initialiser
    env = TicTacToeEnvironment()
    elo_system = ELOSystem()
    tournament = Tournament(env, elo_system)
    model_manager = ModelManager()
    
    # Charger les modèles
    print("📁 Chargement des modèles...")
    models_list = model_manager.list_models()
    
    if len(models_list) < 2:
        print("❌ Au moins 2 modèles sont nécessaires pour un tournoi!")
        return
    
    # Sélectionner les modèles (top 5 ou demander)
    print(f"\nModèles disponibles ({len(models_list)}):")
    for i, model_info in enumerate(models_list[:10], 1):
        print(f"  {i}. {model_info['name']} - {model_info['states']} états")
    
    print("\nOptions:")
    print("  1. Tournoi avec les 5 meilleurs modèles (auto)")
    print("  2. Sélection manuelle")
    print("  3. Tous les modèles (peut être très long!)")
    
    choice = input("\nVotre choix (1-3): ").strip()
    
    if choice == "1":
        selected_models = models_list[:5]
    elif choice == "3":
        selected_models = models_list
    else:
        # Sélection manuelle
        indices = input("Indices des modèles (ex: 1,2,3): ").strip().split(',')
        selected_models = [models_list[int(i)-1] for i in indices]
    
    print(f"\n🎮 {len(selected_models)} modèles sélectionnés")
    
    # Charger les agents
    agents_dict = {}
    for model_info in selected_models:
        agent = QLearningAgent()
        model_manager.load_model(agent, model_info['path'])
        agents_dict[model_info['name']] = agent
    
    # Type de tournoi
    print("\nType de tournoi:")
    print("  1. Round-Robin (tous contre tous)")
    print("  2. Elimination Bracket (élimination directe)")
    
    tournament_type = input("Votre choix (1-2): ").strip()
    
    games_per_match = int(input("Parties par match (défaut: 100): ") or "100")
    
    # Lancer le tournoi
    if tournament_type == "1":
        result = tournament.round_robin(agents_dict, games_per_match)
    else:
        result = tournament.elimination_bracket(agents_dict, games_per_match)
    
    # Afficher le classement ELO
    print("\n" + "=" * 70)
    print("🏅 CLASSEMENT ELO")
    print("=" * 70 + "\n")
    
    leaderboard = elo_system.get_leaderboard()
    for rank, (name, rating) in enumerate(leaderboard[:10], 1):
        print(f"  {rank}. {name}: {rating:.0f} ELO")
    
    print("\n" + "=" * 70)
    print("✅ Tournoi terminé!")
    print("📊 Résultats sauvegardés dans models/tournament_history.json")
    print("🏅 Ratings ELO sauvegardés dans models/elo_ratings.json")
    print("=" * 70)

if __name__ == "__main__":
    main()
