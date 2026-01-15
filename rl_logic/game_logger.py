"""
Logger détaillé des parties jouées
Enregistre chaque coup, chaque état, chaque décision
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import numpy as np


class GameLogger:
    """
    Logger détaillé pour les parties de Morpion.
    Enregistre: état initial, tous les coups, temps de réflexion, résultat final.
    """
    
    def __init__(self, logs_dir: str = "logs"):
        """
        Initialise le logger de parties.
        
        Args:
            logs_dir: Répertoire des logs
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Fichier des parties détaillées
        self.games_detailed_file = self.logs_dir / "games_detailed.json"
        
        # Partie en cours
        self.current_game: Optional[Dict] = None
        
        # Historique des parties
        self.games: List[Dict] = []
        self._load_games()
    
    def start_game(self, mode: str, player_x: str, player_o: str, 
                   config: Optional[Dict] = None):
        """
        Démarre l'enregistrement d'une nouvelle partie.
        
        Args:
            mode: Mode de jeu (HH, HA, AA)
            player_x: Nom du joueur X
            player_o: Nom du joueur O
            config: Configuration de la partie (epsilon IA, etc.)
        """
        self.current_game = {
            'game_id': len(self.games) + 1,
            'timestamp_start': datetime.now().isoformat(),
            'timestamp_end': None,
            'mode': mode,
            'player_x': player_x,
            'player_o': player_o,
            'config': config or {},
            'moves': [],
            'states': [],
            'winner': None,
            'reason': None,  # normal, timeout, error, quit
            'duration': 0.0,
            'stats': {}
        }
        
        # Enregistrer l'état initial
        self._add_state([[0, 0, 0], [0, 0, 0], [0, 0, 0]], 1)
    
    def log_move(self, player: str, player_num: int, action: int, 
                 row: int, col: int, board_state: np.ndarray,
                 thinking_time: float = 0.0, q_values: Optional[Dict] = None):
        """
        Enregistre un coup joué.
        
        Args:
            player: Nom du joueur
            player_num: Numéro du joueur (1 ou -1)
            action: Action choisie (0-8)
            row, col: Position du coup
            board_state: État du plateau après le coup
            thinking_time: Temps de réflexion en secondes
            q_values: Q-valeurs pour les actions possibles (pour IA)
        """
        if self.current_game is None:
            return
        
        move = {
            'move_number': len(self.current_game['moves']) + 1,
            'timestamp': datetime.now().isoformat(),
            'player': player,
            'player_num': player_num,
            'action': action,
            'position': {'row': row, 'col': col},
            'thinking_time': thinking_time,
            'q_values': q_values or {}
        }
        
        self.current_game['moves'].append(move)
        self._add_state(board_state.tolist(), -player_num)  # Prochain joueur
    
    def end_game(self, winner: Optional[int], reason: str = "normal", 
                 final_board: Optional[np.ndarray] = None):
        """
        Termine l'enregistrement de la partie.
        
        Args:
            winner: 1 (X), -1 (O) ou None (nul)
            reason: Raison de fin (normal, timeout, error, quit)
            final_board: État final du plateau
        """
        if self.current_game is None:
            return
        
        end_time = datetime.now()
        start_time = datetime.fromisoformat(self.current_game['timestamp_start'])
        duration = (end_time - start_time).total_seconds()
        
        self.current_game['timestamp_end'] = end_time.isoformat()
        self.current_game['duration'] = duration
        self.current_game['winner'] = 'X' if winner == 1 else ('O' if winner == -1 else 'Draw')
        self.current_game['reason'] = reason
        
        # Statistiques de la partie
        self.current_game['stats'] = {
            'total_moves': len(self.current_game['moves']),
            'avg_thinking_time': np.mean([m['thinking_time'] for m in self.current_game['moves']]) if self.current_game['moves'] else 0.0,
            'max_thinking_time': max([m['thinking_time'] for m in self.current_game['moves']]) if self.current_game['moves'] else 0.0,
        }
        
        # Ajouter l'état final si fourni
        if final_board is not None:
            self._add_state(final_board.tolist(), 0)
        
        # Sauvegarder
        self.games.append(self.current_game)
        self._save_games()
        self.current_game = None
    
    def cancel_game(self):
        """Annule la partie en cours sans la sauvegarder"""
        self.current_game = None
    
    def _add_state(self, board: List[List[int]], next_player: int):
        """Ajoute un état du plateau à l'historique"""
        if self.current_game is None:
            return
        
        state = {
            'state_number': len(self.current_game['states']) + 1,
            'board': board,
            'next_player': next_player
        }
        self.current_game['states'].append(state)
    
    def _load_games(self):
        """Charge l'historique des parties depuis le fichier"""
        if self.games_detailed_file.exists():
            try:
                with open(self.games_detailed_file, 'r', encoding='utf-8') as f:
                    self.games = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.games = []
        else:
            self.games = []
    
    def _save_games(self):
        """Sauvegarde l'historique des parties"""
        with open(self.games_detailed_file, 'w', encoding='utf-8') as f:
            json.dump(self.games, f, indent=2, ensure_ascii=False)
    
    def get_game(self, game_id: int) -> Optional[Dict]:
        """Récupère une partie par son ID"""
        for game in self.games:
            if game['game_id'] == game_id:
                return game
        return None
    
    def get_recent_games(self, n: int = 10) -> List[Dict]:
        """Récupère les n dernières parties"""
        return self.games[-n:] if len(self.games) >= n else self.games
    
    def get_games_by_mode(self, mode: str) -> List[Dict]:
        """Récupère toutes les parties d'un mode donné"""
        return [g for g in self.games if g['mode'] == mode]
    
    def get_games_by_player(self, player_name: str) -> List[Dict]:
        """Récupère toutes les parties d'un joueur"""
        return [g for g in self.games if player_name in [g['player_x'], g['player_o']]]
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Génère un résumé statistique de toutes les parties"""
        if not self.games:
            return {}
        
        total = len(self.games)
        by_mode = {}
        by_winner = {'X': 0, 'O': 0, 'Draw': 0}
        total_moves = []
        total_duration = []
        
        for game in self.games:
            mode = game['mode']
            by_mode[mode] = by_mode.get(mode, 0) + 1
            by_winner[game['winner']] += 1
            total_moves.append(game['stats']['total_moves'])
            total_duration.append(game['duration'])
        
        return {
            'total_games': total,
            'by_mode': by_mode,
            'by_winner': by_winner,
            'avg_moves': np.mean(total_moves),
            'avg_duration': np.mean(total_duration),
            'total_duration': sum(total_duration)
        }
    
    def export_game_pgn(self, game_id: int) -> str:
        """
        Exporte une partie au format PGN-like (adapté pour Morpion).
        
        Args:
            game_id: ID de la partie
        
        Returns:
            Chaîne de caractères au format PGN
        """
        game = self.get_game(game_id)
        if not game:
            return ""
        
        pgn = []
        pgn.append(f"[Game \"{game['game_id']}\"]")
        pgn.append(f"[Date \"{game['timestamp_start']}\"]")
        pgn.append(f"[Mode \"{game['mode']}\"]")
        pgn.append(f"[PlayerX \"{game['player_x']}\"]")
        pgn.append(f"[PlayerO \"{game['player_o']}\"]")
        pgn.append(f"[Result \"{game['winner']}\"]")
        pgn.append(f"[Moves \"{game['stats']['total_moves']}\"]")
        pgn.append(f"[Duration \"{game['duration']:.2f}s\"]")
        pgn.append("")
        
        # Coups
        for move in game['moves']:
            player_symbol = 'X' if move['player_num'] == 1 else 'O'
            pos = f"{move['position']['row']}{move['position']['col']}"
            pgn.append(f"{move['move_number']}. {player_symbol}{pos}")
        
        pgn.append(f"\nRésultat: {game['winner']}")
        
        return "\n".join(pgn)


# Instance globale
_global_game_logger: Optional[GameLogger] = None


def get_game_logger() -> GameLogger:
    """Retourne l'instance globale du logger de parties"""
    global _global_game_logger
    if _global_game_logger is None:
        _global_game_logger = GameLogger()
    return _global_game_logger
