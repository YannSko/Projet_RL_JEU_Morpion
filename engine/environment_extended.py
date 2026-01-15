"""
Environnements Morpion étendus - 4x4, 5x5, variantes
"""

import numpy as np
from typing import List, Tuple, Optional


class TicTacToeExtended:
    """
    Environnement de Morpion étendu avec tailles variables.
    Supporte 3x3, 4x4, 5x5
    """
    
    PLAYER_X = 1
    PLAYER_O = -1
    EMPTY = 0
    
    def __init__(self, board_size: int = 3, win_length: int = None):
        """
        Initialise l'environnement.
        
        Args:
            board_size: Taille du plateau (3, 4, ou 5)
            win_length: Nombre d'alignements pour gagner (défaut: 3 pour tous)
        """
        if board_size not in [3, 4, 5]:
            raise ValueError("board_size doit être 3, 4 ou 5")
        
        self.board_size = board_size
        self.win_length = win_length or 3  # Toujours 3 alignés
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.current_player = self.PLAYER_X
    
    def reset(self) -> tuple:
        """
        Réinitialise l'environnement.
        
        Returns:
            État initial
        """
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = self.PLAYER_X
        return self._state()
    
    def _state(self) -> tuple:
        """Retourne l'état actuel sous forme de tuple (hashable)"""
        return tuple(self.board.flatten())
    
    def legal_actions(self, state: tuple = None) -> List[int]:
        """
        Retourne les actions légales.
        
        Args:
            state: État (optionnel, utilise l'état actuel si None)
        
        Returns:
            Liste des positions vides (0 à board_size²-1)
        """
        board = self.board if state is None else np.array(state).reshape(self.board_size, self.board_size)
        return [i for i in range(self.board_size ** 2) if board.flatten()[i] == self.EMPTY]
    
    def apply_action(self, action: int, update_state: bool = True) -> Tuple[tuple, float, bool]:
        """
        Applique une action.
        
        Args:
            action: Position à jouer (0 à board_size²-1)
            update_state: Mettre à jour l'état interne
        
        Returns:
            (nouvel_état, récompense, done)
        """
        row, col = action // self.board_size, action % self.board_size
        
        if self.board[row, col] != self.EMPTY:
            # Action illégale
            return self._state(), -10, True
        
        # Jouer le coup
        self.board[row, col] = self.current_player
        
        # Vérifier victoire
        winner = self.get_winner()
        done = False
        reward = 0
        
        if winner == self.current_player:
            reward = 1
            done = True
        elif winner == -self.current_player:
            reward = -1
            done = True
        elif len(self.legal_actions()) == 0:
            # Match nul
            reward = 0
            done = True
        
        # Changer de joueur
        if update_state and not done:
            self.current_player *= -1
        
        return self._state(), reward, done
    
    def get_winner(self) -> Optional[int]:
        """
        Vérifie s'il y a un gagnant.
        
        Returns:
            PLAYER_X, PLAYER_O, ou None
        """
        # Lignes
        for row in range(self.board_size):
            for col in range(self.board_size - self.win_length + 1):
                window = self.board[row, col:col+self.win_length]
                if np.all(window == self.PLAYER_X):
                    return self.PLAYER_X
                if np.all(window == self.PLAYER_O):
                    return self.PLAYER_O
        
        # Colonnes
        for col in range(self.board_size):
            for row in range(self.board_size - self.win_length + 1):
                window = self.board[row:row+self.win_length, col]
                if np.all(window == self.PLAYER_X):
                    return self.PLAYER_X
                if np.all(window == self.PLAYER_O):
                    return self.PLAYER_O
        
        # Diagonales (bas-droite)
        for row in range(self.board_size - self.win_length + 1):
            for col in range(self.board_size - self.win_length + 1):
                window = [self.board[row+i, col+i] for i in range(self.win_length)]
                if all(x == self.PLAYER_X for x in window):
                    return self.PLAYER_X
                if all(x == self.PLAYER_O for x in window):
                    return self.PLAYER_O
        
        # Diagonales (bas-gauche)
        for row in range(self.board_size - self.win_length + 1):
            for col in range(self.win_length - 1, self.board_size):
                window = [self.board[row+i, col-i] for i in range(self.win_length)]
                if all(x == self.PLAYER_X for x in window):
                    return self.PLAYER_X
                if all(x == self.PLAYER_O for x in window):
                    return self.PLAYER_O
        
        return None
    
    def is_terminal(self) -> bool:
        """Vérifie si le jeu est terminé"""
        return self.get_winner() is not None or len(self.legal_actions()) == 0
    
    def get_board_copy(self) -> np.ndarray:
        """Retourne une copie du plateau"""
        return self.board.copy()


