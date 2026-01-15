"""
Gestionnaire de modèles
Gère la sauvegarde, le chargement et le versionnage des modèles Q-Learning.
"""

import pickle
import json
import os
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path


class ModelManager:
    """
    Gère la persistance des modèles Q-Learning.
    Supporte le versionnage automatique avec horodatage.
    """
    
    def __init__(self, models_dir: str = "models"):
        """
        Initialise le gestionnaire de modèles.
        
        Args:
            models_dir: Répertoire de sauvegarde des modèles
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Fichiers par défaut
        self.default_model = self.models_dir / "q_table.pkl"
        self.metadata_file = self.models_dir / "models_metadata.json"
        
        # Charger ou créer les métadonnées
        self.metadata = self._load_metadata()
    
    def save_model(self, agent, name: Optional[str] = None, 
                   versioned: bool = False, metadata: Optional[Dict] = None) -> str:
        """
        Sauvegarde un modèle Q-Learning.
        
        Args:
            agent: Agent QLearningAgent à sauvegarder
            name: Nom du fichier (sans extension). Si None, utilise le nom par défaut.
            versioned: Si True, ajoute un horodatage au nom du fichier
            metadata: Métadonnées additionnelles à sauvegarder
        
        Returns:
            Chemin du fichier sauvegardé
        """
        # Générer le nom du fichier
        if name is None:
            filepath = self.default_model
        else:
            if versioned:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}.pkl"
            else:
                filename = f"{name}.pkl"
            filepath = self.models_dir / filename
        
        # Préparer les données à sauvegarder
        model_data = {
            'q_table': agent.get_q_table_copy(),
            'hyperparameters': {
                'alpha': agent.alpha,
                'gamma': agent.gamma,
                'epsilon': agent.epsilon,
                'epsilon_start': agent.epsilon_start,
                'epsilon_min': agent.epsilon_min,
                'epsilon_decay': agent.epsilon_decay
            },
            'stats': agent.get_stats(),
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        # Sauvegarder avec pickle
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        # Mettre à jour les métadonnées
        self._update_metadata(str(filepath), model_data)
        
        print(f"✓ Modèle sauvegardé: {filepath}")
        print(f"  États: {model_data['stats']['total_states']}")
        print(f"  Epsilon: {model_data['stats']['epsilon']:.6f}")
        
        return str(filepath)
    
    def load_model(self, agent, filepath: Optional[str] = None) -> bool:
        """
        Charge un modèle Q-Learning.
        
        Args:
            agent: Agent QLearningAgent à charger
            filepath: Chemin du fichier à charger (utilise le défaut si None)
        
        Returns:
            True si le chargement a réussi, False sinon
        """
        if filepath is None:
            filepath = self.default_model
        else:
            filepath = Path(filepath)
        
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            # Charger la Q-table
            agent.load_q_table(model_data['q_table'])
            
            # Restaurer les hyperparamètres
            params = model_data['hyperparameters']
            agent.alpha = params['alpha']
            agent.gamma = params['gamma']
            agent.epsilon = params['epsilon']
            agent.epsilon_start = params['epsilon_start']
            agent.epsilon_min = params['epsilon_min']
            agent.epsilon_decay = params['epsilon_decay']
            
            print(f"✓ Modèle chargé: {filepath}")
            print(f"  États appris: {len(agent.q_table)}")
            print(f"  Epsilon: {agent.epsilon:.6f}")
            print(f"  Date: {model_data.get('timestamp', 'N/A')}")
            
            return True
        
        except FileNotFoundError:
            print(f"✗ Fichier non trouvé: {filepath}")
            return False
        except Exception as e:
            print(f"✗ Erreur lors du chargement: {e}")
            return False
    
    def model_exists(self, filepath: Optional[str] = None) -> bool:
        """
        Vérifie si un modèle existe.
        
        Args:
            filepath: Chemin du modèle. Si None, vérifie le modèle par défaut.
        
        Returns:
            True si le modèle existe, False sinon
        """
        if filepath is None:
            filepath = self.default_model
        else:
            filepath = Path(filepath)
        
        return filepath.exists()
    
    def list_models(self) -> List[Dict]:
        """
        Liste tous les modèles disponibles avec leurs informations.
        Utilise le fichier de métadonnées pour de meilleures performances.
        
        Returns:
            Liste de dictionnaires contenant les infos de chaque modèle
        """
        models = []
        
        # Recharger les métadonnées depuis le fichier
        self.metadata = self._load_metadata()
        
        # Utiliser les métadonnées si disponibles
        if self.metadata:
            for filepath, meta in self.metadata.items():
                filepath_obj = Path(filepath)
                if filepath_obj.exists():
                    models.append({
                        'name': filepath_obj.name,
                        'path': str(filepath_obj),
                        'timestamp': meta.get('timestamp', 'N/A'),
                        'states': meta.get('states', 0),
                        'epsilon': meta.get('epsilon', 1.0),
                        'size_mb': filepath_obj.stat().st_size / (1024 * 1024),
                        # Inclure les métadonnées complètes
                        'metadata': meta.get('metadata', {}),
                        'final_win_rate': meta.get('final_win_rate', 0),
                        'final_draw_rate': meta.get('final_draw_rate', 0),
                        'final_loss_rate': meta.get('final_loss_rate', 0),
                        'total_episodes': meta.get('total_episodes', 0),
                    })
        else:
            # Fallback : charger directement depuis les fichiers
            for pkl_file in self.models_dir.glob("*.pkl"):
                try:
                    with open(pkl_file, 'rb') as f:
                        model_data = pickle.load(f)
                    
                    metadata = model_data.get('metadata', {})
                    models.append({
                        'name': pkl_file.name,
                        'path': str(pkl_file),
                        'timestamp': model_data.get('timestamp', 'N/A'),
                        'states': model_data['stats']['total_states'],
                        'epsilon': model_data['stats']['epsilon'],
                        'size_mb': pkl_file.stat().st_size / (1024 * 1024),
                        'metadata': metadata,
                        'final_win_rate': metadata.get('final_win_rate', 0),
                        'final_draw_rate': metadata.get('final_draw_rate', 0),
                        'final_loss_rate': metadata.get('final_loss_rate', 0),
                        'total_episodes': metadata.get('total_episodes', 0),
                    })
                except Exception as e:
                    print(f"Erreur lecture {pkl_file.name}: {e}")
        
        # Trier par date (plus récent en premier)
        models.sort(key=lambda x: x['timestamp'], reverse=True)
        return models
    
    def delete_model(self, filepath: str) -> bool:
        """
        Supprime un modèle.
        
        Args:
            filepath: Chemin du fichier à supprimer
        
        Returns:
            True si la suppression a réussi
        """
        try:
            filepath = Path(filepath)
            if filepath.exists():
                filepath.unlink()
                # Retirer des métadonnées
                if str(filepath) in self.metadata:
                    del self.metadata[str(filepath)]
                    self._save_metadata()
                print(f"✓ Modèle supprimé: {filepath}")
                return True
            else:
                print(f"✗ Fichier introuvable: {filepath}")
                return False
        except Exception as e:
            print(f"✗ Erreur lors de la suppression: {e}")
            return False
    
    def get_best_model(self, metric: str = 'composite_score') -> Optional[str]:
        """
        Retourne le chemin du meilleur modèle selon un critère.
        
        Args:
            metric: Critère de sélection ('composite_score', 'win_rate', 
                   'performance_score', 'states', 'epsilon', 'timestamp')
        
        Returns:
            Chemin du meilleur modèle ou None
        """
        # Utiliser le comparateur pour une analyse avancée
        if metric in ['composite_score', 'win_rate', 'performance_score', 
                     'efficiency_score', 'robustness_score']:
            try:
                from .model_comparator import ModelComparator
                comparator = ModelComparator(str(self.models_dir))
                best_model = comparator.get_best_model(metric)
                return best_model['filepath'] if best_model else None
            except ImportError:
                print("⚠ ModelComparator non disponible, utilisation méthode simple")
        
        # Méthode simple pour les autres critères
        models = self.list_models()
        if not models:
            return None
        
        if metric == 'states':
            best = max(models, key=lambda x: x['states'])
        elif metric == 'epsilon':
            best = min(models, key=lambda x: x['epsilon'])
        elif metric == 'timestamp':
            best = max(models, key=lambda x: x['timestamp'])
        else:
            best = models[0]
        
        return best['path']
    
    def _load_metadata(self) -> Dict:
        """Charge les métadonnées des modèles"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_metadata(self):
        """Sauvegarde les métadonnées"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Erreur sauvegarde métadonnées: {e}")
    
    def _update_metadata(self, filepath: str, model_data: Dict):
        """Met à jour les métadonnées avec les infos d'un modèle"""
        # Inclure TOUTES les métadonnées du modèle
        full_metadata = model_data.get('metadata', {})
        
        self.metadata[filepath] = {
            'timestamp': model_data['timestamp'],
            'states': model_data['stats']['total_states'],
            'epsilon': model_data['stats']['epsilon'],
            'metadata': full_metadata,
            # Ajouter les infos importantes au niveau racine pour faciliter l'accès
            'final_win_rate': full_metadata.get('final_win_rate', 0),
            'final_draw_rate': full_metadata.get('final_draw_rate', 0),
            'final_loss_rate': full_metadata.get('final_loss_rate', 0),
            'total_episodes': full_metadata.get('total_episodes', 0),
        }
        self._save_metadata()
    
    def export_to_json(self, agent, filepath: str):
        """
        Exporte la Q-table en format JSON (lisible).
        
        Args:
            agent: Agent à exporter
            filepath: Chemin du fichier JSON
        """
        data = {
            'q_table': {
                str(state): {str(action): float(q) 
                           for action, q in actions.items()}
                for state, actions in agent.q_table.items()
            },
            'hyperparameters': {
                'alpha': agent.alpha,
                'gamma': agent.gamma,
                'epsilon': agent.epsilon
            },
            'stats': agent.get_stats(),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Q-table exportée en JSON: {filepath}")
    
    def load_best_model(self, agent, metric: str = 'composite_score') -> bool:
        """
        Charge automatiquement le meilleur modèle selon un critère.
        
        Args:
            agent: Agent dans lequel charger le modèle
            metric: Critère de sélection du meilleur modèle
        
        Returns:
            True si le chargement a réussi, False sinon
        """
        best_path = self.get_best_model(metric)
        
        if best_path is None:
            print(f"✗ Aucun modèle trouvé pour le critère '{metric}'")
            return False
        
        print(f"📊 Meilleur modèle selon '{metric}': {Path(best_path).name}")
        return self.load_model(agent, best_path)
    
    def analyze_models(self, top_n: int = 10) -> None:
        """
        Affiche une analyse comparative des modèles.
        
        Args:
            top_n: Nombre de modèles à afficher dans le top
        """
        try:
            from .model_comparator import ModelComparator
            
            comparator = ModelComparator(str(self.models_dir))
            
            # Afficher le rapport
            report = comparator.generate_report()
            print(report)
            
            # Afficher le tableau des top modèles
            print("\n📊 TABLEAU DÉTAILLÉ DES MEILLEURS MODÈLES")
            print("=" * 80)
            df = comparator.compare_top_models(top_n)
            print(df.to_string(index=False))
            
        except ImportError as e:
            print(f"⚠ Erreur d'import: {e}")
            print("Veuillez vous assurer que pandas est installé: pip install pandas")
        except Exception as e:
            print(f"✗ Erreur lors de l'analyse: {e}")
    
    def export_metrics(self, output_csv: str = "models/models_metrics.csv") -> None:
        """
        Exporte les métriques de tous les modèles en CSV.
        
        Args:
            output_csv: Chemin du fichier CSV de sortie
        """
        try:
            from .model_comparator import ModelComparator
            
            comparator = ModelComparator(str(self.models_dir))
            comparator.export_metrics_csv(output_csv)
            
        except ImportError as e:
            print(f"⚠ Erreur d'import: {e}")
            print("Veuillez vous assurer que pandas est installé: pip install pandas")
        except Exception as e:
            print(f"✗ Erreur lors de l'export: {e}")