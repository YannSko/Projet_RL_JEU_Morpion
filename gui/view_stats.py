"""
Vue des statistiques
Affiche les courbes d'apprentissage et les statistiques de l'agent.
"""

import pygame
from typing import List, Tuple
from .assets import Assets
from rl_logic.logger import RLLogger
from rl_logic.agent import QLearningAgent


class StatsView:
    """Vue des statistiques et monitoring"""
    
    def __init__(self, screen: pygame.Surface, assets: Assets, logger: RLLogger):
        """
        Initialise la vue des statistiques.
        
        Args:
            screen: Surface Pygame principale
            assets: Gestionnaire d'assets
            logger: Logger RL
        """
        self.screen = screen
        self.assets = assets
        self.logger = logger
        self.agent = None
        
        # Dimensions
        self.margin = 20
        self.graph_height = 150
    
    def set_agent(self, agent: QLearningAgent):
        """
        Définit l'agent à monitorer.
        
        Args:
            agent: Agent QLearningAgent
        """
        self.agent = agent
    
    def draw(self):
        """Dessine la vue des statistiques"""
        # Fond
        self.screen.fill((240, 240, 240))
        
        # Titre
        self.assets.draw_text(
            self.screen,
            "STATISTIQUES ET MONITORING",
            (self.assets.window_size // 2, self.margin),
            font_size='large',
            color=self.assets.colors.TEXT_DARK,
            centered=True
        )
        
        y_offset = 80
        
        # Section 1: Stats de l'agent
        self._draw_agent_stats(y_offset)
        y_offset += 150
        
        # Section 2: Stats des parties
        self._draw_game_stats(y_offset)
        y_offset += 150
        
        # Section 3: Courbe d'apprentissage (si disponible)
        if len(self.logger.training_stats) > 10:
            self._draw_learning_curve(y_offset)
        
        # Instructions
        self.assets.draw_text(
            self.screen,
            "ECHAP: Retour au menu",
            (self.assets.window_size // 2, self.assets.window_size - 20),
            font_size='small',
            color=self.assets.colors.TEXT_DARK,
            centered=True
        )
    
    def _draw_agent_stats(self, y_start: int):
        """Dessine les statistiques de l'agent"""
        if self.agent is None:
            return
        
        stats = self.agent.get_stats()
        
        # Titre de section
        self.assets.draw_text(
            self.screen,
            "Agent Q-Learning",
            (self.margin, y_start),
            font_size='medium',
            color=self.assets.colors.TEXT_DARK
        )
        
        y = y_start + 35
        line_height = 25
        
        # Afficher les stats
        stats_lines = [
            f"États appris: {stats['total_states']}",
            f"Paires (état, action): {stats['total_state_actions']}",
            f"Q-valeur moyenne: {stats['avg_q_value']:.4f}",
            f"Epsilon actuel: {stats['epsilon']:.6f}",
            f"Alpha: {stats['alpha']} | Gamma: {stats['gamma']}"
        ]
        
        for line in stats_lines:
            self.assets.draw_text(
                self.screen,
                line,
                (self.margin + 20, y),
                font_size='small',
                color=self.assets.colors.TEXT_DARK
            )
            y += line_height
    
    def _draw_game_stats(self, y_start: int):
        """Dessine les statistiques des parties"""
        game_stats = self.logger.get_game_stats(last_n=100)
        
        # Titre de section
        self.assets.draw_text(
            self.screen,
            "Statistiques des parties (dernières 100)",
            (self.margin, y_start),
            font_size='medium',
            color=self.assets.colors.TEXT_DARK
        )
        
        y = y_start + 35
        line_height = 25
        
        # Afficher les stats
        stats_lines = [
            f"Total: {game_stats['total_games']} parties",
            f"Victoires: {game_stats['wins']} ({game_stats['win_rate']:.1f}%)",
            f"Défaites: {game_stats['losses']} ({game_stats['loss_rate']:.1f}%)",
            f"Nuls: {game_stats['draws']} ({game_stats['draw_rate']:.1f}%)",
            f"Moyenne coups: {game_stats['avg_moves']:.1f}"
        ]
        
        for line in stats_lines:
            self.assets.draw_text(
                self.screen,
                line,
                (self.margin + 20, y),
                font_size='small',
                color=self.assets.colors.TEXT_DARK
            )
            y += line_height
        
        # Barres de progression pour les taux
        bar_width = 250
        bar_height = 20
        x_bars = self.assets.window_size - bar_width - self.margin
        y_bars = y_start + 35
        
        # Barre victoires
        win_rect = pygame.Rect(x_bars, y_bars, bar_width, bar_height)
        self.assets.draw_progress_bar(
            self.screen,
            win_rect,
            game_stats['win_rate'] / 100,
            self.assets.colors.PLOT_WIN
        )
        
        # Barre défaites
        loss_rect = pygame.Rect(x_bars, y_bars + 30, bar_width, bar_height)
        self.assets.draw_progress_bar(
            self.screen,
            loss_rect,
            game_stats['loss_rate'] / 100,
            self.assets.colors.PLOT_LOSS
        )
        
        # Barre nuls
        draw_rect = pygame.Rect(x_bars, y_bars + 60, bar_width, bar_height)
        self.assets.draw_progress_bar(
            self.screen,
            draw_rect,
            game_stats['draw_rate'] / 100,
            self.assets.colors.PLOT_DRAW
        )
    
    def _draw_learning_curve(self, y_start: int):
        """Dessine la courbe d'apprentissage"""
        curves = self.logger.get_training_curves(window=50)
        
        if not curves or not curves['episodes']:
            return
        
        # Titre
        self.assets.draw_text(
            self.screen,
            "Courbe d'apprentissage (taux de victoire)",
            (self.margin, y_start),
            font_size='medium',
            color=self.assets.colors.TEXT_DARK
        )
        
        # Zone du graphique
        graph_rect = pygame.Rect(
            self.margin,
            y_start + 40,
            self.assets.window_size - 2 * self.margin,
            self.graph_height
        )
        
        # Fond du graphique
        pygame.draw.rect(self.screen, self.assets.colors.PLOT_BG, graph_rect)
        pygame.draw.rect(self.screen, self.assets.colors.PLOT_GRID, graph_rect, 2)
        
        # Lignes de grille horizontales (0%, 50%, 100%)
        for i in [0, 50, 100]:
            y_grid = graph_rect.bottom - int(graph_rect.height * i / 100)
            pygame.draw.line(
                self.screen,
                self.assets.colors.PLOT_GRID,
                (graph_rect.left, y_grid),
                (graph_rect.right, y_grid),
                1
            )
            # Label
            label = f"{i}%"
            self.assets.draw_text(
                self.screen,
                label,
                (graph_rect.left - 35, y_grid - 8),
                font_size='tiny',
                color=self.assets.colors.TEXT_DARK
            )
        
        # Tracer la courbe
        if len(curves['win_rates_smooth']) > 1:
            points = []
            max_episode = max(curves['episodes'])
            
            for i, (episode, win_rate) in enumerate(zip(curves['episodes'], curves['win_rates_smooth'])):
                # Position x proportionnelle
                x = graph_rect.left + int((episode / max_episode) * graph_rect.width)
                # Position y (inversée car y augmente vers le bas)
                y = graph_rect.bottom - int((win_rate / 100) * graph_rect.height)
                points.append((x, y))
            
            # Dessiner la ligne
            if len(points) > 1:
                pygame.draw.lines(
                    self.screen,
                    self.assets.colors.PLOT_WIN,
                    False,
                    points,
                    3
                )