class MorpionVariants:
    """Variantes de Morpion avec contraintes"""
    
    @staticmethod
    def no_center_rule(env: TicTacToeExtended) -> bool:
        """
        Contrainte: Le centre est interdit.
        
        Returns:
            True si le centre est libre (contrainte respectée)
        """
        center = env.board_size // 2
        return env.board[center, center] == env.EMPTY
    
    @staticmethod
    def corners_first_rule(env: TicTacToeExtended, moves_count: int) -> List[int]:
        """
        Contrainte: Premiers coups doivent être dans les coins.
        
        Args:
            env: Environnement
            moves_count: Nombre de coups joués
        
        Returns:
            Actions légales selon la contrainte
        """
        if moves_count < 2:  # Premiers 2 coups
            corners = [
                0,  # Haut-gauche
                env.board_size - 1,  # Haut-droite
                env.board_size * (env.board_size - 1),  # Bas-gauche
                env.board_size ** 2 - 1  # Bas-droite
            ]
            legal = env.legal_actions()
            return [a for a in legal if a in corners]
        else:
            return env.legal_actions()


class UltimateTicTacToe:
    """
    Ultimate Tic-Tac-Toe : Méta-jeu complexe
    9 plateaux 3x3 dans un grand plateau 3x3
    """
    
    def __init__(self):
        """Initialise l'Ultimate Tic-Tac-Toe"""
        # 9 sous-plateaux 3x3
        self.sub_boards = [np.zeros((3, 3), dtype=int) for _ in range(9)]
        # Plateau principal (états des sous-plateaux)
        self.main_board = np.zeros((3, 3), dtype=int)
        self.current_player = 1
        self.active_board = None  # None = peut jouer n'importe où
    
    def reset(self) -> dict:
        """Réinitialise le jeu"""
        self.sub_boards = [np.zeros((3, 3), dtype=int) for _ in range(9)]
        self.main_board = np.zeros((3, 3), dtype=int)
        self.current_player = 1
        self.active_board = None
        return self._state()
    
    def _state(self) -> dict:
        """Retourne l'état actuel"""
        return {
            'sub_boards': [board.copy() for board in self.sub_boards],
            'main_board': self.main_board.copy(),
            'active_board': self.active_board,
            'current_player': self.current_player
        }
    
    def legal_actions(self) -> List[Tuple[int, int]]:
        """
        Retourne les actions légales.
        
        Returns:
            Liste de (board_index, position)
        """
        actions = []
        
        if self.active_board is not None:
            # Doit jouer sur le plateau actif
            if self.main_board.flatten()[self.active_board] == 0:
                board = self.sub_boards[self.active_board]
                for pos in range(9):
                    if board.flatten()[pos] == 0:
                        actions.append((self.active_board, pos))
            else:
                # Le plateau actif est terminé, peut jouer n'importe où
                self.active_board = None
                return self.legal_actions()
        else:
            # Peut jouer sur n'importe quel plateau non terminé
            for board_idx in range(9):
                if self.main_board.flatten()[board_idx] == 0:
                    board = self.sub_boards[board_idx]
                    for pos in range(9):
                        if board.flatten()[pos] == 0:
                            actions.append((board_idx, pos))
        
        return actions
    
    def apply_action(self, action: Tuple[int, int]) -> Tuple[dict, float, bool]:
        """
        Applique une action.
        
        Args:
            action: (board_index, position)
        
        Returns:
            (state, reward, done)
        """
        board_idx, pos = action
        row, col = pos // 3, pos % 3
        
        # Jouer le coup
        self.sub_boards[board_idx][row, col] = self.current_player
        
        # Vérifier victoire sur le sous-plateau
        winner = self._check_sub_board_winner(board_idx)
        if winner:
            self.main_board.flat[board_idx] = winner
        
        # Vérifier victoire globale
        global_winner = self._check_winner(self.main_board)
        done = False
        reward = 0
        
        if global_winner == self.current_player:
            reward = 1
            done = True
        elif global_winner:
            reward = -1
            done = True
        elif len(self.legal_actions()) == 0:
            reward = 0
            done = True
        
        # Définir le prochain plateau actif
        if not done:
            self.active_board = pos
            self.current_player *= -1
        
        return self._state(), reward, done
    
    def _check_sub_board_winner(self, board_idx: int) -> Optional[int]:
        """Vérifie le gagnant d'un sous-plateau"""
        return self._check_winner(self.sub_boards[board_idx])
    
    def _check_winner(self, board: np.ndarray) -> Optional[int]:
        """Vérifie le gagnant d'un plateau 3x3"""
        # Lignes
        for row in range(3):
            if abs(board[row, :].sum()) == 3:
                return board[row, 0]
        
        # Colonnes
        for col in range(3):
            if abs(board[:, col].sum()) == 3:
                return board[0, col]
        
        # Diagonales
        if abs(np.diag(board).sum()) == 3:
            return board[0, 0]
        if abs(np.diag(np.fliplr(board)).sum()) == 3:
            return board[0, 2]
        
        return None
