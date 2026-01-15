"""
Système de tournoi pour comparer les modèles
Round-robin, brackets, et statistiques
"""

import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime
from engine.environment import TicTacToeEnvironment
from .elo_system import ELOSystem


class Tournament:
    """
    Organise des tournois entre modèles Q-Learning.
    Supporte round-robin et elimination brackets.
    """
    
    def __init__(self, env: TicTacToeEnvironment, elo_system: Optional[ELOSystem] = None):
        """
        Initialise le tournoi.
        
        Args:
            env: Environnement de jeu
            elo_system: Système ELO (créé si None)
        """
        self.env = env
        self.elo_system = elo_system or ELOSystem()
        self.results = []
        self.tournament_history = Path("models/tournament_history.json")
    
    def play_match(self, agent1, agent2, num_games: int = 100, 
                   agent1_name: str = "Agent 1", agent2_name: str = "Agent 2") -> Dict:
        """
        Fait jouer 2 agents l'un contre l'autre.
        
        Args:
            agent1: Premier agent
            agent2: Deuxième agent
            num_games: Nombre de parties
            agent1_name: Nom du premier agent
            agent2_name: Nom du deuxième agent
        
        Returns:
            Dictionnaire avec les résultats
        """
        wins_agent1 = 0
        wins_agent2 = 0
        draws = 0
        
        for game in range(num_games):
            # Alterner qui commence
            agent1_starts = game % 2 == 0
            
            state = self.env.reset()
            done = False
            
            current_agent = agent1 if agent1_starts else agent2
            other_agent = agent2 if agent1_starts else agent1
            
            while not done:
                # Tour de l'agent actuel (sans exploration)
                legal_actions = self.env.legal_actions(state)
                action = current_agent.choose_action(state, legal_actions, epsilon=0.0)
                state, reward, done = self.env.apply_action(action)
                
                if not done:
                    # Échanger les agents
                    current_agent, other_agent = other_agent, current_agent
            
            # Enregistrer le résultat
            winner = self.env.get_winner()
            agent1_symbol = self.env.PLAYER_X if agent1_starts else self.env.PLAYER_O
            
            if winner == agent1_symbol:
                wins_agent1 += 1
            elif winner is None:
                draws += 1
            else:
                wins_agent2 += 1
        
        # Calculer les statistiques
        total = num_games
        result = {
            'agent1_name': agent1_name,
            'agent2_name': agent2_name,
            'num_games': num_games,
            'wins_agent1': wins_agent1,
            'wins_agent2': wins_agent2,
            'draws': draws,
            'win_rate_agent1': (wins_agent1 / total) * 100,
            'win_rate_agent2': (wins_agent2 / total) * 100,
            'draw_rate': (draws / total) * 100,
            'score_agent1': wins_agent1 + draws * 0.5,  # Score ELO
            'score_agent2': wins_agent2 + draws * 0.5
        }
        
        return result
    
    def round_robin(self, agents_dict: Dict[str, any], games_per_match: int = 100,
                    update_elo: bool = True) -> Dict:
        """
        Tournoi round-robin : chaque agent joue contre tous les autres.
        
        Args:
            agents_dict: Dictionnaire {nom: agent}
            games_per_match: Nombre de parties par match
            update_elo: Mettre à jour les ratings ELO
        
        Returns:
            Résultats complets du tournoi
        """
        print("\n" + "=" * 70)
        print(f"🏆 TOURNOI ROUND-ROBIN - {len(agents_dict)} participants")
        print("=" * 70 + "\n")
        
        agent_names = list(agents_dict.keys())
        matches = []
        standings = {name: {'wins': 0, 'draws': 0, 'losses': 0, 'points': 0} 
                    for name in agent_names}
        
        total_matches = len(agent_names) * (len(agent_names) - 1) // 2
        match_count = 0
        start_time = time.time()
        
        # Jouer tous les matchs
        for i, name1 in enumerate(agent_names):
            for name2 in agent_names[i+1:]:
                match_count += 1
                
                print(f"Match {match_count}/{total_matches}: {name1} vs {name2}")
                
                result = self.play_match(
                    agents_dict[name1],
                    agents_dict[name2],
                    games_per_match,
                    name1,
                    name2
                )
                
                matches.append(result)
                
                # Mettre à jour les standings
                if result['wins_agent1'] > result['wins_agent2']:
                    standings[name1]['wins'] += 1
                    standings[name2]['losses'] += 1
                    standings[name1]['points'] += 3  # 3 points pour une victoire
                elif result['wins_agent1'] < result['wins_agent2']:
                    standings[name1]['losses'] += 1
                    standings[name2]['wins'] += 1
                    standings[name2]['points'] += 3
                else:
                    standings[name1]['draws'] += 1
                    standings[name2]['draws'] += 1
                    standings[name1]['points'] += 1  # 1 point pour un nul
                    standings[name2]['points'] += 1
                
                # Mettre à jour ELO
                if update_elo:
                    elo_score_1 = result['score_agent1'] / games_per_match
                    elo_score_2 = result['score_agent2'] / games_per_match
                    new_rating1, new_rating2 = self.elo_system.update_ratings(
                        name1, name2, elo_score_1, elo_score_2
                    )
                    
                    print(f"  Résultat: {result['wins_agent1']}-{result['draws']}-{result['wins_agent2']}")
                    print(f"  ELO: {name1} {new_rating1:.0f} ({new_rating1 - self.elo_system.get_rating(name1):+.0f}), "
                          f"{name2} {new_rating2:.0f} ({new_rating2 - self.elo_system.get_rating(name2):+.0f})")
                else:
                    print(f"  Résultat: {result['wins_agent1']}-{result['draws']}-{result['wins_agent2']}")
                
                print()
        
        duration = time.time() - start_time
        
        # Classer les agents
        rankings = sorted(standings.items(), 
                         key=lambda x: (x[1]['points'], x[1]['wins']), 
                         reverse=True)
        
        # Afficher le podium
        print("\n" + "=" * 70)
        print("🏆 CLASSEMENT FINAL")
        print("=" * 70 + "\n")
        
        for rank, (name, stats) in enumerate(rankings, 1):
            elo_rating = self.elo_system.get_rating(name)
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
            
            print(f"{medal} {name}")
            print(f"   Points: {stats['points']} | "
                  f"W-D-L: {stats['wins']}-{stats['draws']}-{stats['losses']} | "
                  f"ELO: {elo_rating:.0f}")
        
        print(f"\n⏱️  Durée totale: {duration:.1f}s")
        print("=" * 70 + "\n")
        
        # Sauvegarder les résultats
        tournament_result = {
            'type': 'round_robin',
            'timestamp': datetime.now().isoformat(),
            'participants': agent_names,
            'games_per_match': games_per_match,
            'total_matches': total_matches,
            'duration': duration,
            'standings': standings,
            'rankings': [(name, stats) for name, stats in rankings],
            'matches': matches,
            'champion': rankings[0][0] if rankings else None
        }
        
        self._save_tournament(tournament_result)
        
        return tournament_result
    
    def get_bracket_matches(self, agent_names: List[str]) -> List[Tuple[int, int]]:
        """
        Génère les paires de matchs pour un bracket éliminatoire.
        
        Args:
            agent_names: Liste des noms d'agents
        
        Returns:
            Liste de paires d'indices
        """
        n = len(agent_names)
        # Arrondir à la puissance de 2 supérieure
        bracket_size = 1
        while bracket_size < n:
            bracket_size *= 2
        
        matches = []
        for i in range(bracket_size // 2):
            if i < n and (bracket_size - 1 - i) < n:
                matches.append((i, bracket_size - 1 - i))
            elif i < n:
                matches.append((i, None))  # Bye
        
        return matches
    
    def elimination_bracket(self, agents_dict: Dict[str, any], 
                           games_per_match: int = 100) -> Dict:
        """
        Tournoi à élimination directe.
        
        Args:
            agents_dict: Dictionnaire {nom: agent}
            games_per_match: Nombre de parties par match
        
        Returns:
            Résultats du tournoi
        """
        print("\n" + "=" * 70)
        print(f"🏆 TOURNOI À ÉLIMINATION - {len(agents_dict)} participants")
        print("=" * 70 + "\n")
        
        agent_names = list(agents_dict.keys())
        remaining = agent_names.copy()
        round_num = 1
        all_matches = []
        
        while len(remaining) > 1:
            print(f"\n{'═' * 70}")
            print(f"ROUND {round_num} - {len(remaining)} participants")
            print(f"{'═' * 70}\n")
            
            next_round = []
            
            # Générer les matchs pour ce round
            for i in range(0, len(remaining), 2):
                if i + 1 < len(remaining):
                    name1 = remaining[i]
                    name2 = remaining[i + 1]
                    
                    print(f"Match: {name1} vs {name2}")
                    
                    result = self.play_match(
                        agents_dict[name1],
                        agents_dict[name2],
                        games_per_match,
                        name1,
                        name2
                    )
                    
                    all_matches.append(result)
                    
                    # Déterminer le gagnant
                    if result['wins_agent1'] > result['wins_agent2']:
                        winner = name1
                    elif result['wins_agent2'] > result['wins_agent1']:
                        winner = name2
                    else:
                        # En cas d'égalité, sudden death (1 partie)
                        print("  ÉGALITÉ! Sudden death...")
                        tiebreak = self.play_match(
                            agents_dict[name1],
                            agents_dict[name2],
                            1,
                            name1,
                            name2
                        )
                        winner = name1 if tiebreak['wins_agent1'] > 0 else name2
                    
                    print(f"  ✅ Gagnant: {winner}\n")
                    next_round.append(winner)
                else:
                    # Bye - avance automatiquement
                    print(f"{remaining[i]} avance automatiquement (bye)\n")
                    next_round.append(remaining[i])
            
            remaining = next_round
            round_num += 1
        
        champion = remaining[0]
        
        print("\n" + "=" * 70)
        print(f"🏆 CHAMPION: {champion}")
        print("=" * 70 + "\n")
        
        tournament_result = {
            'type': 'elimination_bracket',
            'timestamp': datetime.now().isoformat(),
            'participants': agent_names,
            'games_per_match': games_per_match,
            'total_rounds': round_num - 1,
            'matches': all_matches,
            'champion': champion
        }
        
        self._save_tournament(tournament_result)
        
        return tournament_result
    
    def _save_tournament(self, result: Dict):
        """Sauvegarde les résultats du tournoi"""
        # Charger l'historique existant
        history = []
        if self.tournament_history.exists():
            try:
                with open(self.tournament_history, 'r') as f:
                    history = json.load(f)
            except:
                history = []
        
        # Ajouter le nouveau tournoi
        history.append(result)
        
        # Sauvegarder
        self.tournament_history.parent.mkdir(exist_ok=True)
        with open(self.tournament_history, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_tournament_history(self, limit: int = 10) -> List[Dict]:
        """
        Retourne l'historique des tournois.
        
        Args:
            limit: Nombre maximum de tournois à retourner
        
        Returns:
            Liste des tournois (plus récents en premier)
        """
        if not self.tournament_history.exists():
            return []
        
        try:
            with open(self.tournament_history, 'r') as f:
                history = json.load(f)
            return history[-limit:][::-1]  # Plus récents en premier
        except:
            return []
