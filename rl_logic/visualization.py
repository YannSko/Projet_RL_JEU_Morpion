"""
Visualisation - Q-table, graphiques, heatmaps
Pour analyse et démos
"""

import pygame
import numpy as np
from typing import Dict, List, Tuple, Optional
import matplotlib
matplotlib.use('Agg')  # Backend pour pygame
import matplotlib.pyplot as plt
from io import BytesIO


class QTableVisualizer:
    """Visualise la Q-table sous forme de heatmap"""
    
    def __init__(self, screen: pygame.Surface, assets):
        """
        Initialise le visualiseur.
        
        Args:
            screen: Surface Pygame
            assets: Assets du jeu
        """
        self.screen = screen
        self.assets = assets
    
    def draw_q_values_for_state(self, board: np.ndarray, q_values: List[Tuple[int, float]],
                                x_start: int = 50, y_start: int = 50, cell_size: int = 80):
        """
        Dessine les Q-values sur le plateau.
        
        Args:
            board: Plateau de jeu (3x3)
            q_values: Liste de (action, q_value)
            x_start: Position X de départ
            y_start: Position Y de départ
            cell_size: Taille des cellules
        """
        # Créer un dict pour accès rapide
        q_dict = {action: q_val for action, q_val in q_values}
        
        # Dessiner le plateau
        for row in range(3):
            for col in range(3):
                action = row * 3 + col
                x = x_start + col * cell_size
                y = y_start + row * cell_size
                
                # Fond de la cellule
                if board[row, col] != 0:
                    # Case occupée - gris foncé
                    color = (60, 60, 60)
                elif action in q_dict:
                    # Couleur selon Q-value
                    q_val = q_dict[action]
                    color = self._q_value_to_color(q_val)
                else:
                    color = (40, 40, 40)
                
                rect = pygame.Rect(x, y, cell_size, cell_size)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, self.assets.colors.TEXT_COLOR, rect, 2)
                
                # Afficher la Q-value si disponible
                if action in q_dict and board[row, col] == 0:
                    q_val = q_dict[action]
                    text = f"{q_val:.3f}"
                    self.assets.draw_text(
                        self.screen,
                        text,
                        (x + cell_size // 2, y + cell_size // 2),
                        font_size='tiny',
                        centered=True
                    )
                
                # Afficher X ou O si occupé
                if board[row, col] == 1:
                    self.assets.draw_text(
                        self.screen,
                        "X",
                        (x + cell_size // 2, y + cell_size // 2),
                        font_size='large',
                        color=self.assets.colors.SUCCESS_COLOR,
                        centered=True
                    )
                elif board[row, col] == -1:
                    self.assets.draw_text(
                        self.screen,
                        "O",
                        (x + cell_size // 2, y + cell_size // 2),
                        font_size='large',
                        color=self.assets.colors.ERROR_COLOR,
                        centered=True
                    )
    
    def _q_value_to_color(self, q_value: float) -> Tuple[int, int, int]:
        """Convertit une Q-value en couleur (heatmap)"""
        # Normaliser entre 0 et 1 (supposer Q entre -1 et 1)
        normalized = (q_value + 1) / 2
        normalized = max(0, min(1, normalized))
        
        # Gradient vert -> jaune -> rouge
        if normalized > 0.5:
            # Vert à jaune
            t = (normalized - 0.5) * 2
            r = int(255 * t)
            g = 200
            b = 0
        else:
            # Bleu à vert
            t = normalized * 2
            r = 0
            g = int(200 * t)
            b = int(150 * (1 - t))
        
        return (r, g, b)


class TrainingGraphs:
    """Génère des graphiques d'entraînement"""
    
    @staticmethod
    def create_training_progress_graph(episode_data: List[int], 
                                      win_rate_data: List[float],
                                      epsilon_data: List[float]) -> pygame.Surface:
        """
        Crée un graphique de progression d'entraînement.
        
        Args:
            episode_data: Numéros d'épisodes
            win_rate_data: Win rates correspondants
            epsilon_data: Epsilons correspondants
        
        Returns:
            Surface Pygame avec le graphique
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
        
        # Win rate
        ax1.plot(episode_data, win_rate_data, 'g-', linewidth=2, label='Win Rate')
        ax1.set_xlabel('Épisodes')
        ax1.set_ylabel('Win Rate (%)', color='g')
        ax1.tick_params(axis='y', labelcolor='g')
        ax1.grid(True, alpha=0.3)
        ax1.set_title('Progression de l\'entraînement')
        
        # Epsilon
        ax2.plot(episode_data, epsilon_data, 'b-', linewidth=2, label='Epsilon')
        ax2.set_xlabel('Épisodes')
        ax2.set_ylabel('Epsilon', color='b')
        ax2.tick_params(axis='y', labelcolor='b')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Convertir en surface Pygame
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, facecolor='#2d2d2d', edgecolor='none')
        buf.seek(0)
        
        surface = pygame.image.load(buf)
        plt.close()
        
        return surface
    
    @staticmethod
    def create_metrics_comparison_chart(models_data: List[Dict]) -> pygame.Surface:
        """
        Crée un graphique de comparaison des modèles.
        
        Args:
            models_data: Liste de dictionnaires avec les métriques
        
        Returns:
            Surface Pygame avec le graphique
        """
        if not models_data:
            # Image vide
            fig = plt.figure(figsize=(8, 6))
            plt.text(0.5, 0.5, 'Aucune donnée', ha='center', va='center')
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            surface = pygame.image.load(buf)
            plt.close()
            return surface
        
        # Graphique en barres
        names = [m['name'][:15] for m in models_data[:10]]  # Top 10
        scores = [m.get('composite_score', 0) for m in models_data[:10]]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(names, scores, color='skyblue')
        
        # Colorer selon le score
        for i, (bar, score) in enumerate(zip(bars, scores)):
            if score >= 80:
                bar.set_color('green')
            elif score >= 60:
                bar.set_color('orange')
            else:
                bar.set_color('red')
        
        ax.set_xlabel('Score Composite')
        ax.set_title('Comparaison des Modèles')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, facecolor='#2d2d2d', edgecolor='none')
        buf.seek(0)
        
        surface = pygame.image.load(buf)
        plt.close()
        
        return surface


class RealtimeTrainingVisualization:
    """Visualisation en temps réel pendant l'entraînement"""
    
    def __init__(self, screen: pygame.Surface, assets):
        """
        Initialise la visualisation en temps réel.
        
        Args:
            screen: Surface Pygame
            assets: Assets du jeu
        """
        self.screen = screen
        self.assets = assets
        self.episode_history = []
        self.win_rate_history = []
        self.epsilon_history = []
        self.max_points = 100  # Garder les 100 derniers points
    
    def update(self, episode: int, win_rate: float, epsilon: float):
        """
        Met à jour les données.
        
        Args:
            episode: Numéro d'épisode
            win_rate: Win rate actuel
            epsilon: Epsilon actuel
        """
        self.episode_history.append(episode)
        self.win_rate_history.append(win_rate)
        self.epsilon_history.append(epsilon)
        
        # Limiter la taille
        if len(self.episode_history) > self.max_points:
            self.episode_history.pop(0)
            self.win_rate_history.pop(0)
            self.epsilon_history.pop(0)
    
    def draw(self, x: int = 50, y: int = 50, width: int = 500, height: int = 300):
        """
        Dessine le graphique en temps réel.
        
        Args:
            x, y: Position
            width, height: Dimensions
        """
        if len(self.episode_history) < 2:
            return
        
        # Fond
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (30, 30, 30), rect)
        pygame.draw.rect(self.screen, self.assets.colors.TEXT_COLOR, rect, 2)
        
        # Dessiner win rate
        self._draw_line_graph(
            self.win_rate_history,
            x, y, width, height,
            (0, 255, 0),  # Vert
            0, 100  # Min/max
        )
        
        # Dessiner epsilon (échelle différente)
        self._draw_line_graph(
            self.epsilon_history,
            x, y, width, height,
            (0, 100, 255),  # Bleu
            0, 1  # Min/max
        )
        
        # Légende
        self.assets.draw_text(
            self.screen,
            f"Win Rate: {self.win_rate_history[-1]:.1f}% | Epsilon: {self.epsilon_history[-1]:.4f}",
            (x + width // 2, y - 15),
            font_size='tiny',
            centered=True
        )
    
    def _draw_line_graph(self, data: List[float], x: int, y: int, 
                        width: int, height: int, color: Tuple[int, int, int],
                        min_val: float, max_val: float):
        """Dessine une ligne de graphique"""
        if len(data) < 2:
            return
        
        points = []
        for i, value in enumerate(data):
            # Normaliser
            normalized = (value - min_val) / (max_val - min_val)
            normalized = max(0, min(1, normalized))
            
            px = x + (i / (len(data) - 1)) * width
            py = y + height - (normalized * height)
            points.append((px, py))
        
        if len(points) >= 2:
            pygame.draw.lines(self.screen, color, False, points, 2)
