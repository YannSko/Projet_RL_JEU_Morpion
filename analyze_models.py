"""
Script d'analyse et de comparaison des modèles
Permet de comparer tous les modèles entraînés et identifier le meilleur.
"""

import argparse
from pathlib import Path
from rl_logic.model_manager import ModelManager
from rl_logic.model_comparator import ModelComparator
from rl_logic.agent import QLearningAgent
from engine.environment import TicTacToeEnvironment


def analyze_all_models(models_dir: str = "models", top_n: int = 10):
    """
    Analyse complète de tous les modèles.
    
    Args:
        models_dir: Répertoire des modèles
        top_n: Nombre de modèles à afficher dans le top
    """
    print("\n" + "=" * 80)
    print(" ANALYSE COMPLÈTE DES MODÈLES")
    print("=" * 80 + "\n")
    
    manager = ModelManager(models_dir)
    manager.analyze_models(top_n)


def export_metrics(models_dir: str = "models", output_file: str = "models/models_metrics.csv"):
    """
    Exporte toutes les métriques en CSV.
    
    Args:
        models_dir: Répertoire des modèles
        output_file: Fichier de sortie
    """
    print("\n📊 Export des métriques en cours...")
    manager = ModelManager(models_dir)
    manager.export_metrics(output_file)


def load_best_model_demo(models_dir: str = "models", metric: str = "composite_score"):
    """
    Démontre le chargement du meilleur modèle.
    
    Args:
        models_dir: Répertoire des modèles
        metric: Critère de sélection
    """
    print("\n" + "=" * 80)
    print(f" CHARGEMENT DU MEILLEUR MODÈLE (critère: {metric})")
    print("=" * 80 + "\n")
    
    # Créer un agent vide
    agent = QLearningAgent()
    
    # Charger le meilleur modèle
    manager = ModelManager(models_dir)
    success = manager.load_best_model(agent, metric)
    
    if success:
        print("\n✅ Meilleur modèle chargé avec succès !")
        print(f"\nStatistiques de l'agent:")
        stats = agent.get_stats()
        print(f"  États dans la Q-table: {stats['total_states']}")
        print(f"  Paires état-action: {stats['total_state_actions']}")
        print(f"  Q-value moyenne: {stats['avg_q_value']:.4f}")
        print(f"  Q-value max: {stats['max_q_value']:.4f}")
        print(f"  Q-value min: {stats['min_q_value']:.4f}")
        print(f"\nHyperparamètres:")
        print(f"  Alpha (α): {agent.alpha}")
        print(f"  Gamma (γ): {agent.gamma}")
        print(f"  Epsilon (ε): {agent.epsilon:.6f}")
    else:
        print("\n❌ Échec du chargement du modèle")


def compare_models(models_dir: str = "models", filters: dict = None):
    """
    Compare les modèles avec filtres optionnels.
    
    Args:
        models_dir: Répertoire des modèles
        filters: Filtres à appliquer
    """
    print("\n" + "=" * 80)
    print(" COMPARAISON DES MODÈLES")
    print("=" * 80 + "\n")
    
    comparator = ModelComparator(models_dir)
    comparator.compute_metrics_for_all_models()
    
    if filters:
        print(f"Application des filtres: {filters}\n")
        filtered = comparator.filter_models(filters)
        print(f"Modèles correspondants: {len(filtered)}\n")
        
        for model in filtered[:20]:  # Afficher max 20
            print(f"  • {model['filename']}")
            print(f"    Score: {model['composite_score']:.2f} | "
                  f"Win: {model['win_rate']:.1f}% | "
                  f"États: {model['states_learned']}")
    else:
        # Afficher le rapport complet
        comparator.generate_report()


def show_categories(models_dir: str = "models"):
    """
    Affiche les modèles par catégories.
    
    Args:
        models_dir: Répertoire des modèles
    """
    print("\n" + "=" * 80)
    print(" CATÉGORISATION DES MODÈLES")
    print("=" * 80 + "\n")
    
    comparator = ModelComparator(models_dir)
    comparator.compute_metrics_for_all_models()
    categories = comparator.get_models_by_category()
    
    for category, models in categories.items():
        print(f"\n{category.upper().replace('_', ' ')} ({len(models)} modèles):")
        print("─" * 80)
        
        # Afficher les 5 premiers de chaque catégorie
        for model in models[:5]:
            print(f"  • {model['filename']}")
            print(f"    Win: {model['win_rate']:.1f}% | "
                  f"Score: {model['composite_score']:.1f} | "
                  f"Épisodes: {model['total_episodes']}")


def main():
    """Point d'entrée principal du script."""
    parser = argparse.ArgumentParser(
        description="Analyse et comparaison des modèles Q-Learning pour le Morpion"
    )
    
    parser.add_argument(
        "command",
        choices=["analyze", "export", "load", "compare", "categories"],
        help="Commande à exécuter"
    )
    
    parser.add_argument(
        "--models-dir",
        default="models",
        help="Répertoire contenant les modèles (défaut: models)"
    )
    
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Nombre de modèles à afficher dans le top (défaut: 10)"
    )
    
    parser.add_argument(
        "--metric",
        default="composite_score",
        choices=["composite_score", "win_rate", "performance_score", 
                "efficiency_score", "robustness_score"],
        help="Critère de sélection du meilleur modèle (défaut: composite_score)"
    )
    
    parser.add_argument(
        "--output",
        default="models/models_metrics.csv",
        help="Fichier de sortie pour l'export (défaut: models/models_metrics.csv)"
    )
    
    parser.add_argument(
        "--min-win-rate",
        type=float,
        help="Filtre: win rate minimum"
    )
    
    parser.add_argument(
        "--max-episodes",
        type=int,
        help="Filtre: nombre max d'épisodes"
    )
    
    parser.add_argument(
        "--min-episodes",
        type=int,
        help="Filtre: nombre min d'épisodes"
    )
    
    args = parser.parse_args()
    
    # Construire les filtres
    filters = {}
    if args.min_win_rate:
        filters['min_win_rate'] = args.min_win_rate
    if args.max_episodes:
        filters['max_episodes'] = args.max_episodes
    if args.min_episodes:
        filters['min_episodes'] = args.min_episodes
    
    # Exécuter la commande
    if args.command == "analyze":
        analyze_all_models(args.models_dir, args.top_n)
    
    elif args.command == "export":
        export_metrics(args.models_dir, args.output)
    
    elif args.command == "load":
        load_best_model_demo(args.models_dir, args.metric)
    
    elif args.command == "compare":
        compare_models(args.models_dir, filters if filters else None)
    
    elif args.command == "categories":
        show_categories(args.models_dir)


if __name__ == "__main__":
    main()
