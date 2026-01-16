"""
Script pour réévaluer tous les modèles avec epsilon=0 (évaluation pure)
et mettre à jour leurs métadonnées avec les vraies métriques de performance.
"""

from pathlib import Path
from typing import Dict
import time
from rl_logic.model_manager import ModelManager
from rl_logic.agent import QLearningAgent
from engine.environment import TicTacToeEnvironment
from rl_logic.trainer import Trainer

def reevaluate_model(model_path: str, num_games: int = 1000) -> Dict:
    """
    Réévalue un modèle avec epsilon=0 sur num_games parties.
    
    Args:
        model_path: Chemin vers le modèle
        num_games: Nombre de parties d'évaluation
    
    Returns:
        Dictionnaire avec les résultats d'évaluation
    """
    # Charger le modèle
    agent = QLearningAgent()
    env = TicTacToeEnvironment()
    manager = ModelManager()
    
    success = manager.load_model(agent, model_path)
    if not success:
        return None
    
    # Créer un trainer pour l'évaluation
    trainer = Trainer(agent, env)
    
    # Évaluation pure (epsilon=0, pas de mise à jour)
    eval_results = trainer.evaluate(
        num_games=num_games,
        epsilon=0.0,
        verbose=False
    )
    
    total = eval_results['wins'] + eval_results['losses'] + eval_results['draws']
    
    return {
        'eval_win_rate': eval_results['wins'] / total * 100,
        'eval_draw_rate': eval_results['draws'] / total * 100,
        'eval_loss_rate': eval_results['losses'] / total * 100,
        'eval_games': num_games,
        'eval_timestamp': time.time()
    }

def reevaluate_all_models(num_games: int = 1000, max_models: int = None):
    """
    Réévalue tous les modèles et met à jour leurs métadonnées.
    
    Args:
        num_games: Nombre de parties d'évaluation par modèle
        max_models: Limite du nombre de modèles (None = tous)
    """
    print("\n" + "="*70)
    print("🔄 RÉÉVALUATION DES MODÈLES")
    print("="*70)
    print(f"Parties par modèle: {num_games}")
    print(f"Epsilon: 0.0 (exploitation pure)")
    print("="*70 + "\n")
    
    manager = ModelManager()
    models = manager.list_models()
    
    if max_models:
        models = models[:max_models]
    
    print(f"📦 {len(models)} modèles à réévaluer\n")
    
    results = []
    
    for i, model_info in enumerate(models, 1):
        model_path = model_info['path']
        model_name = model_info['name']
        
        print(f"[{i}/{len(models)}] {model_name[:50]}...", end=" ", flush=True)
        
        # Réévaluer
        try:
            eval_data = reevaluate_model(model_path, num_games)
            
            if eval_data:
                # Récupérer les anciennes métadonnées
                old_metadata = model_info.get('metadata', {})
                old_win_rate = old_metadata.get('final_win_rate', 0)
                
                # Calculer la différence
                new_win_rate = eval_data['eval_win_rate']
                diff = new_win_rate - old_win_rate
                
                # Afficher les résultats
                print(f"✓ {new_win_rate:.1f}% (Δ {diff:+.1f}%)")
                
                # Mettre à jour les métadonnées
                # On garde les anciennes mais on ajoute les nouvelles d'évaluation
                updated_metadata = old_metadata.copy()
                updated_metadata.update({
                    'eval_results': eval_data,
                    'original_train_win_rate': old_win_rate,  # Sauvegarder l'ancien
                    'final_win_rate': new_win_rate,  # Remplacer par le nouveau
                    'final_draw_rate': eval_data['eval_draw_rate'],
                    'final_loss_rate': eval_data['eval_loss_rate']
                })
                
                # Sauvegarder les nouvelles métadonnées
                # (On va juste mettre à jour le fichier metadata séparé)
                results.append({
                    'name': model_name,
                    'path': model_path,
                    'old_win_rate': old_win_rate,
                    'new_win_rate': new_win_rate,
                    'difference': diff,
                    'metadata': updated_metadata
                })
            else:
                print("✗ Échec du chargement")
        
        except Exception as e:
            print(f"✗ Erreur: {e}")
    
    # Résumé
    print("\n" + "="*70)
    print("📊 RÉSUMÉ DE LA RÉÉVALUATION")
    print("="*70)
    
    if results:
        avg_diff = sum(r['difference'] for r in results) / len(results)
        max_diff = max(results, key=lambda x: abs(x['difference']))
        
        print(f"\n✅ {len(results)}/{len(models)} modèles réévalués")
        print(f"\n📈 Statistiques:")
        print(f"   • Différence moyenne: {avg_diff:+.2f}%")
        print(f"   • Plus grande diff: {max_diff['difference']:+.1f}% ({max_diff['name'][:40]})")
        
        # Top 5 des différences les plus importantes
        print(f"\n🔝 Top 5 des plus grandes différences:")
        sorted_by_diff = sorted(results, key=lambda x: abs(x['difference']), reverse=True)
        for i, r in enumerate(sorted_by_diff[:5], 1):
            print(f"   {i}. {r['name'][:40]}")
            print(f"      Train: {r['old_win_rate']:.1f}% → Eval: {r['new_win_rate']:.1f}% "
                  f"({r['difference']:+.1f}%)")
        
        # Sauvegarder les résultats dans un fichier JSON
        import json
        output_file = Path('models') / 'reevaluation_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': time.time(),
                'num_games': num_games,
                'models_evaluated': len(results),
                'avg_difference': avg_diff,
                'results': [
                    {
                        'name': r['name'],
                        'old_win_rate': r['old_win_rate'],
                        'new_win_rate': r['new_win_rate'],
                        'difference': r['difference']
                    }
                    for r in results
                ]
            }, f, indent=2)
        
        print(f"\n💾 Résultats sauvegardés dans: {output_file}")
        
        # Option pour mettre à jour les métadonnées
        print("\n" + "="*70)
        response = input("Voulez-vous mettre à jour les métadonnées des modèles ? (oui/non): ")
        
        if response.lower() in ['oui', 'o', 'yes', 'y']:
            print("\n🔄 Mise à jour des métadonnées...")
            
            # Charger les métadonnées existantes
            metadata_file = Path('models') / 'models_metadata.json'
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    all_metadata = json.load(f)
            else:
                all_metadata = {}
            
            # Mettre à jour
            for r in results:
                model_name = r['name']
                all_metadata[model_name] = r['metadata']
            
            # Sauvegarder
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(all_metadata, f, indent=2)
            
            print(f"✅ Métadonnées mises à jour: {metadata_file}")
        else:
            print("⏭️  Métadonnées non modifiées")
    
    print("\n" + "="*70)
    print("✅ RÉÉVALUATION TERMINÉE")
    print("="*70 + "\n")

