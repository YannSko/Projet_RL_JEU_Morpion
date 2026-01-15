"""
Vue pour le système de tournoi
"""

import pygame
from typing import Dict, List, Optional
from rl_logic.tournament import Tournament
from rl_logic.elo_system import ELOSystem
from rl_logic.model_manager import ModelManager
from rl_logic.agent import QLearningAgent
from engine.environment import TicTacToeEnvironment


class TournamentView:
    """Vue pour gérer les tournois entre modèles"""
    
    def __init__(self, screen: pygame.Surface, assets, model_manager: ModelManager):
        """
        Initialise la vue tournoi.
        
        Args:
            screen: Surface Pygame
            assets: Assets du jeu
            model_manager: Gestionnaire de modèles
        """
        self.screen = screen
        self.assets = assets
        self.model_manager = model_manager
        self.env = TicTacToeEnvironment()
        self.elo_system = ELOSystem()
        self.tournament = Tournament(self.env, self.elo_system)
        
        # État
        self.models_list = []
        self.selected_models = set()
        self.scroll_offset = 0
        self.tournament_running = False
        self.tournament_result = None
        
        # Boutons
        self._create_buttons()
    
    def _create_buttons(self):
        """Crée les boutons de l'interface"""
        self.buttons = {
            'back': pygame.Rect(20, 20, 100, 35),
            'round_robin': pygame.Rect(450, 50, 180, 35),
            'elimination': pygame.Rect(450, 95, 180, 35),
            'view_elo': pygame.Rect(450, 140, 180, 35),
            'select_all': pygame.Rect(450, 185, 180, 35),
            'clear': pygame.Rect(450, 230, 180, 35)
        }
    
    def load_models(self):
        """Charge la liste des modèles"""
        self.models_list = self.model_manager.list_models()
    
    def handle_click(self, pos: tuple) -> Optional[str]:
        """
        Gère les clics de souris.
        
        Args:
            pos: Position du clic
        
        Returns:
            Action à effectuer (None, 'back', etc.)
        """
        # Boutons
        if self.buttons['back'].collidepoint(pos):
            return 'back'
        
        if self.buttons['select_all'].collidepoint(pos):
            self.selected_models = set(range(len(self.models_list)))
            return None
        
        if self.buttons['clear'].collidepoint(pos):
            self.selected_models.clear()
            return None
        
        if self.buttons['round_robin'].collidepoint(pos) and len(self.selected_models) >= 2:
            self._run_round_robin()
            return None
        
        if self.buttons['elimination'].collidepoint(pos) and len(self.selected_models) >= 2:
            self._run_elimination()
            return None
        
        if self.buttons['view_elo'].collidepoint(pos):
            self.tournament_result = {'type': 'elo_leaderboard'}
            return None
        
        # Sélection de modèles
        for i, model in enumerate(self.models_list[:20]):  # Limiter à 20
            model_y = 120 + i * 40 - self.scroll_offset
            model_rect = pygame.Rect(50, model_y, 350, 35)
            
            if model_rect.collidepoint(pos):
                if i in self.selected_models:
                    self.selected_models.remove(i)
                else:
                    self.selected_models.add(i)
                return None
        
        return None
    
    def handle_scroll(self, direction: int):
        """Gère le défilement"""
        self.scroll_offset += direction * 40
        self.scroll_offset = max(0, self.scroll_offset)
    
    def _run_round_robin(self):
        """Lance un tournoi round-robin"""
        print("\n🏆 Lancement du tournoi round-robin...")
        
        # Charger les agents sélectionnés
        agents_dict = {}
        for idx in self.selected_models:
            model_info = self.models_list[idx]
            agent = QLearningAgent()
            self.model_manager.load_model(agent, model_info['path'])
            agents_dict[model_info['name']] = agent
        
        # Lancer le tournoi
        self.tournament_running = True
        self.tournament_result = self.tournament.round_robin(agents_dict, games_per_match=50)
        self.tournament_running = False
        
        print("✅ Tournoi terminé!")
    
    def _run_elimination(self):
        """Lance un tournoi à élimination"""
        print("\n🏆 Lancement du tournoi à élimination...")
        
        # Charger les agents
        agents_dict = {}
        for idx in self.selected_models:
            model_info = self.models_list[idx]
            agent = QLearningAgent()
            self.model_manager.load_model(agent, model_info['path'])
            agents_dict[model_info['name']] = agent
        
        # Lancer
        self.tournament_running = True
        self.tournament_result = self.tournament.elimination_bracket(agents_dict, games_per_match=50)
        self.tournament_running = False
        
        print("✅ Tournoi terminé!")
    
    def draw(self):
        """Dessine la vue"""
        self.screen.fill(self.assets.colors.BG_COLOR)
        
        # Titre
        self.assets.draw_text(
            self.screen,
            "🏆 TOURNOI - Compétition entre Modèles",
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
        
        # Section gauche - Liste des modèles
        pygame.draw.rect(self.screen, (40, 40, 40), pygame.Rect(40, 100, 370, 520))
        pygame.draw.rect(self.screen, self.assets.colors.TEXT_COLOR, pygame.Rect(40, 100, 370, 520), 2)
        
        self.assets.draw_text(
            self.screen,
            f"Modèles disponibles ({len(self.models_list)}) - {len(self.selected_models)} sélectionnés",
            (225, 110),
            font_size='medium',
            centered=True
        )
        
        # Liste des modèles
        for i, model in enumerate(self.models_list[:20]):
            model_y = 140 + i * 40 - self.scroll_offset
            
            if model_y < 130 or model_y > 600:
                continue
            
            is_selected = i in self.selected_models
            color = self.assets.colors.SUCCESS_COLOR if is_selected else (60, 60, 60)
            
            model_rect = pygame.Rect(50, model_y, 350, 35)
            pygame.draw.rect(self.screen, color, model_rect)
            pygame.draw.rect(self.screen, self.assets.colors.TEXT_COLOR, model_rect, 1)
            
            name = model['name'][:25] + "..." if len(model['name']) > 25 else model['name']
            self.assets.draw_text(
                self.screen,
                name,
                (60, model_y + 18),
                font_size='tiny',
                color=(255, 255, 255)
            )
            
            # ELO rating
            elo = self.elo_system.get_rating(model['name'])
            self.assets.draw_text(
                self.screen,
                f"ELO: {elo:.0f}",
                (370, model_y + 18),
                font_size='tiny',
                color=(200, 200, 200)
            )
        
        # Section droite - Actions et résultats
        pygame.draw.rect(self.screen, (40, 40, 40), pygame.Rect(430, 30, 210, 590))
        pygame.draw.rect(self.screen, self.assets.colors.TEXT_COLOR, pygame.Rect(430, 30, 210, 590), 2)
        
        # Boutons d'action
        self.assets.draw_button(
            self.screen,
            self.buttons['round_robin'],
            "🔄 Round-Robin",
            hovered=False,
            enabled=len(self.selected_models) >= 2
        )
        
        self.assets.draw_button(
            self.screen,
            self.buttons['elimination'],
            "🏅 Élimination",
            hovered=False,
            enabled=len(self.selected_models) >= 2
        )
        
        self.assets.draw_button(
            self.screen,
            self.buttons['view_elo'],
            "📊 Classement ELO",
            hovered=False
        )
        
        self.assets.draw_button(
            self.screen,
            self.buttons['select_all'],
            "☑️  Tout sélectionner",
            hovered=False
        )
        
        self.assets.draw_button(
            self.screen,
            self.buttons['clear'],
            "❌ Désélectionner",
            hovered=False
        )
        
        # Afficher les résultats si disponibles
        if self.tournament_result:
            y_offset = 290
            
            if self.tournament_result['type'] == 'round_robin':
                self.assets.draw_text(
                    self.screen,
                    "🏆 RÉSULTATS",
                    (535, y_offset),
                    font_size='medium',
                    centered=True
                )
                
                y_offset += 30
                rankings = self.tournament_result.get('rankings', [])
                
                for i, (name, stats) in enumerate(rankings[:5], 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    
                    self.assets.draw_text(
                        self.screen,
                        f"{medal} {name[:12]}",
                        (440, y_offset),
                        font_size='tiny'
                    )
                    
                    self.assets.draw_text(
                        self.screen,
                        f"{stats['points']}pts",
                        (615, y_offset),
                        font_size='tiny'
                    )
                    
                    y_offset += 25
            
            elif self.tournament_result['type'] == 'elimination_bracket':
                self.assets.draw_text(
                    self.screen,
                    "🏆 CHAMPION",
                    (535, y_offset),
                    font_size='medium',
                    centered=True
                )
                
                y_offset += 30
                champion = self.tournament_result.get('champion', 'N/A')
                
                self.assets.draw_text(
                    self.screen,
                    champion[:20],
                    (535, y_offset),
                    font_size='medium',
                    color=self.assets.colors.SUCCESS_COLOR,
                    centered=True
                )
            
            elif self.tournament_result['type'] == 'elo_leaderboard':
                self.assets.draw_text(
                    self.screen,
                    "📊 TOP ELO",
                    (535, y_offset),
                    font_size='medium',
                    centered=True
                )
                
                y_offset += 30
                leaderboard = self.elo_system.get_leaderboard(10)
                
                for i, (name, rating) in enumerate(leaderboard[:8], 1):
                    self.assets.draw_text(
                        self.screen,
                        f"{i}. {name[:12]}",
                        (440, y_offset),
                        font_size='tiny'
                    )
                    
                    self.assets.draw_text(
                        self.screen,
                        f"{rating:.0f}",
                        (615, y_offset),
                        font_size='tiny',
                        color=self.assets.colors.ACCENT_COLOR
                    )
                    
                    y_offset += 25
        
        # Message de chargement si tournoi en cours
        if self.tournament_running:
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            self.assets.draw_text(
                self.screen,
                "⏳ Tournoi en cours...",
                (self.screen.get_width() // 2, self.screen.get_height() // 2),
                font_size='large',
                centered=True
            )
