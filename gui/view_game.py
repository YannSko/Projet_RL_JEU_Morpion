"""
Vue du jeu - Interface de jeu Morpion
Gère l'affichage du plateau et les interactions.
"""

import pygame
import time
from typing import Optional, Tuple, Dict
from engine.environment import TicTacToeEnvironment
from rl_logic.agent import QLearningAgent
from .assets import Assets


class GameView:
    """Vue du jeu de Morpion"""
    
    # Niveaux d'IA
    IA_LEVELS = {
        "Débutant": 0.5,
        "Intermédiaire": 0.2,
        "Expert": 0.0
    }
    
    def __init__(self, screen: pygame.Surface, assets: Assets):
        """
        Initialise la vue du jeu.
        
        Args:
            screen: Surface Pygame principale
            assets: Gestionnaire d'assets
        """
        self.screen = screen
        self.assets = assets
        
        # État du jeu
        self.env = TicTacToeEnvironment()
        self.agent = None
        self.agent_name = "Modèle par défaut"  # Nom du modèle actuel
        self.game_mode = None  # 'HH', 'HA', 'AA'
        self.ai_level = "Expert"
        self.game_over = False
        self.winner = None
        self.num_moves = 0
        self.game_start_time = 0
        
        # Interface
        self.info_height = 60
        self.debug_mode = False  # Mode debug pour afficher Q-values
        
        # Boutons de fin de partie
        self._create_end_game_buttons()
    
    def _create_end_game_buttons(self):
        """Crée les boutons pour la fin de partie"""
        button_width = 200
        button_height = 50
        spacing = 20
        center_x = self.assets.window_size // 2
        center_y = self.assets.window_size // 2 + 80
        
        self.replay_button = pygame.Rect(
            center_x - button_width - spacing // 2,
            center_y,
            button_width,
            button_height
        )
        
        self.menu_button = pygame.Rect(
            center_x + spacing // 2,
            center_y,
            button_width,
            button_height
        )
    
    def set_agent(self, agent: QLearningAgent, name: str = "Modèle par défaut"):
        """
        Définit l'agent IA à utiliser.
        
        Args:
            agent: Agent QLearningAgent
            name: Nom du modèle
        """
        self.agent = agent
        self.agent_name = name
    
    def start_game(self, mode: str, ai_level: str = "Expert"):
        """
        Démarre une nouvelle partie.
        
        Args:
            mode: Mode de jeu ('HH', 'HA', 'AA')
            ai_level: Niveau de l'IA
        """
        self.game_mode = mode
        self.ai_level = ai_level
        self.reset_game()
    
    def toggle_debug(self):
        """Active/désactive le mode debug"""
        self.debug_mode = not self.debug_mode
    
    def reset_game(self):
        """Réinitialise le jeu"""
        self.env.reset()
        self.game_over = False
        self.winner = None
        self.num_moves = 0
        self.game_start_time = time.time()
        
        # Si IA vs IA, l'IA joue en premier
        if self.game_mode == 'AA':
            self._ai_move()
    
    def handle_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """
        Gère un clic sur le plateau.
        
        Args:
            pos: Position du clic (x, y)
        
        Returns:
            Action à effectuer: 'replay', 'menu', ou None
        """
        # Si jeu terminé, vérifier les clics sur les boutons
        if self.game_over:
            if self.replay_button.collidepoint(pos):
                return 'replay'
            elif self.menu_button.collidepoint(pos):
                return 'menu'
            return None
        
        # Ajuster la position pour la zone de jeu
        adjusted_pos = (pos[0], pos[1] - self.info_height)
        row, col = self.assets.get_cell_from_pos(adjusted_pos)
        
        if row == -1 or col == -1:
            return False
        
        # Vérifier si c'est le tour d'un humain
        if self.game_mode == 'HH':
            self._human_move(row, col)
        elif self.game_mode == 'HA':
            # Humain joue X, IA joue O
            if self.env.current_player == self.env.PLAYER_X:
                self._human_move(row, col)
        elif self.game_mode == 'AA':
            # Pas de clic possible en mode IA vs IA
            pass
        
        return None
    
    def update(self) -> bool:
        """
        Met à jour la logique du jeu.
        
        Returns:
            True si un changement nécessite un redraw
        """
        if self.game_over:
            return False
        
        # Si c'est le tour de l'IA
        if self.game_mode == 'HA' and self.env.current_player == self.env.PLAYER_O:
            pygame.time.wait(300)  # Petit délai pour rendre visible
            self._ai_move()
            return True
        elif self.game_mode == 'AA' and not self.game_over:
            pygame.time.wait(500)
            self._ai_move()
            return True
        
        return False
    
    def draw(self):
        """Dessine la vue du jeu"""
        # Fond
        self.screen.fill(self.assets.colors.BG_COLOR)
        
        # Zone d'information en haut
        self._draw_info_bar()
        
        # Décaler la surface de jeu
        game_surface = self.assets.create_surface(
            self.assets.window_size,
            self.assets.window_size,
            self.assets.colors.BG_COLOR
        )
        
        # Grille
        self.assets.draw_grid(game_surface)
        
        # Dessiner les symboles
        board = self.env.get_board_copy()
        for row in range(self.env.GRID_SIZE):
            for col in range(self.env.GRID_SIZE):
                if board[row, col] == self.env.PLAYER_X:
                    self.assets.draw_cross(game_surface, row, col)
                elif board[row, col] == self.env.PLAYER_O:
                    self.assets.draw_circle(game_surface, row, col)
        
        # Blitter la surface de jeu
        self.screen.blit(game_surface, (0, self.info_height))
        
        # Afficher Q-values en mode debug
        if self.debug_mode and not self.game_over and self.agent is not None:
            self._draw_q_values()
        
        # Overlay de fin de partie
        if self.game_over:
            self._draw_game_over_overlay()
    
    def _draw_info_bar(self):
        """Dessine la barre d'information en haut"""
        # Fond de la barre
        info_rect = pygame.Rect(0, 0, self.assets.window_size, self.info_height)
        info_surface = pygame.Surface((info_rect.width, info_rect.height))
        info_surface.set_alpha(230)
        info_surface.fill((40, 40, 40))
        self.screen.blit(info_surface, info_rect.topleft)
        
        # Mode de jeu et modèle
        mode_text_map = {
            'HH': 'Humain vs Humain',
            'HA': f'Humain vs IA ({self.ai_level}) - {self.agent_name}',
            'AA': f'IA vs IA ({self.ai_level}) - {self.agent_name}'
        }
        
        if self.game_mode in mode_text_map:
            mode_text = mode_text_map[self.game_mode]
            self.assets.draw_text(
                self.screen,
                mode_text,
                (10, 10),
                font_size='small'
            )
        
        # État du jeu (droite)
        if self.game_over:
            # Déterminer le gagnant avec nom
            if self.winner == self.env.PLAYER_X:
                if self.game_mode == 'HH':
                    result = "🏆 JOUEUR 1 (X) GAGNE !"
                elif self.game_mode == 'HA':
                    result = "🏆 HUMAIN (X) GAGNE !"
                else:  # AA
                    result = "🏆 IA 1 (X) GAGNE !"
                color = self.assets.colors.SUCCESS_COLOR
            elif self.winner == self.env.PLAYER_O:
                if self.game_mode == 'HH':
                    result = "🏆 JOUEUR 2 (O) GAGNE !"
                elif self.game_mode == 'HA':
                    result = f"🏆 IA {self.ai_level} (O) GAGNE !"
                else:  # AA
                    result = f"🏆 IA 2 {self.ai_level} (O) GAGNE !"
                color = self.assets.colors.ERROR_COLOR
            else:
                result = "🤝 MATCH NUL"
                color = self.assets.colors.WARNING_COLOR
            
            self.assets.draw_text(
                self.screen,
                result,
                (self.assets.window_size - 10, 10),
                font_size='small',
                color=color,
                centered=False
            )
            
            # Instruction
            self.assets.draw_text(
                self.screen,
                "ESPACE: Rejouer | ECHAP: Menu",
                (self.assets.window_size // 2, 35),
                font_size='tiny',
                centered=True
            )
        else:
            # Tour actuel
            player_symbol = "X" if self.env.current_player == self.env.PLAYER_X else "O"
            turn_text = f"Tour: {player_symbol}"
            self.assets.draw_text(
                self.screen,
                turn_text,
                (self.assets.window_size - 10, 20),
                font_size='small',
                centered=False
            )
    
    def _human_move(self, row: int, col: int) -> bool:
        """
        Traite un coup humain.
        
        Args:
            row: Ligne
            col: Colonne
        
        Returns:
            True si le coup a été joué
        """
        action = self.env.get_action_from_position(row, col)
        legal_actions = self.env.legal_actions()
        
        if action in legal_actions:
            self._apply_action(action)
            return True
        
        return False
    
    def _ai_move(self):
        """L'IA joue un coup"""
        if self.game_over or self.agent is None:
            return
        
        state = self.env.get_state()
        legal_actions = self.env.legal_actions()
        
        if not legal_actions:
            return
        
        # Choisir l'action selon le niveau
        epsilon = self.IA_LEVELS[self.ai_level]
        action = self.agent.choose_action(state, legal_actions, epsilon)
        
        self._apply_action(action)
    
    def _apply_action(self, action: int):
        """
        Applique une action et met à jour l'état du jeu.
        
        Args:
            action: Action à appliquer
        """
        state, reward, done = self.env.apply_action(action)
        self.num_moves += 1
        
        if done:
            self._end_game()
    
    def _end_game(self):
        """Termine la partie"""
        self.game_over = True
        self.winner = self.env.get_winner()
    
    def is_game_over(self) -> bool:
        """Retourne True si la partie est terminée"""
        return self.game_over
    
    def _draw_q_values(self):
        """Affiche les Q-values sur les cases vides"""
        state = self.env.get_state()
        legal_actions = self.env.legal_actions()
        
        if not legal_actions:
            return
        
        # Obtenir toutes les Q-values pour les actions légales
        q_values = [(action, self.agent.get_q_value(state, action)) 
                   for action in legal_actions]
        
        # Trouver min et max pour normaliser les couleurs
        if q_values:
            q_vals = [q for _, q in q_values]
            min_q = min(q_vals)
            max_q = max(q_vals)
            q_range = max_q - min_q if max_q != min_q else 1.0
            
            for action, q_value in q_values:
                row, col = action // 3, action % 3
                
                # Calculer position sur l'écran
                cell_x = col * self.assets.cell_size + self.assets.cell_size // 2
                cell_y = row * self.assets.cell_size + self.assets.cell_size // 2 + self.info_height
                
                # Normaliser Q-value pour couleur (0 à 1)
                if q_range > 0:
                    normalized = (q_value - min_q) / q_range
                else:
                    normalized = 0.5
                
                # Couleur : rouge (mauvais) -> jaune -> vert (bon)
                if normalized < 0.5:
                    # Rouge à jaune
                    r = 255
                    g = int(255 * (normalized * 2))
                    b = 0
                else:
                    # Jaune à vert
                    r = int(255 * (1 - (normalized - 0.5) * 2))
                    g = 255
                    b = 0
                
                color = (r, g, b)
                
                # Fond semi-transparent
                overlay = pygame.Surface((self.assets.cell_size - 20, 50))
                overlay.set_alpha(180)
                overlay.fill((40, 40, 40))
                overlay_rect = overlay.get_rect(center=(cell_x, cell_y))
                self.screen.blit(overlay, overlay_rect)
                
                # Texte Q-value
                q_text = f"Q: {q_value:.3f}"
                self.assets.draw_text(
                    self.screen,
                    q_text,
                    (cell_x, cell_y),
                    font_size='tiny',
                    color=color,
                    centered=True
                )
        
        # Instructions en haut
        self.assets.draw_text(
            self.screen,
            "MODE DEBUG - D: Désactiver",
            (self.assets.window_size // 2, self.info_height + 10),
            font_size='tiny',
            color=self.assets.colors.WARNING_COLOR,
            centered=True
        )
    
    def _draw_game_over_overlay(self):
        """Dessine l'overlay de fin de partie au centre"""
        # Fond semi-transparent
        overlay = pygame.Surface((self.assets.window_size, self.assets.window_size))
        overlay.set_alpha(200)
        overlay.fill((30, 30, 30))
        self.screen.blit(overlay, (0, 0))
        
        # Panneau central
        panel_width = 500
        panel_height = 300
        panel_x = (self.assets.window_size - panel_width) // 2
        panel_y = (self.assets.window_size - panel_height) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # Fond du panneau
        pygame.draw.rect(self.screen, (50, 50, 50), panel_rect, border_radius=20)
        pygame.draw.rect(self.screen, self.assets.colors.TEXT_COLOR, panel_rect, 3, border_radius=20)
        
        # Déterminer le message et la couleur
        if self.winner == self.env.PLAYER_X:
            if self.game_mode == 'HH':
                message = "🏆 JOUEUR 1 GAGNE !"
            elif self.game_mode == 'HA':
                message = "🏆 HUMAIN GAGNE !"
            else:
                message = "🏆 IA 1 GAGNE !"
            color = self.assets.colors.SUCCESS_COLOR
        elif self.winner == self.env.PLAYER_O:
            if self.game_mode == 'HH':
                message = "🏆 JOUEUR 2 GAGNE !"
            elif self.game_mode == 'HA':
                message = f"🏆 IA {self.ai_level} GAGNE !"
            else:
                message = f"🏆 IA 2 GAGNE !"
            color = self.assets.colors.ERROR_COLOR
        else:
            message = "🤝 MATCH NUL"
            color = self.assets.colors.WARNING_COLOR
        
        # Titre
        self.assets.draw_text(
            self.screen,
            message,
            (self.assets.window_size // 2, panel_y + 60),
            font_size='large',
            color=color,
            centered=True
        )
        
        # Statistiques
        stats_text = f"{self.num_moves} coups joués"
        self.assets.draw_text(
            self.screen,
            stats_text,
            (self.assets.window_size // 2, panel_y + 120),
            font_size='small',
            centered=True
        )
        
        # Boutons
        mouse_pos = pygame.mouse.get_pos()
        
        # Bouton Rejouer
        replay_hovered = self.replay_button.collidepoint(mouse_pos)
        self.assets.draw_button(
            self.screen,
            self.replay_button,
            "🔄 Rejouer",
            hovered=replay_hovered
        )
        
        # Bouton Menu
        menu_hovered = self.menu_button.collidepoint(mouse_pos)
        self.assets.draw_button(
            self.screen,
            self.menu_button,
            "🏠 Menu",
            hovered=menu_hovered
        )
    
    def get_game_result(self) -> Dict:
        """
        Retourne les résultats de la partie.
        
        Returns:
            Dictionnaire avec les résultats
        """
        if self.game_mode == 'HH':
            player_x, player_o = "Humain 1", "Humain 2"
        elif self.game_mode == 'HA':
            player_x, player_o = "Humain", f"IA ({self.ai_level})"
        else:
            player_x, player_o = f"IA ({self.ai_level})", f"IA ({self.ai_level})"
        
        duration = time.time() - self.game_start_time
        
        return {
            'player_x': player_x,
            'player_o': player_o,
            'winner': self.winner,
            'num_moves': self.num_moves,
            'duration': duration
        }
    
    def get_current_state(self) -> Tuple[tuple, any]:
        """
        Retourne l'état actuel du jeu pour le Coach.
        
        Returns:
            (state_tuple, board_array)
        """
        # get_state() retourne (board_flat, current_player)
        state_tuple = self.env.get_state()  # État complet
        board = self.env.get_board_copy()
        return state_tuple, board