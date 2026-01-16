"""
Script pour afficher les nouvelles métriques RL des modèles
Affiche Bellman Error, TD Error Stats, Return Variance, Sample Efficiency, Policy Entropy
"""

from rl_logic.model_manager import ModelManager
from rl_logic.metrics import ModelMetrics
from pathlib import Path
import sys


def display_rl_metrics(model_name: str = None):
    """
    Affiche les métriques RL d'un modèle spécifique ou du meilleur.
    
    Args:
        model_name: Nom du modèle (None = meilleur modèle)
    """
    print("\n" + "=" * 80)
    print(" 🧠 MÉTRIQUES REINFORCEMENT LEARNING - ANALYSE DÉTAILLÉE")
    print("=" * 80 + "\n")
    
    manager = ModelManager()
    
    # Charger le modèle
    if model_name:
        print(f"📁 Chargement du modèle : {model_name}")
        from rl_logic.agent import QLearningAgent
        from engine.environment import TicTacToeEnvironment
        
        env = TicTacToeEnvironment()
        agent = QLearningAgent(env)
        success = manager.load_model(agent, str(manager.models_dir / model_name))
        
        if not success:
            print(f"❌ Modèle '{model_name}' introuvable!")
            return
        
        # Récupérer métadonnées
        metadata = manager.metadata.get(str(manager.models_dir / model_name), {})
    else:
        print("🏆 Chargement du meilleur modèle (composite_score)...")
        from rl_logic.agent import QLearningAgent
        from engine.environment import TicTacToeEnvironment
        
        # Trouver le meilleur modèle via la liste
        models_list = manager.list_models()
        if not models_list:
            print("❌ Aucun modèle disponible!")
            return
        
        # Prendre le premier (déjà trié par composite_score)
        best_model = models_list[0]
        model_name = best_model['name']
        model_path = best_model['path']
        metadata = best_model.get('metadata', {})
        
        env = TicTacToeEnvironment()
        agent = QLearningAgent(env)
        success = manager.load_model(agent, model_path)
        
        if not success:
            print("❌ Erreur lors du chargement!")
            return
    
    print(f"✅ Modèle chargé : {model_name}\n")
    
    # Préparer les données pour le calcul des métriques
    model_data = {
        'states': len(agent.q_table),
        'epsilon': agent.epsilon,
        'metadata': metadata
    }
    
    # Calculer toutes les métriques (avec Q-table)
    metrics = ModelMetrics.compute_all_metrics(
        model_data, 
        q_table=agent.q_table,
        episode_rewards=None  # Pas d'historique d'épisodes pour les modèles sauvegardés
    )
    
    # Afficher les métriques classiques
    print("=" * 80)
    print(" 📊 MÉTRIQUES CLASSIQUES")
    print("=" * 80)
    print(f"  Win Rate:           {metrics['win_rate']:.2f}%")
    print(f"  Draw Rate:          {metrics['draw_rate']:.2f}%")
    print(f"  Loss Rate:          {metrics['loss_rate']:.2f}%")
    print(f"  Performance Score:  {metrics['performance_score']:.2f}")
    print(f"  Efficiency Score:   {metrics['efficiency_score']:.2f}")
    print(f"  Robustness Score:   {metrics['robustness_score']:.2f}")
    print(f"  Learning Speed:     {metrics['learning_speed']:.2f}")
    print(f"  States Learned:     {metrics['states_learned']}")
    print(f"  Total Episodes:     {metrics['total_episodes']}")
    
    # Afficher les NOUVELLES métriques RL
    print("\n" + "=" * 80)
    print(" 🧠 NOUVELLES MÉTRIQUES REINFORCEMENT LEARNING")
    print("=" * 80)
    
    # Sample Efficiency
    sample_eff = metrics.get('sample_efficiency', 0)
    sample_status = "✅ Excellent" if sample_eff > 5.0 else "⚠️ Moyen" if sample_eff > 2.0 else "❌ Faible"
    print(f"\n  1️⃣ Sample Efficiency")
    print(f"     Score: {sample_eff:.2f} {sample_status}")
    print(f"     → Performance obtenue par 1000 épisodes")
    print(f"     → Plus élevé = meilleur apprentissage")
    
    # Bellman Error
    if 'bellman_error' in metrics:
        bellman = metrics['bellman_error']
        bellman_status = "✅ Convergé" if bellman < 0.1 else "⚠️ Bon" if bellman < 0.3 else "❌ Instable"
        print(f"\n  2️⃣ Bellman Error")
        print(f"     Score: {bellman:.4f} {bellman_status}")
        print(f"     → Mesure la convergence de la Q-table")
        print(f"     → Plus petit = meilleure convergence")
    
    # Return Variance
    ret_var = metrics.get('return_variance', 0)
    var_status = "✅ Stable" if ret_var < 0.3 else "⚠️ Moyen" if ret_var < 0.5 else "❌ Instable"
    print(f"\n  3️⃣ Return Variance")
    print(f"     Score: {ret_var:.4f} {var_status}")
    print(f"     → Mesure la stabilité de la politique")
    print(f"     → Plus petit = politique plus consistante")
    
    # Policy Entropy
    if 'policy_entropy' in metrics:
        entropy = metrics['policy_entropy']
        entropy_status = "✅ Déterministe" if entropy < 0.3 else "⚠️ Bon" if entropy < 0.7 else "❌ Trop exploratoire"
        print(f"\n  4️⃣ Policy Entropy")
        print(f"     Score: {entropy:.4f} {entropy_status}")
        print(f"     → Mesure le déterminisme de la politique")
        print(f"     → 0 = totalement déterministe, >1 = exploratoire")
    
    # TD Error Stats
    if 'td_error_stats' in metrics:
        td_stats = metrics['td_error_stats']
        print(f"\n  5️⃣ TD Error Statistics")
        print(f"     Mean:     {td_stats['mean']:.4f}")
        print(f"     Std Dev:  {td_stats['std']:.4f}")
        print(f"     Variance: {td_stats['variance']:.4f}")
        print(f"     → Qualité de l'apprentissage temporel")
    
    # Q-Table Quality
    if 'q_table_quality' in metrics:
        q_quality = metrics['q_table_quality']
        print(f"\n  📊 Q-Table Quality")
        print(f"     Mean Q-value:  {q_quality['mean']:.4f}")
        print(f"     Std Dev:       {q_quality['std']:.4f}")
        print(f"     Range:         {q_quality['range']:.4f}")
        print(f"     Min/Max:       {q_quality['min']:.4f} / {q_quality['max']:.4f}")
    
    # Score Composite Final
    composite = metrics.get('composite_score', 0)
    composite_status = "🏆 Excellent" if composite > 70 else "✅ Bon" if composite > 50 else "⚠️ Moyen"
    print("\n" + "=" * 80)
    print(" 🎯 SCORE COMPOSITE GLOBAL")
    print("=" * 80)
    print(f"  Score: {composite:.2f}/100 {composite_status}")
    print(f"  → Combinaison pondérée de toutes les métriques")
    print(f"  → 30% Performance, 12% Efficiency, 15% Robustness")
    print(f"  → 12% Learning Speed, 10% Sample Efficiency")
    print(f"  → 8% Return Variance, 8% Convergence, 5% Entropy")
    
    # Hyperparamètres
    hyperparams = metrics.get('hyperparameters', {})
    if hyperparams:
        print("\n" + "=" * 80)
        print(" ⚙️ HYPERPARAMÈTRES")
        print("=" * 80)
        print(f"  Alpha (α):         {hyperparams.get('alpha', 'N/A')}")
        print(f"  Gamma (γ):         {hyperparams.get('gamma', 'N/A')}")
        print(f"  Epsilon Final:     {hyperparams.get('epsilon_final', agent.epsilon):.4f}")
        print(f"  Epsilon Min:       {hyperparams.get('epsilon_min', 'N/A')}")
        print(f"  Epsilon Decay:     {hyperparams.get('epsilon_decay', 'N/A')}")
    
    print("\n" + "=" * 80 + "\n")


