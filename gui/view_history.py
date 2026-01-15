"""
Vue Historique des Parties
Affiche l'historique complet des parties jouées.
"""

import pygame
from typing import List, Dict
from datetime import datetime
from .assets import Assets


class HistoryView:
    """Vue de l'historique des parties"""
    
    def __init__(self, screen: pygame.Surface, assets: Assets, logger):
        """
        Initialise la vue historique.
        
        Args:
            screen: Surface Pygame principale
            assets: Gestionnaire d'assets
            logger: RLLogger pour accéder aux données
        """
        self.screen = screen
        self.assets = assets
        self.logger = logger
        
        # Pagination
        self.page = 0
        self.items_per_page = 10
        self.total_games = 0
        self.games = []
        
        # Boutons
        self._create_buttons()
    
    def _create_buttons(self):
        """Crée les boutons de navigation"""
        button_width = 120
        button_height = 40
        spacing = 20
        y = self.assets.window_size - 60
        
        # Centrer les boutons
        total_width = button_width * 3 + spacing * 2
        start_x = (self.assets.window_size - total_width) // 2
        
        self.buttons = {
            'prev': pygame.Rect(start_x, y, button_width, button_height),
            'refresh': pygame.Rect(start_x + button_width + spacing, y, button_width, button_height),
            'next': pygame.Rect(start_x + (button_width + spacing) * 2, y, button_width, button_height)
        }
    
    def load_games(self):
        """Charge l'historique des parties depuis le logger"""
        self.games = self.logger.games_history
        self.total_games = len(self.games)
        
        # Ajuster la page si nécessaire
        max_page = max(0, (self.total_games - 1) // self.items_per_page)
        if self.page > max_page:
            self.page = max_page
    
    def handle_click(self, pos: tuple) -> bool:
        """
        Gère les clics sur les boutons.
        
        Args:
            pos: Position du clic (x, y)
        
        Returns:
            True si un bouton a été cliqué
        """
        if self.buttons['prev'].collidepoint(pos):
            if self.page > 0:
                self.page -= 1
            return True
        
        elif self.buttons['next'].collidepoint(pos):
            max_page = (self.total_games - 1) // self.items_per_page
            if self.page < max_page:
                self.page += 1
            return True
        
        elif self.buttons['refresh'].collidepoint(pos):
            self.load_games()
            return True
        
        return False
    
    def draw(self):
        """Dessine la vue historique"""
        self.screen.fill(self.assets.colors.BG_COLOR)
        
        # Titre
        self.assets.draw_text(
            self.screen,
            "📜 HISTORIQUE DES PARTIES",
            (self.assets.window_size // 2, 30),
            font_size='medium',
            color=self.assets.colors.TEXT_COLOR,
            centered=True
        )
        
        # Statistiques globales
        stats_y = 80
        if self.total_games > 0:
            stats_text = f"Total: {self.total_games} parties jouées"
            self.assets.draw_text(
                self.screen,
                stats_text,
                (self.assets.window_size // 2, stats_y),
                font_size='small',
                centered=True
            )
        else:
            self.assets.draw_text(
                self.screen,
                "Aucune partie enregistrée",
                (self.assets.window_size // 2, stats_y + 100),
                font_size='small',
                color=self.assets.colors.WARNING_COLOR,
                centered=True
            )
        
        # Liste des parties
        if self.total_games > 0:
            self._draw_games_list()
        
        # Boutons de navigation
        self._draw_buttons()
        
        # Instructions
        self.assets.draw_text(
            self.screen,
            "ECHAP: Retour au menu",
            (self.assets.window_size // 2, self.assets.window_size - 20),
            font_size='tiny',
            centered=True
        )
    
    def _draw_games_list(self):
        """Dessine la liste des parties"""
        start_y = 130
        line_height = 45
        
        # Calculer les indices de début et fin
        start_idx = self.page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, self.total_games)
        
        # Afficher les parties (plus récentes en premier)
        for i in range(start_idx, end_idx):
            game = self.games[-(i + 1)]  # Inverser l'ordre
            y = start_y + (i - start_idx) * line_height
            self._draw_game_entry(game, y, i + 1)
    
    def _draw_game_entry(self, game: Dict, y: int, game_num: int):
        """
        Dessine une entrée de partie.
        
        Args:
            game: Dictionnaire avec les infos de la partie
            y: Position Y
            game_num: Numéro de la partie
        """
        x_left = 20
        x_right = self.assets.window_size - 20
        
        # Fond de ligne (alternance)
        if game_num % 2 == 0:
            bg_rect = pygame.Rect(10, y - 5, self.assets.window_size - 20, 40)
            pygame.draw.rect(self.screen, (50, 50, 50), bg_rect)
        
        # Numéro de partie
        num_text = f"#{self.total_games - game_num + 1}"
        self.assets.draw_text(
            self.screen,
            num_text,
            (x_left, y),
            font_size='tiny',
            centered=False
        )
        
        # Joueurs
        players_text = f"{game['player_x']} vs {game['player_o']}"
        self.assets.draw_text(
            self.screen,
            players_text,
            (x_left + 60, y),
            font_size='tiny',
            centered=False
        )
        
        # Résultat
        winner = game.get('winner')
        if winner == 'X':
            result = "X gagne"
            color = self.assets.colors.SUCCESS_COLOR
        elif winner == 'O':
            result = "O gagne"
            color = self.assets.colors.ERROR_COLOR
        else:
            result = "Nul"
            color = self.assets.colors.WARNING_COLOR
        
        self.assets.draw_text(
            self.screen,
            result,
            (x_right - 150, y),
            font_size='tiny',
            color=color,
            centered=False
        )
        
        # Nombre de coups
        moves_text = f"{game.get('num_moves', '?')} coups"
        self.assets.draw_text(
            self.screen,
            moves_text,
            (x_right, y),
            font_size='tiny',
            centered=False
        )
        
        # Timestamp (ligne suivante)
        if 'timestamp' in game:
            try:
                timestamp = datetime.fromisoformat(game['timestamp'])
                time_text = timestamp.strftime("%d/%m/%Y %H:%M")
            except:
                time_text = game['timestamp']
            
            self.assets.draw_text(
                self.screen,
                time_text,
                (x_left + 60, y + 15),
                font_size='tiny',
                color=(150, 150, 150),
                centered=False
            )
    
    def _draw_buttons(self):
        """Dessine les boutons de navigation"""
        # Bouton Précédent
        self.assets.draw_button(
            self.screen,
            self.buttons['prev'],
            "◀ Précédent",
            enabled=(self.page > 0)
        )
        
        # Bouton Actualiser
        self.assets.draw_button(
            self.screen,
            self.buttons['refresh'],
            "🔄 Actualiser"
        )
        
        # Bouton Suivant
        max_page = max(0, (self.total_games - 1) // self.items_per_page)
        self.assets.draw_button(
            self.screen,
            self.buttons['next'],
            "Suivant ▶",
            enabled=(self.page < max_page)
        )
        
        # Numéro de page
        if self.total_games > 0:
            page_text = f"Page {self.page + 1}/{max_page + 1}"
            self.assets.draw_text(
                self.screen,
                page_text,
                (self.assets.window_size // 2, self.assets.window_size - 90),
                font_size='tiny',
                centered=True
            )
