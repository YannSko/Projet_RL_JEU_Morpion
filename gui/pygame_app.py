"""
Application Pygame principale
Point d'entrée de l'interface graphique.
"""

import pygame
import sys
from typing import Dict
from engine.environment import TicTacToeEnvironment
from rl_logic.agent import QLearningAgent
from rl_logic.trainer import Trainer
from rl_logic.logger import RLLogger
from rl_logic.model_manager import ModelManager
from rl_logic.app_logger import init_app_logger, get_app_logger
from rl_logic.game_logger import get_game_logger
from .assets import Assets
from .view_game import GameView
from .view_stats import StatsView
from .view_history import HistoryView
from .view_models import ModelsView
from .view_tournament import TournamentView
from .view_automl import AutoMLView


class GameGUI:
    """Application principale de l'interface graphique"""
    
    def __init__(self, window_size: int = 660):
        """
        Initialise l'application.
        
        Args:
            window_size: Taille de la fenêtre
        """
        pygame.init()
        self.window_size = window_size
        self.screen = pygame.display.set_mode((window_size, window_size))
        pygame.display.set_caption("Morpion - Q-Learning RL")
        self.clock = pygame.time.Clock()
        
        # Loggers
        self.app_logger = init_app_logger()
        self.game_logger = get_game_logger()
        self.app_logger.log_info("Interface Pygame initialisée", window_size=window_size)
        
        # Assets et vues
        self.assets = Assets(window_size)
        
        # Composants RL
        self.env = TicTacToeEnvironment()
        self.agent = QLearningAgent()
        self.logger = RLLogger()
        self.model_manager = ModelManager()
        self.trainer = Trainer(self.agent, self.env, self.logger, self.model_manager)
        
        # Charger le modèle existant
        self.model_manager.load_model(self.agent)
        
        # Vues
        self.game_view = GameView(self.screen, self.assets)
        self.game_view.set_agent(self.agent, "q_table.pkl")
        
        self.stats_view = StatsView(self.screen, self.assets, self.logger)
        self.stats_view.set_agent(self.agent)
        
        self.history_view = HistoryView(self.screen, self.assets, self.logger)
        self.history_view.load_games()
        
        self.models_view = ModelsView(self.screen, self.assets, self.model_manager, self.agent)
        
        self.tournament_view = TournamentView(self.screen, self.assets, self.model_manager)
        self.tournament_view.load_models()
        
        self.automl_view = AutoMLView(self.screen, self.assets)
        
        # État de l'application
        self.current_view = 'menu'  # 'menu', 'game', 'stats', 'train', 'level_select', 'history', 'models', 'tournament', 'automl'
        self.selected_mode = None
        self.coach_mode = False  # Mode Coach activé/désactivé
        
        # Boutons du menu
        self._create_menu_buttons()
        self._create_level_buttons()
    
    def _create_menu_buttons(self):
        """Crée les boutons du menu principal"""
        button_width = 300
        button_height = 45
        start_x = (self.window_size - button_width) // 2
        start_y = 80
        spacing = 53
        
        self.menu_buttons = [
            {
                'rect': pygame.Rect(start_x, start_y, button_width, button_height),
                'text': '👥 Humain vs Humain',
                'action': 'start_HH'
            },
            {
                'rect': pygame.Rect(start_x, start_y + spacing, button_width, button_height),
                'text': '🎮 Humain vs IA',
                'action': 'select_level_HA'
            },
            {
                'rect': pygame.Rect(start_x, start_y + spacing * 2, button_width, button_height),
                'text': '🤖 IA vs IA',
                'action': 'select_level_AA'
            },
            {
                'rect': pygame.Rect(start_x, start_y + spacing * 3, button_width, button_height),
                'text': '⚡ Entraînement Rapide',
                'action': 'train'
            },
            {
                'rect': pygame.Rect(start_x, start_y + spacing * 4, button_width, button_height),
                'text': '📊 Statistiques',
                'action': 'stats'
            },
            {
                'rect': pygame.Rect(start_x, start_y + spacing * 5, button_width, button_height),
                'text': '📜 Historique des Parties',
                'action': 'history'
            },
            {
                'rect': pygame.Rect(start_x, start_y + spacing * 6, button_width, button_height),
                'text': '🧠 Gestion des Modèles',
                'action': 'models'
            },
            {
                'rect': pygame.Rect(start_x, start_y + spacing * 7, button_width, button_height),
                'text': '🏆 Tournoi',
                'action': 'tournament'
            },
            {
                'rect': pygame.Rect(start_x, start_y + spacing * 8, button_width, button_height),
                'text': '🤖 AutoML',
                'action': 'automl'
            },
            {
                'rect': pygame.Rect(start_x, start_y + spacing * 9, button_width, button_height),
                'text': '🧑‍🏫 Mode Coach',
                'action': 'toggle_coach'
            }
        ]
    
    def _create_level_buttons(self):
        """Crée les boutons de sélection du niveau"""
        button_width = 300
        button_height = 50
        start_x = (self.window_size - button_width) // 2
        start_y = 200
        spacing = 70
        
        self.level_buttons = [
            {
                'rect': pygame.Rect(start_x, start_y, button_width, button_height),
                'text': 'Expert (ε=0)',
                'level': 'Expert'
            },
            {
                'rect': pygame.Rect(start_x, start_y + spacing, button_width, button_height),
                'text': 'Intermédiaire (ε=0.2)',
                'level': 'Intermédiaire'
            },
            {
                'rect': pygame.Rect(start_x, start_y + spacing * 2, button_width, button_height),
                'text': 'Débutant (ε=0.5)',
                'level': 'Débutant'
            }
        ]
    
    def run(self):
        """Boucle principale de l'application"""
        running = True
        self.app_logger.log_info("Boucle principale démarrée")
        
        try:
            while running:
                # Gestion des événements
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.app_logger.log_info("Événement QUIT reçu")
                        running = False
                    
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.app_logger.log_click(event.pos[0], event.pos[1], 
                                                 event.button, self.current_view)
                        self._handle_mouse_click(event.pos)
                    
                    elif event.type == pygame.KEYDOWN:
                        key_name = pygame.key.name(event.key)
                        self.app_logger.log_keypress(key_name, self.current_view)
                        
                        # Touche C pour toggle Coach mode en jeu
                        if event.key == pygame.K_c and self.current_view == 'game':
                            self.coach_mode = not self.coach_mode
                            print(f"Mode Coach: {'Activé' if self.coach_mode else 'Désactivé'}")
                        
                        self._handle_key_press(event.key)
                    
                    elif event.type == pygame.MOUSEWHEEL:
                        # Gérer le scroll dans certaines vues
                        if self.current_view == 'tournament':
                            self.tournament_view.handle_scroll(event.y)
                
                # Mise à jour
                if self.current_view == 'game':
                    self.game_view.update()
                
                    # Enregistrer la partie si terminée
                    if self.game_view.is_game_over():
                        result = self.game_view.get_game_result()
                        self.logger.log_game(
                            result['player_x'],
                            result['player_o'],
                            result['winner'],
                            result['num_moves'],
                            result['duration']
                        )
                
                # Affichage
                self._draw()
                
                pygame.display.flip()
                self.clock.tick(60)
        
        except Exception as e:
            self.app_logger.log_crash(e, "Erreur dans la boucle principale")
            raise
        finally:
            self.app_logger.log_shutdown()
            pygame.quit()
            sys.exit()
    
    def _handle_mouse_click(self, pos):
        """Gère les clics de souris"""
        if self.current_view == 'menu':
            self._handle_menu_click(pos)
        elif self.current_view == 'level_select':
            self._handle_level_click(pos)
        elif self.current_view == 'game':
            action = self.game_view.handle_click(pos)
            if action == 'replay':
                self.app_logger.log_info("Rejouer partie depuis overlay")
                self.game_view.reset_game()
            elif action == 'menu':
                self.app_logger.log_navigation('game', 'menu')
                self.current_view = 'menu'
        elif self.current_view == 'history':
            self.history_view.handle_click(pos)
        elif self.current_view == 'models':
            action = self.models_view.handle_click(pos)
            if action == 'load':
                # Rafraîchir la vue du jeu avec le nouvel agent
                model_path = self.models_view.get_selected_model_path()
                if model_path:
                    import os
                    model_name = os.path.basename(model_path)
                    self.game_view.set_agent(self.agent, model_name)
                    self.stats_view.set_agent(self.agent)
        elif self.current_view == 'tournament':
            action = self.tournament_view.handle_click(pos)
            if action == 'back':
                self.current_view = 'menu'
        elif self.current_view == 'automl':
            action = self.automl_view.handle_click(pos)
            if action == 'back':
                self.current_view = 'menu'
    
    def _handle_menu_click(self, pos):
        """Gère les clics sur le menu"""
        for button in self.menu_buttons:
            if button['rect'].collidepoint(pos):
                action = button['action']
                self.app_logger.log_info(f"Bouton menu cliqué", action=action)
                
                if action == 'start_HH':
                    self.app_logger.log_navigation('menu', 'game')
                    self.app_logger.log_game_start('HH', 'Joueur 1', 'Joueur 2')
                    self.game_view.start_game('HH')
                    self.current_view = 'game'
                
                elif action in ['select_level_HA', 'select_level_AA']:
                    self.selected_mode = action.split('_')[-1]
                    self.app_logger.log_navigation('menu', 'level_select')
                    self.current_view = 'level_select'
                
                elif action == 'train':
                    self.app_logger.log_info("Démarrage entraînement rapide")
                    self._quick_training()
                
                elif action == 'stats':
                    self.app_logger.log_navigation('menu', 'stats')
                    self.current_view = 'stats'
                
                elif action == 'history':
                    self.app_logger.log_navigation('menu', 'history')
                    self.history_view.load_games()
                    self.current_view = 'history'
                
                elif action == 'models':
                    self.app_logger.log_navigation('menu', 'models')
                    self.models_view.refresh_models()
                    self.current_view = 'models'
                
                elif action == 'tournament':
                    self.app_logger.log_navigation('menu', 'tournament')
                    self.tournament_view.load_models()
                    self.current_view = 'tournament'
                
                elif action == 'automl':
                    self.app_logger.log_navigation('menu', 'automl')
                    self.current_view = 'automl'
                
                elif action == 'toggle_coach':
                    self.coach_mode = not self.coach_mode
                    msg = f"Mode Coach {'activé ✅' if self.coach_mode else 'désactivé ❌'}"
                    print(msg)
                    self.app_logger.log_info(msg)
    
    def _handle_level_click(self, pos):
        """Gère les clics sur la sélection de niveau"""
        for button in self.level_buttons:
            if button['rect'].collidepoint(pos):
                level = button['level']
                player1 = 'Humain' if self.selected_mode == 'HA' else 'Agent'
                player2 = 'Agent' if self.selected_mode == 'HA' else 'Agent'
                self.app_logger.log_info(f"Niveau sélectionné", mode=self.selected_mode, level=level)
                self.app_logger.log_navigation('level_select', 'game')
                self.app_logger.log_game_start(self.selected_mode, player1, player2)
                self.game_view.start_game(self.selected_mode, level)
                self.current_view = 'game'
    
    def _handle_key_press(self, key):
        """Gère les touches du clavier"""
        if key == pygame.K_ESCAPE:
            if self.current_view != 'menu':
                self.app_logger.log_navigation(self.current_view, 'menu')
                self.current_view = 'menu'
        
        elif key == pygame.K_SPACE:
            if self.current_view == 'game' and self.game_view.is_game_over():
                self.app_logger.log_info("Reset partie avec ESPACE")
                self.game_view.reset_game()
        
        elif key == pygame.K_d:
            if self.current_view == 'game':
                self.game_view.toggle_debug()
                status = "activé" if self.game_view.debug_mode else "désactivé"
                self.app_logger.log_info(f"Mode debug {status}")
    
    def _draw(self):
        """Dessine l'interface selon la vue actuelle"""
        if self.current_view == 'menu':
            self._draw_menu()
        elif self.current_view == 'level_select':
            self._draw_level_select()
        elif self.current_view == 'game':
            self.game_view.draw()
            # Afficher le mode Coach si activé
            if self.coach_mode:
                self._draw_coach_hints()
        elif self.current_view == 'stats':
            self.stats_view.draw()
        elif self.current_view == 'history':
            self.history_view.draw()
        elif self.current_view == 'models':
            self.models_view.draw()
        elif self.current_view == 'tournament':
            self.tournament_view.draw()
        elif self.current_view == 'automl':
            self.automl_view.draw()
    
    def _draw_menu(self):
        """Dessine le menu principal"""
        self.screen.fill(self.assets.colors.BG_COLOR)
        
        # Titre
        self.assets.draw_text(
            self.screen,
            "MORPION - Q-LEARNING",
            (self.window_size // 2, 70),
            font_size='large',
            centered=True
        )
        
        # Info agent
        stats = self.agent.get_stats()
        info_text = f"États: {stats['total_states']} | Epsilon: {stats['epsilon']:.4f}"
        self.assets.draw_text(
            self.screen,
            info_text,
            (self.window_size // 2, 110),
            font_size='tiny',
            centered=True
        )
        
        # Boutons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.menu_buttons:
            hovered = button['rect'].collidepoint(mouse_pos)
            self.assets.draw_button(
                self.screen,
                button['rect'],
                button['text'],
                hovered
            )
    
    def _draw_level_select(self):
        """Dessine la sélection du niveau"""
        self.screen.fill(self.assets.colors.BG_COLOR)
        
        # Titre
        self.assets.draw_text(
            self.screen,
            "CHOISIR LE NIVEAU DE L'IA",
            (self.window_size // 2, 100),
            font_size='large',
            centered=True
        )
        
        # Boutons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.level_buttons:
            hovered = button['rect'].collidepoint(mouse_pos)
            self.assets.draw_button(
                self.screen,
                button['rect'],
                button['text'],
                hovered
            )
        
        # Instructions
        self.assets.draw_text(
            self.screen,
            "ECHAP: Retour",
            (self.window_size // 2, self.window_size - 30),
            font_size='small',
            centered=True
        )
    
    def _quick_training(self):
        """Lance un entraînement rapide"""
        # Écran de configuration des hyperparamètres
        config = self._get_training_config()
        
        if config is None:
            self.app_logger.log_info("Entraînement annulé")
            return
        
        # Appliquer les hyperparamètres à l'agent
        self.agent.alpha = config['alpha']
        self.agent.gamma = config['gamma']
        self.agent.epsilon = config['epsilon']
        self.agent.epsilon_start = config['epsilon']
        self.agent.epsilon_min = config['epsilon_min']
        self.agent.epsilon_decay = config['epsilon_decay']
        
        num_episodes = config['num_episodes']
        
        # Logger le début avec config complète
        self.app_logger.log_training_start(num_episodes, config)
        
        # Écran d'entraînement
        self.screen.fill(self.assets.colors.BG_COLOR)
        self.assets.draw_text(
            self.screen,
            "ENTRAÎNEMENT EN COURS...",
            (self.window_size // 2, self.window_size // 2),
            font_size='large',
            centered=True
        )
        pygame.display.flip()
        
        # Lancer l'entraînement
        print(f"\n{'='*70}")
        print(f"Entraînement: {num_episodes} épisodes")
        print(f"{'='*70}\n")
        
        import time
        start_time = time.time()
        self.trainer.reset_stats()
        train_stats = self.trainer.train(num_episodes, verbose=True)
        duration = time.time() - start_time
        
        # Logger la fin
        final_stats = {
            'states': self.agent.get_stats()['total_states'],
            'epsilon': self.agent.epsilon,
            'win_rate': train_stats.get('win_rate', 0)
        }
        self.app_logger.log_training_end(num_episodes, duration, final_stats)
        
        # Évaluation
        eval_stats = self.trainer.evaluate(100, verbose=True)
        
        # Rafraîchir la liste des modèles si la vue existe
        if hasattr(self, 'models_view'):
            self.models_view.refresh_models()
        
        # Afficher les résultats
        self._show_training_results(train_stats, eval_stats)
    
    def _get_training_config(self) -> dict:
        """Interface de configuration des hyperparamètres"""
        # Valeurs par défaut
        config = {
            'num_episodes': 10000,
            'alpha': 0.2,
            'gamma': 0.99,
            'epsilon': 1.0,
            'epsilon_min': 0.01,
            'epsilon_decay': 0.9995
        }
        
        param_names = ['num_episodes', 'alpha', 'gamma', 'epsilon', 'epsilon_min', 'epsilon_decay']
        param_labels = [
            'Épisodes',
            'Alpha (α)',
            'Gamma (γ)',
            'Epsilon initial (ε)',
            'Epsilon min',
            'Epsilon decay'
        ]
        param_ranges = [
            (100, 100000),    # num_episodes
            (0.01, 1.0),      # alpha
            (0.5, 1.0),       # gamma
            (0.1, 1.0),       # epsilon
            (0.001, 0.1),     # epsilon_min
            (0.99, 0.9999)    # epsilon_decay
        ]
        
        current_param = 0
        input_text = str(config[param_names[current_param]])
        error_message = ""
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Valider le paramètre actuel
                        try:
                            if param_names[current_param] == 'num_episodes':
                                value = int(input_text)
                            else:
                                value = float(input_text)
                            
                            # Vérifier les limites
                            min_val, max_val = param_ranges[current_param]
                            if min_val <= value <= max_val:
                                config[param_names[current_param]] = value
                                current_param += 1
                                error_message = ""  # Réinitialiser le message d'erreur
                                
                                if current_param >= len(param_names):
                                    # Tous les paramètres validés, afficher confirmation
                                    self.screen.fill(self.assets.colors.BG_COLOR)
                                    self.assets.draw_text(
                                        self.screen,
                                        "✓ CONFIGURATION VALIDÉE",
                                        (self.window_size // 2, self.window_size // 2),
                                        font_size='large',
                                        color=self.assets.colors.SUCCESS_COLOR,
                                        centered=True
                                    )
                                    pygame.display.flip()
                                    pygame.time.wait(500)  # Pause de 500ms
                                    return config
                                
                                input_text = str(config[param_names[current_param]])
                            else:
                                error_message = f"❌ Valeur hors limites [{min_val} - {max_val}]"
                        except ValueError:
                            error_message = "❌ Valeur invalide"
                    
                    elif event.key == pygame.K_ESCAPE:
                        return None
                    
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    
                    elif event.key == pygame.K_UP and current_param > 0:
                        # Paramètre précédent
                        current_param -= 1
                        input_text = str(config[param_names[current_param]])
                    
                    elif event.unicode in '0123456789.':
                        input_text += event.unicode
            
            # Dessiner
            self.screen.fill(self.assets.colors.BG_COLOR)
            
            self.assets.draw_text(
                self.screen,
                "CONFIGURATION ENTRAÎNEMENT",
                (self.window_size // 2, 40),
                font_size='large',
                centered=True
            )
            
            # Afficher tous les paramètres
            start_y = 100
            line_height = 60
            
            for i, (name, label) in enumerate(zip(param_names, param_labels)):
                y = start_y + i * line_height
                
                # Label
                color = self.assets.colors.SUCCESS_COLOR if i == current_param else self.assets.colors.TEXT_COLOR
                self.assets.draw_text(
                    self.screen,
                    f"{label}:",
                    (50, y),
                    font_size='small',
                    color=color,
                    centered=False
                )
                
                # Valeur
                if i == current_param:
                    display_text = input_text
                else:
                    display_text = str(config[name])
                
                # Boîte de valeur
                value_rect = pygame.Rect(350, y - 15, 250, 35)
                if i == current_param:
                    self.assets.draw_button(self.screen, value_rect, display_text, hovered=True)
                else:
                    pygame.draw.rect(self.screen, (60, 60, 60), value_rect, border_radius=5)
                    pygame.draw.rect(self.screen, self.assets.colors.TEXT_COLOR, value_rect, 2, border_radius=5)
                    self.assets.draw_text(
                        self.screen,
                        display_text,
                        (value_rect.centerx, value_rect.centery),
                        font_size='small',
                        centered=True
                    )
                
                # Range
                min_val, max_val = param_ranges[i]
                range_text = f"[{min_val} - {max_val}]"
                self.assets.draw_text(
                    self.screen,
                    range_text,
                    (620, y),
                    font_size='tiny',
                    color=(150, 150, 150),
                    centered=False
                )
            
            # Instructions
            self.assets.draw_text(
                self.screen,
                "ENTRÉE: Valider | ↑: Précédent | ECHAP: Annuler",
                (self.window_size // 2, self.window_size - 60),
                font_size='tiny',
                centered=True
            )
            
            # Message d'erreur si présent
            if error_message:
                self.assets.draw_text(
                    self.screen,
                    error_message,
                    (self.window_size // 2, self.window_size - 30),
                    font_size='small',
                    color=self.assets.colors.ERROR_COLOR,
                    centered=True
                )
            
            pygame.display.flip()
            self.clock.tick(30)
    
    def _get_training_input(self) -> int:
        """Demande le nombre d'épisodes d'entraînement"""
        input_text = ""
        entering = True
        
        while entering:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and input_text:
                        entering = False
                    elif event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isdigit():
                        input_text += event.unicode
            
            # Dessiner
            self.screen.fill(self.assets.colors.BG_COLOR)
            
            self.assets.draw_text(
                self.screen,
                "ENTRAÎNEMENT RAPIDE",
                (self.window_size // 2, 150),
                font_size='large',
                centered=True
            )
            
            self.assets.draw_text(
                self.screen,
                "Nombre d'épisodes? (ex: 5000)",
                (self.window_size // 2, 250),
                font_size='small',
                centered=True
            )
            
            # Zone de saisie
            input_rect = pygame.Rect(
                self.window_size // 2 - 100,
                320,
                200,
                40
            )
            self.assets.draw_button(self.screen, input_rect, input_text or "0")
            
            self.assets.draw_text(
                self.screen,
                "ENTRÉE: Valider | ECHAP: Annuler",
                (self.window_size // 2, 400),
                font_size='tiny',
                centered=True
            )
            
            pygame.display.flip()
            self.clock.tick(30)
        
        try:
            return int(input_text)
        except ValueError:
            return None
    
    def _show_training_results(self, train_stats: Dict, eval_stats: Dict):
        """Affiche les résultats de l'entraînement"""
        waiting = True
        
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_ESCAPE, pygame.K_SPACE]:
                        waiting = False
            
            self.screen.fill(self.assets.colors.BG_COLOR)
            
            self.assets.draw_text(
                self.screen,
                "ENTRAÎNEMENT TERMINÉ",
                (self.window_size // 2, 50),
                font_size='large',
                centered=True
            )
            
            y = 120
            line_height = 30
            
            results = [
                f"Épisodes: {train_stats['num_episodes']}",
                f"Durée: {train_stats['duration']:.1f}s",
                f"Vitesse: {train_stats['speed']:.0f} ép/s",
                f"",
                f"Entraînement:",
                f"  Victoires: {train_stats['win_rate']:.1f}%",
                f"  États appris: {train_stats['states_learned']}",
                f"",
                f"Évaluation (100 parties):",
                f"  Victoires: {eval_stats['win_rate']:.1f}%",
                f"  Nuls: {eval_stats['draw_rate']:.1f}%"
            ]
            
            for line in results:
                if line:
                    self.assets.draw_text(
                        self.screen,
                        line,
                        (self.window_size // 2, y),
                        font_size='small',
                        centered=True
                    )
                y += line_height
            
            self.assets.draw_text(
                self.screen,
                "ESPACE/ECHAP: Continuer",
                (self.window_size // 2, self.window_size - 30),
                font_size='small',
                centered=True
            )
            
            pygame.display.flip()
            self.clock.tick(30)
    
    def _draw_coach_hints(self):
        """Dessine les hints du Coach IA"""
        try:
            from rl_logic.coach import AICoach
            import numpy as np
            
            # Créer le coach si nécessaire
            if not hasattr(self, 'coach'):
                self.coach = AICoach(self.agent, self.env)
            
            # Obtenir l'état actuel du jeu
            if not hasattr(self.game_view, 'get_current_state'):
                print("⚠️ game_view n'a pas get_current_state")
                return
            
            state_tuple, board = self.game_view.get_current_state()
            legal_actions = self.env.legal_actions(state_tuple)
            
            if not legal_actions or self.game_view.is_game_over():
                return
            
            # Obtenir le meilleur coup et la confiance
            best_action, best_q, confidence = self.coach.get_best_action_with_confidence(state_tuple, legal_actions)
            
            if best_action is None:
                return
            
            # Panel des hints - FOND SEMI-TRANSPARENT SOMBRE
            panel_rect = pygame.Rect(10, 450, 250, 200)
            # Créer surface semi-transparente
            panel_surface = pygame.Surface((250, 200))
            panel_surface.fill((20, 20, 20))
            panel_surface.set_alpha(230)
            self.screen.blit(panel_surface, (10, 450))
            
            # Bordure colorée
            pygame.draw.rect(self.screen, (255, 200, 0), panel_rect, 3)
            
            # Titre - GROS ET VISIBLE
            title_font = pygame.font.Font(None, 32)
            title_surface = title_font.render("COACH IA", True, (255, 200, 0))
            title_rect = title_surface.get_rect(center=(135, 470))
            self.screen.blit(title_surface, title_rect)
            
            # Meilleur coup - EN VERT CLAIR
            row, col = best_action // 3, best_action % 3
            move_font = pygame.font.Font(None, 28)
            move_text = f"Coup: ({row}, {col})"
            move_surface = move_font.render(move_text, True, (0, 255, 100))
            self.screen.blit(move_surface, (20, 500))
            
            # Q-value - EN BLANC
            q_font = pygame.font.Font(None, 24)
            q_text = f"Q-value: {best_q:.3f}"
            q_surface = q_font.render(q_text, True, (255, 255, 255))
            self.screen.blit(q_surface, (20, 530))
            
            # Confiance - EN CYAN
            conf_short = confidence[:18] if len(confidence) > 18 else confidence
            conf_font = pygame.font.Font(None, 22)
            conf_text = f"{conf_short}"
            conf_surface = conf_font.render(conf_text, True, (100, 200, 255))
            self.screen.blit(conf_surface, (20, 555))
            
            # Explication - EN JAUNE
            explanation = self.coach.explain_action(state_tuple, best_action, board)
            exp_font = pygame.font.Font(None, 20)
            parts = explanation.split('|')[:2]
            y = 580
            for part in parts:
                part = part.strip()
                if len(part) > 24:
                    part = part[:21] + "..."
                exp_surface = exp_font.render(part, True, (255, 255, 100))
                self.screen.blit(exp_surface, (15, y))
                y += 22
            
            # Indicateur visuel sur le plateau (cercle)
            if hasattr(self.game_view, 'board_offset'):
                cell_size = 150
                offset = self.game_view.board_offset
                highlight_x = offset + col * cell_size + cell_size // 2
                highlight_y = offset + row * cell_size + cell_size // 2
                
                pygame.draw.circle(
                    self.screen,
                    self.assets.colors.ACCENT_COLOR,
                    (highlight_x, highlight_y),
                    70,
                    4
                )
        
        except Exception as e:
            # Afficher l'erreur dans le terminal pour debug
            print(f"❌ Erreur Mode Coach: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Point d'entrée principal"""
    app = GameGUI()
    app.run()


if __name__ == "__main__":
    main()
