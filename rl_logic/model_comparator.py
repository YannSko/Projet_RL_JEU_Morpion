"""
Module de comparaison de modèles
Compare et classe les modèles selon différentes métriques.
"""

import pickle
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .metrics import ModelMetrics
import pandas as pd


class ModelComparator:
    """
    Compare plusieurs modèles et identifie le meilleur selon différents critères.
    """
    
    def __init__(self, models_dir: str = "models"):
        """
        Initialise le comparateur.
        
        Args:
            models_dir: Répertoire contenant les modèles
        """
        self.models_dir = Path(models_dir)
        self.metadata_file = self.models_dir / "models_metadata.json"
        self.models_metrics = []
    
    def load_models_metadata(self) -> List[Dict]:
        """
        Charge les métadonnées de tous les modèles.
        
        Returns:
            Liste des métadonnées des modèles
        """
        if not self.metadata_file.exists():
            print(f"Fichier de métadonnées introuvable: {self.metadata_file}")
            return []
        
        with open(self.metadata_file, 'r') as f:
            metadata = json.load(f)
        
        models = []
        for filepath, model_info in metadata.items():
            model_info['filepath'] = filepath
            model_info['filename'] = Path(filepath).name
            models.append(model_info)
        
        return models
    
    def load_model_data(self, filepath: str) -> Optional[Dict]:
        """
        Charge les données complètes d'un modèle.
        
        Args:
            filepath: Chemin du fichier modèle
        
        Returns:
            Données du modèle ou None si erreur
        """
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Erreur chargement {filepath}: {e}")
            return None
    
    def compute_metrics_for_all_models(self, include_q_table: bool = False) -> List[Dict]:
        """
        Calcule les métriques pour tous les modèles.
        
        Args:
            include_q_table: Si True, inclut les métriques de Q-table (plus lent)
        
        Returns:
            Liste des modèles avec leurs métriques
        """
        models_metadata = self.load_models_metadata()
        self.models_metrics = []
        
        print(f"\n📊 Calcul des métriques pour {len(models_metadata)} modèles...")
        
        for i, model_info in enumerate(models_metadata, 1):
            filepath = model_info['filepath']
            
            # Charger les données complètes si nécessaire
            q_table = None
            if include_q_table:
                model_data = self.load_model_data(filepath)
                if model_data:
                    q_table = model_data.get('q_table')
            
            # Calculer les métriques
            metrics = ModelMetrics.compute_all_metrics(model_info, q_table)
            metrics['filepath'] = filepath
            metrics['filename'] = model_info['filename']
            metrics['timestamp'] = model_info.get('timestamp', 'N/A')
            
            self.models_metrics.append(metrics)
            
            if i % 10 == 0:
                print(f"  Traité {i}/{len(models_metadata)} modèles...")
        
        print(f"✓ Métriques calculées pour {len(self.models_metrics)} modèles\n")
        return self.models_metrics
    
    def rank_models(self, criterion: str = 'composite_score', 
                   top_n: Optional[int] = None) -> List[Dict]:
        """
        Classe les modèles selon un critère.
        
        Args:
            criterion: Critère de classement ('composite_score', 'win_rate', 
                      'performance_score', 'efficiency_score', etc.)
            top_n: Nombre de modèles à retourner (tous si None)
        
        Returns:
            Liste des modèles classés
        """
        if not self.models_metrics:
            self.compute_metrics_for_all_models()
        
        # Filtrer les modèles qui ont le critère
        valid_models = [m for m in self.models_metrics if criterion in m]
        
        # Trier par critère (descendant)
        ranked = sorted(valid_models, key=lambda x: x[criterion], reverse=True)
        
        return ranked[:top_n] if top_n else ranked
    
    def get_best_model(self, criterion: str = 'composite_score') -> Optional[Dict]:
        """
        Retourne le meilleur modèle selon un critère.
        
        Args:
            criterion: Critère de sélection
        
        Returns:
            Meilleur modèle ou None
        """
        ranked = self.rank_models(criterion, top_n=1)
        return ranked[0] if ranked else None
    
    def compare_top_models(self, top_n: int = 10) -> pd.DataFrame:
        """
        Compare les top N modèles avec toutes les métriques.
        
        Args:
            top_n: Nombre de modèles à comparer
        
        Returns:
            DataFrame avec la comparaison
        """
        top_models = self.rank_models('composite_score', top_n=top_n)
        
        if not top_models:
            return pd.DataFrame()
        
        # Créer le DataFrame
        data = []
        for model in top_models:
            data.append({
                'Modèle': model['filename'],
                'Score Composite': f"{model['composite_score']:.2f}",
                'Win Rate (%)': f"{model['win_rate']:.2f}",
                'Draw Rate (%)': f"{model.get('draw_rate', 0):.2f}",
                'Loss Rate (%)': f"{model.get('loss_rate', 0):.2f}",
                'Performance': f"{model['performance_score']:.2f}",
                'Efficacité': f"{model['efficiency_score']:.2f}",
                'Robustesse': f"{model['robustness_score']:.2f}",
                'États': model['states_learned'],
                'Épisodes': model['total_episodes'],
                'Epsilon': f"{model['epsilon']:.4f}",
                'Timestamp': model['timestamp']
            })
        
        return pd.DataFrame(data)
    
    def filter_models(self, filters: Dict) -> List[Dict]:
        """
        Filtre les modèles selon des critères.
        
        Args:
            filters: Dictionnaire de filtres (ex: {'min_win_rate': 80, 'max_episodes': 50000})
        
        Returns:
            Liste des modèles filtrés
        """
        if not self.models_metrics:
            self.compute_metrics_for_all_models()
        
        filtered = self.models_metrics.copy()
        
        # Appliquer les filtres
        if 'min_win_rate' in filters:
            filtered = [m for m in filtered if m['win_rate'] >= filters['min_win_rate']]
        
        if 'max_win_rate' in filters:
            filtered = [m for m in filtered if m['win_rate'] <= filters['max_win_rate']]
        
        if 'min_episodes' in filters:
            filtered = [m for m in filtered if m['total_episodes'] >= filters['min_episodes']]
        
        if 'max_episodes' in filters:
            filtered = [m for m in filtered if m['total_episodes'] <= filters['max_episodes']]
        
        if 'min_states' in filters:
            filtered = [m for m in filtered if m['states_learned'] >= filters['min_states']]
        
        if 'max_states' in filters:
            filtered = [m for m in filtered if m['states_learned'] <= filters['max_states']]
        
        if 'min_composite_score' in filters:
            filtered = [m for m in filtered if m['composite_score'] >= filters['min_composite_score']]
        
        return filtered
    
    def get_models_by_category(self) -> Dict[str, List[Dict]]:
        """
        Catégorise les modèles selon leurs caractéristiques.
        
        Returns:
            Dictionnaire de catégories avec leurs modèles
        """
        if not self.models_metrics:
            self.compute_metrics_for_all_models()
        
        categories = {
            'high_performance': [],  # Win rate > 90%
            'medium_performance': [],  # Win rate 70-90%
            'low_performance': [],  # Win rate < 70%
            'efficient': [],  # Haut efficiency_score
            'overtrained': [],  # Beaucoup d'épisodes, performance moyenne
            'fast_learners': [],  # Bon score avec peu d'épisodes
        }
        
        for model in self.models_metrics:
            win_rate = model['win_rate']
            episodes = model['total_episodes']
            efficiency = model['efficiency_score']
            
            # Performance
            if win_rate >= 90:
                categories['high_performance'].append(model)
            elif win_rate >= 70:
                categories['medium_performance'].append(model)
            else:
                categories['low_performance'].append(model)
            
            # Efficacité
            if efficiency > 25:
                categories['efficient'].append(model)
            
            # Sur-entraînement
            if episodes > 100000 and win_rate < 85:
                categories['overtrained'].append(model)
            
            # Apprentissage rapide
            if episodes < 20000 and win_rate > 80:
                categories['fast_learners'].append(model)
        
        return categories
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        Génère un rapport complet de comparaison.
        
        Args:
            output_file: Fichier de sortie (affiche si None)
        
        Returns:
            Contenu du rapport
        """
        if not self.models_metrics:
            self.compute_metrics_for_all_models()
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("RAPPORT DE COMPARAISON DES MODÈLES")
        report_lines.append("=" * 80)
        report_lines.append(f"\nNombre total de modèles: {len(self.models_metrics)}\n")
        
        # Meilleur modèle global
        best = self.get_best_model('composite_score')
        if best:
            report_lines.append("\n" + "─" * 80)
            report_lines.append("🏆 MEILLEUR MODÈLE (Score Composite)")
            report_lines.append("─" * 80)
            report_lines.append(f"Fichier: {best['filename']}")
            report_lines.append(f"Score Composite: {best['composite_score']:.2f}/100")
            report_lines.append(f"Win Rate: {best['win_rate']:.2f}%")
            report_lines.append(f"Draw Rate: {best.get('draw_rate', 0):.2f}%")
            report_lines.append(f"Loss Rate: {best.get('loss_rate', 0):.2f}%")
            report_lines.append(f"Performance Score: {best['performance_score']:.2f}")
            report_lines.append(f"États appris: {best['states_learned']}")
            report_lines.append(f"Épisodes: {best['total_episodes']}")
            report_lines.append(f"Efficacité: {best['efficiency_score']:.2f}")
            report_lines.append(f"Robustesse: {best['robustness_score']:.2f}")
            report_lines.append(f"Epsilon: {best['epsilon']:.6f}")
        
        # Top 10
        report_lines.append("\n" + "─" * 80)
        report_lines.append("📊 TOP 10 MODÈLES")
        report_lines.append("─" * 80)
        
        top_10 = self.rank_models('composite_score', top_n=10)
        for i, model in enumerate(top_10, 1):
            report_lines.append(f"\n{i}. {model['filename']}")
            report_lines.append(f"   Score: {model['composite_score']:.2f} | "
                              f"Win: {model['win_rate']:.1f}% | "
                              f"États: {model['states_learned']} | "
                              f"Épisodes: {model['total_episodes']}")
        
        # Catégories
        categories = self.get_models_by_category()
        report_lines.append("\n" + "─" * 80)
        report_lines.append("📁 CATÉGORIES DE MODÈLES")
        report_lines.append("─" * 80)
        
        for cat_name, models in categories.items():
            if models:
                report_lines.append(f"\n{cat_name.upper().replace('_', ' ')}: {len(models)} modèles")
        
        # Statistiques globales
        report_lines.append("\n" + "─" * 80)
        report_lines.append("📈 STATISTIQUES GLOBALES")
        report_lines.append("─" * 80)
        
        win_rates = [m['win_rate'] for m in self.models_metrics]
        composite_scores = [m['composite_score'] for m in self.models_metrics]
        
        import numpy as np
        report_lines.append(f"\nWin Rate moyen: {np.mean(win_rates):.2f}%")
        report_lines.append(f"Win Rate médian: {np.median(win_rates):.2f}%")
        report_lines.append(f"Win Rate min: {np.min(win_rates):.2f}%")
        report_lines.append(f"Win Rate max: {np.max(win_rates):.2f}%")
        report_lines.append(f"\nScore Composite moyen: {np.mean(composite_scores):.2f}")
        report_lines.append(f"Score Composite médian: {np.median(composite_scores):.2f}")
        
        report_lines.append("\n" + "=" * 80 + "\n")
        
        report = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✓ Rapport sauvegardé dans: {output_file}")
        
        return report
    
    def export_metrics_csv(self, output_file: str = "models/models_metrics.csv"):
        """
        Exporte toutes les métriques en CSV.
        
        Args:
            output_file: Fichier de sortie
        """
        if not self.models_metrics:
            self.compute_metrics_for_all_models()
        
        # Créer le DataFrame
        data = []
        for model in self.models_metrics:
            row = {
                'filename': model['filename'],
                'composite_score': model['composite_score'],
                'win_rate': model['win_rate'],
                'draw_rate': model.get('draw_rate', 0),
                'loss_rate': model.get('loss_rate', 0),
                'performance_score': model['performance_score'],
                'efficiency_score': model['efficiency_score'],
                'robustness_score': model['robustness_score'],
                'learning_speed': model['learning_speed'],
                'states_learned': model['states_learned'],
                'total_episodes': model['total_episodes'],
                'avg_reward': model['avg_reward'],
                'avg_moves': model['avg_moves'],
                'epsilon': model['epsilon'],
                'timestamp': model['timestamp']
            }
            
            # Ajouter les hyperparamètres
            hyperparams = model.get('hyperparameters', {})
            row['alpha'] = hyperparams.get('alpha', 'N/A')
            row['gamma'] = hyperparams.get('gamma', 'N/A')
            row['epsilon_decay'] = hyperparams.get('epsilon_decay', 'N/A')
            
            data.append(row)
        
        df = pd.DataFrame(data)
        df = df.sort_values('composite_score', ascending=False)
        df.to_csv(output_file, index=False)
        print(f"✓ Métriques exportées dans: {output_file}")
