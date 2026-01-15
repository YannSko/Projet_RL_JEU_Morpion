"""
Gestion des assets graphiques
Couleurs, polices, dessins et constantes d'interface.
"""

import pygame
from typing import Tuple


class Colors:
    """Palette de couleurs pour l'interface"""
    
    # Couleurs principales
    BG_COLOR = (28, 170, 156)  # Turquoise
    LINE_COLOR = (23, 145, 135)  # Turquoise foncé
    
    # Couleurs des symboles
    CIRCLE_COLOR = (239, 231, 200)  # Beige clair (O)
    CROSS_COLOR = (66, 66, 66)  # Gris foncé (X)
    
    # Couleurs de texte et UI
    TEXT_COLOR = (255, 255, 255)  # Blanc
    TEXT_DARK = (50, 50, 50)  # Gris foncé
    
    # Couleurs des boutons
    BUTTON_COLOR = (52, 152, 219)  # Bleu
    BUTTON_HOVER = (41, 128, 185)  # Bleu foncé
    BUTTON_DISABLED = (149, 165, 166)  # Gris
    
    # Couleurs de statut
    SUCCESS_COLOR = (46, 204, 113)  # Vert
    WARNING_COLOR = (241, 196, 15)  # Jaune
    ERROR_COLOR = (231, 76, 60)  # Rouge
    INFO_COLOR = (52, 152, 219)  # Bleu
    
    # Couleurs des graphiques
    PLOT_BG = (245, 245, 245)  # Gris très clair
    PLOT_GRID = (200, 200, 200)  # Gris clair
    PLOT_WIN = (46, 204, 113)  # Vert
    PLOT_LOSS = (231, 76, 60)  # Rouge
    PLOT_DRAW = (241, 196, 15)  # Jaune
    PLOT_EPSILON = (155, 89, 182)  # Violet


