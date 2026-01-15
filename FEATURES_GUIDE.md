# 🎮 Guide Complet des Fonctionnalités - Morpion Q-Learning RL

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Modes de Jeu](#modes-de-jeu)
3. [Système de Tournoi](#système-de-tournoi)
4. [AutoML - Optimisation Automatique](#automl---optimisation-automatique)
5. [Mode Coach IA](#mode-coach-ia)
6. [Variantes de Jeu](#variantes-de-jeu)
7. [Visualisations](#visualisations)
8. [Système ELO](#système-elo)
9. [Commandes et Utilisation](#commandes-et-utilisation)

---

## 🎯 Vue d'ensemble

Ce projet implémente un système complet de **Reinforcement Learning** pour le jeu de Morpion, avec des fonctionnalités avancées d'analyse, de compétition et d'optimisation automatique.

### Fonctionnalités Principales

✅ **Modes de Jeu Classiques**
- Humain vs Humain
- Humain vs IA (3 niveaux)
- IA vs IA

✅ **Système de Tournoi**
- Round-Robin (tous contre tous)
- Élimination directe (bracket)
- Classement ELO des modèles

✅ **AutoML**
- Grid Search automatique
- Random Search
- Optimisation des hyperparamètres

✅ **Mode Coach IA**
- Hints en temps réel
- Explication des coups
- Visualisation des Q-values

✅ **Variantes de Jeu**
- Morpion 4x4
- Morpion 5x5
- Ultimate Tic-Tac-Toe

✅ **Métriques Avancées**
- Performance Score
- Efficiency Score
- Robustness Score
- Learning Speed
- Composite Score

---

## 🎮 Modes de Jeu

### 1. Humain vs Humain 👥
Jouez à deux sur le même ordinateur.

**Utilisation:**
```python
python run.py
# Menu → Humain vs Humain
```

### 2. Humain vs IA 🎯
Affrontez l'IA avec 3 niveaux de difficulté:
- **Débutant** (ε=0.5): L'IA explore encore, fait des erreurs
- **Intermédiaire** (ε=0.2): Bon niveau, quelques erreurs
- **Expert** (ε=0.0): Joue toujours le meilleur coup

**Utilisation:**
```python
python run.py
# Menu → Humain vs IA → Sélectionnez le niveau
```

### 3. IA vs IA 🤖
Regardez deux IAs s'affronter.

---

## 🏆 Système de Tournoi

### Tournoi Round-Robin

**Description:**
Chaque modèle joue contre tous les autres. Le classement est basé sur les points:
- Victoire: 3 points
- Nul: 1 point
- Défaite: 0 point

**Utilisation:**

```bash
# Via script
python run_tournament.py

# Via GUI
python run.py
# Menu → Tournoi → Sélectionnez les modèles → Round-Robin
```

**Exemple de sortie:**
```
🏆 CLASSEMENT FINAL
═══════════════════════════════════════════════════════════
🥇 model_expert_v5.pkl
   Points: 15 | W-D-L: 5-0-0 | ELO: 1650

🥈 model_advanced_v3.pkl
   Points: 9 | W-D-L: 3-0-2 | ELO: 1520

🥉 model_baseline.pkl
   Points: 6 | W-D-L: 2-0-3 | ELO: 1480
```

### Tournoi à Élimination

**Description:**
Format bracket à élimination directe. Les gagnants avancent jusqu'à la finale.

**Caractéristiques:**
- Automatic bye pour nombre impair
- Sudden death en cas d'égalité
- Affichage du champion

---

## 🤖 AutoML - Optimisation Automatique

### Grid Search

**Description:**
Teste **toutes** les combinaisons d'hyperparamètres.

**Configuration par défaut:**
```python
param_grid = {
    'alpha': [0.1, 0.15, 0.2, 0.25, 0.3],        # 5 valeurs
    'gamma': [0.90, 0.92, 0.95, 0.97, 0.99],     # 5 valeurs
    'epsilon_decay': [0.990, 0.995, 0.997, 0.999] # 4 valeurs
}
# Total: 5 × 5 × 4 = 100 configurations
```

**Utilisation:**
```bash
python run_automl.py

# Choisir Grid Search
# Entrer le nombre d'épisodes (ex: 10000)
# Entrer le nombre de parties d'évaluation (ex: 100)
```

**Temps estimé:**
- Grid Fast (18 configs): ~15-30 minutes
- Grid Full (100 configs): ~1-2 heures

### Random Search

**Description:**
Échantillonne aléatoirement dans l'espace des hyperparamètres.

**Distributions par défaut:**
```python
param_distributions = {
    'alpha': (0.05, 0.5),
    'gamma': (0.85, 0.99),
    'epsilon_decay': (0.98, 0.9999),
    'epsilon_min': (0.001, 0.1)
}
```

**Avantages:**
- Plus rapide que Grid Search
- Explore mieux l'espace
- Bon pour trouver des configurations surprenantes

**Utilisation:**
```bash
python run_automl.py
# Choisir Random Search
# Entrer le nombre d'itérations (ex: 20)
```

### Résultats

Les résultats sont sauvegardés dans `models/automl_results.csv`:
```csv
config_id,timestamp,config_alpha,config_gamma,win_rate,composite_score,...
1,2026-01-15T12:00:00,0.2,0.95,0.85,87.5,...
2,2026-01-15T12:15:00,0.15,0.99,0.88,89.2,...
```

**Meilleure configuration affichée:**
```
🏆 MEILLEURE CONFIGURATION (Score: 89.2)
  alpha: 0.15
  gamma: 0.99
  epsilon_decay: 0.997
```

---

## 🧑‍🏫 Mode Coach IA

### Description

Le Mode Coach affiche en temps réel:
1. **Meilleur coup** suggéré
2. **Q-value** du coup
3. **Niveau de confiance** de l'IA
4. **Explication** stratégique

### Activation

**Méthode 1: Via le menu**
```python
python run.py
# Menu → Mode Coach (toggle)
```

**Méthode 2: Pendant le jeu**
Appuyez sur la touche `C` pendant une partie

### Interface

```
┌─────────────────────────┐
│   🧑‍🏫 COACH IA          │
├─────────────────────────┤
│ Meilleur coup: (1, 1)   │
│ Q-value: 0.875          │
│ Confiance: TRÈS CONFIANT│
│                         │
│ 🛡️ BLOQUE l'adversaire  │
│ 📍 Contrôle le centre   │
│ ✨ Excellent coup       │
└─────────────────────────┘
```

### Types d'explications

- 🏆 **Coup gagnant**: Ce coup vous fait gagner immédiatement
- 🛡️ **Bloque l'adversaire**: Empêche l'adversaire de gagner
- 📍 **Contrôle le centre**: Position stratégique centrale
- 📐 **Position de coin**: Coin stratégique
- ⚔️ **Crée une menace**: Aligne 2 symboles
- ✨ **Excellent coup**: Q-value > 0.8

### Niveaux de confiance

- **TRÈS CONFIANT**: Différence de Q-value > 0.5
- **CONFIANT**: Différence > 0.2
- **ASSEZ SÛR**: Différence > 0.05
- **PEU SÛR**: Différence > 0
- **HÉSITANT**: Plusieurs coups équivalents

---

## 🎲 Variantes de Jeu

### Morpion 4x4

**Règles:**
- Plateau 4×4 (16 cases)
- Toujours 3 alignés pour gagner
- Plus de possibilités stratégiques

**Utilisation:**
```python
from engine.environment_extended import TicTacToeExtended

env = TicTacToeExtended(board_size=4, win_length=3)
```

### Morpion 5x5

**Règles:**
- Plateau 5×5 (25 cases)
- 3 alignés pour gagner
- Jeu beaucoup plus complexe

```python
env = TicTacToeExtended(board_size=5, win_length=3)
```

### Ultimate Tic-Tac-Toe

**Règles:**
- 9 plateaux 3×3 dans un grand plateau 3×3
- Quand vous jouez dans une case, cela détermine le sous-plateau où l'adversaire doit jouer
- Gagnez 3 sous-plateaux alignés pour gagner le jeu

```python
from engine.environment_extended import UltimateTicTacToe

env = UltimateTicTacToe()
```

### Variantes avec Contraintes

**Centre interdit:**
```python
from engine.environment_extended import MorpionVariants

env = TicTacToeExtended(board_size=3)
# Vérifier avant chaque coup:
if not MorpionVariants.no_center_rule(env):
    print("Le centre est interdit!")
```

**Coins obligatoires (premiers coups):**
```python
legal_actions = MorpionVariants.corners_first_rule(env, moves_count)
```

---

## 📊 Visualisations

### Q-table Heatmap

**Description:**
Affiche les Q-values sous forme de carte de chaleur colorée.

**Utilisation:**
```python
from rl_logic.visualization import QTableVisualizer

visualizer = QTableVisualizer(screen, assets)
visualizer.draw_q_values_for_state(board, q_values)
```

**Couleurs:**
- 🟢 Vert: Q-value élevée (bon coup)
- 🟡 Jaune: Q-value moyenne
- 🔵 Bleu: Q-value faible (mauvais coup)

### Graphiques d'Entraînement

**Temps Réel:**
```python
from rl_logic.visualization import RealtimeTrainingVisualization

viz = RealtimeTrainingVisualization(screen, assets)
viz.update(episode, win_rate, epsilon)
viz.draw()
```

**Post-Entraînement:**
```python
from rl_logic.visualization import TrainingGraphs

graph = TrainingGraphs.create_training_progress_graph(
    episodes, win_rates, epsilons
)
screen.blit(graph, (0, 0))
```

### Dashboard Comparatif

**Description:**
Compare visuellement les performances de tous les modèles.

```python
graph = TrainingGraphs.create_metrics_comparison_chart(models_data)
```

Affiche un graphique en barres avec:
- 🟢 Vert: Score ≥ 80
- 🟠 Orange: Score ≥ 60
- 🔴 Rouge: Score < 60

---

## 🏅 Système ELO

### Principe

Le système ELO (comme aux échecs) classe les modèles selon leurs performances en match:
- Rating initial: **1500**
- Victoire: Gagne des points ELO
- Défaite: Perd des points ELO
- Les points gagnés/perdus dépendent de la différence de rating

### Formule

```
Score attendu = 1 / (1 + 10^((Rating_B - Rating_A) / 400))
Nouveau rating = Rating ancien + K × (Score réel - Score attendu)
```

Où:
- **K = 32** (facteur de sensibilité)
- **Score réel**: 1 (victoire), 0.5 (nul), 0 (défaite)

### Exemple

```
Avant match:
  Model A: 1500 ELO
  Model B: 1600 ELO

Score attendu pour A: 0.36 (36% de chances de gagner)

Si A gagne:
  Nouveau rating A: 1500 + 32 × (1 - 0.36) = 1520 (+20)
  Nouveau rating B: 1600 + 32 × (0 - 0.64) = 1580 (-20)
```

### Classement

```bash
python run_tournament.py
# Après le tournoi, voir le classement ELO
```

**Fichier de sauvegarde:** `models/elo_ratings.json`

---

## 💻 Commandes et Utilisation

### Installation

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer (Windows)
venv\Scripts\activate

# Activer (Linux/Mac)
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Lancer l'Interface GUI

```bash
python run.py
```

### Scripts Spécialisés

**Tournoi:**
```bash
python run_tournament.py
```

**AutoML:**
```bash
python run_automl.py
```

**Analyse de modèles:**
```bash
python analyze_models.py
```

**Rebuild metadata (si nécessaire):**
```bash
python rebuild_metadata.py
```

### Raccourcis Clavier (en jeu)

- `C`: Toggle Mode Coach
- `D`: Toggle Mode Debug (affiche Q-values)
- `ESPACE`: Rejouer (après une partie)
- `ECHAP`: Retour au menu

---

## 📈 Métriques Détaillées

Voir `METRICS_GUIDE.md` pour les détails complets des métriques.

### Résumé Rapide

| Métrique | Description | Formule | Bon Score |
|----------|-------------|---------|-----------|
| **Performance** | Victoires + nuls | `win_rate + 0.5×draw_rate` | > 80% |
| **Efficiency** | Efficacité d'apprentissage | `win_rate / log(states)` | > 10 |
| **Robustness** | Stabilité | `avg_reward × factor` | > 0.5 |
| **Learning Speed** | Vitesse d'apprentissage | `win_rate / log(episodes)` | > 8 |
| **Composite** | Score global | `0.4×P + 0.25×E + 0.2×R + 0.15×L` | > 70 |

---

## 🎓 Pour Aller Plus Loin

### Optimiser un Modèle

1. **AutoML** pour trouver les meilleurs hyperparamètres
2. **Entraîner** avec ces hyperparamètres (50k-100k épisodes)
3. **Tournoi** pour valider les performances
4. **Coach** pour analyser la stratégie

### Créer un Modèle Champion

```bash
# 1. Optimiser les hyperparamètres
python run_automl.py
# Choisir Random Search, 30 itérations, 15000 épisodes

# 2. Noter la meilleure config (ex: alpha=0.18, gamma=0.97, decay=0.9975)

# 3. Entraîner un modèle final
python run.py
# Menu → Entraînement Rapide
# Entrer 100000 épisodes

# 4. Tester en tournoi
python run_tournament.py
# Round-Robin avec tous les modèles

# 5. Analyser avec le Coach
python run.py
# Mode Coach activé, jouer contre le modèle
```

---

## 📁 Structure des Fichiers

```
Projet_RL_JEU_Morpion/
├── engine/
│   ├── environment.py          # Environnement 3x3 classique
│   └── environment_extended.py # Variantes 4x4, 5x5, Ultimate
├── rl_logic/
│   ├── agent.py                # Agent Q-Learning
│   ├── trainer.py              # Entraînement
│   ├── metrics.py              # Calcul des métriques
│   ├── model_comparator.py     # Comparaison de modèles
│   ├── model_manager.py        # Gestion des modèles
│   ├── elo_system.py           # Système ELO
│   ├── tournament.py           # Tournois
│   ├── automl.py               # AutoML
│   ├── coach.py                # Mode Coach
│   └── visualization.py        # Visualisations
├── gui/
│   ├── pygame_app.py           # Application principale
│   ├── view_game.py            # Vue du jeu
│   ├── view_stats.py           # Vue statistiques
│   ├── view_models.py          # Gestion des modèles
│   ├── view_tournament.py      # Interface tournoi
│   └── view_automl.py          # Interface AutoML
├── models/                     # Modèles sauvegardés
│   ├── *.pkl                   # Fichiers de modèles
│   ├── models_metadata.json    # Métadonnées
│   ├── elo_ratings.json        # Ratings ELO
│   ├── tournament_history.json # Historique tournois
│   └── automl_results.csv      # Résultats AutoML
├── logs/                       # Logs et historiques
├── run.py                      # Lancer le GUI
├── run_tournament.py           # Lancer un tournoi
├── run_automl.py               # Lancer AutoML
├── FEATURES_GUIDE.md          # Ce fichier
└── METRICS_GUIDE.md           # Guide des métriques
```

---

## 🎯 Bonnes Pratiques

### Pour l'Entraînement

1. **Commencer petit**: 10k épisodes pour tester
2. **Augmenter progressivement**: 50k, 100k, 200k
3. **Sauvegarder régulièrement**: Ne perdez pas vos progrès
4. **Comparer**: Utilisez les métriques pour évaluer

### Pour les Tournois

1. **Sélectionner 5-10 modèles**: Ne surchargez pas
2. **100 parties/match minimum**: Pour des résultats statistiques fiables
3. **Round-Robin pour classement**: Élimination pour le fun
4. **Analyser les résultats**: Qui bat qui ? Pourquoi ?

### Pour l'AutoML

1. **Random Search d'abord**: Plus rapide, bonnes approximations
2. **Grid Search autour des meilleurs**: Affiner
3. **Plusieurs exécutions**: La randomisation peut varier les résultats
4. **Garder un log**: Notez les meilleures configs

---

## 🐛 Dépannage

### L'IA joue mal

- Vérifiez epsilon (doit être proche de 0 pour Expert)
- Le modèle a-t-il assez d'états appris ? (>100)
- Entraînez plus longtemps

### AutoML lent

- Réduisez le nombre d'épisodes (5k-10k pour tests rapides)
- Utilisez Grid Fast au lieu de Grid Full
- Random Search avec moins d'itérations (10-15)

### Tournoi ne se lance pas

- Au moins 2 modèles requis
- Vérifiez que les modèles se chargent (`models_view`)
- Regardez les logs dans `logs/`

### Mode Coach ne s'affiche pas

- Appuyez sur `C` pendant une partie
- Vérifiez que vous jouez contre l'IA (Humain vs IA)
- L'agent doit avoir des états appris

---

## 📞 Support

Pour toute question ou problème:
1. Consultez `METRICS_GUIDE.md` pour les métriques
2. Vérifiez les logs dans `logs/`
3. Testez avec `test_metrics.py` et `test_display.py`

---

## 🚀 Roadmap Future (Idées)

- [ ] Interface web (Flask/Streamlit)
- [ ] Deep Q-Learning (DQN)
- [ ] Multijoueur en ligne
- [ ] Analyse vidéo des parties
- [ ] Export des tournois en PDF
- [ ] Replay animé des parties
- [ ] Bracket visualization graphique
- [ ] Mode spectateur avec commentaires IA

---

**Bon jeu et bon apprentissage ! 🎮🤖**
