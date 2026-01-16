"""
Test rapide de l'entraînement avec évaluation post-training
"""
from rl_logic.agent import QLearningAgent
from engine.environment import TicTacToeEnvironment
from rl_logic.trainer import Trainer
from rl_logic.model_manager import ModelManager

def test_train_with_eval():
    """Test d'un entraînement court avec évaluation"""
    print("\n" + "="*70)
    print("🧪 TEST : ENTRAÎNEMENT + ÉVALUATION POST-TRAINING")
    print("="*70)
    
    # Initialiser
    agent = QLearningAgent(
        alpha=0.15,
        gamma=0.92,
        epsilon=1.0,
        epsilon_min=0.01,
        epsilon_decay=0.9995
    )
    env = TicTacToeEnvironment()
    manager = ModelManager()
    trainer = Trainer(agent, env, model_manager=manager)
    
    # Entraîner avec évaluation automatique
    print("\n🎓 Lancement de l'entraînement...")
    results = trainer.train(
        num_episodes=5000,      # Entraînement court
        eval_games=200,         # 200 parties d'évaluation par seed
        eval_seeds=5,           # 5 seeds différentes (robustesse)
        verbose=True
    )
    
    # Vérifier les métadonnées du modèle sauvegardé
    print("\n" + "="*70)
    print("📋 VÉRIFICATION DES MÉTADONNÉES")
    print("="*70)
    
    models = manager.list_models()
    latest_model = models[0]  # Le plus récent
    
    metadata = latest_model.get('metadata', {})
    
    print(f"\n📦 Modèle: {latest_model['name']}")
    print(f"\n✅ Métriques principales (depuis évaluation):")
    print(f"   • final_win_rate: {metadata.get('final_win_rate', 0):.1f}%")
    print(f"   • final_draw_rate: {metadata.get('final_draw_rate', 0):.1f}%")
    print(f"   • final_loss_rate: {metadata.get('final_loss_rate', 0):.1f}%")
    print(f"   • eval_games: {metadata.get('eval_games', 0)}")
    print(f"   • eval_seeds: {metadata.get('eval_seeds', 1)}")
    print(f"   • metrics_source: {metadata.get('metrics_source', 'N/A')}")
    
    # Statistiques de robustesse
    if 'eval_robustness' in metadata:
        robustness = metadata['eval_robustness']
        print(f"\n🎲 Robustesse (multi-seed):")
        print(f"   • Écart-type: {robustness.get('win_rate_std', 0):.2f}%")
        print(f"   • Min: {robustness.get('win_rate_min', 0):.1f}%")
        print(f"   • Max: {robustness.get('win_rate_max', 0):.1f}%")
        
        # Détails par seed
        if robustness.get('seed_results'):
            print(f"\n   📋 Résultats par seed:")
            for seed_res in robustness['seed_results'][:5]:  # Afficher max 5 seeds
                print(f"      Seed {seed_res['seed']}: {seed_res['win_rate']:.1f}% "
                      f"({seed_res['wins']}/{seed_res['num_games']})")
    
    if 'training_stats' in metadata:
        train_stats = metadata['training_stats']
        print(f"\n📊 Statistiques d'entraînement (référence):")
        print(f"   • train_win_rate: {train_stats.get('train_win_rate', 0):.1f}%")
        print(f"   • train_draw_rate: {train_stats.get('train_draw_rate', 0):.1f}%")
        print(f"   • train_loss_rate: {train_stats.get('train_loss_rate', 0):.1f}%")
        
        # Calculer la différence
        eval_wr = metadata.get('final_win_rate', 0)
        train_wr = train_stats.get('train_win_rate', 0)
        diff = eval_wr - train_wr
        
        print(f"\n📈 Différence Eval - Train:")
        print(f"   Win Rate: {diff:+.1f}% ", end="")
        if diff > 5:
            print("✨ (évaluation bien meilleure)")
        elif diff > 0:
            print("✅ (évaluation légèrement meilleure)")
        elif diff > -5:
            print("⚖️ (similaire)")
        else:
            print("⚠️ (surapprentissage possible)")
    
    print("\n" + "="*70)
    print("✅ TEST TERMINÉ")
    print("="*70)
    print("\n💡 Les métriques sont maintenant basées sur l'ÉVALUATION (ε=0)")
    print("   et non sur la moyenne d'entraînement !")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_train_with_eval()
