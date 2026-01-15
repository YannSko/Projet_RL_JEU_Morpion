"""
Vue Sélection de Modèles
Permet de sélectionner, charger et gérer les modèles Q-Learning.
"""

import pygame
import os
from typing import List, Dict, Optional
from datetime import datetime
from .assets import Assets


class ModelsView:
    """Vue de gestion des modèles"""
    
    def __init__(self, screen: pygame.Surface, assets: Assets, model_manager, agent):
        """
        Initialise la vue des modèles.
        
        Args:
            screen: Surface Pygame principale
            assets: Gestionnaire d'assets
            model_manager: ModelManager pour gérer les modèles
            agent: Agent Q-Learning actuel
        """
        self.screen = screen
        self.assets = assets
        self.model_manager = model_manager
        self.agent = agent
        
        # État
        self.models = []
        self.selected_model = None
        self.current_model_path = None
        
        # Pagination
        self.page = 0
        self.items_per_page = 8  # Augmenté car les entrées sont plus compactes
        
        # Boutons
        self._create_buttons()
        
        # Charger la liste des modèles
        self.refresh_models()
    
    def _create_buttons(self):
        """Crée les boutons d'action"""
        button_width = 120
        button_height = 40
        spacing = 12
        y = self.assets.window_size - 60
        
        # Centrer les boutons (maintenant 5 boutons)
        total_width = button_width * 5 + spacing * 4
        start_x = (self.assets.window_size - total_width) // 2
        
        self.buttons = {
            'prev': pygame.Rect(start_x, y, button_width, button_height),
            'load': pygame.Rect(start_x + (button_width + spacing), y, button_width, button_height),
            'best': pygame.Rect(start_x + (button_width + spacing) * 2, y, button_width, button_height),
            'refresh': pygame.Rect(start_x + (button_width + spacing) * 3, y, button_width, button_height),
            'next': pygame.Rect(start_x + (button_width + spacing) * 4, y, button_width, button_height)
        }
    
    def refresh_models(self):
        """Actualise la liste des modèles disponibles"""
        self.models = self.model_manager.list_models()
        
        # Trier par timestamp (plus récent en premier)
        self.models.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Déterminer le modèle actuellement chargé
        if os.path.exists(str(self.model_manager.default_model)):
            self.current_model_path = str(self.model_manager.default_model)
        else:
            self.current_model_path = None
    
    def handle_click(self, pos: tuple) -> Optional[str]:
        """
        Gère les clics sur les boutons et les modèles.
        
        Args:
            pos: Position du clic (x, y)
        
        Returns:
            Action effectuée ou None
        """
        # Boutons de navigation
        if self.buttons['prev'].collidepoint(pos):
            if self.page > 0:
                self.page -= 1
            return 'navigate'
        
        elif self.buttons['next'].collidepoint(pos):
            max_page = max(0, (len(self.models) - 1) // self.items_per_page)
            if self.page < max_page:
                self.page += 1
            return 'navigate'
        
        elif self.buttons['refresh'].collidepoint(pos):
            self.refresh_models()
            return 'refresh'
        
        elif self.buttons['load'].collidepoint(pos):
            if self.selected_model is not None:
                self._load_selected_model()
                return 'load'
        
        elif self.buttons['best'].collidepoint(pos):
            self._load_best_model()
            return 'load_best'
        
        # Clic sur un modèle
        model_idx = self._get_model_at_pos(pos)
        if model_idx is not None:
            self.selected_model = model_idx
            return 'select'
        
        return None
    
    def _get_model_at_pos(self, pos: tuple) -> Optional[int]:
        """
        Retourne l'index du modèle cliqué.
        
        Args:
            pos: Position du clic (x, y)
        
        Returns:
            Index du modèle ou None
        """
        start_y = 130
        line_height = 60
        
        start_idx = self.page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.models))
        
        for i in range(start_idx, end_idx):
            y = start_y + (i - start_idx) * line_height
            rect = pygame.Rect(10, y - 5, 480, 55)
            
            if rect.collidepoint(pos):
                return i
        
        return None
    
    def _load_selected_model(self):
        """Charge le modèle sélectionné"""
        if self.selected_model is None or self.selected_model >= len(self.models):
            return
        
        model = self.models[self.selected_model]
        success = self.model_manager.load_model(self.agent, model['path'])
        
        if success:
            self.current_model_path = model['path']
            print(f"✓ Modèle chargé: {model['name']}")
        else:
            print(f"✗ Échec du chargement: {model['name']}")
    
    def _load_best_model(self):
        """Charge automatiquement le meilleur modèle selon le score composite"""
        print("\n" + "="*70)
        print("🏆 CHARGEMENT DU MEILLEUR MODÈLE")
        print("="*70)
        
        success = self.model_manager.load_best_model(self.agent, metric='composite_score')
        
        if success:
            # Rafraîchir et trouver le modèle chargé pour le sélectionner
            self.refresh_models()
            
            # Trouver l'index du meilleur modèle dans la liste
            best_path = self.model_manager.get_best_model('composite_score')
            for i, model in enumerate(self.models):
                if model['path'] == best_path:
                    self.selected_model = i
                    self.page = i // self.items_per_page
                    break
            
            self.current_model_path = best_path
            print("✅ Meilleur modèle chargé avec succès !")
            print("="*70 + "\n")
        else:
            print("❌ Échec du chargement du meilleur modèle")
            print("="*70 + "\n")
    
    def draw(self):
        """Dessine la vue des modèles"""
        self.screen.fill(self.assets.colors.BG_COLOR)
        
        # Titre
        self.assets.draw_text(
            self.screen,
            "🧠 GESTION DES MODÈLES",
            (self.assets.window_size // 2, 30),
            font_size='medium',
            color=self.assets.colors.TEXT_COLOR,
            centered=True
        )
        
        # Info modèle actuel
        current_text = "Modèle actuel: "
        if self.current_model_path:
            current_text += os.path.basename(self.current_model_path)
            color = self.assets.colors.SUCCESS_COLOR
        else:
            current_text += "Aucun"
            color = self.assets.colors.WARNING_COLOR
        
        self.assets.draw_text(
            self.screen,
            current_text,
            (self.assets.window_size // 2, 70),
            font_size='small',
            color=color,
            centered=True
        )
        
        # Stats de l'agent actuel
        stats = self.agent.get_stats()
        stats_text = f"États appris: {stats['total_states']} | Epsilon: {stats['epsilon']:.4f}"
        self.assets.draw_text(
            self.screen,
            stats_text,
            (self.assets.window_size // 2, 95),
            font_size='tiny',
            centered=True
        )
        
        # Ligne de séparation verticale
        separator_x = 500
        pygame.draw.line(
            self.screen,
            self.assets.colors.TEXT_COLOR,
            (separator_x, 120),
            (separator_x, self.assets.window_size - 60),
            2
        )
        
        # Liste des modèles (côté gauche)
        if len(self.models) > 0:
            self._draw_models_list()
        else:
            self.assets.draw_text(
                self.screen,
                "Aucun modèle disponible",
                (250, 250),
                font_size='small',
                color=self.assets.colors.WARNING_COLOR,
                centered=True
            )
        
        # Panneau de détails (côté droit)
        if self.selected_model is not None and self.selected_model < len(self.models):
            self._draw_model_details()
        else:
            self.assets.draw_text(
                self.screen,
                "Sélectionnez un modèle\npour voir les détails",
                (650, 300),
                font_size='small',
                color=(150, 150, 150),
                centered=True
            )
        
        # Boutons
        self._draw_buttons()
        
        # Instructions
        self.assets.draw_text(
            self.screen,
            "Cliquez sur un modèle pour les détails | ECHAP: Menu",
            (self.assets.window_size // 2, self.assets.window_size - 20),
            font_size='tiny',
            centered=True
        )
    
    def _draw_models_list(self):
        """Dessine la liste des modèles (côté gauche)"""
        start_y = 130
        line_height = 60
        
        start_idx = self.page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.models))
        
        for i in range(start_idx, end_idx):
            model = self.models[i]
            y = start_y + (i - start_idx) * line_height
            self._draw_model_entry(model, y, i)
    
    def _draw_model_entry(self, model: Dict, y: int, idx: int):
        """
        Dessine une entrée de modèle dans la liste.
        
        Args:
            model: Dictionnaire avec les infos du modèle
            y: Position Y
            idx: Index du modèle
        """
        x_left = 20
        x_right = 480
        
        # Fond (sélection ou alternance)
        bg_rect = pygame.Rect(10, y - 5, 480, 55)
        
        if idx == self.selected_model:
            # Modèle sélectionné
            pygame.draw.rect(self.screen, (70, 100, 150), bg_rect)
            pygame.draw.rect(self.screen, self.assets.colors.SUCCESS_COLOR, bg_rect, 2)
        elif model['path'] == self.current_model_path:
            # Modèle actuel
            pygame.draw.rect(self.screen, (60, 80, 60), bg_rect)
        elif idx % 2 == 0:
            # Alternance
            pygame.draw.rect(self.screen, (50, 50, 50), bg_rect)
        
        # Nom du modèle
        name = model['name']
        if len(name) > 25:
            name = name[:22] + "..."
        
        # Indicateur sélection
        if idx == self.selected_model:
            prefix = "► "
        elif model['path'] == self.current_model_path:
            prefix = "● "
        else:
            prefix = ""
        
        self.assets.draw_text(
            self.screen,
            prefix + name,
            (x_left, y),
            font_size='tiny',
            centered=False
        )
        
        # Performance simplifiée
        metadata = model.get('metadata', {})
        if 'final_win_rate' in metadata:
            perf_text = f"{metadata['final_win_rate']:.0f}%"
            color = self.assets.colors.SUCCESS_COLOR if metadata['final_win_rate'] > 80 else self.assets.colors.WARNING_COLOR
        else:
            perf_text = "N/A"
            color = (150, 150, 150)
        
        self.assets.draw_text(
            self.screen,
            perf_text,
            (x_right - 30, y),
            font_size='tiny',
            color=color,
            centered=False
        )
        
        # Date (ligne suivante)
        try:
            timestamp = datetime.fromisoformat(model['timestamp'])
            date_text = timestamp.strftime("%d/%m %H:%M")
        except:
            date_text = model['timestamp'][:10] if len(model['timestamp']) > 10 else model['timestamp']
        
        self.assets.draw_text(
            self.screen,
            date_text,
            (x_left, y + 25),
            font_size='tiny',
            color=(150, 150, 150),
            centered=False
        )
        
        # États
        states_text = f"{model['states']} états"
        self.assets.draw_text(
            self.screen,
            states_text,
            (x_right - 80, y + 25),
            font_size='tiny',
            color=(150, 150, 150),
            centered=False
        )
    
    def _draw_model_details(self):
        """Affiche les détails complets du modèle sélectionné (côté droit)"""
        model = self.models[self.selected_model]
        metadata = model.get('metadata', {})
        
        x_start = 515
        y = 125
        line_height = 22  # Réduit pour avoir plus d'espace
        
        # Titre
        self.assets.draw_text(
            self.screen,
            "📊 DÉTAILS",
            (630, y),
            font_size='small',
            color=self.assets.colors.SUCCESS_COLOR,
            centered=True
        )
        y += 30
        
        # Calculer les métriques avancées
        metrics = self._calculate_model_metrics(model)
        
        # Afficher le score composite en premier (si disponible)
        if metrics and 'composite_score' in metrics:
            score_color = self._get_score_color(metrics['composite_score'])
            self.assets.draw_text(
                self.screen,
                f"🏆 Score: {metrics['composite_score']:.1f}/100",
                (630, y),
                font_size='tiny',
                color=score_color,
                centered=True
            )
            y += line_height
        
        # Nom complet (raccourci si nécessaire)
        name = model['name']
        if len(name) > 18:
            name = name[:15] + "..."
        self.assets.draw_text(
            self.screen,
            name,
            (x_start, y),
            font_size='tiny',
            centered=False
        )
        y += line_height
        
        # Date (format court)
        try:
            timestamp = datetime.fromisoformat(model['timestamp'])
            date_text = timestamp.strftime("%d/%m %H:%M")
        except:
            date_text = model['timestamp'][:10] if len(model['timestamp']) > 10 else model['timestamp']
        
        self.assets.draw_text(
            self.screen,
            date_text,
            (x_start, y),
            font_size='tiny',
            color=(150, 150, 150),
            centered=False
        )
        y += line_height + 5
        
        # Section Performance
        self.assets.draw_text(
            self.screen,
            "─ PERFORMANCE ─",
            (630, y),
            font_size='tiny',
            color=self.assets.colors.WARNING_COLOR,
            centered=True
        )
        y += line_height
        
        if 'total_episodes' in metadata:
            self.assets.draw_text(
                self.screen,
                f"Épisodes: {metadata['total_episodes']:,}",
                (x_start, y),
                font_size='tiny',
                centered=False
            )
            y += line_height
        
        if 'final_win_rate' in metadata:
            win_rate = metadata['final_win_rate']
            color = self.assets.colors.SUCCESS_COLOR if win_rate > 80 else self.assets.colors.WARNING_COLOR
            self.assets.draw_text(
                self.screen,
                f"Win: {win_rate:.1f}%",
                (x_start, y),
                font_size='tiny',
                color=color,
                centered=False
            )
            y += line_height
        
        if 'final_draw_rate' in metadata:
            self.assets.draw_text(
                self.screen,
                f"Draw: {metadata['final_draw_rate']:.1f}%",
                (x_start, y),
                font_size='tiny',
                centered=False
            )
            y += line_height
        
        if 'final_loss_rate' in metadata:
            self.assets.draw_text(
                self.screen,
                f"Loss: {metadata['final_loss_rate']:.1f}%",
                (x_start, y),
                font_size='tiny',
                centered=False
            )
            y += line_height + 5
        
        # Section Hyperparamètres
        self.assets.draw_text(
            self.screen,
            "─ HYPERPARAMS ─",
            (630, y),
            font_size='tiny',
            color=self.assets.colors.WARNING_COLOR,
            centered=True
        )
        y += line_height
        
        hyperparams = metadata.get('hyperparameters', {})
        if hyperparams and any(hyperparams.values()):
            # Afficher les hyperparamètres depuis les métadonnées
            if 'alpha' in hyperparams:
                self.assets.draw_text(
                    self.screen,
                    f"α: {hyperparams['alpha']}",
                    (x_start, y),
                    font_size='tiny',
                    centered=False
                )
                y += line_height
            
            if 'gamma' in hyperparams:
                self.assets.draw_text(
                    self.screen,
                    f"γ: {hyperparams['gamma']}",
                    (x_start, y),
                    font_size='tiny',
                    centered=False
                )
                y += line_height
            
            if 'epsilon_final' in hyperparams:
                self.assets.draw_text(
                    self.screen,
                    f"ε final: {hyperparams['epsilon_final']:.4f}",
                    (x_start, y),
                    font_size='tiny',
                    centered=False
                )
                y += line_height
            
            if 'epsilon_decay' in hyperparams:
                self.assets.draw_text(
                    self.screen,
                    f"ε decay: {hyperparams['epsilon_decay']}",
                    (x_start, y),
                    font_size='tiny',
                    centered=False
                )
                y += line_height + 5
        else:
            # Modèle ancien sans métadonnées - afficher les valeurs du modèle chargé
            self.assets.draw_text(
                self.screen,
                "Ancien modèle - Valeurs actuelles:",
                (x_start, y),
                font_size='small',
                color=self.assets.colors.WARNING_COLOR,
                centered=False
            )
            y += line_height
            
            # Lire les valeurs de l'agent si c'est le modèle chargé
            if model['path'] == self.current_model_path:
                self.assets.draw_text(
                    self.screen,
                    f"Alpha (α): {self.agent.alpha}",
                    (x_start, y),
                    font_size='small',
                    centered=False
                )
                y += line_height
                
                self.assets.draw_text(
                    self.screen,
                    f"Gamma (γ): {self.agent.gamma}",
                    (x_start, y),
                    font_size='small',
                    centered=False
                )
                y += line_height
                
                self.assets.draw_text(
                    self.screen,
                    f"Epsilon actuel: {self.agent.epsilon:.6f}",
                    (x_start, y),
                    font_size='small',
                    centered=False
                )
                y += line_height
                
                self.assets.draw_text(
                    self.screen,
                    f"Epsilon min: {self.agent.epsilon_min}",
                    (x_start, y),
                    font_size='small',
                    centered=False
                )
                y += line_height
                
                self.assets.draw_text(
                    self.screen,
                    f"Epsilon decay: {self.agent.epsilon_decay}",
                    (x_start, y),
                    font_size='small',
                    centered=False
                )
                y += line_height
            else:
                self.assets.draw_text(
                    self.screen,
                    "Chargez le modèle pour voir",
                    (x_start, y),
                    font_size='small',
                    color=(150, 150, 150),
                    centered=False
                )
                y += line_height
                self.assets.draw_text(
                    self.screen,
                    "ses hyperparamètres",
                    (x_start, y),
                    font_size='small',
                    color=(150, 150, 150),
                    centered=False
                )
                y += line_height
            
            y += 10
        
        # Section Métriques
        self.assets.draw_text(
            self.screen,
            "─ MÉTRIQUES ─",
            (630, y),
            font_size='tiny',
            color=self.assets.colors.WARNING_COLOR,
            centered=True
        )
        y += line_height
        
        # Afficher les métriques avancées si disponibles
        if metrics and 'performance_score' in metrics:
            perf_score = metrics.get('performance_score', 0)
            eff_score = metrics.get('efficiency_score', 0)
            rob_score = metrics.get('robustness_score', 0)
            
            # Performance
            self.assets.draw_text(
                self.screen,
                f"Perf: {perf_score:.1f}",
                (x_start, y),
                font_size='tiny',
                color=self._get_score_color(perf_score),
                centered=False
            )
            y += line_height
            
            # Efficacité
            eff_color = self.assets.colors.SUCCESS_COLOR if eff_score > 25 else self.assets.colors.WARNING_COLOR
            self.assets.draw_text(
                self.screen,
                f"Efficacité: {eff_score:.1f}",
                (x_start, y),
                font_size='tiny',
                color=eff_color,
                centered=False
            )
            y += line_height
            
            # Robustesse
            rob_color = self.assets.colors.SUCCESS_COLOR if rob_score > 1.5 else self.assets.colors.WARNING_COLOR
            self.assets.draw_text(
                self.screen,
                f"Robustesse: {rob_score:.2f}",
                (x_start, y),
                font_size='tiny',
                color=rob_color,
                centered=False
            )
            y += line_height
        else:
            # Ancien modèle sans métriques complètes
            self.assets.draw_text(
                self.screen,
                "Métriques non disponibles",
                (x_start, y),
                font_size='tiny',
                color=(150, 150, 150),
                centered=False
            )
            y += line_height
            self.assets.draw_text(
                self.screen,
                "(modèle ancien)",
                (x_start, y),
                font_size='tiny',
                color=(150, 150, 150),
                centered=False
            )
            y += line_height
        
        performance = metadata.get('performance', {})
        if performance:
            if 'states_learned' in performance:
                self.assets.draw_text(
                    self.screen,
                    f"États: {performance['states_learned']}",
                    (x_start, y),
                    font_size='tiny',
                    centered=False
                )
                y += line_height
            
            if 'avg_reward' in performance:
                self.assets.draw_text(
                    self.screen,
                    f"Reward: {performance['avg_reward']:.3f}",
                    (x_start, y),
                    font_size='tiny',
                    centered=False
                )
                y += line_height
        
        if 'training_time' in metadata and metadata['training_time'] > 0:
            minutes = int(metadata['training_time'] // 60)
            seconds = int(metadata['training_time'] % 60)
            self.assets.draw_text(
                self.screen,
                f"Temps: {minutes}m{seconds}s",
                (x_start, y),
                font_size='tiny',
                centered=False
            )
    
    def _draw_buttons(self):
        """Dessine les boutons d'action"""
        # Bouton Précédent
        self.assets.draw_button(
            self.screen,
            self.buttons['prev'],
            "◀ Préc.",
            enabled=(self.page > 0)
        )
        
        # Bouton Charger
        self.assets.draw_button(
            self.screen,
            self.buttons['load'],
            "📥 Charger",
            enabled=(self.selected_model is not None)
        )
        
        # Bouton Meilleur Modèle
        self.assets.draw_button(
            self.screen,
            self.buttons['best'],
            "🏆 Meilleur",
            enabled=(len(self.models) > 0)
        )
        
        # Bouton Actualiser
        self.assets.draw_button(
            self.screen,
            self.buttons['refresh'],
            "🔄 Refresh"
        )
        
        # Bouton Suivant
        max_page = max(0, (len(self.models) - 1) // self.items_per_page)
        self.assets.draw_button(
            self.screen,
            self.buttons['next'],
            "Suiv. ▶",
            enabled=(self.page < max_page)
        )
        
        # Numéro de page
        if len(self.models) > 0:
            max_page = max(0, (len(self.models) - 1) // self.items_per_page)
            page_text = f"Page {self.page + 1}/{max_page + 1} | Total: {len(self.models)} modèles"
            self.assets.draw_text(
                self.screen,
                page_text,
                (self.assets.window_size // 2, self.assets.window_size - 90),
                font_size='tiny',
                centered=True
            )
    
    def get_selected_model_path(self) -> Optional[str]:
        """Retourne le chemin du modèle sélectionné"""
        if self.selected_model is not None and self.selected_model < len(self.models):
            return self.models[self.selected_model]['path']
        return None
    
    def _calculate_model_metrics(self, model: Dict) -> Optional[Dict]:
        """Calcule les métriques avancées pour un modèle"""
        try:
            from rl_logic.metrics import ModelMetrics
            
            # Vérifier qu'on a les données essentielles
            # Chercher dans l'ordre : niveau racine puis dans metadata
            win_rate = model.get('final_win_rate', 0)
            if win_rate == 0:
                # Essayer dans metadata
                metadata = model.get('metadata', {})
                win_rate = metadata.get('final_win_rate', 0)
            
            # Si toujours pas de win_rate, c'est un ancien modèle
            if win_rate == 0:
                return None
            
            # Récupérer toutes les métadonnées
            metadata = model.get('metadata', {})
            
            # Créer une structure fusionnée
            combined_metadata = {
                'final_win_rate': model.get('final_win_rate', metadata.get('final_win_rate', 0)),
                'final_draw_rate': model.get('final_draw_rate', metadata.get('final_draw_rate', 0)),
                'final_loss_rate': model.get('final_loss_rate', metadata.get('final_loss_rate', 0)),
                'total_episodes': model.get('total_episodes', metadata.get('total_episodes', 0)),
            }
            
            # Ajouter les autres données de metadata
            for key, value in metadata.items():
                if key not in combined_metadata:
                    combined_metadata[key] = value
            
            # Structure pour le calcul des métriques
            model_data = {
                'states': model.get('states', 0),
                'epsilon': model.get('epsilon', 1.0),
                'metadata': combined_metadata,
                'timestamp': model.get('timestamp', '')
            }
            
            metrics = ModelMetrics.compute_all_metrics(model_data)
            return metrics
            
        except Exception as e:
            # En cas d'erreur, afficher dans la console pour debug
            print(f"⚠️ Erreur calcul métriques pour {model.get('name', 'N/A')}: {e}")
            return None
    
    def _get_score_color(self, score: float) -> tuple:
        """Retourne une couleur selon le score"""
        if score >= 80:
            return self.assets.colors.SUCCESS_COLOR
        elif score >= 60:
            return self.assets.colors.WARNING_COLOR
        else:
            return self.assets.colors.ERROR_COLOR