"""
Mode Coach IA - Explainability et Hints
Montre les Q-values et explique les décisions
"""

from typing import List, Tuple, Dict, Optional
import numpy as np


class AICoach:
    """
    Coach IA qui explique les décisions de l'agent.
    Fournit des hints et des explications sur les coups.
    """
    
    def __init__(self, agent, env):
        """
        Initialise le coach.
        
        Args:
            agent: Agent Q-Learning
            env: Environnement du jeu
        """
        self.agent = agent
        self.env = env
    
    def get_q_values_for_state(self, state: tuple, legal_actions: List[int]) -> List[Tuple[int, float]]:
        """
        Retourne les Q-values pour toutes les actions légales.
        
        Args:
            state: État actuel
            legal_actions: Actions légales
        
        Returns:
            Liste de (action, q_value) triée par q_value décroissant
        """
        q_values = [(action, self.agent.get_q_value(state, action)) 
                   for action in legal_actions]
        return sorted(q_values, key=lambda x: x[1], reverse=True)
    
    def get_best_action_with_confidence(self, state: tuple, legal_actions: List[int]) -> Tuple[int, float, str]:
        """
        Retourne la meilleure action avec un niveau de confiance.
        
        Args:
            state: État actuel
            legal_actions: Actions légales
        
        Returns:
            (action, q_value, confidence_level)
        """
        if not legal_actions:
            return None, 0.0, "AUCUNE ACTION"
        
        q_values = self.get_q_values_for_state(state, legal_actions)
        best_action, best_q = q_values[0]
        
        # Calculer la confiance
        if len(q_values) == 1:
            confidence = "CERTAIN (seul coup légal)"
        elif len(q_values) > 1:
            second_best_q = q_values[1][1]
            diff = best_q - second_best_q
            
            if diff > 0.5:
                confidence = "TRÈS CONFIANT"
            elif diff > 0.2:
                confidence = "CONFIANT"
            elif diff > 0.05:
                confidence = "ASSEZ SÛR"
            elif diff > 0:
                confidence = "PEU SÛR"
            else:
                confidence = "HÉSITANT (plusieurs coups équivalents)"
        else:
            confidence = "INCONNU"
        
        return best_action, best_q, confidence
    
    def explain_action(self, state: tuple, action: int, board: np.ndarray = None) -> str:
        """
        Explique pourquoi une action est bonne ou mauvaise.
        
        Args:
            state: État actuel
            action: Action à expliquer
            board: Plateau de jeu (optionnel)
        
        Returns:
            Explication textuelle
        """
        q_value = self.agent.get_q_value(state, action)
        
        # Analyse stratégique basique
        explanations = []
        
        if board is not None:
            row, col = action // 3, action % 3
            
            # Vérifier si c'est un coup gagnant
            if self._is_winning_move(board, action):
                explanations.append("🏆 COUP GAGNANT!")
            
            # Vérifier si c'est un coup bloquant
            elif self._is_blocking_move(board, action):
                explanations.append("🛡️  BLOQUE l'adversaire")
            
            # Vérifier position stratégique
            if action == 4:  # Centre
                explanations.append("📍 Contrôle le centre")
            elif action in [0, 2, 6, 8]:  # Coins
                explanations.append("📐 Position de coin (stratégique)")
            
            # Vérifier si crée une menace
            if self._creates_threat(board, action):
                explanations.append("⚔️  Crée une menace")
        
        # Q-value analyse
        if q_value > 0.8:
            explanations.append(f"✨ Excellent coup (Q={q_value:.3f})")
        elif q_value > 0.5:
            explanations.append(f"👍 Bon coup (Q={q_value:.3f})")
        elif q_value > 0:
            explanations.append(f"➡️  Coup acceptable (Q={q_value:.3f})")
        elif q_value == 0:
            explanations.append(f"❓ Coup non appris (Q={q_value:.3f})")
        else:
            explanations.append(f"⚠️  Coup risqué (Q={q_value:.3f})")
        
        return " | ".join(explanations) if explanations else f"Q-value: {q_value:.3f}"
    
    def get_hints(self, state: tuple, legal_actions: List[int], board: np.ndarray = None) -> List[Dict]:
        """
        Génère des hints pour le joueur.
        
        Args:
            state: État actuel
            legal_actions: Actions légales
            board: Plateau de jeu (optionnel)
        
        Returns:
            Liste de hints avec actions et explications
        """
        q_values = self.get_q_values_for_state(state, legal_actions)
        
        hints = []
        for i, (action, q_val) in enumerate(q_values[:3]):  # Top 3
            hint = {
                'rank': i + 1,
                'action': action,
                'position': f"({action // 3}, {action % 3})",
                'q_value': q_val,
                'explanation': self.explain_action(state, action, board),
                'is_best': i == 0
            }
            hints.append(hint)
        
        return hints
    
    def _is_winning_move(self, board: np.ndarray, action: int) -> bool:
        """Vérifie si le coup est gagnant"""
        # Créer un board temporaire
        temp_board = board.copy()
        current_player = 1  # Supposer joueur X
        temp_board[action // 3, action % 3] = current_player
        
        # Vérifier victoire
        return self._check_win(temp_board, current_player)
    
    def _is_blocking_move(self, board: np.ndarray, action: int) -> bool:
        """Vérifie si le coup bloque l'adversaire"""
        # Créer un board temporaire
        temp_board = board.copy()
        opponent = -1  # Adversaire
        temp_board[action // 3, action % 3] = opponent
        
        # Vérifier si l'adversaire gagnerait
        return self._check_win(temp_board, opponent)
    
    def _creates_threat(self, board: np.ndarray, action: int) -> bool:
        """Vérifie si le coup crée une menace (2 alignés)"""
        temp_board = board.copy()
        current_player = 1
        row, col = action // 3, action % 3
        temp_board[row, col] = current_player
        
        # Vérifier lignes, colonnes, diagonales
        # Ligne
        if np.sum(temp_board[row, :] == current_player) == 2 and np.sum(temp_board[row, :] == 0) == 1:
            return True
        # Colonne
        if np.sum(temp_board[:, col] == current_player) == 2 and np.sum(temp_board[:, col] == 0) == 1:
            return True
        # Diagonales
        if row == col:
            if np.sum(np.diag(temp_board) == current_player) == 2 and np.sum(np.diag(temp_board) == 0) == 1:
                return True
        if row + col == 2:
            if np.sum(np.diag(np.fliplr(temp_board)) == current_player) == 2 and np.sum(np.diag(np.fliplr(temp_board)) == 0) == 1:
                return True
        
        return False
    
    def _check_win(self, board: np.ndarray, player: int) -> bool:
        """Vérifie si un joueur a gagné"""
        # Lignes
        for row in range(3):
            if np.all(board[row, :] == player):
                return True
        
        # Colonnes
        for col in range(3):
            if np.all(board[:, col] == player):
                return True
        
        # Diagonales
        if np.all(np.diag(board) == player):
            return True
        if np.all(np.diag(np.fliplr(board)) == player):
            return True
        
        return False
    
    def compare_actions(self, state: tuple, action1: int, action2: int) -> str:
        """
        Compare deux actions.
        
        Args:
            state: État actuel
            action1: Première action
            action2: Deuxième action
        
        Returns:
            Comparaison textuelle
        """
        q1 = self.agent.get_q_value(state, action1)
        q2 = self.agent.get_q_value(state, action2)
        
        diff = abs(q1 - q2)
        
        if q1 > q2:
            if diff > 0.5:
                return f"Action {action1} est BEAUCOUP MEILLEURE ({q1:.3f} vs {q2:.3f})"
            elif diff > 0.2:
                return f"Action {action1} est meilleure ({q1:.3f} vs {q2:.3f})"
            else:
                return f"Action {action1} est légèrement meilleure ({q1:.3f} vs {q2:.3f})"
        elif q2 > q1:
            if diff > 0.5:
                return f"Action {action2} est BEAUCOUP MEILLEURE ({q2:.3f} vs {q1:.3f})"
            elif diff > 0.2:
                return f"Action {action2} est meilleure ({q2:.3f} vs {q1:.3f})"
            else:
                return f"Action {action2} est légèrement meilleure ({q2:.3f} vs {q1:.3f})"
        else:
            return f"Les deux actions sont équivalentes ({q1:.3f})"