class Assets:
    """
    Gestionnaire des assets graphiques.
    Gère les polices, dimensions et fonctions de dessin.
    """
    
    def __init__(self, window_size: int = 600):
        """
        Initialise les assets.
        
        Args:
            window_size: Taille de la fenêtre (carrée)
        """
        pygame.init()
        pygame.font.init()
        
        # Dimensions
        self.window_size = window_size
        self.grid_size = 3
        self.cell_size = window_size // self.grid_size
        
        # Épaisseurs et espacements
        self.line_width = 5
        self.circle_radius = self.cell_size // 3
        self.circle_width = 10
        self.cross_width = 15
        self.cross_space = self.cell_size // 4
        
        # Polices
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        # Couleurs
        self.colors = Colors()
    
    def draw_grid(self, surface: pygame.Surface):
        """
        Dessine la grille du jeu de Morpion.
        
        Args:
            surface: Surface Pygame où dessiner
        """
        # Lignes horizontales
        for i in range(1, self.grid_size):
            y = i * self.cell_size
            pygame.draw.line(
                surface,
                self.colors.LINE_COLOR,
                (0, y),
                (self.window_size, y),
                self.line_width
            )
        
        # Lignes verticales
        for i in range(1, self.grid_size):
            x = i * self.cell_size
            pygame.draw.line(
                surface,
                self.colors.LINE_COLOR,
                (x, 0),
                (x, self.window_size),
                self.line_width
            )
    
    def draw_cross(self, surface: pygame.Surface, row: int, col: int):
        """
        Dessine un X dans une case.
        
        Args:
            surface: Surface Pygame
            row: Ligne (0-2)
            col: Colonne (0-2)
        """
        center_x = col * self.cell_size + self.cell_size // 2
        center_y = row * self.cell_size + self.cell_size // 2
        
        # Première diagonale (\)
        pygame.draw.line(
            surface,
            self.colors.CROSS_COLOR,
            (center_x - self.cross_space, center_y - self.cross_space),
            (center_x + self.cross_space, center_y + self.cross_space),
            self.cross_width
        )
        
        # Deuxième diagonale (/)
        pygame.draw.line(
            surface,
            self.colors.CROSS_COLOR,
            (center_x + self.cross_space, center_y - self.cross_space),
            (center_x - self.cross_space, center_y + self.cross_space),
            self.cross_width
        )
    
    def draw_circle(self, surface: pygame.Surface, row: int, col: int):
        """
        Dessine un O dans une case.
        
        Args:
            surface: Surface Pygame
            row: Ligne (0-2)
            col: Colonne (0-2)
        """
        center_x = col * self.cell_size + self.cell_size // 2
        center_y = row * self.cell_size + self.cell_size // 2
        
        pygame.draw.circle(
            surface,
            self.colors.CIRCLE_COLOR,
            (center_x, center_y),
            self.circle_radius,
            self.cross_width
        )
    
    def draw_button(self, surface: pygame.Surface, rect: pygame.Rect,
                   text: str, hovered: bool = False, disabled: bool = False, enabled: bool = True):
        """
        Dessine un bouton avec texte.
        
        Args:
            surface: Surface Pygame
            rect: Rectangle du bouton
            text: Texte du bouton
            hovered: Si True, utilise la couleur hover
            disabled: Si True, bouton désactivé
            enabled: Si False, bouton désactivé (alias de disabled)
        """
        # Gérer les deux paramètres disabled et enabled
        is_disabled = disabled or not enabled
        
        # Couleur du bouton
        if is_disabled:
            color = self.colors.BUTTON_DISABLED
        elif hovered:
            color = self.colors.BUTTON_HOVER
        else:
            color = self.colors.BUTTON_COLOR
        
        # Fond du bouton
        pygame.draw.rect(surface, color, rect, border_radius=10)
        
        # Bordure
        pygame.draw.rect(surface, self.colors.TEXT_COLOR, rect, 2, border_radius=10)
        
        # Texte
        text_color = self.colors.TEXT_DARK if is_disabled else self.colors.TEXT_COLOR
        text_surface = self.font_small.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)
    
    def draw_text(self, surface: pygame.Surface, text: str,
                 position: Tuple[int, int], font_size: str = 'medium',
                 color: Tuple[int, int, int] = None, centered: bool = False):
        """
        Dessine du texte à une position.
        
        Args:
            surface: Surface Pygame
            text: Texte à afficher
            position: Position (x, y)
            font_size: Taille de police ('tiny', 'small', 'medium', 'large')
            color: Couleur du texte (blanc par défaut)
            centered: Si True, centre le texte sur la position
        """
        # Sélectionner la police
        font_map = {
            'tiny': self.font_tiny,
            'small': self.font_small,
            'medium': self.font_medium,
            'large': self.font_large
        }
        font = font_map.get(font_size, self.font_medium)
        
        # Couleur
        if color is None:
            color = self.colors.TEXT_COLOR
        
        # Rendre le texte
        text_surface = font.render(text, True, color)
        
        if centered:
            text_rect = text_surface.get_rect(center=position)
            surface.blit(text_surface, text_rect)
        else:
            surface.blit(text_surface, position)
    
    def draw_info_box(self, surface: pygame.Surface, rect: pygame.Rect,
                     title: str, content: str, box_type: str = 'info'):
        """
        Dessine une boîte d'information.
        
        Args:
            surface: Surface Pygame
            rect: Rectangle de la boîte
            title: Titre de la boîte
            content: Contenu de la boîte
            box_type: Type ('info', 'success', 'warning', 'error')
        """
        # Couleur selon le type
        type_colors = {
            'info': self.colors.INFO_COLOR,
            'success': self.colors.SUCCESS_COLOR,
            'warning': self.colors.WARNING_COLOR,
            'error': self.colors.ERROR_COLOR
        }
        color = type_colors.get(box_type, self.colors.INFO_COLOR)
        
        # Fond semi-transparent
        box_surface = pygame.Surface((rect.width, rect.height))
        box_surface.set_alpha(230)
        box_surface.fill((255, 255, 255))
        surface.blit(box_surface, rect.topleft)
        
        # Bordure colorée
        pygame.draw.rect(surface, color, rect, 3, border_radius=8)
        
        # Titre
        title_surface = self.font_medium.render(title, True, color)
        title_rect = title_surface.get_rect(
            centerx=rect.centerx,
            top=rect.top + 10
        )
        surface.blit(title_surface, title_rect)
        
        # Contenu
        content_surface = self.font_small.render(content, True, self.colors.TEXT_DARK)
        content_rect = content_surface.get_rect(
            centerx=rect.centerx,
            top=title_rect.bottom + 10
        )
        surface.blit(content_surface, content_rect)
    
    def draw_progress_bar(self, surface: pygame.Surface, rect: pygame.Rect,
                         progress: float, color: Tuple[int, int, int] = None):
        """
        Dessine une barre de progression.
        
        Args:
            surface: Surface Pygame
            rect: Rectangle de la barre
            progress: Progression (0.0 - 1.0)
            color: Couleur de la barre (vert par défaut)
        """
        if color is None:
            color = self.colors.SUCCESS_COLOR
        
        # Fond
        pygame.draw.rect(surface, (220, 220, 220), rect, border_radius=5)
        
        # Progression
        progress = max(0.0, min(1.0, progress))
        fill_width = int(rect.width * progress)
        if fill_width > 0:
            fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
            pygame.draw.rect(surface, color, fill_rect, border_radius=5)
        
        # Bordure
        pygame.draw.rect(surface, self.colors.TEXT_DARK, rect, 2, border_radius=5)
        
        # Texte du pourcentage
        percent_text = f"{int(progress * 100)}%"
        text_surface = self.font_tiny.render(percent_text, True, self.colors.TEXT_DARK)
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)
    
    def get_cell_from_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """
        Convertit une position de clic en coordonnées de case.
        
        Args:
            pos: Position (x, y) du clic
        
        Returns:
            Tuple (ligne, colonne) ou (-1, -1) si hors grille
        """
        x, y = pos
        col = x // self.cell_size
        row = y // self.cell_size
        
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            return (row, col)
        return (-1, -1)
    
    def create_surface(self, width: int, height: int,
                      bg_color: Tuple[int, int, int] = None) -> pygame.Surface:
        """
        Crée une nouvelle surface Pygame.
        
        Args:
            width: Largeur
            height: Hauteur
            bg_color: Couleur de fond (transparente par défaut)
        
        Returns:
            Surface Pygame
        """
        surface = pygame.Surface((width, height))
        if bg_color:
            surface.fill(bg_color)
        else:
            surface.set_colorkey((0, 0, 0))  # Transparent
        return surface
