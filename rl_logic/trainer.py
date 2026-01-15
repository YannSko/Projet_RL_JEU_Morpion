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
             save_interval: int = 1000, log_interval: int = 100) -> Dict:
        """
        Entraîne l'agent sur un nombre d'épisodes.
        
        Args:
            num_episodes: Nombre d'épisodes d'entraînement
            verbose: Affiche les statistiques pendant l'entraînement
            save_interval: Intervalle de sauvegarde du modèle (en épisodes)
            log_interval: Intervalle de logging (en épisodes)
        
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
        
        # Sauvegarde finale uniquement (modèle par défaut + version avec timestamp)
        final_win_rate = self.wins / num_episodes * 100
        final_draw_rate = self.draws / num_episodes * 100
        final_loss_rate = self.losses / num_episodes * 100
        
        final_metadata = {
            'total_episodes': num_episodes,
            'final_win_rate': final_win_rate,
            'final_draw_rate': final_draw_rate,
            'final_loss_rate': final_loss_rate,
            'training_time': time.time() - start_time,
            'hyperparameters': {
                'alpha': self.agent.alpha,
                'gamma': self.agent.gamma,
                'epsilon_start': initial_epsilon,
                'epsilon_final': self.agent.epsilon,
                'epsilon_min': self.agent.epsilon_min,
                'epsilon_decay': self.agent.epsilon_decay
            },
            'performance': {
                'states_learned': len(self.agent.q_table),
                'avg_reward': sum(self.episode_rewards) / len(self.episode_rewards) if self.episode_rewards else 0,
                'avg_moves': sum(self.episode_lengths) / len(self.episode_lengths) if self.episode_lengths else 0
            }
        }
        
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
                epsilon: float = 0.0) -> Dict:
        """
        Évalue l'agent contre un adversaire aléatoire sans mise à jour.
        
        Args:
            num_games: Nombre de parties à jouer
            verbose: Affiche les résultats
            epsilon: Taux d'exploration pour l'évaluation (0 = exploitation pure)
        
        Returns:
            Dictionnaire avec les statistiques d'évaluation
        """
        print(f"\n{'='*70}")
        print(f"ÉVALUATION: {num_games} parties (epsilon={epsilon})")
        print(f"{'='*70}\n")
        
        # Sauvegarder et modifier l'epsilon
        original_epsilon = self.agent.epsilon
        self.agent.set_epsilon(epsilon)
        
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
        
        # Restaurer l'epsilon
        self.agent.set_epsilon(original_epsilon)
        
        duration = time.time() - start_time
        
        # Logger l'évaluation
        self.logger.log_evaluation(
            num_games, wins, losses, draws,
            agent_config=self.agent.get_stats()
        )
        
        # Afficher les résultats
        if verbose:
            total = wins + losses + draws
            print(f"Résultats contre adversaire aléatoire:")
            print(f"  Victoires: {wins}/{total} ({wins/total*100:.1f}%)")
            print(f"  Défaites: {losses}/{total} ({losses/total*100:.1f}%)")
            print(f"  Nuls: {draws}/{total} ({draws/total*100:.1f}%)")
            print(f"  Durée: {duration:.2f}s")
            print(f"  Vitesse: {num_games/duration:.0f} parties/s")
            print(f"{'='*70}\n")
        
        return {
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'num_games': num_games,
            'win_rate': wins / num_games * 100,
            'loss_rate': losses / num_games * 100,
            'draw_rate': draws / num_games * 100,
            'duration': duration
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
