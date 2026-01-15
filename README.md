# 🎮 Morpion - Q-Learning Reinforcement Learning

Projet complet de **Reinforcement Learning** pour le jeu de Morpion avec interface Pygame, système de tournoi, AutoML et métriques avancées.

## 🚀 Démarrage Rapide

### Installation

```bash
# Créer et activer l'environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt
```

### Lancer l'application

```bash
python run.py
```

## ✨ Fonctionnalités Principales

### 🎯 Modes de Jeu
- **👥 Humain vs Humain** - Jouez à deux
- **🎮 Humain vs IA** - Affrontez l'IA (3 niveaux de difficulté)
- **🤖 IA vs IA** - Regardez deux IAs s'affronter
- **⚡ Entraînement Rapide** - Entraînez un nouveau modèle

### 🏆 Système de Tournoi
- **Round-Robin** - Tous les modèles s'affrontent
- **Élimination** - Bracket à élimination directe
- **Classement ELO** - Rating style échecs pour chaque modèle

```bash
python run_tournament.py
```

### 🤖 AutoML - Optimisation Automatique
Trouve automatiquement les meilleurs hyperparamètres :
- **Grid Search** - Teste toutes les combinaisons
- **Random Search** - Échantillonnage aléatoire intelligent

```bash
python run_automl.py
```

### 🧑‍🏫 Mode Coach IA
Assistance en temps réel pendant le jeu :
- Suggestions du meilleur coup
- Explication stratégique
- Visualisation des Q-values
- Niveau de confiance de l'IA

**Activation :** Appuyez sur `C` pendant une partie

### 📊 Métriques Avancées
- **Performance Score** - Taux de victoire + nuls
- **Efficiency Score** - Rapport performance/états appris
- **Robustness Score** - Stabilité et cohérence
- **Learning Speed** - Vitesse d'apprentissage
- **Composite Score** - Score global pondéré

### 🎲 Variantes de Jeu
- Morpion **4x4** et **5x5**
- **Ultimate Tic-Tac-Toe** (9 plateaux)
- Variantes avec contraintes

## 📁 Structure du Projet

```
Projet_RL_JEU_Morpion/
├── engine/              # Environnements de jeu
│   ├── environment.py           # Morpion 3x3 classique
│   └── environment_extended.py  # Variantes 4x4, 5x5, Ultimate
├── rl_logic/            # Logique RL
│   ├── agent.py                 # Agent Q-Learning
│   ├── trainer.py               # Entraînement
│   ├── metrics.py               # Calcul des métriques
│   ├── model_manager.py         # Gestion des modèles
│   ├── elo_system.py            # Système ELO
│   ├── tournament.py            # Tournois
│   ├── automl.py                # AutoML
│   ├── coach.py                 # Mode Coach
│   └── visualization.py         # Visualisations
├── gui/                 # Interface Pygame
│   ├── pygame_app.py            # Application principale
│   ├── view_game.py             # Vue du jeu
│   ├── view_tournament.py       # Interface tournoi
│   ├── view_automl.py           # Interface AutoML
│   └── view_models.py           # Gestion des modèles
├── models/              # Modèles sauvegardés
├── logs/                # Logs et historiques
├── run.py               # Lancer le GUI
├── run_tournament.py    # Lancer un tournoi
└── run_automl.py        # Lancer AutoML
```

## 🎯 Utilisation

### Menu Principal

```
┌─────────────────────────────────────┐
│   MORPION - Q-LEARNING              │
├─────────────────────────────────────┤
│ 👥 Humain vs Humain                 │
│ 🎮 Humain vs IA                     │
│ 🤖 IA vs IA                         │
│ ⚡ Entraînement Rapide              │
│ 📊 Statistiques                     │
│ 📜 Historique des Parties           │
│ 🧠 Gestion des Modèles              │
│ 🏆 Tournoi                          │
│ 🤖 AutoML                           │
│ 🧑‍🏫 Mode Coach                     │
└─────────────────────────────────────┘
```

### Raccourcis Clavier

- **C** - Toggle Mode Coach (en jeu)
- **D** - Toggle Mode Debug (affiche Q-values)
- **ESPACE** - Rejouer après une partie
- **ECHAP** - Retour au menu

