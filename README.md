# 🎮 Morpion Q-Learning - Intelligence Artificielle par Apprentissage par Renforcement

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Pygame](https://img.shields.io/badge/pygame--ce-2.5+-green.svg)](https://github.com/pygame-community/pygame-ce)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Projet académique complet d'**Apprentissage par Renforcement (RL)** appliqué au jeu de Morpion. Interface graphique moderne, système de tournoi, optimisation automatique des hyperparamètres (AutoML), métriques avancées et mode Coach IA pour l'explainability.

---

## 📋 Table des Matières

- [✨ Fonctionnalités](#-fonctionnalités)
- [🚀 Démarrage Rapide](#-démarrage-rapide)
- [🎯 Modes de Jeu](#-modes-de-jeu)
- [🧠 Métriques d'Évaluation](#-métriques-dévaluation)
- [🏆 Système de Tournoi](#-système-de-tournoi)
- [🤖 AutoML](#-automl)
- [🧑‍🏫 Mode Coach](#-mode-coach)
- [🎨 Interface Moderne](#-interface-moderne)
- [📁 Architecture](#-architecture)
- [📖 Documentation](#-documentation)
- [🛠️ Technologies](#️-technologies)

---

## ✨ Fonctionnalités

### 🎲 **Jeu Complet**
- **5 modes de jeu** : Humain vs Humain, Humain vs IA, IA vs IA, Entraînement, Coach
- **3 niveaux de difficulté** : Débutant (ε=0.5), Intermédiaire (ε=0.2), Expert (ε=0)
- **Interface moderne** : Thème sombre élégant avec effets visuels (glow, ombres, dégradés)

### 🧠 **Apprentissage par Renforcement**
- **Algorithme Q-Learning** : Off-policy TD control avec exploration ε-greedy
- **Métriques avancées** : 10+ métriques incluant Bellman Error, TD Error, Sample Efficiency
- **Multi-seed evaluation** : Évaluation robuste avec 3-5 seeds différentes
- **Séparation train/eval** : Métriques calculées en post-training avec ε=0

### 🏆 **Système Compétitif**
- **Tournois automatiques** : Round-Robin et Élimination directe
- **Classement ELO** : Système de rating style échecs (1500±200 points)
- **218+ modèles** : Bibliothèque de modèles pré-entraînés

### 🤖 **Optimisation Automatique**
- **AutoML intégré** : Grid Search et Random Search
- **Optimisation multi-critères** : Composite Score, Sample Efficiency, Bellman Error
- **Configuration flexible** : Espaces d'hyperparamètres personnalisables

### 🧑‍🏫 **Explainability**
- **Mode Coach IA** : Suggestions en temps réel du meilleur coup
- **Visualisation Q-values** : Affichage coloré des scores de chaque case
- **Explications stratégiques** : Raisons du choix (attaque, défense, blocage)
- **Niveau de confiance** : Évaluation de la certitude de l'IA

### 📊 **Analyse et Visualisation**
- **Historique complet** : Toutes les parties sauvegardées
- **Graphiques détaillés** : Évolution des performances, learning curves
- **Statistiques avancées** : Win rate, moyenne, std, coefficient de variation
- **Export de données** : JSON, CSV pour analyse externe

---

## 🚀 Démarrage Rapide

### Prérequis
- **Python 3.9+** (testé avec Python 3.14)
- **pip** pour l'installation des dépendances

### Installation

```bash
# 1. Cloner le dépôt
git clone <votre-repo>
cd Projet_RL_JEU_Morpion

# 2. Créer environnement virtuel (recommandé)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt
```

### Lancement Rapide

```bash
# Interface graphique principale
python run.py

# Lancer un tournoi
python run_tournament.py

# Optimiser les hyperparamètres
python run_automl.py

# Analyser tous les modèles
python analyze_models.py

# Afficher métriques détaillées
python display_rl_metrics.py
```

---

## 🎯 Modes de Jeu

### 👥 **Humain vs Humain**
Jouez à deux sur le même ordinateur. Idéal pour tester l'interface.

### 🎮 **Humain vs IA**
Affrontez l'IA avec 3 niveaux de difficulté :
- **🌱 Débutant** : ε=0.5 (50% aléatoire)
- **⚡ Intermédiaire** : ε=0.2 (20% aléatoire)
- **🔥 Expert** : ε=0 (politique optimale pure)

**Raccourci** : Appuyez sur **C** pour activer le Mode Coach et voir les suggestions de l'IA

### 🤖 **IA vs IA**
Regardez deux IAs s'affronter pour comparer les stratégies.

### ⚡ **Entraînement Rapide**
Interface de configuration des hyperparamètres :
- Nombre d'épisodes : 1,000 - 1,000,000
- Learning rate (α) : 0.01 - 1.0
- Discount factor (γ) : 0.5 - 0.99
- Epsilon decay : linéaire ou exponentiel
- Post-training evaluation avec multi-seed

### 🧠 **Gestion des Modèles**
- **Liste complète** : 218+ modèles disponibles
- **Tri multi-critères** : Composite Score, Sample Efficiency, Bellman Error
- **Détails complets** : Hyperparamètres, métriques, historique
- **Actions** : Charger, renommer, supprimer, importer

---

## 🧠 Métriques d'Évaluation

Le projet implémente **10 métriques** pour évaluer la qualité des modèles RL :

### 📊 **Métriques Classiques**

| Métrique | Description | Formule | Bon Score |
|----------|-------------|---------|-----------|
| **Performance Score** | Taux de victoire + bonus nuls | `win_rate + 0.5 × draw_rate` | **> 85%** |
| **Efficiency Score** | Ratio perf/complexité | `win_rate / log(states + 1)` | **> 10** |
| **Learning Speed** | Vitesse d'apprentissage | `win_rate / log(episodes + 1)` | **> 8** |
| **Robustness Score** | Stabilité de la politique | `avg_reward × robustness_factor` | **> 0.6** |

### 🧠 **Métriques RL Avancées** (Nouvelles)

| Métrique | Signification | Interprétation | Bon Score |
|----------|---------------|----------------|-----------|
| **Bellman Error** | Convergence de la Q-table | Erreur moyenne sur équation de Bellman | **< 0.1** |
| **TD Error Mean** | Biais d'apprentissage | Moyenne des erreurs TD | **< 0.15** |
| **TD Error Variance** | Stabilité apprentissage | Variance des erreurs TD | **< 0.3** |
| **Return Variance** | Consistance de la politique | Variance des retours cumulés | **< 0.4** |
| **Sample Efficiency** | Efficacité d'apprentissage | `win_rate / (episodes / 1000)` | **> 5.0** |
| **Policy Entropy** | Déterminisme (0 = optimal) | Entropie de la politique π(s) | **< 0.5** |

### 🎯 **Score Global**

**Composite Score** : Score pondéré combinant toutes les métriques
- **Pondération** : Performance (35%), Efficiency (20%), RL metrics (45%)
- **Échelle** : 0-100
- **Excellence** : > 75
- **Bon** : 60-75
- **Acceptable** : 50-60

### 📈 **Évaluation Multi-Seed**

Chaque modèle est évalué avec **3-5 seeds différentes** pour garantir la robustesse :
- **Moyenne** : Performance moyenne sur tous les seeds
- **Écart-type** : Mesure de la variabilité
- **Min/Max** : Pire et meilleur cas
- **CV** (Coefficient de Variation) : Stabilité relative (< 5% = excellent)

**Exemple** :
```
Win Rate: 86.1% ± 0.7%  (min: 85.5%, max: 86.8%, CV: 0.8%)
        ↓         ↓                               ↓
     moyenne   écart-type                    très stable
```

**Documentation complète** : [docs/METRICS_GUIDE.md](docs/METRICS_GUIDE.md)

---

## 🏆 Système de Tournoi

### **Types de Tournois**

#### 🔄 **Round-Robin**
Chaque modèle affronte tous les autres :
- **Nombre de matchs** : n×(n-1)/2 pour n modèles
- **Parties par match** : Configurable (50-500)
- **Classement** : Par victoires puis différence de buts
- **Durée** : ~2-10 minutes selon modèles

#### 🏅 **Élimination Directe**
Bracket à élimination (8, 16, 32 modèles) :
- **Format** : Single elimination
- **Seed automatique** : Par ELO rating
- **Best-of** : 1, 3 ou 5 parties
- **Finales** : Demi-finales, petite finale, grande finale

### **Système ELO**

Chaque modèle a un **rating ELO** actualisé après chaque partie :

```python
# Formule
new_rating = old_rating + K × (score - expected_score)

# Paramètres
K = 32              # Facteur de changement
Initial = 1500      # Rating de départ
Score = 1 / 0.5 / 0 # Victoire / Nul / Défaite
```

**Classement typique** :
- **🏆 Élite** : > 1700 (top 5%)
- **⭐ Expert** : 1600-1700 (top 20%)
- **✅ Bon** : 1500-1600 (moyenne)
- **📚 En apprentissage** : < 1500

**Sauvegarde** : `models/elo_ratings.json`

**Lancer un tournoi** :
```bash
python run_tournament.py
# Choisir le type et la configuration dans l'interface
```

---

## 🤖 AutoML

Optimisation automatique des hyperparamètres pour trouver la meilleure configuration.

### **Algorithmes Disponibles**

#### 🔍 **Grid Search**
Teste toutes les combinaisons possibles :
- **Grid Fast** : Espace réduit (2-3 valeurs/paramètre) → ~100 configs
- **Grid Full** : Espace complet (5-7 valeurs/paramètre) → ~1000 configs
- **Avantage** : Exhaustif, trouve l'optimum global
- **Inconvénient** : Lent pour grands espaces

#### 🎲 **Random Search**
Échantillonnage aléatoire intelligent :
- **Iterations** : 10-50 (configurable)
- **Distribution** : Uniforme ou log-uniforme selon le paramètre
- **Avantage** : Rapide, bonne approximation
- **Inconvénient** : Peut manquer l'optimum

### **Espaces d'Hyperparamètres**

```python
# Configuration typique
alpha (learning rate):     [0.01, 0.05, 0.1, 0.3, 0.5, 0.7, 0.9]
gamma (discount factor):   [0.5, 0.7, 0.85, 0.9, 0.95, 0.99]
epsilon_start:             [0.8, 0.9, 1.0]
epsilon_min:               [0.001, 0.01, 0.05]
epsilon_decay:             [0.995, 0.998, 0.999, 0.9995]
```

### **Critères d'Optimisation**

Trois critères principaux (sélectionnable) :
1. **Composite Score** : Score global (défaut)
2. **Sample Efficiency** : Meilleur rapport performance/coût
3. **Bellman Error** : Meilleure convergence

### **Workflow AutoML**

```bash
# 1. Lancer AutoML
python run_automl.py

# 2. Choisir algorithme
#    → Random Search (rapide, recommandé)
#    → Grid Fast (exhaustif, moyen)

# 3. Configuration
#    Iterations: 20
#    Episodes: 10,000-50,000
#    Criterion: composite_score

# 4. Attendre résultats
#    Progression en temps réel
#    Meilleur modèle sauvegardé automatiquement

# 5. Charger le modèle optimisé
#    models/automl_best_YYYYMMDD_HHMMSS.pkl
```

**Durée typique** :
- Random Search (20 iter, 10k ep) : **~5-10 min**
- Grid Fast (100 configs, 10k ep) : **~30-60 min**
- Grid Full (1000 configs, 50k ep) : **~6-12 heures**

**Documentation** : [docs/FEATURES_GUIDE.md](docs/FEATURES_GUIDE.md)

---

## 🧑‍🏫 Mode Coach

Assistant IA en temps réel pour apprendre la stratégie optimale du Morpion.

### **Activation**
Appuyez sur **C** pendant une partie (Humain vs IA)

### **Panneau Coach** (boîte jaune)
```
┌─────────────────────┐
│   COACH IA          │
├─────────────────────┤
│ Coup: (1, 2)        │  ← Position recommandée
│ Q-value: 0.948      │  ← Score du coup (0-1)
│ CONFIANT            │  ← Niveau de confiance
│ ✓ Excellent coup    │  ← Explication stratégique
│ ⚡ Bloque victoire   │
└─────────────────────┘
```

### **Q-Values sur la Grille**

Chaque case vide affiche son **score Q** avec code couleur :
- 🟢 **Vert** (Q > 0.7) : Excellent coup
- 🟡 **Jaune** (0.3 < Q < 0.7) : Coup moyen
- 🔴 **Rouge** (Q < 0.3) : Mauvais coup

**Exemple** :
```
┌─────┬─────┬─────┐
│  X  │     │  O  │
│     │0.946│0.403│  ← Q-values affichés
├─────┼─────┼─────┤
│     │0.948│     │
│0.191│     │     │  ← 0.191 = mauvais
├─────┼─────┼─────┤
│     │     │     │
│0.170│0.175│0.485│
└─────┴─────┴─────┘
```

### **Explications Stratégiques**

Le Coach fournit des raisons contextuelles :
- **"Bloque victoire adverse"** : Défense urgente
- **"Crée double menace"** : Coup offensif fort
- **"Prend le centre"** : Stratégie positionnelle
- **"Force la main"** : Contrôle du jeu

### **Utilisation Pédagogique**

1. **Jouez naturellement** : Faites votre coup instinctif
2. **Comparez** : Regardez la suggestion du Coach
3. **Analysez** : Comprenez pourquoi l'alternative est meilleure
4. **Apprenez** : Intégrez les patterns stratégiques

**Raccourcis** :
- **C** : Toggle Coach (on/off)
- **D** : Toggle Debug (affiche tous les Q-values)

---

## 🎨 Interface Moderne

### **Design Dark Mode Élégant**

- **Palette** : Bleu nuit profond (#141923) avec accents cyan et corail
- **Symboles** :
  - ❌ **X** : Rouge corail (#ED6A5E) avec effet glow
  - ⭕ **O** : Bleu cyan (#63B3ED) avec effet glow
- **Grille** : Lignes avec effet glow subtil pour profondeur

### **Effets Visuels**

#### Boutons Modernes
- **Ombres portées** : Profondeur visuelle
- **Bordures arrondies** : 12px radius
- **Hover animé** : Changement de couleur + élévation
- **4 styles** : primary (bleu), success (vert), danger (rouge), neutral (gris)

#### Cartes (Cards)
- Fond semi-transparent avec blur
- Barre latérale colorée pour accentuation
- Organisation claire label/valeur
- Effet hover avec bordure lumineuse

#### Barres de Progression
- Dégradés horizontaux
- Highlight 3D en haut
- Texte avec ombre pour lisibilité

### **Typographie**

Hiérarchie claire avec 5 niveaux :
- **Title** : 56px - Titres principaux
- **Large** : 42px - Sous-titres
- **Medium** : 32px - Texte important
- **Small** : 24px - Texte normal
- **Tiny** : 18px - Détails

### **Responsive**

- Fenêtre : **900×1050px** (ajustée pour tous les boutons)
- Dimensionnement dynamique selon `window_size`
- Support multi-résolutions

**Documentation UI** : [docs/UI_IMPROVEMENTS.md](docs/UI_IMPROVEMENTS.md)

---

## 📁 Architecture

```
Projet_RL_JEU_Morpion/
│
├── 📂 engine/                    # Environnements de jeu
│   ├── environment.py            # Morpion 3x3 classique
│   ├── environment_extended.py   # Variantes 4x4, 5x5, Ultimate
│   └── __init__.py
│
├── 📂 rl_logic/                  # Logique d'apprentissage
│   ├── agent.py                  # Q-Learning Agent
│   ├── trainer.py                # Entraînement et évaluation
│   ├── metrics.py                # Calcul des 10 métriques
│   ├── model_manager.py          # Gestion des modèles
│   ├── model_comparator.py       # Comparaison de modèles
│   ├── elo_system.py             # Système de rating ELO
│   ├── tournament.py             # Tournois Round-Robin/Elimination
│   ├── automl.py                 # Optimisation hyperparamètres
│   ├── coach.py                  # Mode Coach IA
│   ├── visualization.py          # Graphiques et plots
│   ├── logger.py                 # Logging RL
│   ├── app_logger.py             # Logging application
│   ├── game_logger.py            # Logging parties
│   └── __init__.py
│
├── 📂 gui/                       # Interface Pygame
│   ├── pygame_app.py             # Application principale
│   ├── assets.py                 # Couleurs, polices, dessins
│   ├── view_game.py              # Interface de jeu
│   ├── view_stats.py             # Statistiques et graphiques
│   ├── view_history.py           # Historique des parties
│   ├── view_models.py            # Gestion des modèles
│   ├── view_tournament.py        # Interface tournoi
│   ├── view_automl.py            # Interface AutoML
│   └── __init__.py
│
├── 📂 models/                    # Modèles sauvegardés (218+)
│   ├── q_table.pkl               # Modèle par défaut
│   ├── best_score.pkl            # Meilleur composite score
│   ├── sample_eff_best.pkl       # Meilleur sample efficiency
│   ├── elo_ratings.json          # Classement ELO
│   ├── models_metadata.json      # Métadonnées tous modèles
│   └── tournament_history.json   # Historique tournois
│
├── 📂 logs/                      # Logs et historiques
│   ├── training_stats.csv        # Stats d'entraînement
│   ├── game_history.json         # Toutes les parties
│   └── evaluation_results.json   # Résultats évaluations
│
├── 📂 docs/                      # Documentation détaillée
│   ├── FEATURES_GUIDE.md         # Guide complet des features
│   ├── METRICS_GUIDE.md          # Documentation métriques
│   ├── METRICS_CLASSIFICATION.md # Classification métriques
│   ├── UI_IMPROVEMENTS.md        # Améliorations interface
│   ├── TRAIN_EVAL_FIXED.md       # Séparation train/eval
│   ├── MULTI_SEED_EVAL.md        # Évaluation multi-seed
│   ├── SORT_SYSTEM_GUIDE.md      # Système de tri
│   └── IMPLEMENTATION_SUMMARY.md # Résumé implémentation
│
├── 📜 run.py                     # Lancer GUI principal
├── 📜 run_tournament.py          # Lancer un tournoi
├── 📜 run_automl.py              # Lancer AutoML
├── 📜 analyze_models.py          # Analyser tous les modèles
├── 📜 display_rl_metrics.py      # Afficher métriques détaillées
├── 📜 rebuild_metadata.py        # Reconstruire métadonnées
├── 📜 test_metrics.py            # Tests métriques
├── 📜 test_display.py            # Tests affichage
├── 📜 requirements.txt           # Dépendances Python
├── 📜 LICENSE                    # Licence MIT
└── 📜 README.md                  # Ce fichier
```

---

## 📖 Documentation

### **Guides Complets**

- **[docs/FEATURES_GUIDE.md](docs/FEATURES_GUIDE.md)** - Guide détaillé de toutes les fonctionnalités
- **[docs/METRICS_GUIDE.md](docs/METRICS_GUIDE.md)** - Documentation complète des 10 métriques
- **[docs/UI_IMPROVEMENTS.md](docs/UI_IMPROVEMENTS.md)** - Design moderne et palette de couleurs
- **[docs/TRAIN_EVAL_FIXED.md](docs/TRAIN_EVAL_FIXED.md)** - Séparation train/eval et bonnes pratiques
- **[docs/MULTI_SEED_EVAL.md](docs/MULTI_SEED_EVAL.md)** - Évaluation robuste multi-seed

### **Documentation Technique**

- **[docs/METRICS_CLASSIFICATION.md](docs/METRICS_CLASSIFICATION.md)** - Classification détaillée des métriques
- **[docs/SORT_SYSTEM_GUIDE.md](docs/SORT_SYSTEM_GUIDE.md)** - Système de tri multi-critères
- **[docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)** - Résumé de l'architecture

---

## 🛠️ Technologies

### **Backend**
- **Python 3.9+** (testé jusqu'à 3.14)
- **NumPy** - Calculs matriciels et Q-table
- **Pandas** - Analyse de données et statistiques
- **Matplotlib** - Visualisations et graphiques

### **Frontend**
- **Pygame-CE 2.5+** - Interface graphique moderne
  - Rendu 2D accéléré
  - Gestion événements
  - Animations fluides

### **Machine Learning**
- **Q-Learning** - Algorithme de base (from scratch)
- **ε-greedy** - Stratégie d'exploration
- **Bellman Equation** - Mise à jour valeurs Q
- **TD Learning** - Temporal Difference

### **Outils**
- **JSON** - Sauvegarde modèles et métadonnées
- **Pickle** - Sérialisation Q-tables
- **CSV** - Export statistiques

---

## 🐛 Dépannage

### **L'IA joue mal**
- ✅ Vérifiez `epsilon` : doit être ~0.01 pour Expert
- ✅ États appris : minimum 2000-3000
- ✅ Entraînez plus longtemps : 50k-100k épisodes

### **AutoML trop lent**
- ✅ Réduisez les épisodes : 5k-10k pour tests rapides
- ✅ Utilisez Random Search au lieu de Grid
- ✅ Limitez à 10-20 itérations

### **Erreur "pygame not found"**
```bash
pip install pygame-ce  # Pour Python 3.14+
# ou
pip install pygame     # Pour Python 3.9-3.13
```

### **Modèles introuvables**
```bash
python rebuild_metadata.py  # Reconstruire l'index
```

### **Performances lentes**
- Désactivez les effets visuels dans `assets.py`
- Réduisez la fréquence de rafraîchissement (ligne 228 de `pygame_app.py`)

---

## 🚀 Roadmap & Améliorations Futures

### **Court Terme**
- [ ] Interface web (Flask/Streamlit)
- [ ] Export tournois en PDF
- [ ] Replay animé des parties
- [ ] Mode spectateur amélioré

### **Moyen Terme**
- [ ] Deep Q-Learning (DQN)
- [ ] Réseau de neurones au lieu de Q-table
- [ ] Transfer learning entre variantes
- [ ] Multi-agent RL (Self-play)

### **Long Terme**
- [ ] Policy Gradient Methods (REINFORCE, A3C)
- [ ] AlphaZero-style MCTS
- [ ] Multijoueur en ligne
- [ ] API REST pour intégration externe

---

## 📄 Licence

Ce projet est sous licence **MIT**. Voir [LICENSE](LICENSE) pour plus de détails.

---

## 👨‍💻 Auteur & Contributions

**Projet Académique** - Cours de Machine Learning

Ce projet démontre :
- ✅ Implémentation complète d'un algorithme RL from scratch
- ✅ Architecture modulaire et maintenable
- ✅ Interface utilisateur professionnelle
- ✅ Métriques rigoureuses et évaluation robuste
- ✅ Optimisation automatique (AutoML)
- ✅ Explainability et pédagogie (Mode Coach)

---

**🎮 Bon jeu et bon apprentissage !**

*Pour débuter, lancez simplement `python run.py` et explorez les différents modes.*
