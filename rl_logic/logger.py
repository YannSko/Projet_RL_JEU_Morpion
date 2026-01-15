"""
Logger pour l'apprentissage par renforcement
Enregistre l'historique des parties, les courbes d'apprentissage et les statistiques.
"""

import json
import csv
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import numpy as np


class RLLogger:
    """
    Logger pour l'entraînement et l'évaluation d'agents RL.
    Enregistre: historique des parties, courbes de récompenses, statistiques.
    """
    
    def __init__(self, logs_dir: str = "logs"):
        """
        Initialise le logger.
        
        Args:
            logs_dir: Répertoire de sauvegarde des logs
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Fichiers de log
        self.games_file = self.logs_dir / "game_history.json"
        self.training_file = self.logs_dir / "training_stats.csv"
        self.eval_file = self.logs_dir / "evaluation_results.json"
        
        # Historique en mémoire
        self.games_history: List[Dict] = []
        self.training_stats: List[Dict] = []
        self.evaluation_results: List[Dict] = []
        
        # Charger les historiques existants
        self._load_histories()
    
    def log_game(self, player_x: str, player_o: str, winner: Optional[int],
                 num_moves: int, duration: float = 0.0, metadata: Optional[Dict] = None):
        """
        Enregistre une partie jouée.
        
        Args:
            player_x: Nom du joueur X
            player_o: Nom du joueur O
            winner: 1 (X), -1 (O) ou None (nul)
            num_moves: Nombre de coups joués
            duration: Durée de la partie en secondes
            metadata: Métadonnées additionnelles
        """
        game_record = {
            'timestamp': datetime.now().isoformat(),
            'player_x': player_x,
            'player_o': player_o,
            'winner': 'X' if winner == 1 else ('O' if winner == -1 else 'Draw'),
            'num_moves': num_moves,
            'duration': duration,
            'metadata': metadata or {}
        }
        
        self.games_history.append(game_record)
        self._save_games()
    
    def log_training_step(self, episode: int, epsilon: float, win_rate: float,
                         loss_rate: float, draw_rate: float, avg_reward: float = 0.0,
                         avg_moves: float = 0.0, q_table_size: int = 0):
        """
        Enregistre un pas d'entraînement.
        
        Args:
            episode: Numéro de l'épisode
            epsilon: Valeur actuelle d'epsilon
            win_rate: Taux de victoire (%)
            loss_rate: Taux de défaite (%)
            draw_rate: Taux de nul (%)
            avg_reward: Récompense moyenne
            avg_moves: Nombre moyen de coups par partie
            q_table_size: Taille de la Q-table
        """
        stats = {
            'episode': episode,
            'timestamp': datetime.now().isoformat(),
            'epsilon': epsilon,
            'win_rate': win_rate,
            'loss_rate': loss_rate,
            'draw_rate': draw_rate,
            'avg_reward': avg_reward,
            'avg_moves': avg_moves,
            'q_table_size': q_table_size
        }
        
        self.training_stats.append(stats)
        self._save_training_stats()
    
    def log_evaluation(self, num_games: int, wins: int, losses: int, draws: int,
                      agent_config: Dict, metadata: Optional[Dict] = None):
        """
        Enregistre les résultats d'une évaluation.
        
        Args:
            num_games: Nombre de parties jouées
            wins: Nombre de victoires
            losses: Nombre de défaites
            draws: Nombre de nuls
            agent_config: Configuration de l'agent évalué
            metadata: Métadonnées additionnelles
        """
        eval_record = {
            'timestamp': datetime.now().isoformat(),
            'num_games': num_games,
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win_rate': wins / num_games * 100 if num_games > 0 else 0,
            'loss_rate': losses / num_games * 100 if num_games > 0 else 0,
            'draw_rate': draws / num_games * 100 if num_games > 0 else 0,
            'agent_config': agent_config,
            'metadata': metadata or {}
        }
        
        self.evaluation_results.append(eval_record)
        self._save_evaluation()
    
    def get_game_stats(self, player_name: Optional[str] = None,
                      last_n: Optional[int] = None) -> Dict:
        """
        Calcule les statistiques des parties.
        
        Args:
            player_name: Filtrer par joueur (None = toutes les parties)
            last_n: Ne considérer que les N dernières parties
        
        Returns:
            Dictionnaire avec les statistiques
        """
        games = self.games_history[-last_n:] if last_n else self.games_history
        
        if player_name:
            games = [g for g in games 
                    if g['player_x'] == player_name or g['player_o'] == player_name]
        
        if not games:
            return self._empty_stats()
        
        total_games = len(games)
        wins = losses = draws = 0
        total_moves = sum(g['num_moves'] for g in games)
        total_duration = sum(g['duration'] for g in games)
        
        for game in games:
            if player_name:
                player_symbol = 'X' if game['player_x'] == player_name else 'O'
                if game['winner'] == player_symbol:
                    wins += 1
                elif game['winner'] == 'Draw':
                    draws += 1
                else:
                    losses += 1
            else:
                if game['winner'] == 'X':
                    wins += 1
                elif game['winner'] == 'O':
                    losses += 1
                else:
                    draws += 1
        
        return {
            'total_games': total_games,
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win_rate': wins / total_games * 100,
            'loss_rate': losses / total_games * 100,
            'draw_rate': draws / total_games * 100,
            'avg_moves': total_moves / total_games,
            'avg_duration': total_duration / total_games if total_duration > 0 else 0
        }
    
    def get_training_curves(self, window: int = 100) -> Dict:
        """
        Calcule les courbes d'apprentissage (moyennes glissantes).
        
        Args:
            window: Taille de la fenêtre pour la moyenne glissante
        
        Returns:
            Dictionnaire avec les courbes
        """
        if not self.training_stats:
            return {}
        
        # Convertir en nombres (au cas où ce sont des strings du CSV)
        episodes = [int(s['episode']) if isinstance(s['episode'], str) else s['episode'] 
                   for s in self.training_stats]
        win_rates = [float(s['win_rate']) if isinstance(s['win_rate'], str) else s['win_rate'] 
                    for s in self.training_stats]
        epsilons = [float(s['epsilon']) if isinstance(s['epsilon'], str) else s['epsilon'] 
                   for s in self.training_stats]
        q_sizes = [int(s['q_table_size']) if isinstance(s['q_table_size'], (str, float)) else s['q_table_size'] 
                  for s in self.training_stats]
        
        # Moyennes glissantes
        win_rates_smooth = self._moving_average(win_rates, window)
        
        return {
            'episodes': episodes,
            'win_rates': win_rates,
            'win_rates_smooth': win_rates_smooth,
            'epsilons': epsilons,
            'q_table_sizes': q_sizes
        }
    
    def get_recent_games(self, n: int = 10) -> List[Dict]:
        """
        Retourne les N dernières parties.
        
        Args:
            n: Nombre de parties à retourner
        
        Returns:
            Liste des dernières parties
        """
        return self.games_history[-n:] if self.games_history else []
    
    def print_summary(self, last_n_games: Optional[int] = None):
        """
        Affiche un résumé des statistiques.
        
        Args:
            last_n_games: Nombre de parties récentes à considérer
        """
        print("\n" + "=" * 60)
        print("RÉSUMÉ DES STATISTIQUES")
        print("=" * 60)
        
        # Stats des parties
        stats = self.get_game_stats(last_n=last_n_games)
        suffix = f" (dernières {last_n_games})" if last_n_games else ""
        
        print(f"\nParties jouées{suffix}:")
        print(f"  Total: {stats['total_games']}")
        print(f"  Victoires: {stats['wins']} ({stats['win_rate']:.1f}%)")
        print(f"  Défaites: {stats['losses']} ({stats['loss_rate']:.1f}%)")
        print(f"  Nuls: {stats['draws']} ({stats['draw_rate']:.1f}%)")
        print(f"  Moyenne coups/partie: {stats['avg_moves']:.1f}")
        
        # Stats d'entraînement
        if self.training_stats:
            latest = self.training_stats[-1]
            print(f"\nDernier entraînement:")
            print(f"  Épisode: {latest['episode']}")
            print(f"  Epsilon: {latest['epsilon']:.6f}")
            print(f"  Taille Q-table: {latest['q_table_size']}")
            print(f"  Taux victoire: {latest['win_rate']:.1f}%")
        
        # Stats d'évaluation
        if self.evaluation_results:
            latest_eval = self.evaluation_results[-1]
            print(f"\nDernière évaluation:")
            print(f"  Parties: {latest_eval['num_games']}")
            print(f"  Taux victoire: {latest_eval['win_rate']:.1f}%")
            print(f"  Taux nul: {latest_eval['draw_rate']:.1f}%")
        
        print("=" * 60 + "\n")
    
    def clear_history(self, confirm: bool = False):
        """
        Efface tout l'historique.
        
        Args:
            confirm: Doit être True pour effectuer l'effacement
        """
        if confirm:
            self.games_history = []
            self.training_stats = []
            self.evaluation_results = []
            self._save_games()
            self._save_training_stats()
            self._save_evaluation()
            print("✓ Historique effacé")
        else:
            print("⚠ Passez confirm=True pour effacer l'historique")
    
    def _empty_stats(self) -> Dict:
        """Retourne des statistiques vides"""
        return {
            'total_games': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'win_rate': 0.0,
            'loss_rate': 0.0,
            'draw_rate': 0.0,
            'avg_moves': 0.0,
            'avg_duration': 0.0
        }
    
    def _moving_average(self, data: List[float], window: int) -> List[float]:
        """Calcule une moyenne glissante"""
        if len(data) < window:
            return data
        return [np.mean(data[max(0, i-window):i+1]) for i in range(len(data))]
    
    def _load_histories(self):
        """Charge les historiques depuis les fichiers"""
        # Charger les parties
        if self.games_file.exists():
            try:
                with open(self.games_file, 'r', encoding='utf-8') as f:
                    self.games_history = json.load(f)
            except Exception:
                self.games_history = []
        
        # Charger les stats d'entraînement
        if self.training_file.exists():
            try:
                with open(self.training_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.training_stats = [
                        {k: float(v) if k not in ['episode', 'timestamp'] else v 
                         for k, v in row.items()}
                        for row in reader
                    ]
            except Exception:
                self.training_stats = []
        
        # Charger les évaluations
        if self.eval_file.exists():
            try:
                with open(self.eval_file, 'r', encoding='utf-8') as f:
                    self.evaluation_results = json.load(f)
            except Exception:
                self.evaluation_results = []
    
    def _save_games(self):
        """Sauvegarde l'historique des parties"""
        try:
            with open(self.games_file, 'w', encoding='utf-8') as f:
                json.dump(self.games_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde parties: {e}")
    
    def _save_training_stats(self):
        """Sauvegarde les stats d'entraînement en CSV"""
        try:
            if not self.training_stats:
                return
            
            with open(self.training_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = self.training_stats[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.training_stats)
        except Exception as e:
            print(f"Erreur sauvegarde stats: {e}")
    
    def _save_evaluation(self):
        """Sauvegarde les résultats d'évaluation"""
        try:
            with open(self.eval_file, 'w', encoding='utf-8') as f:
                json.dump(self.evaluation_results, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur sauvegarde évaluations: {e}")