## 📖 Guides Détaillés

- **[FEATURES_GUIDE.md](FEATURES_GUIDE.md)** - Guide complet de toutes les fonctionnalités
- **[METRICS_GUIDE.md](METRICS_GUIDE.md)** - Documentation détaillée des métriques

## 🔧 Scripts Utiles

### Analyser tous les modèles
```bash
python analyze_models.py
```

### Reconstruire les métadonnées
```bash
python rebuild_metadata.py
```

### Tests
```bash
python test_metrics.py
python test_display.py
```

## 📊 Exemple de Workflow

### 1. Optimiser les Hyperparamètres
```bash
python run_automl.py
# Choisir Random Search
# 20 itérations, 10000 épisodes
```

### 2. Entraîner le Modèle Final
```bash
python run.py
# Menu → Entraînement Rapide
# 100000 épisodes avec les meilleurs hyperparamètres
```

### 3. Évaluer en Tournoi
```bash
python run_tournament.py
# Round-Robin avec tous les modèles
# 100 parties par match
```

### 4. Analyser avec le Coach
```bash
python run.py
# Mode Coach activé
# Jouer contre le meilleur modèle
```

## 🏆 Système ELO

Chaque modèle a un **rating ELO** (comme aux échecs) :
- Rating initial : **1500**
- Victoire : **+20 à +32 points** (selon l'adversaire)
- Défaite : **-20 à -32 points**

Classement sauvegardé dans `models/elo_ratings.json`

## 📈 Métriques - Résumé Rapide

| Métrique | Formule | Bon Score |
|----------|---------|-----------|
| Performance | `win_rate + 0.5×draw_rate` | > 80% |
| Efficiency | `win_rate / log(states)` | > 10 |
| Robustness | `avg_reward × factor` | > 0.5 |
| Learning Speed | `win_rate / log(episodes)` | > 8 |
| **Composite** | `Moyenne pondérée` | **> 70** |

## 🛠️ Technologies

- **Python 3.9+**
- **Pygame** - Interface graphique
- **NumPy** - Calculs numériques
- **Pandas** - Analyse de données
- **Matplotlib** - Visualisations

## 📝 Dépendances

```txt
pygame>=2.5.0
numpy>=1.24.0
pandas>=2.0.0
matplotlib>=3.8.0
```

## 🎓 Concepts RL Implémentés

- **Q-Learning** - Algorithme de base
- **ε-greedy** - Exploration vs Exploitation
- **Decay d'epsilon** - Réduction progressive de l'exploration
- **State-Action Values** - Q-table
- **Reward Shaping** - Structure des récompenses
- **Model Evaluation** - Métriques avancées

## 🐛 Dépannage

### L'IA joue mal
- Vérifiez epsilon (doit être ~0 pour Expert)
- Le modèle a-t-il >100 états appris ?
- Entraînez plus longtemps

### AutoML trop lent
- Réduisez les épisodes (5k-10k pour tests)
- Utilisez Grid Fast au lieu de Grid Full
- Random Search avec 10-15 itérations

### Erreurs au lancement
- Vérifiez que toutes les dépendances sont installées
- Activez bien le venv
- Consultez les logs dans `logs/`

## 🚀 Améliorations Futures

- [ ] Interface web (Flask/Streamlit)
- [ ] Deep Q-Learning (DQN)
- [ ] Multijoueur en ligne
- [ ] Replay animé des parties
- [ ] Export tournois en PDF
- [ ] Bracket visualization graphique

## 👨‍💻 Développement

Ce projet démontre :
- ✅ Reinforcement Learning from scratch
- ✅ Architecture modulaire et extensible
- ✅ Interface utilisateur complète
- ✅ Métriques et évaluation rigoureuses
- ✅ AutoML et optimisation automatique
- ✅ Explainability (Mode Coach)

## 📄 Licence

Voir fichier [LICENSE](LICENSE)

---

**Bon jeu et bon apprentissage ! 🎮🤖**

*Pour plus de détails, consultez [FEATURES_GUIDE.md](FEATURES_GUIDE.md)*
