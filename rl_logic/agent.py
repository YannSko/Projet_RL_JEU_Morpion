"""
Agents d'apprentissage par renforcement
- QLearningAgent: Agent Q-Learning tabulaire
- RandomAgent: Agent aléatoire (baseline)
"""

import numpy as np
import random
from typing import Tuple, Dict, Optional, List
from collections import defaultdict


class QLearningAgent:
    """
    Agent utilisant l'algorithme Q-Learning tabulaire.
    Politique ε-greedy pour l'exploration/exploitation.
    """
    
    def __init__(self, alpha: float = 0.2, gamma: float = 0.99, 
                 epsilon: float = 1.0, epsilon_min: float = 0.01, 
                 epsilon_decay: float = 0.9995):
        """
        Initialise l'agent Q-Learning.
        
        Args:
            alpha: Taux d'apprentissage (learning rate)
            gamma: Facteur d'actualisation (discount factor)
            epsilon: Taux d'exploration initial
            epsilon_min: Taux d'exploration minimal
            epsilon_decay: Facteur de décroissance de epsilon
        """
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_start = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        
        # Q-table: {état: {action: Q-valeur}}
        self.q_table: Dict[Tuple, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
    
    def get_q_value(self, state: Tuple, action: int) -> float:
        """
        Retourne la Q-valeur pour une paire (état, action).
        
        Args:
            state: État du jeu
            action: Action à évaluer
        
        Returns:
            Q-valeur (0 si jamais visité)
        """
        return self.q_table[state][action]
    
    def get_max_q_value(self, state: Tuple, legal_actions: List[int]) -> float:
        """
        Retourne la Q-valeur maximale pour un état donné.
        
        Args:
            state: État du jeu
            legal_actions: Liste des actions légales
        
        Returns:
            Q-valeur maximale (0 si aucune action)
        """
        if not legal_actions:
            return 0.0
        return max(self.get_q_value(state, action) for action in legal_actions)
    
    def get_best_action(self, state: Tuple, legal_actions: List[int]) -> int:
        """
        Retourne la meilleure action selon la Q-table.
        En cas d'égalité, choisit aléatoirement parmi les meilleures.
        
        Args:
            state: État du jeu
            legal_actions: Liste des actions légales
        
        Returns:
            Meilleure action
        
        Raises:
            ValueError: Si aucune action légale
        """
        if not legal_actions:
            raise ValueError("Aucune action légale disponible")
        
        # Obtenir toutes les Q-valeurs
        q_values = [(action, self.get_q_value(state, action)) 
                    for action in legal_actions]
        
        # Trouver la valeur maximale
        max_q = max(q_values, key=lambda x: x[1])[1]
        
        # Obtenir toutes les actions avec la valeur maximale
        best_actions = [action for action, q in q_values if q == max_q]
        
        # Choisir aléatoirement parmi les meilleures
        return random.choice(best_actions)
    
    def choose_action(self, state: Tuple, legal_actions: List[int], 
                     epsilon: Optional[float] = None) -> int:
        """
        Choisit une action selon la politique ε-greedy.
        
        Args:
            state: État actuel
            legal_actions: Liste des actions légales
            epsilon: Taux d'exploration (utilise self.epsilon si None)
        
        Returns:
            Action choisie
        """
        if not legal_actions:
            raise ValueError("Aucune action légale disponible")
        
        if epsilon is None:
            epsilon = self.epsilon
        
        # Exploration: action aléatoire
        if random.random() < epsilon:
            return random.choice(legal_actions)
        
        # Exploitation: meilleure action
        return self.get_best_action(state, legal_actions)
    
    def update(self, state: Tuple, action: int, reward: float, 
               next_state: Tuple, next_legal_actions: List[int], done: bool):
        """
        Met à jour la Q-table selon la formule de Q-learning:
        Q[s,a] = Q[s,a] + α * (reward + γ * max(Q[s',a']) - Q[s,a])
        
        Args:
            state: État actuel
            action: Action prise
            reward: Récompense reçue
            next_state: État suivant
            next_legal_actions: Actions légales dans l'état suivant
            done: True si l'épisode est terminé
        """
        current_q = self.get_q_value(state, action)
        
        if done:
            # État terminal: pas de valeur future
            target = reward
        else:
            # Calcul du TD target
            max_next_q = self.get_max_q_value(next_state, next_legal_actions)
            target = reward + self.gamma * max_next_q
        
        # Mise à jour Q-learning
        new_q = current_q + self.alpha * (target - current_q)
        self.q_table[state][action] = new_q
    
    def decay_epsilon(self):
        """Diminue le taux d'exploration selon epsilon_decay"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def set_epsilon(self, epsilon: float):
        """
        Définit le taux d'exploration.
        
        Args:
            epsilon: Nouveau taux d'exploration (entre 0 et 1)
        """
        self.epsilon = max(0.0, min(1.0, epsilon))
    
    def reset_epsilon(self):
        """Réinitialise epsilon à sa valeur de départ"""
        self.epsilon = self.epsilon_start
    
    def get_stats(self) -> Dict:
        """
        Retourne des statistiques sur la Q-table.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        total_states = len(self.q_table)
        total_state_actions = sum(len(actions) for actions in self.q_table.values())
        
        all_q_values = [q for actions in self.q_table.values() 
                       for q in actions.values()]
        
        if all_q_values:
            avg_q = np.mean(all_q_values)
            max_q = np.max(all_q_values)
            min_q = np.min(all_q_values)
            std_q = np.std(all_q_values)
        else:
            avg_q = max_q = min_q = std_q = 0.0
        
        return {
            'total_states': total_states,
            'total_state_actions': total_state_actions,
            'avg_q_value': avg_q,
            'max_q_value': max_q,
            'min_q_value': min_q,
            'std_q_value': std_q,
            'epsilon': self.epsilon,
            'alpha': self.alpha,
            'gamma': self.gamma
        }
    
    def get_q_table_copy(self) -> Dict:
        """
        Retourne une copie de la Q-table (pour sauvegarde).
        
        Returns:
            Copie de la Q-table
        """
        return {state: dict(actions) for state, actions in self.q_table.items()}
    
    def load_q_table(self, q_table_dict: Dict):
        """
        Charge une Q-table depuis un dictionnaire.
        
        Args:
            q_table_dict: Dictionnaire représentant la Q-table
        """
        self.q_table = defaultdict(lambda: defaultdict(float))
        for state, actions in q_table_dict.items():
            for action, q_value in actions.items():
                self.q_table[state][action] = q_value


class RandomAgent:
    """
    Agent qui joue aléatoirement.
    Utilisé comme baseline et adversaire d'entraînement.
    """
    
    def choose_action(self, state: Tuple, legal_actions: List[int], 
                     epsilon: Optional[float] = None) -> int:
        """
        Choisit une action aléatoire parmi les actions légales.
        
        Args:
            state: État actuel (non utilisé)
            legal_actions: Liste des actions légales
            epsilon: Non utilisé (pour compatibilité d'interface)
        
        Returns:
            Action aléatoire
        """
        return random.choice(legal_actions)
    
    def update(self, *args, **kwargs):
        """Ne fait rien (l'agent aléatoire n'apprend pas)"""
        pass
    
    def get_stats(self) -> Dict:
        """Retourne des statistiques vides"""
        return {
            'type': 'Random',
            'epsilon': 1.0  # Toujours aléatoire
        }