def compare_top_models(top_n: int = 5):
    """
    Compare les N meilleurs modèles sur les nouvelles métriques RL.
    
    Args:
        top_n: Nombre de modèles à comparer
    """
    print("\n" + "=" * 80)
    print(f" 🏆 COMPARAISON DES {top_n} MEILLEURS MODÈLES - MÉTRIQUES RL")
    print("=" * 80 + "\n")
    
    from rl_logic.agent import QLearningAgent
    from engine.environment import TicTacToeEnvironment
    
    manager = ModelManager()
    models_list = manager.list_models()
    
    if len(models_list) < top_n:
        top_n = len(models_list)
        print(f"⚠️ Seulement {top_n} modèles disponibles\n")
    
    # Charger et calculer les métriques pour chaque modèle
    models_metrics = []
    env = TicTacToeEnvironment()
    
    for model_info in models_list[:top_n]:
        model_name = model_info['name']
        model_path = model_info['path']
        
        agent = QLearningAgent(env)
        success = manager.load_model(agent, model_path)
        
        if success:
            metadata = model_info.get('metadata', {})
            model_data = {
                'states': len(agent.q_table),
                'epsilon': agent.epsilon,
                'metadata': metadata
            }
            metrics = ModelMetrics.compute_all_metrics(model_data, q_table=agent.q_table)
            models_metrics.append((model_name, metrics))
    
    # Afficher le tableau comparatif
    print(f"{'Modèle':<35} | {'Composite':>9} | {'Sample Eff':>10} | {'Bellman':>8} | {'Entropy':>8}")
    print("-" * 80)
    
    for model_name, metrics in models_metrics:
        composite = metrics.get('composite_score', 0)
        sample_eff = metrics.get('sample_efficiency', 0)
        bellman = metrics.get('bellman_error', 0)
        entropy = metrics.get('policy_entropy', 0)
        
        # Tronquer le nom si trop long
        display_name = model_name[:33] + ".." if len(model_name) > 35 else model_name
        
        print(f"{display_name:<35} | {composite:>9.2f} | {sample_eff:>10.2f} | {bellman:>8.4f} | {entropy:>8.4f}")
    
    print("\n" + "=" * 80 + "\n")


def main():
    """Point d'entrée principal."""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--compare":
            top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            compare_top_models(top_n)
        else:
            model_name = sys.argv[1]
            display_rl_metrics(model_name)
    else:
        # Afficher le meilleur modèle par défaut
        display_rl_metrics()
        print("\n💡 Autres usages:")
        print("   python display_rl_metrics.py <nom_modele>")
        print("   python display_rl_metrics.py --compare [nombre]")


if __name__ == "__main__":
    main()
