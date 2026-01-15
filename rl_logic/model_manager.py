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
        
        Returns:
            Liste de dictionnaires contenant les infos de chaque modèle
        """
        models = []
        for pkl_file in self.models_dir.glob("*.pkl"):
            try:
                with open(pkl_file, 'rb') as f:
                    model_data = pickle.load(f)
                
                models.append({
                    'name': pkl_file.name,
                    'path': str(pkl_file),
                    'timestamp': model_data.get('timestamp', 'N/A'),
                    'states': model_data['stats']['total_states'],
                    'epsilon': model_data['stats']['epsilon'],
                    'size_mb': pkl_file.stat().st_size / (1024 * 1024)
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
    
    def get_best_model(self, metric: str = 'states') -> Optional[str]:
        """
        Retourne le chemin du meilleur modèle selon un critère.
        
        Args:
            metric: Critère de sélection ('states', 'epsilon', 'timestamp')
        
        Returns:
            Chemin du meilleur modèle ou None
        """
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
        self.metadata[filepath] = {
            'timestamp': model_data['timestamp'],
            'states': model_data['stats']['total_states'],
            'epsilon': model_data['stats']['epsilon'],
            'metadata': model_data.get('metadata', {})
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
