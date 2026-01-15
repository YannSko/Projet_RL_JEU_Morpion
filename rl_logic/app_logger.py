"""
Logger d'application pour suivre les événements, clics et erreurs
Enregistre tous les événements de l'application Pygame pour le debugging
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import traceback


class AppLogger:
    """
    Logger d'application pour tracer tous les événements.
    Enregistre: clics, événements clavier, erreurs, crashes, navigation.
    """
    
    def __init__(self, logs_dir: str = "logs", app_name: str = "morpion_rl"):
        """
        Initialise le logger d'application.
        
        Args:
            logs_dir: Répertoire des logs
            app_name: Nom de l'application pour les fichiers de log
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Fichier de log avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.logs_dir / f"app_{timestamp}.log"
        
        # Configuration du logger
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(logging.DEBUG)
        
        # Format détaillé
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler fichier
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Handler console (erreurs uniquement)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Compteurs de statistiques
        self.stats = {
            'clicks': 0,
            'keypress': 0,
            'errors': 0,
            'warnings': 0,
            'info_events': 0
        }
        
        self.log_info("=" * 70)
        self.log_info(f"APPLICATION DÉMARRÉE - {app_name}")
        self.log_info(f"Fichier de log: {self.log_file}")
        self.log_info("=" * 70)
    
    def log_info(self, message: str, **kwargs):
        """Enregistre une information"""
        self.stats['info_events'] += 1
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        if extra_info:
            message = f"{message} | {extra_info}"
        self.logger.info(message)
    
    def log_warning(self, message: str, **kwargs):
        """Enregistre un avertissement"""
        self.stats['warnings'] += 1
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        if extra_info:
            message = f"{message} | {extra_info}"
        self.logger.warning(message)
    
    def log_error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Enregistre une erreur"""
        self.stats['errors'] += 1
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        if extra_info:
            message = f"{message} | {extra_info}"
        
        if error:
            message = f"{message} | Exception: {str(error)}"
            self.logger.error(message)
            self.logger.error(traceback.format_exc())
        else:
            self.logger.error(message)
    
    def log_click(self, x: int, y: int, button: int = 1, view: str = "unknown"):
        """
        Enregistre un clic de souris.
        
        Args:
            x, y: Coordonnées du clic
            button: Bouton de la souris (1=gauche, 2=milieu, 3=droit)
            view: Vue actuelle (menu, game, stats, etc.)
        """
        self.stats['clicks'] += 1
        button_name = {1: "LEFT", 2: "MIDDLE", 3: "RIGHT"}.get(button, f"BUTTON{button}")
        self.log_info(f"CLICK", x=x, y=y, button=button_name, view=view)
    
    def log_keypress(self, key: str, view: str = "unknown"):
        """
        Enregistre une touche pressée.
        
        Args:
            key: Nom de la touche
            view: Vue actuelle
        """
        self.stats['keypress'] += 1
        self.log_info(f"KEYPRESS", key=key, view=view)
    
    def log_navigation(self, from_view: str, to_view: str):
        """Enregistre un changement de vue"""
        self.log_info(f"NAVIGATION", from_view=from_view, to_view=to_view)
    
    def log_game_start(self, mode: str, player1: str, player2: str):
        """Enregistre le début d'une partie"""
        self.log_info(f"GAME_START", mode=mode, player1=player1, player2=player2)
    
    def log_game_move(self, player: str, action: int, row: int, col: int):
        """Enregistre un coup joué"""
        self.log_info(f"GAME_MOVE", player=player, action=action, position=f"({row},{col})")
    
    def log_game_end(self, winner: str, num_moves: int, duration: float):
        """Enregistre la fin d'une partie"""
        self.log_info(f"GAME_END", winner=winner, moves=num_moves, duration_s=f"{duration:.2f}")
    
    def log_training_start(self, num_episodes: int, config: Dict[str, Any]):
        """Enregistre le début d'un entraînement"""
        config_str = ", ".join([f"{k}={v}" for k, v in config.items()])
        self.log_info(f"TRAINING_START", episodes=num_episodes, config=config_str)
    
    def log_training_progress(self, episode: int, total: int, stats: Dict[str, Any]):
        """Enregistre la progression de l'entraînement"""
        stats_str = ", ".join([f"{k}={v}" for k, v in stats.items()])
        self.log_info(f"TRAINING_PROGRESS", episode=f"{episode}/{total}", stats=stats_str)
    
    def log_training_end(self, total_episodes: int, duration: float, final_stats: Dict[str, Any]):
        """Enregistre la fin d'un entraînement"""
        stats_str = ", ".join([f"{k}={v}" for k, v in final_stats.items()])
        self.log_info(f"TRAINING_END", episodes=total_episodes, duration_s=f"{duration:.2f}", stats=stats_str)
    
    def log_model_save(self, filepath: str, states_count: int):
        """Enregistre la sauvegarde d'un modèle"""
        self.log_info(f"MODEL_SAVE", filepath=filepath, states=states_count)
    
    def log_model_load(self, filepath: str, states_count: int):
        """Enregistre le chargement d'un modèle"""
        self.log_info(f"MODEL_LOAD", filepath=filepath, states=states_count)
    
    def log_crash(self, error: Exception, context: str = ""):
        """Enregistre un crash de l'application"""
        self.log_error(f"CRASH - {context}", error=error)
        self.log_info("=" * 70)
        self.log_info("APPLICATION STATS AT CRASH:")
        for key, value in self.stats.items():
            self.log_info(f"  {key}: {value}")
        self.log_info("=" * 70)
    
    def log_shutdown(self):
        """Enregistre la fermeture normale de l'application"""
        self.log_info("=" * 70)
        self.log_info("APPLICATION SHUTDOWN")
        self.log_info("Session statistics:")
        for key, value in self.stats.items():
            self.log_info(f"  {key}: {value}")
        self.log_info("=" * 70)
    
    def get_stats(self) -> Dict[str, int]:
        """Retourne les statistiques de la session"""
        return self.stats.copy()
    
    def get_log_file(self) -> Path:
        """Retourne le chemin du fichier de log"""
        return self.log_file


# Instance globale pour faciliter l'accès
_global_logger: Optional[AppLogger] = None


def get_app_logger() -> AppLogger:
    """Retourne l'instance globale du logger d'application"""
    global _global_logger
    if _global_logger is None:
        _global_logger = AppLogger()
    return _global_logger


def init_app_logger(logs_dir: str = "logs", app_name: str = "morpion_rl") -> AppLogger:
    """
    Initialise le logger d'application global.
    
    Args:
        logs_dir: Répertoire des logs
        app_name: Nom de l'application
    
    Returns:
        Instance du logger
    """
    global _global_logger
    _global_logger = AppLogger(logs_dir, app_name)
    return _global_logger
