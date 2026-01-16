"""
Module d'entraînement des agents RL
Gère la boucle d'entraînement, l'évaluation et la décroissance de l'epsilon.
"""

import time
from typing import Tuple, Optional, Dict
from engine.environment import TicTacToeEnvironment
from .agent import QLearningAgent, RandomAgent
from .logger import RLLogger
from .model_manager import ModelManager


class Trainer:
    """
    Gère l'entraînement et l'évaluation des agents Q-Learning.
    Intègre le logging automatique et la gestion des modèles.
    """
    
    def __init__(self, agent: QLearningAgent, env: TicTacToeEnvironment,
                 logger: Optional[RLLogger] = None,
                 model_manager: Optional[ModelManager] = None):
        """
        Initialise le trainer.
        
        Args:
            agent: Agent QLearningAgent à entraîner
            env: Environnement du jeu
            logger: Logger pour l'enregistrement (créé si None)
            model_manager: Gestionnaire de modèles (créé si None)
        """
        self.agent = agent
        self.env = env
        self.logger = logger or RLLogger()
        self.model_manager = model_manager or ModelManager()
        self.opponent = RandomAgent()
        
        # Statistiques d'entraînement (buffer avant logging)
        self.episode_rewards = []
        self.episode_lengths = []
        self.wins = 0
        self.losses = 0
        self.draws = 0
    
    def play_episode(self, agent_starts: bool = True, 
                    update_agent: bool = True) -> Tuple[Optional[int], int]:
        """
        Joue un épisode complet (une partie).
        
        Args:
            agent_starts: Si True, l'agent joue en premier (X), sinon en second (O)
            update_agent: Si True, met à jour la Q-table de l'agent
        
        Returns:
            winner: 1 (X), -1 (O) ou None (nul)
            num_moves: Nombre de coups joués
        """
        state = self.env.reset()
        done = False
        num_moves = 0
        
        # Si l'agent ne commence pas, l'adversaire joue
        if not agent_starts:
            legal_actions = self.env.legal_actions(state)
            action = self.opponent.choose_action(state, legal_actions)
            state, _, done = self.env.apply_action(action)
            num_moves += 1
        
        # Boucle de jeu
        agent_prev_state = None
        agent_prev_action = None
        
        while not done:
            # Tour de l'agent
            legal_actions = self.env.legal_actions(state)
            action = self.agent.choose_action(state, legal_actions)
            
            next_state, reward, done = self.env.apply_action(action)
            num_moves += 1
            
            # Sauvegarder pour mise à jour après le tour de l'adversaire
            agent_prev_state = state
            agent_prev_action = action
            
            # Si l'agent gagne directement
            if update_agent and done:
                next_legal_actions = self.env.legal_actions(next_state)
                self.agent.update(state, action, reward, next_state, 
                                next_legal_actions, done)
            
            if done:
                break
            
            state = next_state
            
            # Tour de l'adversaire
            legal_actions = self.env.legal_actions(state)
            opponent_action = self.opponent.choose_action(state, legal_actions)
            
            state, opponent_reward, done = self.env.apply_action(opponent_action)
            num_moves += 1
            
            # Mise à jour de l'agent après le tour de l'adversaire
            if update_agent:
                # Si l'adversaire a gagné, l'agent reçoit une récompense négative
                if done and opponent_reward > 0:
                    final_reward = -1.0
                elif done and opponent_reward == 0.5:
                    final_reward = 0.5  # Match nul
                else:
                    final_reward = 0.0  # Partie continue
                
                next_legal_actions = self.env.legal_actions(state)
                self.agent.update(agent_prev_state, agent_prev_action, final_reward, 
                                state, next_legal_actions, done)
        
        winner = self.env.get_winner()
        return winner, num_moves
    
    def train(self, num_episodes: int, verbose: bool = True, 
             save_interval: int = 1000, log_interval: int = 100,
             eval_games: int = 1000, eval_seeds: int = 3) -> Dict:
        """
        Entraîne l'agent sur un nombre d'épisodes.
        
        Args:
            num_episodes: Nombre d'épisodes d'entraînement
            verbose: Affiche les statistiques pendant l'entraînement
            save_interval: Intervalle de sauvegarde du modèle (en épisodes)
            log_interval: Intervalle de logging (en épisodes)
            eval_games: Nombre de parties pour l'évaluation post-training (0 = pas d'évaluation)
            eval_seeds: Nombre de seeds différentes pour l'évaluation (pour robustesse)
        
        Returns:
            Dictionnaire avec les statistiques d'entraînement
        """
        start_time = time.time()
        initial_epsilon = self.agent.epsilon
        
        print("\n" + "=" * 70)
        print(f"DÉBUT DE L'ENTRAÎNEMENT: {num_episodes} épisodes")
        print("=" * 70)
        print(f"Configuration:")
        print(f"  Alpha (α): {self.agent.alpha}")
        print(f"  Gamma (γ): {self.agent.gamma}")
        print(f"  Epsilon initial (ε): {initial_epsilon:.4f}")
        print(f"  Epsilon min: {self.agent.epsilon_min:.4f}")
        print(f"  Decay: {self.agent.epsilon_decay:.6f}")
        print("=" * 70 + "\n")
        
        for episode in range(1, num_episodes + 1):
            # Alterner qui commence (pour un entraînement équilibré)
            agent_starts = episode % 2 == 1
            
            winner, num_moves = self.play_episode(agent_starts, update_agent=True)
            
            # Enregistrer les résultats
            agent_symbol = self.env.PLAYER_X if agent_starts else self.env.PLAYER_O
            
            if winner == agent_symbol:
                self.wins += 1
                reward = 1.0
            elif winner is None:
                self.draws += 1
                reward = 0.0
            else:
                self.losses += 1
                reward = -1.0
            
            self.episode_rewards.append(reward)
            self.episode_lengths.append(num_moves)
            
            # Décroissance de l'epsilon
            self.agent.decay_epsilon()
            
            # Logging périodique
            if episode % log_interval == 0:
                self._log_progress(episode)
            
            # Affichage périodique
            if verbose and episode % 1000 == 0:
                self._print_progress(episode, num_episodes)
        
        # ============================================================
        # ÉVALUATION POST-TRAINING (ε=0, pas de mise à jour)
        # ============================================================
        print("\n" + "=" * 70)
        print("🎯 ÉVALUATION POST-TRAINING MULTI-SEED")
        print("=" * 70)
        print(f"L'entraînement est terminé. Évaluation de la performance réelle...")
        print(f"Parties d'évaluation: {eval_games} × {eval_seeds} seeds")
        print(f"Epsilon: 0.0 (exploitation pure, pas d'exploration)")
        print(f"Mise à jour Q-table: NON (évaluation seulement)")
        print(f"Seeds: Reproductibles (42, 43, 44, ...)")
        print("=" * 70)
        
        # Évaluation pure avec epsilon=0 et multiples seeds
        eval_results = self.evaluate(
            num_games=eval_games,
            epsilon=0.0,
            num_seeds=eval_seeds,
            verbose=True
        )
        
        # ============================================================
        # MÉTADONNÉES AVEC SÉPARATION TRAIN/EVAL
        # ============================================================
        
        # Statistiques d'ENTRAÎNEMENT (historiques)
        train_win_rate = self.wins / num_episodes * 100
        train_draw_rate = self.draws / num_episodes * 100
        train_loss_rate = self.losses / num_episodes * 100
        
        # Statistiques d'ÉVALUATION (vraie performance)
        eval_win_rate = eval_results['win_rate']
        eval_draw_rate = eval_results['draw_rate']
        eval_loss_rate = eval_results['loss_rate']
        
        final_metadata = {
            # Informations générales
            'total_episodes': num_episodes,
            'training_time': time.time() - start_time,
            
            # ✅ MÉTRIQUES PRINCIPALES (depuis ÉVALUATION)
            'final_win_rate': eval_win_rate,
            'final_draw_rate': eval_draw_rate,
            'final_loss_rate': eval_loss_rate,
            'eval_games': eval_games,
            'eval_seeds': eval_seeds,
            
            # 📊 Statistiques de robustesse (multi-seed)
            'eval_robustness': {
                'win_rate_std': eval_results.get('win_rate_std', 0),
                'win_rate_min': eval_results.get('win_rate_min', eval_win_rate),
                'win_rate_max': eval_results.get('win_rate_max', eval_win_rate),
                'seed_results': eval_results.get('all_seed_results', [])
            },
            
            # Statistiques d'entraînement (pour référence)
            'training_stats': {
                'train_win_rate': train_win_rate,
                'train_draw_rate': train_draw_rate,
                'train_loss_rate': train_loss_rate,
                'avg_reward': sum(self.episode_rewards) / len(self.episode_rewards) if self.episode_rewards else 0,
                'avg_moves': sum(self.episode_lengths) / len(self.episode_lengths) if self.episode_lengths else 0
            },
            
            # Hyperparamètres
            'hyperparameters': {
                'alpha': self.agent.alpha,
                'gamma': self.agent.gamma,
                'epsilon_start': initial_epsilon,
                'epsilon_final': self.agent.epsilon,
                'epsilon_min': self.agent.epsilon_min,
                'epsilon_decay': self.agent.epsilon_decay
            },
            
            # Performance actuelle
            'performance': {
                'states_learned': len(self.agent.q_table),
                'avg_reward': sum(self.episode_rewards) / len(self.episode_rewards) if self.episode_rewards else 0,
                'avg_moves': sum(self.episode_lengths) / len(self.episode_lengths) if self.episode_lengths else 0
            },
            
            # Flag pour indiquer que les métriques viennent de l'évaluation
            'metrics_source': 'evaluation',  # 'evaluation' vs 'training'
            'eval_epsilon': 0.0
        }
        
        # Afficher le résumé comparatif
        print("\n" + "=" * 70)
        print("📊 COMPARAISON TRAIN vs EVAL")
        print("=" * 70)
        print(f"Win Rate:")
        print(f"  • Training (moyenne): {train_win_rate:.1f}%")
        print(f"  • Evaluation (ε=0):   {eval_win_rate:.1f}% ", end="")
        if eval_seeds > 1:
            print(f"± {eval_results.get('win_rate_std', 0):.1f}% ", end="")
        diff_str = f"{'✨ +' + str(round(eval_win_rate - train_win_rate, 1)) + '%' if eval_win_rate > train_win_rate else '⚠️ ' + str(round(eval_win_rate - train_win_rate, 1)) + '%'}"
        print(diff_str)
        print(f"\nLoss Rate:")
        print(f"  • Training: {train_loss_rate:.1f}%")
        print(f"  • Evaluation: {eval_loss_rate:.1f}%")
        
        if eval_seeds > 1:
            print(f"\n🎲 Robustesse (variance sur {eval_seeds} seeds):")
            print(f"  • Écart-type: {eval_results.get('win_rate_std', 0):.2f}%")
            print(f"  • Min-Max: [{eval_results.get('win_rate_min', 0):.1f}%, {eval_results.get('win_rate_max', 0):.1f}%]")
        
        print("=" * 70 + "\n")
        
        # Sauvegarder le modèle par défaut
        self.model_manager.save_model(
            self.agent,
            name="q_table",
            metadata=final_metadata
        )
        
        # Sauvegarder aussi une version avec timestamp pour l'historique
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_name = f"model_{num_episodes}ep"
        self.model_manager.save_model(
            self.agent,
            name=version_name,
            versioned=True,
            metadata=final_metadata
        )
        
        duration = time.time() - start_time
        return self._get_training_stats(num_episodes, duration)
    
    def evaluate(self, num_games: int = 100, verbose: bool = True,
                epsilon: float = 0.0, num_seeds: int = 1) -> Dict:
        """
        Évalue l'agent contre un adversaire aléatoire sans mise à jour.
        
        Args:
            num_games: Nombre de parties à jouer par seed
            verbose: Affiche les résultats
            epsilon: Taux d'exploration pour l'évaluation (0 = exploitation pure)
            num_seeds: Nombre de seeds différentes à tester (pour robustesse)
        
        Returns:
            Dictionnaire avec les statistiques d'évaluation (moyenne sur toutes les seeds)
        """
        import random
        import numpy as np
        
        print(f"\n{'='*70}")
        print(f"ÉVALUATION: {num_games} parties × {num_seeds} seed(s) (epsilon={epsilon})")
        print(f"{'='*70}\n")
        
        # Sauvegarder et modifier l'epsilon
        original_epsilon = self.agent.epsilon
        self.agent.set_epsilon(epsilon)
        
        # Résultats pour chaque seed
        all_results = []
        # Résultats pour chaque seed
        all_results = []
        
        overall_start_time = time.time()
        
        for seed_idx in range(num_seeds):
            # Définir une seed différente pour chaque run
            seed = 42 + seed_idx  # Seeds reproductibles : 42, 43, 44, ...
            random.seed(seed)
            np.random.seed(seed)
            
            if num_seeds > 1 and verbose:
                print(f"🎲 Seed {seed_idx + 1}/{num_seeds} (seed={seed})")
            
            wins = 0
            losses = 0
            draws = 0
            
            start_time = time.time()
            
            for game in range(1, num_games + 1):
                agent_starts = game % 2 == 1
                winner, num_moves = self.play_episode(agent_starts, update_agent=False)
                
                agent_symbol = self.env.PLAYER_X if agent_starts else self.env.PLAYER_O
                
                if winner == agent_symbol:
                    wins += 1
                elif winner is None:
                    draws += 1
                else:
                    losses += 1
                
                # Enregistrer dans l'historique
                player_x = "Agent" if agent_starts else "Random"
                player_o = "Random" if agent_starts else "Agent"
                self.logger.log_game(player_x, player_o, winner, num_moves,
                                   time.time() - start_time)
            
            duration = time.time() - start_time
            
            # Stocker les résultats de cette seed
            seed_results = {
                'seed': seed,
                'wins': wins,
                'losses': losses,
                'draws': draws,
                'num_games': num_games,
                'win_rate': wins / num_games * 100,
                'loss_rate': losses / num_games * 100,
                'draw_rate': draws / num_games * 100,
                'duration': duration
            }
            all_results.append(seed_results)
            
            if num_seeds > 1 and verbose:
                print(f"  Win: {wins}/{num_games} ({seed_results['win_rate']:.1f}%)")
        
        # Restaurer l'epsilon
        self.agent.set_epsilon(original_epsilon)
        
        overall_duration = time.time() - overall_start_time
        
        # Calculer les statistiques agrégées
        win_rates = [r['win_rate'] for r in all_results]
        draw_rates = [r['draw_rate'] for r in all_results]
        loss_rates = [r['loss_rate'] for r in all_results]
        
        avg_win_rate = np.mean(win_rates)
        std_win_rate = np.std(win_rates) if num_seeds > 1 else 0.0
        avg_draw_rate = np.mean(draw_rates)
        avg_loss_rate = np.mean(loss_rates)
        
        total_wins = sum(r['wins'] for r in all_results)
        total_losses = sum(r['losses'] for r in all_results)
        total_draws = sum(r['draws'] for r in all_results)
        total_games = sum(r['num_games'] for r in all_results)
        
        # Logger l'évaluation
        self.logger.log_evaluation(
            total_games, total_wins, total_losses, total_draws,
            agent_config=self.agent.get_stats()
        )
        
        # Afficher les résultats
        if verbose:
            print(f"\n📊 Résultats agrégés ({num_seeds} seed(s)):")
            print(f"  Victoires: {total_wins}/{total_games} ({avg_win_rate:.1f}%)", end="")
            if num_seeds > 1:
                print(f" ± {std_win_rate:.1f}%")
            else:
                print()
            print(f"  Défaites: {total_losses}/{total_games} ({avg_loss_rate:.1f}%)")
            print(f"  Nuls: {total_draws}/{total_games} ({avg_draw_rate:.1f}%)")
            print(f"  Durée totale: {overall_duration:.2f}s")
            print(f"  Vitesse: {total_games/overall_duration:.0f} parties/s")
            
            if num_seeds > 1:
                print(f"\n📈 Robustesse:")
                print(f"  Min Win Rate: {min(win_rates):.1f}%")
                print(f"  Max Win Rate: {max(win_rates):.1f}%")
                print(f"  Écart-type: {std_win_rate:.1f}%")
                
                # Coefficient de variation (pour évaluer la stabilité)
                cv = (std_win_rate / avg_win_rate * 100) if avg_win_rate > 0 else 0
                stability = "Très stable" if cv < 2 else "Stable" if cv < 5 else "Variable"
                print(f"  Stabilité: {stability} (CV={cv:.1f}%)")
            
            print(f"{'='*70}\n")
        
        return {
            'wins': total_wins,
            'losses': total_losses,
            'draws': total_draws,
            'num_games': total_games,
            'win_rate': avg_win_rate,
            'loss_rate': avg_loss_rate,
            'draw_rate': avg_draw_rate,
            'duration': overall_duration,
            # Statistiques de robustesse (multi-seed)
            'num_seeds': num_seeds,
            'win_rate_std': std_win_rate,
            'win_rate_min': min(win_rates),
            'win_rate_max': max(win_rates),
            'all_seed_results': all_results  # Détails par seed
        }

    
    def _print_progress(self, episode: int, total_episodes: int):
        """Affiche la progression de l'entraînement"""
        total = self.wins + self.losses + self.draws
        if total == 0:
            return
        
        win_rate = self.wins / total * 100
        loss_rate = self.losses / total * 100
        draw_rate = self.draws / total * 100
        
        # Statistiques sur les 1000 derniers épisodes
        recent_length = min(1000, len(self.episode_lengths))
        avg_length = sum(self.episode_lengths[-recent_length:]) / recent_length
        avg_reward = sum(self.episode_rewards[-recent_length:]) / recent_length
        
        print(f"\n{'─'*70}")
        print(f"Épisode {episode}/{total_episodes} ({episode/total_episodes*100:.1f}%)")
        print(f"{'─'*70}")
        print(f"Exploration:")
        print(f"  Epsilon: {self.agent.epsilon:.6f}")
        print(f"  États appris: {len(self.agent.q_table)}")
        print(f"\nPerformances globales:")
        print(f"  Victoires: {self.wins} ({win_rate:.1f}%)")
        print(f"  Défaites: {self.losses} ({loss_rate:.1f}%)")
        print(f"  Nuls: {self.draws} ({draw_rate:.1f}%)")
        print(f"\nStatistiques (derniers {recent_length} épisodes):")
        print(f"  Récompense moyenne: {avg_reward:.3f}")
        print(f"  Longueur moyenne: {avg_length:.1f} coups")
        print(f"{'─'*70}")
    
    def _log_progress(self, episode: int):
        """Enregistre la progression dans le logger"""
        total = self.wins + self.losses + self.draws
        if total == 0:
            return
        
        win_rate = self.wins / total * 100
        loss_rate = self.losses / total * 100
        draw_rate = self.draws / total * 100
        
        recent_length = min(100, len(self.episode_lengths))
        avg_reward = sum(self.episode_rewards[-recent_length:]) / recent_length
        avg_moves = sum(self.episode_lengths[-recent_length:]) / recent_length
        
        self.logger.log_training_step(
            episode=episode,
            epsilon=self.agent.epsilon,
            win_rate=win_rate,
            loss_rate=loss_rate,
            draw_rate=draw_rate,
            avg_reward=avg_reward,
            avg_moves=avg_moves,
            q_table_size=len(self.agent.q_table)
        )
    
    def _get_training_stats(self, num_episodes: int, duration: float) -> Dict:
        """Génère un rapport de fin d'entraînement"""
        total = self.wins + self.losses + self.draws
        
        stats = {
            'num_episodes': num_episodes,
            'duration': duration,
            'speed': num_episodes / duration,
            'wins': self.wins,
            'losses': self.losses,
            'draws': self.draws,
            'win_rate': self.wins / total * 100 if total > 0 else 0,
            'loss_rate': self.losses / total * 100 if total > 0 else 0,
            'draw_rate': self.draws / total * 100 if total > 0 else 0,
            'avg_episode_length': sum(self.episode_lengths) / len(self.episode_lengths) if self.episode_lengths else 0,
            'avg_reward': sum(self.episode_rewards) / len(self.episode_rewards) if self.episode_rewards else 0,
            'final_epsilon': self.agent.epsilon,
            'states_learned': len(self.agent.q_table)
        }
        
        # Afficher le résumé
        print(f"\n{'='*70}")
        print("ENTRAÎNEMENT TERMINÉ")
        print(f"{'='*70}")
        print(f"Épisodes: {stats['num_episodes']}")
        print(f"Durée: {stats['duration']:.2f}s")
        print(f"Vitesse: {stats['speed']:.0f} épisodes/s")
        print(f"\nRésultats finaux:")
        print(f"  Victoires: {stats['wins']} ({stats['win_rate']:.1f}%)")
        print(f"  Défaites: {stats['losses']} ({stats['loss_rate']:.1f}%)")
        print(f"  Nuls: {stats['draws']} ({stats['draw_rate']:.1f}%)")
        print(f"\nApprentissage:")
        print(f"  États appris: {stats['states_learned']}")
        print(f"  Epsilon final: {stats['final_epsilon']:.6f}")
        print(f"  Récompense moyenne: {stats['avg_reward']:.3f}")
        print(f"  Longueur moyenne: {stats['avg_episode_length']:.1f} coups")
        print(f"{'='*70}\n")
        
        return stats
    
    def reset_stats(self):
        """Réinitialise les statistiques d'entraînement"""
        self.episode_rewards = []
        self.episode_lengths = []
        self.wins = 0
        self.losses = 0
        self.draws = 0
