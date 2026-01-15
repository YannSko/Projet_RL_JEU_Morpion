"""
Script pour reconstruire le fichier models_metadata.json
avec toutes les métadonnées complètes
"""

import pickle
import json
from pathlib import Path

models_dir = Path("models")
metadata_file = models_dir / "models_metadata.json"

print("🔄 Reconstruction des métadonnées...\n")

new_metadata = {}
count = 0

# Parcourir tous les fichiers .pkl
for pkl_file in models_dir.glob("*.pkl"):
    try:
        # Charger le modèle
        with open(pkl_file, 'rb') as f:
            model_data = pickle.load(f)
        
        # Extraire les infos
        stats = model_data.get('stats', {})
        metadata = model_data.get('metadata', {})
        
        # Créer l'entrée de métadonnées
        filepath = str(pkl_file)
        new_metadata[filepath] = {
            'timestamp': model_data.get('timestamp', 'N/A'),
            'states': stats.get('total_states', 0),
            'epsilon': stats.get('epsilon', 1.0),
            'metadata': metadata,
            # Données importantes au niveau racine
            'final_win_rate': metadata.get('final_win_rate', 0),
            'final_draw_rate': metadata.get('final_draw_rate', 0),
            'final_loss_rate': metadata.get('final_loss_rate', 0),
            'total_episodes': metadata.get('total_episodes', 0),
        }
        
        count += 1
        
        # Afficher les modèles avec métriques complètes
        if metadata.get('final_win_rate', 0) > 0:
            print(f"✅ {pkl_file.name}")
            print(f"   Win Rate: {metadata.get('final_win_rate', 0):.1f}%")
        else:
            print(f"⚠️  {pkl_file.name} (ancien modèle)")
            
    except Exception as e:
        print(f"❌ Erreur avec {pkl_file.name}: {e}")

# Sauvegarder les nouvelles métadonnées
with open(metadata_file, 'w') as f:
    json.dump(new_metadata, f, indent=2)

print(f"\n✅ Métadonnées reconstruites pour {count} modèles")
print(f"📁 Fichier: {metadata_file}")
print("\n💡 Relancez l'application et cliquez sur 'Refresh' dans Gestion des Modèles")
