"""
Vue pour l'AutoML - Hyperparameter Tuning
"""

import pygame
import threading
from typing import Dict, Optional
from rl_logic.automl import AutoMLTuner
from engine.environment import TicTacToeEnvironment


class AutoMLView:
    """Vue pour l'optimisation automatique des hyperparamètres"""
    
    def __init__(self, screen: pygame.Surface, assets):
        """
        Initialise la vue AutoML.
        
        Args:
            screen: Surface Pygame
            assets: Assets du jeu
        """
        self.screen = screen
        self.assets = assets
        self.env = TicTacToeEnvironment()
        self.tuner = AutoMLTuner(self.env)
        
        # État
        self.running = False
        self.progress = 0
        self.current_config = 0
        self.total_configs = 0
        self.best_score = 0
        self.best_config = None
        self.results = []
        
        # Configuration
        self.search_type = 'grid_fast'  # 'grid_fast', 'grid_full', 'random'
        self.episodes = 10000
        self.eval_games = 100
        
        # Boutons
        self._create_buttons()
    
    def _create_buttons(self):
        """Crée les boutons de l'interface"""
        self.buttons = {
            'back': pygame.Rect(20, 20, 100, 35),
            'start': pygame.Rect(250, 500, 150, 45),
            'grid_fast': pygame.Rect(100, 200, 150, 35),
            'grid_full': pygame.Rect(100, 245, 150, 35),
            'random': pygame.Rect(100, 290, 150, 35),
            'episodes_minus': pygame.Rect(100, 350, 35, 35),
            'episodes_plus': pygame.Rect(415, 350, 35, 35),
            'eval_minus': pygame.Rect(100, 400, 35, 35),
            'eval_plus': pygame.Rect(415, 400, 35, 35)
        }
    
    def handle_click(self, pos: tuple) -> Optional[str]:
        """
        Gère les clics de souris.
        
        Args:
            pos: Position du clic
        
        Returns:
            Action à effectuer
        """
        if self.buttons['back'].collidepoint(pos):
            return 'back'
        
        if not self.running:
            # Type de recherche
            if self.buttons['grid_fast'].collidepoint(pos):
                self.search_type = 'grid_fast'
            elif self.buttons['grid_full'].collidepoint(pos):
                self.search_type = 'grid_full'
            elif self.buttons['random'].collidepoint(pos):
                self.search_type = 'random'
            
            # Épisodes
            elif self.buttons['episodes_minus'].collidepoint(pos):
                self.episodes = max(1000, self.episodes - 1000)
            elif self.buttons['episodes_plus'].collidepoint(pos):
                self.episodes = min(50000, self.episodes + 1000)
            
            # Évaluation
            elif self.buttons['eval_minus'].collidepoint(pos):
                self.eval_games = max(10, self.eval_games - 10)
            elif self.buttons['eval_plus'].collidepoint(pos):
                self.eval_games = min(500, self.eval_games + 10)
            
            # Démarrer
            elif self.buttons['start'].collidepoint(pos):
                self._start_automl()
        
        return None
    
    def _start_automl(self):
        """Lance l'AutoML en arrière-plan"""
        def run_automl():
            self.running = True
            self.progress = 0
            self.current_config = 0
            self.results = []
            
            try:
                if self.search_type == 'grid_fast':
                    param_grid = {
                        'alpha': [0.15, 0.2, 0.25],
                        'gamma': [0.92, 0.95, 0.99],
                        'epsilon_decay': [0.995, 0.997]
                    }
                    self.total_configs = 3 * 3 * 2
                    result = self.tuner.grid_search(
                        param_grid,
                        self.episodes,
                        self.eval_games,
                        max_configs=self.total_configs
                    )
                
                elif self.search_type == 'grid_full':
                    param_grid = AutoMLTuner.get_default_grid()
                    self.total_configs = 5 * 5 * 4
                    result = self.tuner.grid_search(
                        param_grid,
                        self.episodes,
                        self.eval_games
                    )
                
                else:  # random
                    param_distributions = AutoMLTuner.get_default_distributions()
                    self.total_configs = 20
                    result = self.tuner.random_search(
                        param_distributions,
                        n_iter=self.total_configs,
                        num_episodes=self.episodes,
                        eval_games=self.eval_games
                    )
                
                self.best_config = result['best_config']
                self.best_score = result['best_score']
                self.results = result['all_results']
                
            except Exception as e:
                print(f"Erreur AutoML: {e}")
            
            finally:
                self.running = False
        
        # Lancer dans un thread
        thread = threading.Thread(target=run_automl, daemon=True)
        thread.start()
    
    def draw(self):
        """Dessine la vue"""
        self.screen.fill(self.assets.colors.BG_COLOR)
        
        # Titre
        self.assets.draw_text(
            self.screen,
            "🤖 AUTOML - Optimisation Automatique",
            (self.screen.get_width() // 2, 50),
            font_size='large',
            centered=True
        )
        
        # Bouton retour
        self.assets.draw_button(
            self.screen,
            self.buttons['back'],
            "← Retour",
            hovered=False
        )
        
        # Panel de configuration (gauche)
        pygame.draw.rect(self.screen, (40, 40, 40), pygame.Rect(70, 120, 410, 350))
        pygame.draw.rect(self.screen, self.assets.colors.TEXT_COLOR, pygame.Rect(70, 120, 410, 350), 2)
        
        self.assets.draw_text(
            self.screen,
            "⚙️  CONFIGURATION",
            (275, 140),
            font_size='medium',
            centered=True
        )
        
        # Type de recherche
        y = 180
        self.assets.draw_text(
            self.screen,
            "Type de Recherche:",
            (90, y),
            font_size='small'
        )
        
        y = 200
        for btn_name, label, desc in [
            ('grid_fast', 'Grid Fast (18 configs)', '~15-30 min'),
            ('grid_full', 'Grid Full (100 configs)', '~1-2 heures'),
            ('random', 'Random (20 configs)', '~20-40 min')
        ]:
            is_selected = self.search_type == btn_name.replace('grid_', 'grid_').replace('random', 'random')
            color = self.assets.colors.SUCCESS_COLOR if is_selected else (60, 60, 60)
            
            btn = self.buttons[btn_name]
            pygame.draw.rect(self.screen, color, btn)
            pygame.draw.rect(self.screen, self.assets.colors.TEXT_COLOR, btn, 2)
            
            self.assets.draw_text(
                self.screen,
                label,
                (btn.centerx, btn.centery),
                font_size='tiny',
                color=(255, 255, 255),
                centered=True
            )
            
            self.assets.draw_text(
                self.screen,
                desc,
                (280, y + 18),
                font_size='tiny',
                color=(150, 150, 150)
            )
            
            y += 45
        
        # Épisodes
        y = 350
        self.assets.draw_text(
            self.screen,
            "Épisodes d'entraînement:",
            (90, y),
            font_size='small'
        )
        
        self.assets.draw_button(
            self.screen,
            self.buttons['episodes_minus'],
            "-",
            hovered=False,
            enabled=not self.running
        )
        
        self.assets.draw_text(
            self.screen,
            f"{self.episodes:,}",
            (275, y + 18),
            font_size='medium',
            centered=True
        )
        
        self.assets.draw_button(
            self.screen,
            self.buttons['episodes_plus'],
            "+",
            hovered=False,
            enabled=not self.running
        )
        
        # Parties d'évaluation
        y = 400
        self.assets.draw_text(
            self.screen,
            "Parties d'évaluation:",
            (90, y),
            font_size='small'
        )
        
        self.assets.draw_button(
            self.screen,
            self.buttons['eval_minus'],
            "-",
            hovered=False,
            enabled=not self.running
        )
        
        self.assets.draw_text(
            self.screen,
            f"{self.eval_games}",
            (275, y + 18),
            font_size='medium',
            centered=True
        )
        
        self.assets.draw_button(
            self.screen,
            self.buttons['eval_plus'],
            "+",
            hovered=False,
            enabled=not self.running
        )
        
        # Bouton démarrer
        if not self.running:
            self.assets.draw_button(
                self.screen,
                self.buttons['start'],
                "🚀 DÉMARRER",
                hovered=False,
                enabled=True
            )
        else:
            self.assets.draw_button(
                self.screen,
                self.buttons['start'],
                "⏳ En cours...",
                hovered=False,
                enabled=False
            )
        
        # Panel de résultats (droite)
        pygame.draw.rect(self.screen, (40, 40, 40), pygame.Rect(500, 120, 140, 470))
        pygame.draw.rect(self.screen, self.assets.colors.TEXT_COLOR, pygame.Rect(500, 120, 140, 470), 2)
        
        self.assets.draw_text(
            self.screen,
            "📊 RÉSULTATS",
            (570, 140),
            font_size='medium',
            centered=True
        )
        
        # Afficher les résultats
        if self.running:
            # Barre de progression
            if self.total_configs > 0:
                progress_pct = (len(self.tuner.results) / self.total_configs) * 100
                self.assets.draw_text(
                    self.screen,
                    f"{len(self.tuner.results)}/{self.total_configs}",
                    (570, 180),
                    font_size='medium',
                    centered=True
                )
                
                # Barre
                bar_rect = pygame.Rect(510, 210, 120, 20)
                pygame.draw.rect(self.screen, (60, 60, 60), bar_rect)
                
                if progress_pct > 0:
                    fill_rect = pygame.Rect(510, 210, int(120 * progress_pct / 100), 20)
                    pygame.draw.rect(self.screen, self.assets.colors.SUCCESS_COLOR, fill_rect)
                
                pygame.draw.rect(self.screen, self.assets.colors.TEXT_COLOR, bar_rect, 1)
                
                self.assets.draw_text(
                    self.screen,
                    f"{progress_pct:.0f}%",
                    (570, 245),
                    font_size='tiny',
                    centered=True
                )
        
        if self.best_config:
            y = 280
            self.assets.draw_text(
                self.screen,
                "🏆 MEILLEUR",
                (570, y),
                font_size='small',
                color=self.assets.colors.SUCCESS_COLOR,
                centered=True
            )
            
            y += 35
            self.assets.draw_text(
                self.screen,
                f"Score: {self.best_score:.2f}",
                (570, y),
                font_size='tiny',
                centered=True
            )
            
            y += 25
            for key, value in self.best_config.items():
                self.assets.draw_text(
                    self.screen,
                    f"{key}:",
                    (510, y),
                    font_size='tiny'
                )
                
                self.assets.draw_text(
                    self.screen,
                    f"{value:.3f}",
                    (625, y),
                    font_size='tiny'
                )
                
                y += 20
