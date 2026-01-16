"""
Gestion des assets graphiques
Couleurs, polices, dessins et constantes d'interface.
"""

import pygame
from typing import Tuple


class Colors:
    """Palette de couleurs moderne pour l'interface"""
    
    # 🎨 Thème sombre élégant
    BG_DARK = (20, 25, 35)  # Bleu nuit profond
    BG_MEDIUM = (30, 35, 50)  # Bleu nuit moyen
    BG_LIGHT = (45, 52, 70)  # Bleu nuit clair
    BG_COLOR = (25, 30, 45)  # Fond principal
    
    # Grille moderne
    LINE_COLOR = (60, 70, 90)  # Lignes subtiles
    GRID_GLOW = (100, 120, 160)  # Effet glow sur grille
    
    # Symboles avec couleurs vibrantes
    CIRCLE_COLOR = (99, 179, 237)  # Bleu cyan électrique (O)
    CIRCLE_GLOW = (79, 159, 217)  # Glow pour O
    CROSS_COLOR = (237, 106, 94)  # Rouge corail (X)
    CROSS_GLOW = (217, 86, 74)  # Glow pour X
    
    # Typographie moderne
    TEXT_COLOR = (240, 245, 255)  # Blanc cassé
    TEXT_SECONDARY = (180, 190, 210)  # Gris clair
    TEXT_DARK = (60, 70, 90)  # Gris foncé
    TEXT_ACCENT = (129, 212, 250)  # Bleu accent
    
    # Boutons modernes avec dégradés
    BUTTON_PRIMARY = (88, 101, 242)  # Bleu violet vif
    BUTTON_PRIMARY_HOVER = (108, 121, 255)  # Hover plus clair
    BUTTON_PRIMARY_GLOW = (108, 121, 255, 30)  # Glow subtle
    
    BUTTON_SUCCESS = (16, 185, 129)  # Vert émeraude
    BUTTON_SUCCESS_HOVER = (34, 197, 94)  # Hover plus clair
    
    BUTTON_DANGER = (239, 68, 68)  # Rouge vif
    BUTTON_DANGER_HOVER = (248, 113, 113)  # Hover plus clair
    
    BUTTON_NEUTRAL = (55, 65, 85)  # Gris bleuté
    BUTTON_NEUTRAL_HOVER = (75, 85, 105)  # Hover plus clair
    
    BUTTON_DISABLED = (55, 65, 81)  # Gris désactivé
    
    # Couleurs de statut vibrantes
    SUCCESS_COLOR = (34, 197, 94)  # Vert moderne
    WARNING_COLOR = (251, 191, 36)  # Jaune doré
    ERROR_COLOR = (239, 68, 68)  # Rouge vif
    INFO_COLOR = (59, 130, 246)  # Bleu info
    
    # Graphiques modernes
    PLOT_BG = (30, 35, 50)  # Fond sombre
    PLOT_GRID = (55, 65, 85)  # Grille subtile
    PLOT_WIN = (34, 197, 94)  # Vert
    PLOT_LOSS = (239, 68, 68)  # Rouge
    PLOT_DRAW = (251, 191, 36)  # Jaune
    PLOT_EPSILON = (168, 85, 247)  # Violet électrique
    
    # Effets et accents
    SHADOW = (10, 15, 25, 180)  # Ombre
    GLOW = (129, 212, 250, 50)  # Effet glow
    ACCENT = (129, 212, 250)  # Accent cyan
    HIGHLIGHT = (255, 255, 255, 30)  # Highlight subtle


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
        
        # Polices avec meilleure hiérarchie
        self.font_title = pygame.font.Font(None, 56)  # Titres principaux
        self.font_large = pygame.font.Font(None, 42)  # Sous-titres
        self.font_medium = pygame.font.Font(None, 32)  # Texte important
        self.font_small = pygame.font.Font(None, 24)  # Texte normal
        self.font_tiny = pygame.font.Font(None, 18)  # Détails
        
        # Couleurs
        self.colors = Colors()
        
        # Animation timer pour effets hover
        self.hover_animations = {}  # {button_id: progress}
    
    def draw_grid(self, surface: pygame.Surface):
        """
        Dessine la grille moderne du jeu de Morpion avec effets.
        
        Args:
            surface: Surface Pygame où dessiner
        """
        # Fond avec léger dégradé
        for i in range(self.window_size):
            alpha = 255 - int(i / self.window_size * 20)
            color = (*self.colors.BG_DARK, min(255, max(0, alpha)))
            line = pygame.Surface((self.window_size, 1), pygame.SRCALPHA)
            line.fill(color)
            surface.blit(line, (0, i))
        
        # Lignes horizontales avec effet glow
        for i in range(1, self.grid_size):
            y = i * self.cell_size
            
            # Glow (ligne floue en arrière-plan)
            for offset in range(-2, 3):
                alpha = 30 - abs(offset) * 10
                glow_surface = pygame.Surface((self.window_size, 1), pygame.SRCALPHA)
                glow_surface.fill((*self.colors.GRID_GLOW, alpha))
                surface.blit(glow_surface, (0, y + offset))
            
            # Ligne principale
            pygame.draw.line(
                surface,
                self.colors.LINE_COLOR,
                (0, y),
                (self.window_size, y),
                self.line_width
            )
        
        # Lignes verticales avec effet glow
        for i in range(1, self.grid_size):
            x = i * self.cell_size
            
            # Glow
            for offset in range(-2, 3):
                alpha = 30 - abs(offset) * 10
                glow_surface = pygame.Surface((1, self.window_size), pygame.SRCALPHA)
                glow_surface.fill((*self.colors.GRID_GLOW, alpha))
                surface.blit(glow_surface, (x + offset, 0))
            
            # Ligne principale
            pygame.draw.line(
                surface,
                self.colors.LINE_COLOR,
                (x, 0),
                (x, self.window_size),
                self.line_width
            )
    
    def draw_cross(self, surface: pygame.Surface, row: int, col: int, animated: float = 1.0):
        """
        Dessine un X moderne avec effet glow.
        
        Args:
            surface: Surface Pygame
            row: Ligne (0-2)
            col: Colonne (0-2)
            animated: Facteur d'animation (0.0 à 1.0)
        """
        center_x = col * self.cell_size + self.cell_size // 2
        center_y = row * self.cell_size + self.cell_size // 2
        
        # Ajuster la taille selon l'animation
        space = int(self.cross_space * animated)
        
        # Effet glow rouge
        for glow_offset in range(8, 0, -2):
            glow_alpha = int(20 * animated)
            glow_color = (*self.colors.CROSS_GLOW, glow_alpha)
            
            # Diagonale \
            pygame.draw.line(
                surface,
                glow_color,
                (center_x - space - glow_offset, center_y - space - glow_offset),
                (center_x + space + glow_offset, center_y + space + glow_offset),
                self.cross_width + glow_offset
            )
            
            # Diagonale /
            pygame.draw.line(
                surface,
                glow_color,
                (center_x + space + glow_offset, center_y - space - glow_offset),
                (center_x - space - glow_offset, center_y + space + glow_offset),
                self.cross_width + glow_offset
            )
        
        # Symbole principal
        # Première diagonale (\)
        pygame.draw.line(
            surface,
            self.colors.CROSS_COLOR,
            (center_x - space, center_y - space),
            (center_x + space, center_y + space),
            self.cross_width
        )
        
        # Deuxième diagonale (/)
        pygame.draw.line(
            surface,
            self.colors.CROSS_COLOR,
            (center_x + space, center_y - space),
            (center_x - space, center_y + space),
            self.cross_width
        )
    
    def draw_circle(self, surface: pygame.Surface, row: int, col: int, animated: float = 1.0):
        """
        Dessine un O moderne avec effet glow.
        
        Args:
            surface: Surface Pygame
            row: Ligne (0-2)
            col: Colonne (0-2)
            animated: Facteur d'animation (0.0 à 1.0)
        """
        center_x = col * self.cell_size + self.cell_size // 2
        center_y = row * self.cell_size + self.cell_size // 2
        
        # Rayon ajusté selon l'animation
        radius = int(self.circle_radius * animated)
        
        # Effet glow cyan
        for glow_radius in range(radius + 8, radius, -2):
            glow_alpha = int(15 * animated)
            glow_color = (*self.colors.CIRCLE_GLOW, glow_alpha)
            pygame.draw.circle(
                surface,
                glow_color,
                (center_x, center_y),
                glow_radius,
                self.circle_width + 2
            )
        
        # Cercle principal
        pygame.draw.circle(
            surface,
            self.colors.CIRCLE_COLOR,
            (center_x, center_y),
            radius,
            self.cross_width
        )
    
    def draw_button(self, surface: pygame.Surface, rect: pygame.Rect,
                   text: str, hovered: bool = False, disabled: bool = False, enabled: bool = True,
                   style: str = 'primary', icon: str = None):
        """
        Dessine un bouton moderne avec effets visuels.
        
        Args:
            surface: Surface Pygame
            rect: Rectangle du bouton
            text: Texte du bouton
            hovered: Si True, applique effet hover
            disabled: Si True, bouton désactivé
            enabled: Si False, bouton désactivé (alias)
            style: Style du bouton ('primary', 'success', 'danger', 'neutral')
            icon: Emoji optionnel à afficher
        """
        is_disabled = disabled or not enabled
        
        # Sélection des couleurs selon le style
        style_colors = {
            'primary': (self.colors.BUTTON_PRIMARY, self.colors.BUTTON_PRIMARY_HOVER),
            'success': (self.colors.BUTTON_SUCCESS, self.colors.BUTTON_SUCCESS_HOVER),
            'danger': (self.colors.BUTTON_DANGER, self.colors.BUTTON_DANGER_HOVER),
            'neutral': (self.colors.BUTTON_NEUTRAL, self.colors.BUTTON_NEUTRAL_HOVER)
        }
        
        base_color, hover_color = style_colors.get(style, style_colors['primary'])
        
        if is_disabled:
            color = self.colors.BUTTON_DISABLED
        elif hovered:
            color = hover_color
        else:
            color = base_color
        
        # 🎨 Ombre portée pour profondeur
        if not is_disabled and hovered:
            shadow_rect = rect.copy()
            shadow_rect.y += 2
            shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 60), shadow_surface.get_rect(), border_radius=12)
            surface.blit(shadow_surface, shadow_rect.topleft)
        
        # Fond du bouton avec bordure arrondie
        pygame.draw.rect(surface, color, rect, border_radius=12)
        
        # Effet de highlight en haut
        if not is_disabled:
            highlight_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height // 3)
            highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, (255, 255, 255, 20), highlight_surface.get_rect(), 
                           border_radius=12)
            surface.blit(highlight_surface, highlight_rect.topleft)
        
        # Bordure subtile pour définition
        border_color = self.colors.TEXT_COLOR if hovered else (255, 255, 255, 50)
        pygame.draw.rect(surface, border_color, rect, 2, border_radius=12)
        
        # Texte avec icône optionnelle
        text_color = self.colors.TEXT_SECONDARY if is_disabled else self.colors.TEXT_COLOR
        
        if icon:
            full_text = f"{icon} {text}"
        else:
            full_text = text
        
        # Rendre texte avec anti-aliasing
        text_surface = self.font_small.render(full_text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        
        # Effet de "press" quand hover
        if hovered and not is_disabled:
            text_rect.y += 1
        
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
        Dessine une boîte d'information moderne.
        
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
        
        # Icônes selon le type
        type_icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        icon = type_icons.get(box_type, 'ℹ️')
        
        # Fond sombre moderne avec transparence
        box_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (*self.colors.BG_MEDIUM, 240), box_surface.get_rect(), border_radius=12)
        surface.blit(box_surface, rect.topleft)
        
        # Barre latérale colorée pour accentuation
        bar_rect = pygame.Rect(rect.x, rect.y, 5, rect.height)
        pygame.draw.rect(surface, color, bar_rect, border_radius=12)
        
        # Bordure avec glow
        pygame.draw.rect(surface, color, rect, 2, border_radius=12)
        
        # Titre avec icône
        title_text = f"{icon} {title}"
        title_surface = self.font_medium.render(title_text, True, color)
        title_rect = title_surface.get_rect(
            x=rect.x + 20,
            top=rect.top + 15
        )
        surface.blit(title_surface, title_rect)
        
        # Contenu avec meilleure lisibilité
        content_surface = self.font_small.render(content, True, self.colors.TEXT_COLOR)
        content_rect = content_surface.get_rect(
            x=rect.x + 20,
            top=title_rect.bottom + 12
        )
        surface.blit(content_surface, content_rect)
    
    def draw_progress_bar(self, surface: pygame.Surface, rect: pygame.Rect,
                         progress: float, color: Tuple[int, int, int] = None,
                         show_percentage: bool = True, animated: bool = False):
        """
        Dessine une barre de progression moderne.
        
        Args:
            surface: Surface Pygame
            rect: Rectangle de la barre
            progress: Progression (0.0 - 1.0)
            color: Couleur de la barre (vert par défaut)
            show_percentage: Afficher le pourcentage
            animated: Animation de remplissage
        """
        if color is None:
            color = self.colors.SUCCESS_COLOR
        
        # Fond sombre
        pygame.draw.rect(surface, self.colors.BG_LIGHT, rect, border_radius=10)
        
        # Progression avec dégradé
        progress = max(0.0, min(1.0, progress))
        fill_width = int(rect.width * progress)
        
        if fill_width > 4:
            fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
            
            # Dégradé simple simulé avec plusieurs rectangles
            pygame.draw.rect(surface, color, fill_rect, border_radius=10)
            
            # Highlight en haut
            highlight_rect = pygame.Rect(fill_rect.x, fill_rect.y, fill_rect.width, fill_rect.height // 3)
            highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(highlight_surface, (255, 255, 255, 40), highlight_surface.get_rect(), border_radius=10)
            surface.blit(highlight_surface, highlight_rect.topleft)
        
        # Bordure
        pygame.draw.rect(surface, self.colors.TEXT_SECONDARY, rect, 2, border_radius=10)
        
        # Texte du pourcentage
        if show_percentage:
            percent_text = f"{int(progress * 100)}%"
            text_surface = self.font_small.render(percent_text, True, self.colors.TEXT_COLOR)
            text_rect = text_surface.get_rect(center=rect.center)
            
            # Ombre du texte pour lisibilité
            shadow_surface = self.font_small.render(percent_text, True, (0, 0, 0))
            shadow_rect = text_rect.copy()
            shadow_rect.x += 1
            shadow_rect.y += 1
            surface.blit(shadow_surface, shadow_rect)
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
    
    def draw_card(self, surface: pygame.Surface, rect: pygame.Rect,
                  title: str = None, content: list = None, hovered: bool = False):
        """
        Dessine une carte moderne (card) avec titre et contenu.
        
        Args:
            surface: Surface Pygame
            rect: Rectangle de la carte
            title: Titre optionnel de la carte
            content: Liste de tuples (label, value) pour le contenu
            hovered: Si True, applique effet hover
        """
        # Ombre portée
        if hovered:
            shadow_rect = rect.copy()
            shadow_rect.y += 3
            shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surface, (0, 0, 0, 80), shadow_surface.get_rect(), border_radius=15)
            surface.blit(shadow_surface, shadow_rect.topleft)
        
        # Fond de la carte
        card_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, (*self.colors.BG_MEDIUM, 250), card_surface.get_rect(), border_radius=15)
        surface.blit(card_surface, rect.topleft)
        
        # Bordure avec glow si hover
        border_color = self.colors.ACCENT if hovered else self.colors.BG_LIGHT
        pygame.draw.rect(surface, border_color, rect, 2, border_radius=15)
        
        # Titre
        y_offset = rect.y + 20
        if title:
            title_surface = self.font_medium.render(title, True, self.colors.TEXT_COLOR)
            title_rect = title_surface.get_rect(centerx=rect.centerx, top=y_offset)
            surface.blit(title_surface, title_rect)
            y_offset = title_rect.bottom + 15
            
            # Ligne de séparation
            line_start = (rect.x + 20, y_offset)
            line_end = (rect.x + rect.width - 20, y_offset)
            pygame.draw.line(surface, self.colors.BG_LIGHT, line_start, line_end, 2)
            y_offset += 15
        
        # Contenu
        if content:
            for label, value in content:
                # Label
                label_surface = self.font_small.render(label, True, self.colors.TEXT_SECONDARY)
                label_rect = label_surface.get_rect(x=rect.x + 20, top=y_offset)
                surface.blit(label_surface, label_rect)
                
                # Valeur
                value_str = str(value)
                value_surface = self.font_small.render(value_str, True, self.colors.TEXT_COLOR)
                value_rect = value_surface.get_rect(right=rect.right - 20, top=y_offset)
                surface.blit(value_surface, value_rect)
                
                y_offset += 30
    
    def draw_title_bar(self, surface: pygame.Surface, title: str, subtitle: str = None):
        """
        Dessine une barre de titre moderne avec dégradé.
        
        Args:
            surface: Surface Pygame
            title: Titre principal
            subtitle: Sous-titre optionnel
        """
        # Fond avec dégradé simulé
        bar_height = 100 if subtitle else 80
        bar_rect = pygame.Rect(0, 0, self.window_size, bar_height)
        
        # Couches pour simuler dégradé
        for i in range(bar_height):
            alpha = int(255 * (1 - i / bar_height * 0.3))
            color = (*self.colors.BG_MEDIUM, min(255, alpha))
            line_surface = pygame.Surface((self.window_size, 1), pygame.SRCALPHA)
            line_surface.fill(color)
            surface.blit(line_surface, (0, i))
        
        # Titre
        title_surface = self.font_title.render(title, True, self.colors.TEXT_COLOR)
        title_rect = title_surface.get_rect(centerx=self.window_size // 2, top=20)
        
        # Ombre du titre
        shadow_surface = self.font_title.render(title, True, (0, 0, 0, 100))
        shadow_rect = title_rect.copy()
        shadow_rect.y += 2
        surface.blit(shadow_surface, shadow_rect)
        surface.blit(title_surface, title_rect)
        
        # Sous-titre
        if subtitle:
            subtitle_surface = self.font_small.render(subtitle, True, self.colors.TEXT_SECONDARY)
            subtitle_rect = subtitle_surface.get_rect(centerx=self.window_size // 2, top=title_rect.bottom + 10)
            surface.blit(subtitle_surface, subtitle_rect)
