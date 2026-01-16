"""
AutoML - Hyperparameter Tuning Automatique
Grid Search et Random Search pour Q-Learning
"""

import time
import itertools
import random
from typing import Dict, List, Optional
from pathlib import Path
import csv
from datetime import datetime
from engine.environment import TicTacToeEnvironment
from .agent import QLearningAgent
from .trainer import Trainer
from .logger import RLLogger
from .model_manager import ModelManager


class AutoMLTuner:
    """
    Optimisation automatique des hyperparamètres pour Q-Learning.
    """
    
    def __init__(self, env: TicTacToeEnvironment):
        """
        Initialise le tuner.
        
        Args:
            env: Environnement de jeu
        """
        self.env = env
        self.results = []
        self.results_file = Path("models/automl_results.csv")
        self.best_config = None
        self.best_score = 0
    
    def grid_search(self, param_grid: Dict[str, List], 
                   num_episodes: int = 10000,
                   eval_games: int = 100,
                   max_configs: Optional[int] = None) -> Dict:
        """
        Grid Search : teste toutes les combinaisons d'hyperparamètres.
        
        Args:
            param_grid: Dictionnaire {paramètre: [valeurs]}
            num_episodes: Nombre d'épisodes d'entraînement par config
            eval_games: Nombre de parties d'évaluation
            max_configs: Nombre max de configurations à tester
        
        Returns:
            Meilleure configuration trouvée
        """
        print("\n" + "=" * 70)
        print("🔧 AUTOML - GRID SEARCH")
        print("=" * 70)
        
        # Générer toutes les combinaisons
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        all_combinations = list(itertools.product(*param_values))
        
        if max_configs and len(all_combinations) > max_configs:
            print(f"\n⚠️  {len(all_combinations)} combinaisons possibles, limitation à {max_configs}")
            all_combinations = all_combinations[:max_configs]
        
        total_configs = len(all_combinations)
        print(f"\n📊 Nombre de configurations à tester: {total_configs}")
        print(f"⏱️  Épisodes par config: {num_episodes}")
        print(f"📈 Évaluation: {eval_games} parties\n")
        print("=" * 70 + "\n")
        
        start_time = time.time()
        
        # Tester chaque configuration
        for i, combination in enumerate(all_combinations, 1):
            config = dict(zip(param_names, combination))
            
            print(f"\n[{i}/{total_configs}] Test de configuration:")
            for key, value in config.items():
                print(f"  {key}: {value}")
            print()
            
            # Entraîner et évaluer
            result = self._train_and_evaluate(config, num_episodes, eval_games, i)
            self.results.append(result)
            
            # Mettre à jour le meilleur
            if result['composite_score'] > self.best_score:
                self.best_score = result['composite_score']
                self.best_config = config
                print(f"  🏆 NOUVEAU MEILLEUR! Score: {self.best_score:.2f}")
            else:
                print(f"  Score: {result['composite_score']:.2f} (meilleur: {self.best_score:.2f})")
        
        duration = time.time() - start_time
        
        # Sauvegarder les résultats
        self._save_results()
        
        # Afficher le résumé
        print("\n" + "=" * 70)
        print("🏆 GRID SEARCH TERMINÉ")
        print("=" * 70)
        print(f"\nDurée totale: {duration/60:.1f} minutes")
        print(f"Configurations testées: {total_configs}")
        print(f"\nMEILLEURE CONFIGURATION (Score: {self.best_score:.2f}):")
        for key, value in self.best_config.items():
            print(f"  {key}: {value}")
        print("=" * 70 + "\n")
        
        return {
            'best_config': self.best_config,
            'best_score': self.best_score,
            'all_results': self.results,
            'duration': duration
        }
    
    def random_search(self, param_distributions: Dict[str, tuple], 
                     n_iter: int = 20,
                     num_episodes: int = 10000,
                     eval_games: int = 100) -> Dict:
        """
        Random Search : échantillonne aléatoirement les hyperparamètres.
        
        Args:
            param_distributions: {param: (min, max)}
            n_iter: Nombre d'itérations
            num_episodes: Épisodes d'entraînement par config
            eval_games: Parties d'évaluation
        
        Returns:
            Meilleure configuration trouvée
        """
        print("\n" + "=" * 70)
        print("🎲 AUTOML - RANDOM SEARCH")
        print("=" * 70)
        print(f"\n📊 Nombre d'itérations: {n_iter}")
        print(f"⏱️  Épisodes par config: {num_episodes}")
        print(f"📈 Évaluation: {eval_games} parties\n")
        print("=" * 70 + "\n")
        
        start_time = time.time()
        
        for i in range(1, n_iter + 1):
            # Échantillonner une configuration aléatoire
            config = {}
            for param, (min_val, max_val) in param_distributions.items():
                if param in ['alpha', 'gamma', 'epsilon_decay']:
                    config[param] = random.uniform(min_val, max_val)
                elif param == 'epsilon_min':
                    config[param] = random.uniform(min_val, max_val)
                elif param == 'epsilon':
                    config[param] = random.uniform(min_val, max_val)
            
            print(f"\n[{i}/{n_iter}] Test de configuration:")
            for key, value in config.items():
                print(f"  {key}: {value:.4f}")
            print()
            
            # Entraîner et évaluer
            result = self._train_and_evaluate(config, num_episodes, eval_games, i)
            self.results.append(result)
            
            # Mettre à jour le meilleur
            if result['composite_score'] > self.best_score:
                self.best_score = result['composite_score']
                self.best_config = config
                print(f"  🏆 NOUVEAU MEILLEUR! Score: {self.best_score:.2f}")
            else:
                print(f"  Score: {result['composite_score']:.2f} (meilleur: {self.best_score:.2f})")
        
        duration = time.time() - start_time
        
        # Sauvegarder
        self._save_results()
        
        # Résumé
        print("\n" + "=" * 70)
        print("🏆 RANDOM SEARCH TERMINÉ")
        print("=" * 70)
        print(f"\nDurée totale: {duration/60:.1f} minutes")
        print(f"Configurations testées: {n_iter}")
        print(f"\nMEILLEURE CONFIGURATION (Score: {self.best_score:.2f}):")
        for key, value in self.best_config.items():
            print(f"  {key}: {value:.4f}")
        print("=" * 70 + "\n")
        
        return {
            'best_config': self.best_config,
            'best_score': self.best_score,
            'all_results': self.results,
            'duration': duration
        }
    
    def _train_and_evaluate(self, config: Dict, num_episodes: int, 
                           eval_games: int, config_id: int) -> Dict:
        """
        Entraîne et évalue un agent avec une configuration donnée.
        
        Args:
            config: Configuration des hyperparamètres
            num_episodes: Nombre d'épisodes d'entraînement
            eval_games: Nombre de parties d'évaluation
            config_id: ID de la configuration
        
        Returns:
            Résultats détaillés
        """
        # Créer l'agent avec la configuration
        agent = QLearningAgent(
            alpha=config.get('alpha', 0.2),
            gamma=config.get('gamma', 0.99),
            epsilon=config.get('epsilon', 1.0),
            epsilon_min=config.get('epsilon_min', 0.01),
            epsilon_decay=config.get('epsilon_decay', 0.9995)
        )
        
        # Entraîner
        logger = RLLogger()
        model_manager = ModelManager()
        trainer = Trainer(agent, self.env, logger, model_manager)
        
        train_start = time.time()
        # Évaluation plus courte pour AutoML (gain de temps)
        eval_games = min(500, max(100, num_episodes // 20))
        train_stats = trainer.train(num_episodes, verbose=False, eval_games=eval_games)
        train_duration = time.time() - train_start
        
        # Évaluer
        eval_stats = trainer.evaluate(eval_games, verbose=False, epsilon=0.0)
        
        # Calculer les métriques
        from .metrics import ModelMetrics
        
        metadata = {
            'final_win_rate': eval_stats['win_rate'],
            'final_draw_rate': eval_stats['draw_rate'],
            'final_loss_rate': eval_stats['loss_rate'],
            'total_episodes': num_episodes,
            'hyperparameters': config,
            'performance': {
                'states_learned': len(agent.q_table),
                'avg_reward': train_stats.get('avg_reward', 0),
                'avg_moves': train_stats.get('avg_episode_length', 0)
            }
        }
        
        model_data = {
            'states': len(agent.q_table),
            'epsilon': agent.epsilon,
            'metadata': metadata
        }
        
        metrics = ModelMetrics.compute_all_metrics(model_data)
        
        # Résultat complet
        result = {
            'config_id': config_id,
            'timestamp': datetime.now().isoformat(),
            'config': config,
            'train_duration': train_duration,
            'train_win_rate': train_stats.get('win_rate', 0),
            'eval_win_rate': eval_stats['win_rate'],
            'eval_draw_rate': eval_stats['draw_rate'],
            'eval_loss_rate': eval_stats['loss_rate'],
            'states_learned': len(agent.q_table),
            'final_epsilon': agent.epsilon,
            'composite_score': metrics.get('composite_score', 0),
            'performance_score': metrics.get('performance_score', 0),
            'efficiency_score': metrics.get('efficiency_score', 0),
            'robustness_score': metrics.get('robustness_score', 0),
            'learning_speed': metrics.get('learning_speed', 0)
        }
        
        return result
    
    def _save_results(self):
        """Sauvegarde les résultats en CSV"""
        if not self.results:
            return
        
        self.results_file.parent.mkdir(exist_ok=True)
        
        # En-têtes
        fieldnames = list(self.results[0].keys())
        
        # Aplatir les configs
        flattened_results = []
        for result in self.results:
            flat = result.copy()
            config = flat.pop('config')
            for key, value in config.items():
                flat[f'config_{key}'] = value
            flattened_results.append(flat)
        
        # Écrire le CSV
        with open(self.results_file, 'w', newline='') as f:
            fieldnames = list(flattened_results[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flattened_results)
        
        print(f"\n💾 Résultats sauvegardés: {self.results_file}")
    
    @staticmethod
    def get_default_grid() -> Dict[str, List]:
        """Retourne une grille d'hyperparamètres par défaut"""
        return {
            'alpha': [0.1, 0.15, 0.2, 0.25, 0.3],
            'gamma': [0.90, 0.92, 0.95, 0.97, 0.99],
            'epsilon_decay': [0.990, 0.995, 0.997, 0.999]
        }
    
    @staticmethod
    def get_default_distributions() -> Dict[str, tuple]:
        """Retourne des distributions par défaut pour random search"""
        return {
            'alpha': (0.05, 0.5),
            'gamma': (0.85, 0.99),
            'epsilon_decay': (0.98, 0.9999),
            'epsilon_min': (0.001, 0.1)
        }
