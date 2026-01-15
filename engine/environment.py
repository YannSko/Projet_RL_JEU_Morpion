"""
Environnement du jeu de Morpion (Tic-Tac-Toe)
Gère les règles, les coups légaux, l'application des coups et la détection de fin de partie.
PURE GAME LOGIC - Aucune dépendance IA ou GUI.
"""

import numpy as np
from typing import Tuple, List, Optional


class TicTacToeEnvironment:
    """
    Environnement du jeu de Morpion.
    Implémente l'interface MDP (Markov Decision Process).
    """
    
    # Constantes du jeu
    GRID_SIZE = 3
    PLAYER_X = 1
    PLAYER_O = -1
    EMPTY = 0
    
    def __init__(self):
        """Initialise l'environnement"""
        self.board = None
        self.current_player = None
        self.reset()
    
    def reset(self) -> Tuple:
        """
        Réinitialise le jeu et retourne l'état initial.
        
        Returns:
            État initial du jeu (tuple hashable)
        """
        self.board = np.zeros((self.GRID_SIZE, self.GRID_SIZE), dtype=int)
        self.current_player = self.PLAYER_X
        return self.get_state()
    
    def get_state(self) -> Tuple:
        """
        Retourne l'état actuel sous forme de tuple compact et hashable.
        Format: (plateau aplati, joueur courant)
        
        Returns:
            Tuple représentant l'état actuel
        """
        return (tuple(self.board.flatten()), self.current_player)
    
    def legal_actions(self, state: Optional[Tuple] = None) -> List[int]:
        """
        Retourne la liste des actions légales (indices des cases vides).
        Actions: 0-8 correspondant aux positions du plateau aplati.
        
        Args:
            state: État du jeu (utilise l'état actuel si None)
        
        Returns:
            Liste des indices des cases vides
        """
        if state is None:
            board = self.board
        else:
            board = np.array(state[0]).reshape(self.GRID_SIZE, self.GRID_SIZE)
        
        return [i for i in range(self.GRID_SIZE * self.GRID_SIZE) 
                if board.flat[i] == self.EMPTY]
    
    def apply_action(self, action: int) -> Tuple[Tuple, float, bool]:
        """
        Applique une action (joue un coup) et retourne (nouvel_état, récompense, terminé).
        
        Args:
            action: Indice de la case (0-8)
        
        Returns:
            next_state: Nouvel état après le coup
            reward: Récompense pour le joueur qui vient de jouer
            done: True si la partie est terminée
        
        Raises:
            ValueError: Si l'action est illégale
        """
        if action not in self.legal_actions():
            raise ValueError(f"Action illégale: {action}. Cases disponibles: {self.legal_actions()}")
        
        # Jouer le coup
        row, col = action // self.GRID_SIZE, action % self.GRID_SIZE
        self.board[row, col] = self.current_player
        player_who_played = self.current_player
        
        # Vérifier la fin de partie
        winner = self._check_winner()
        done = winner is not None or len(self.legal_actions()) == 0
        
        # Calculer la récompense (du point de vue du joueur qui vient de jouer)
        if winner == player_who_played:
            reward = 1.0  # Victoire
        elif winner is not None:
            reward = -1.0  # Défaite (ne devrait pas arriver dans le flow normal)
        elif done:
            reward = 0.5  # Match nul (récompense positive pour encourager le nul plutôt que la défaite)
        else:
            reward = 0.0  # Partie en cours
        
        # Changer de joueur
        if not done:
            self.current_player = -self.current_player
        
        return self.get_state(), reward, done
    
    def _check_winner(self) -> Optional[int]:
        """
        Vérifie s'il y a un gagnant.
        
        Returns:
            PLAYER_X (1) ou PLAYER_O (-1) si victoire, None sinon
        """
        # Vérifier les lignes
        for row in range(self.GRID_SIZE):
            if abs(sum(self.board[row, :])) == self.GRID_SIZE:
                return self.board[row, 0]
        
        # Vérifier les colonnes
        for col in range(self.GRID_SIZE):
            if abs(sum(self.board[:, col])) == self.GRID_SIZE:
                return self.board[0, col]
        
        # Vérifier la diagonale principale
        if abs(sum(self.board.diagonal())) == self.GRID_SIZE:
            return self.board[0, 0]
        
        # Vérifier la diagonale secondaire
        if abs(sum(np.fliplr(self.board).diagonal())) == self.GRID_SIZE:
            return self.board[0, self.GRID_SIZE - 1]
        
        return None
    
    def is_terminal(self) -> bool:
        """
        Vérifie si l'état actuel est terminal (fin de partie).
        
        Returns:
            True si la partie est terminée
        """
        return self._check_winner() is not None or len(self.legal_actions()) == 0
    
    def get_winner(self) -> Optional[int]:
        """
        Retourne le gagnant de la partie.
        
        Returns:
            PLAYER_X, PLAYER_O ou None (nul/partie en cours)
        """
        return self._check_winner()
    
    def get_board_copy(self) -> np.ndarray:
        """
        Retourne une copie du plateau actuel.
        
        Returns:
            Copie du plateau numpy
        """
        return self.board.copy()
    
    def set_state(self, state: Tuple):
        """
        Restaure un état donné.
        
        Args:
            state: État à restaurer (tuple)
        """
        board_flat, current_player = state
        self.board = np.array(board_flat).reshape(self.GRID_SIZE, self.GRID_SIZE)
        self.current_player = current_player
    
    def render(self):
        """Affiche le plateau dans la console (pour débogage)"""
        symbols = {self.PLAYER_X: 'X', self.PLAYER_O: 'O', self.EMPTY: '.'}
        print("\n" + "-" * (self.GRID_SIZE * 4 + 1))
        for row in range(self.GRID_SIZE):
            print("| ", end="")
            for col in range(self.GRID_SIZE):
                print(f"{symbols[self.board[row, col]]} | ", end="")
            print("\n" + "-" * (self.GRID_SIZE * 4 + 1))
        print()
    
    def get_action_from_position(self, row: int, col: int) -> int:
        """
        Convertit une position (ligne, colonne) en action.
        
        Args:
            row: Ligne (0-2)
            col: Colonne (0-2)
        
        Returns:
            Action (0-8)
        """
        return row * self.GRID_SIZE + col
    
    def get_position_from_action(self, action: int) -> Tuple[int, int]:
        """
        Convertit une action en position (ligne, colonne).
        
        Args:
            action: Action (0-8)
        
        Returns:
            Tuple (ligne, colonne)
        """
        return action // self.GRID_SIZE, action % self.GRID_SIZE