def compare_train_vs_eval():
    """
    Compare les performances d'entraînement vs évaluation pour analyse.
    """
    print("\n" + "="*70)
    print("📊 ANALYSE TRAIN VS EVAL")
    print("="*70)
    
    manager = ModelManager()
    models = manager.list_models()
    
    # Grouper par nombre d'épisodes
    by_episodes = {}
    for model in models:
        metadata = model.get('metadata', {})
        episodes = metadata.get('total_episodes', 0)
        
        if episodes > 0:
            # Grouper par tranche de 10k épisodes
            group = (episodes // 10000) * 10000
            if group not in by_episodes:
                by_episodes[group] = []
            by_episodes[group].append(model)
    
    print("\n📈 Win Rate moyen par tranche d'épisodes:")
    print("(montre si les modèles avec peu d'épisodes sont sous-estimés)\n")
    
    for episodes in sorted(by_episodes.keys()):
        group_models = by_episodes[episodes]
        avg_win_rate = sum(
            m.get('metadata', {}).get('final_win_rate', 0) 
            for m in group_models
        ) / len(group_models)
        
        print(f"   {episodes:>6d}-{episodes+9999:<6d} épisodes : "
              f"{avg_win_rate:5.1f}% (n={len(group_models)})")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    import sys
    
    # Arguments en ligne de commande
    num_games = 1000
    max_models = None
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--compare":
            compare_train_vs_eval()
            sys.exit(0)
        else:
            num_games = int(sys.argv[1])
    
    if len(sys.argv) > 2:
        max_models = int(sys.argv[2])
    
    # Réévaluer
    reevaluate_all_models(num_games, max_models)
