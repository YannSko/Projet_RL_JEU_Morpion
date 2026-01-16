"""
Module de calcul de métriques pour les modèles Q-Learning
Fournit des métriques avancées pour évaluer et comparer les modèles.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class ModelMetrics:
    """
    Calcule des métriques avancées pour évaluer les modèles Q-Learning.
    """
    
    @staticmethod
    def calculate_performance_score(win_rate: float, draw_rate: float, 
                                    loss_rate: float) -> float:
        """
        Calcule un score de performance pondéré.
        
        Args:
            win_rate: Taux de victoire (0-100)
            draw_rate: Taux de match nul (0-100)
            loss_rate: Taux de défaite (0-100)
        
        Returns:
            Score de performance (0-100)
        """
        # Victoire = 1 point, Nul = 0.5 point, Défaite = 0 point
        return win_rate + (draw_rate * 0.5)
    
    @staticmethod
    def calculate_efficiency_score(win_rate: float, states_learned: int) -> float:
        """
        Calcule un score d'efficacité (performance par état appris).
        
        Args:
            win_rate: Taux de victoire (0-100)
            states_learned: Nombre d'états appris
        
        Returns:
            Score d'efficacité normalisé
        """
        # Un bon modèle a un haut win_rate avec peu d'états
        if states_learned == 0:
            return 0.0
        
        # Normaliser : plus de victoires avec moins d'états = meilleur
        efficiency = win_rate / np.log10(states_learned + 10)
        return efficiency
    
    @staticmethod
    def calculate_robustness_score(avg_reward: float, avg_moves: float) -> float:
        """
        Calcule un score de robustesse basé sur la récompense moyenne et la longueur des parties.
        
        Args:
            avg_reward: Récompense moyenne par épisode
            avg_moves: Nombre moyen de coups par partie
        
        Returns:
            Score de robustesse
        """
        # Un bon modèle gagne rapidement (peu de coups) avec une haute récompense
        if avg_moves == 0:
            return 0.0
        
        # Récompense élevée + parties courtes = meilleur
        robustness = avg_reward * (10.0 / max(avg_moves, 1.0))
        return robustness
    
    @staticmethod
    def calculate_learning_speed(win_rate: float, total_episodes: int) -> float:
        """
        Calcule la vitesse d'apprentissage (performance par épisode).
        
        Args:
            win_rate: Taux de victoire (0-100)
            total_episodes: Nombre total d'épisodes d'entraînement
        
        Returns:
            Score de vitesse d'apprentissage
        """
        if total_episodes == 0:
            return 0.0
        
        # Plus de victoires avec moins d'épisodes = apprentissage plus rapide
        return win_rate / np.log10(total_episodes + 10)
    
    @staticmethod
    def calculate_q_table_quality(q_table: Dict) -> Dict[str, float]:
        """
        Calcule des statistiques sur la qualité de la Q-table.
        
        Args:
            q_table: Q-table du modèle
        
        Returns:
            Dictionnaire avec les statistiques de qualité
        """
        all_q_values = []
        for state_actions in q_table.values():
            all_q_values.extend(state_actions.values())
        
        if not all_q_values:
            return {
                'mean': 0.0,
                'std': 0.0,
                'min': 0.0,
                'max': 0.0,
                'range': 0.0,
                'variance': 0.0
            }
        
        q_array = np.array(all_q_values)
        return {
            'mean': float(np.mean(q_array)),
            'std': float(np.std(q_array)),
            'min': float(np.min(q_array)),
            'max': float(np.max(q_array)),
            'range': float(np.max(q_array) - np.min(q_array)),
            'variance': float(np.var(q_array))
        }
    
    @staticmethod
    def calculate_bellman_error(q_table: Dict, gamma: float = 0.95) -> float:
        """
        Calcule l'erreur de Bellman moyenne sur la Q-table.
        Mesure |Q(s,a) - (R + γ·max Q(s',a'))|.
        
        Args:
            q_table: Q-table du modèle
            gamma: Facteur de discount
        
        Returns:
            Erreur de Bellman moyenne (plus petit = meilleur)
        """
        if not q_table:
            return 0.0
        
        errors = []
        for state, actions in q_table.items():
            if actions:
                max_q = max(actions.values())
                for action, q_value in actions.items():
                    # Estimation simplifiée de l'erreur TD
                    # Dans un vrai scénario, on aurait besoin de R et s'
                    # Ici on estime avec la cohérence interne de la Q-table
                    expected_q = gamma * max_q
                    error = abs(q_value - expected_q)
                    errors.append(error)
        
        return float(np.mean(errors)) if errors else 0.0
    
    @staticmethod
    def calculate_td_error_stats(episode_rewards: List[float]) -> Dict[str, float]:
        """
        Calcule les statistiques d'erreur TD sur les récompenses d'épisodes.
        
        Args:
            episode_rewards: Liste des récompenses par épisode
        
        Returns:
            Statistiques TD (mean, std, variance)
        """
        if not episode_rewards or len(episode_rewards) < 2:
            return {'mean': 0.0, 'std': 0.0, 'variance': 0.0}
        
        rewards_array = np.array(episode_rewards)
        return {
            'mean': float(np.mean(rewards_array)),
            'std': float(np.std(rewards_array)),
            'variance': float(np.var(rewards_array))
        }
    
    @staticmethod
    def calculate_return_variance(episode_rewards: List[float]) -> float:
        """
        Calcule la variance des retours cumulatifs.
        Faible variance = politique stable et consistante.
        
        Args:
            episode_rewards: Liste des récompenses par épisode
        
        Returns:
            Variance des retours (plus petit = meilleur)
        """
        if not episode_rewards or len(episode_rewards) < 2:
            return 0.0
        
        return float(np.var(episode_rewards))
    
    @staticmethod
    def calculate_sample_efficiency(win_rate: float, total_episodes: int) -> float:
        """
        Calcule l'efficacité d'échantillonnage (sample efficiency).
        Performance obtenue / Nombre d'épisodes utilisés.
        
        Args:
            win_rate: Taux de victoire final (0-100)
            total_episodes: Nombre d'épisodes d'entraînement
        
        Returns:
            Score d'efficacité (plus élevé = meilleur)
        """
        if total_episodes == 0:
            return 0.0
        
        # Normaliser par millier d'épisodes
        efficiency = win_rate / (total_episodes / 1000.0)
        return efficiency
    
    @staticmethod
    def calculate_policy_entropy(q_table: Dict, temperature: float = 1.0) -> float:
        """
        Calcule l'entropie de la politique dérivée de la Q-table.
        H(π) = -Σ π(a|s)·log(π(a|s))
        
        Args:
            q_table: Q-table du modèle
            temperature: Paramètre de température pour softmax
        
        Returns:
            Entropie moyenne (haute = exploratoire, basse = déterministe)
        """
        if not q_table:
            return 0.0
        
        entropies = []
        
        for state, actions in q_table.items():
            if not actions:
                continue
            
            # Convertir Q-values en probabilités avec softmax
            q_values = np.array(list(actions.values()))
            exp_q = np.exp(q_values / temperature)
            probs = exp_q / np.sum(exp_q)
            
            # Calculer l'entropie
            # Éviter log(0)
            probs = np.clip(probs, 1e-10, 1.0)
            entropy = -np.sum(probs * np.log(probs))
            entropies.append(entropy)
        
        return float(np.mean(entropies)) if entropies else 0.0
    
    @staticmethod
    def calculate_composite_score(metrics: Dict) -> float:
        """
        Calcule un score composite pour classer les modèles.
        Combine plusieurs métriques avec des poids.
        
        Args:
            metrics: Dictionnaire contenant les métriques du modèle
        
        Returns:
            Score composite (0-100)
        """
        # Pondérations pour chaque métrique
        weights = {
            'performance_score': 0.30,    # 30% - Le plus important
            'efficiency_score': 0.12,     # 12%
            'robustness_score': 0.15,     # 15%
            'learning_speed': 0.12,       # 12%
            'convergence': 0.08,          # 8% - Epsilon proche du minimum
            'sample_efficiency': 0.10,    # 10% - Nouvelles métriques RL
            'return_variance': 0.08,      # 8% - Stabilité (inversé)
            'policy_entropy': 0.05        # 5% - Déterminisme
        }
        
        # Calculer le score de convergence (epsilon proche de min = mieux)
        epsilon = metrics.get('epsilon', 1.0)
        epsilon_min = metrics.get('epsilon_min', 0.01)
        convergence_score = (1 - (epsilon - epsilon_min) / (1 - epsilon_min)) * 100
        
        # Normaliser return_variance (plus petit = meilleur, inverser pour le score)
        return_var = metrics.get('return_variance', 0.5)
        return_var_score = max(0, (1 - min(return_var, 1.0)) * 100)
        
        # Normaliser policy_entropy (basse = bonne politique déterministe)
        policy_ent = metrics.get('policy_entropy', 1.0)
        entropy_score = max(0, (1 - min(policy_ent / 2.0, 1.0)) * 100)
        
        # Score composite pondéré
        composite = (
            metrics.get('performance_score', 0) * weights['performance_score'] +
            metrics.get('efficiency_score', 0) * weights['efficiency_score'] +
            metrics.get('robustness_score', 0) * weights['robustness_score'] +
            metrics.get('learning_speed', 0) * weights['learning_speed'] +
            convergence_score * weights['convergence'] +
            metrics.get('sample_efficiency', 0) * weights['sample_efficiency'] +
            return_var_score * weights['return_variance'] +
            entropy_score * weights['policy_entropy']
        )
        
        return composite
    
    @classmethod
    def compute_all_metrics(cls, model_data: Dict, q_table: Optional[Dict] = None, 
                           episode_rewards: Optional[List[float]] = None) -> Dict:
        """
        Calcule toutes les métriques pour un modèle.
        
        Args:
            model_data: Données du modèle (métadonnées)
            q_table: Q-table du modèle (optionnel)
            episode_rewards: Liste des récompenses par épisode (optionnel)
        
        Returns:
            Dictionnaire avec toutes les métriques calculées
        """
        metadata = model_data.get('metadata', {})
        
        # Extraire les données de base
        win_rate = metadata.get('final_win_rate', metadata.get('win_rate', 0))
        draw_rate = metadata.get('final_draw_rate', metadata.get('draw_rate', 0))
        loss_rate = metadata.get('final_loss_rate', metadata.get('loss_rate', 0))
        
        states_learned = model_data.get('states', metadata.get('performance', {}).get('states_learned', 0))
        total_episodes = metadata.get('total_episodes', 0)
        
        performance_data = metadata.get('performance', {})
        avg_reward = performance_data.get('avg_reward', metadata.get('avg_reward', 0))
        avg_moves = performance_data.get('avg_moves', metadata.get('avg_moves', 0))
        
        hyperparams = metadata.get('hyperparameters', {})
        epsilon = model_data.get('epsilon', hyperparams.get('epsilon_final', 1.0))
        epsilon_min = hyperparams.get('epsilon_min', 0.01)
        gamma = hyperparams.get('gamma', 0.95)
        
        # Calculer toutes les métriques
        metrics = {
            # Métriques de base
            'win_rate': win_rate,
            'draw_rate': draw_rate,
            'loss_rate': loss_rate,
            'states_learned': states_learned,
            'total_episodes': total_episodes,
            'avg_reward': avg_reward,
            'avg_moves': avg_moves,
            'epsilon': epsilon,
            'epsilon_min': epsilon_min,
            
            # Métriques calculées (classiques)
            'performance_score': cls.calculate_performance_score(win_rate, draw_rate, loss_rate),
            'efficiency_score': cls.calculate_efficiency_score(win_rate, states_learned),
            'robustness_score': cls.calculate_robustness_score(avg_reward, avg_moves),
            'learning_speed': cls.calculate_learning_speed(win_rate, total_episodes),
            
            # Nouvelles métriques RL
            'sample_efficiency': cls.calculate_sample_efficiency(win_rate, total_episodes),
            
            # Hyperparamètres
            'hyperparameters': hyperparams
        }
        
        # Ajouter les métriques de Q-table si disponible
        if q_table:
            metrics['q_table_quality'] = cls.calculate_q_table_quality(q_table)
            metrics['bellman_error'] = cls.calculate_bellman_error(q_table, gamma)
            metrics['policy_entropy'] = cls.calculate_policy_entropy(q_table)
        
        # Ajouter les métriques basées sur episode_rewards si disponibles
        if episode_rewards:
            metrics['td_error_stats'] = cls.calculate_td_error_stats(episode_rewards)
            metrics['return_variance'] = cls.calculate_return_variance(episode_rewards)
        else:
            # Valeurs par défaut
            metrics['return_variance'] = 0.3
            metrics['policy_entropy'] = 0.5
        
        # Score composite final
        metrics['composite_score'] = cls.calculate_composite_score(metrics)
        
        return metrics


class ModelEvaluator:
    """
    Évalue les modèles contre différents adversaires.
    """
    
    def __init__(self, env, trainer_class):
        """
        Initialise l'évaluateur.
        
        Args:
            env: Environnement de jeu
            trainer_class: Classe Trainer pour l'évaluation
        """
        self.env = env
        self.trainer_class = trainer_class
    
    def evaluate_against_random(self, agent, num_games: int = 1000) -> Dict:
        """
        Évalue un agent contre un adversaire aléatoire.
        
        Args:
            agent: Agent à évaluer
            num_games: Nombre de parties à jouer
        
        Returns:
            Dictionnaire avec les résultats
        """
        trainer = self.trainer_class(agent, self.env)
        results = trainer.evaluate(num_games=num_games, verbose=False, epsilon=0.0)
        
        return {
            'win_rate': results['win_rate'],
            'draw_rate': results['draw_rate'],
            'loss_rate': results['loss_rate'],
            'total_games': num_games,
            'performance_score': ModelMetrics.calculate_performance_score(
                results['win_rate'], 
                results['draw_rate'], 
                results['loss_rate']
            )
        }
    
    def evaluate_head_to_head(self, agent1, agent2, num_games: int = 1000) -> Dict:
        """
        Évalue deux agents l'un contre l'autre.
        
        Args:
            agent1: Premier agent
            agent2: Deuxième agent
            num_games: Nombre de parties à jouer
        
        Returns:
            Dictionnaire avec les résultats
        """
        wins_agent1 = 0
        wins_agent2 = 0
        draws = 0
        
        for game in range(num_games):
            # Alterner qui commence
            agent1_starts = game % 2 == 0
            
            state = self.env.reset()
            done = False
            
            current_agent = agent1 if agent1_starts else agent2
            other_agent = agent2 if agent1_starts else agent1
            
            while not done:
                # Tour de l'agent actuel
                legal_actions = self.env.legal_actions(state)
                action = current_agent.choose_action(state, legal_actions, epsilon=0.0)
                state, reward, done = self.env.apply_action(action)
                
                if not done:
                    # Échanger les agents
                    current_agent, other_agent = other_agent, current_agent
            
            # Enregistrer le résultat
            winner = self.env.get_winner()
            agent1_symbol = self.env.PLAYER_X if agent1_starts else self.env.PLAYER_O
            
            if winner == agent1_symbol:
                wins_agent1 += 1
            elif winner is None:
                draws += 1
            else:
                wins_agent2 += 1
        
        return {
            'agent1_wins': wins_agent1,
            'agent2_wins': wins_agent2,
            'draws': draws,
            'agent1_win_rate': (wins_agent1 / num_games) * 100,
            'agent2_win_rate': (wins_agent2 / num_games) * 100,
            'draw_rate': (draws / num_games) * 100
        }
