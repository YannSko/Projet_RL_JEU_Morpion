"""
Système ELO Rating pour comparer les modèles
Similaire au système d'échecs
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class ELOSystem:
    """
    Système de classement ELO pour les modèles Q-Learning.
    """
    
    def __init__(self, k_factor: float = 32, initial_rating: float = 1500):
        """
        Initialise le système ELO.
        
        Args:
            k_factor: Facteur K (sensibilité aux changements)
            initial_rating: Rating initial pour nouveaux modèles
        """
        self.k_factor = k_factor
        self.initial_rating = initial_rating
        self.ratings_file = Path("models/elo_ratings.json")
        self.ratings = self._load_ratings()
        self.match_history = []
    
    def _load_ratings(self) -> Dict[str, float]:
        """Charge les ratings depuis le fichier"""
        if self.ratings_file.exists():
            try:
                with open(self.ratings_file, 'r') as f:
                    data = json.load(f)
                    return data.get('ratings', {})
            except:
                return {}
        return {}
    
    def _save_ratings(self):
        """Sauvegarde les ratings"""
        self.ratings_file.parent.mkdir(exist_ok=True)
        data = {
            'ratings': self.ratings,
            'last_updated': datetime.now().isoformat(),
            'k_factor': self.k_factor,
            'initial_rating': self.initial_rating
        }
        with open(self.ratings_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_rating(self, model_name: str) -> float:
        """
        Retourne le rating d'un modèle.
        
        Args:
            model_name: Nom du modèle
        
        Returns:
            Rating ELO du modèle
        """
        return self.ratings.get(model_name, self.initial_rating)
    
    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """
        Calcule le score attendu pour le joueur A.
        
        Args:
            rating_a: Rating du joueur A
            rating_b: Rating du joueur B
        
        Returns:
            Probabilité de victoire de A (0-1)
        """
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    
    def update_ratings(self, model_a: str, model_b: str, 
                      score_a: float, score_b: float) -> Tuple[float, float]:
        """
        Met à jour les ratings après un match.
        
        Args:
            model_a: Nom du modèle A
            model_b: Nom du modèle B
            score_a: Score de A (1=victoire, 0.5=nul, 0=défaite)
            score_b: Score de B (1=victoire, 0.5=nul, 0=défaite)
        
        Returns:
            Nouveaux ratings (rating_a, rating_b)
        """
        # Récupérer les ratings actuels
        rating_a = self.get_rating(model_a)
        rating_b = self.get_rating(model_b)
        
        # Calculer les scores attendus
        expected_a = self.expected_score(rating_a, rating_b)
        expected_b = self.expected_score(rating_b, rating_a)
        
        # Calculer les nouveaux ratings
        new_rating_a = rating_a + self.k_factor * (score_a - expected_a)
        new_rating_b = rating_b + self.k_factor * (score_b - expected_b)
        
        # Sauvegarder
        self.ratings[model_a] = new_rating_a
        self.ratings[model_b] = new_rating_b
        self._save_ratings()
        
        # Historique
        self.match_history.append({
            'timestamp': datetime.now().isoformat(),
            'model_a': model_a,
            'model_b': model_b,
            'score_a': score_a,
            'score_b': score_b,
            'rating_a_before': rating_a,
            'rating_b_before': rating_b,
            'rating_a_after': new_rating_a,
            'rating_b_after': new_rating_b,
            'rating_change_a': new_rating_a - rating_a,
            'rating_change_b': new_rating_b - rating_b
        })
        
        return new_rating_a, new_rating_b
    
    def get_leaderboard(self, top_n: int = None) -> List[Tuple[str, float]]:
        """
        Retourne le classement des modèles.
        
        Args:
            top_n: Nombre de modèles à retourner (tous si None)
        
        Returns:
            Liste de tuples (model_name, rating) triée par rating
        """
        leaderboard = sorted(self.ratings.items(), key=lambda x: x[1], reverse=True)
        return leaderboard[:top_n] if top_n else leaderboard
    
    def reset_rating(self, model_name: str):
        """Réinitialise le rating d'un modèle"""
        if model_name in self.ratings:
            self.ratings[model_name] = self.initial_rating
            self._save_ratings()
    
    def remove_model(self, model_name: str):
        """Supprime un modèle du système ELO"""
        if model_name in self.ratings:
            del self.ratings[model_name]
            self._save_ratings()
    
    def get_stats(self) -> Dict:
        """Retourne des statistiques sur le système ELO"""
        if not self.ratings:
            return {
                'total_models': 0,
                'avg_rating': 0,
                'max_rating': 0,
                'min_rating': 0
            }
        
        ratings_list = list(self.ratings.values())
        return {
            'total_models': len(self.ratings),
            'avg_rating': sum(ratings_list) / len(ratings_list),
            'max_rating': max(ratings_list),
            'min_rating': min(ratings_list),
            'top_model': self.get_leaderboard(1)[0] if self.ratings else None
        }
