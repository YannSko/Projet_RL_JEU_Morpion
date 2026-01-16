# 🎨 Guide Visuel - Interface de Gestion des Modèles

## 📐 Layout de l'Interface

```
┌─────────────────────────────────────────────────────────────────────┐
│                    🎮 MORPION RL - MODÈLES                          │
├──────────────────────────────┬──────────────────────────────────────┤
│                              │                                      │
│  📋 LISTE DES MODÈLES        │    📊 DÉTAILS DU MODÈLE             │
│  (côté gauche)               │    (côté droit)                      │
│                              │                                      │
│  ► model_85000ep...          │    🏆 Score: 85.2/100                │
│    Win: 95%                  │    model_85000ep_20260115_164538     │
│    15/01 16:45               │    15/01 16:45                       │
│                              │                                      │
│    model_50000ep...          │    ─ PERFORMANCE ─                   │
│    Win: 92%                  │    Épisodes: 85,000                  │
│    15/01 21:40               │    Win: 95.0%                        │
│                              │    Draw: 3.5%                        │
│    model_10000ep...          │    Loss: 1.5%                        │
│    Win: 88%                  │                                      │
│    15/01 21:15               │    ─ HYPERPARAMS ─                   │
│                              │    α: 0.15                           │
│  [Plus de modèles...]        │    γ: 0.92                           │
│                              │    ε final: 0.01                     │
│                              │    ε decay: 0.9995                   │
│                              │                                      │
│                              │    ─ MÉTRIQUES ─                     │
│                              │    Perf: 85.0         🟢             │
│                              │    Efficacité: 28.5   🟢             │
│                              │    Robustesse: 1.85   🟢             │
│                              │    Sample Eff: 1.73   🟡             │
│                              │    Bellman: 0.1523    🟡             │
│                              │    RetVar: 0.385      🟡             │
│                              │    Entropy: 0.428     🟡             │
│                              │                                      │
├──────────────────────────────┴──────────────────────────────────────┤
│                                                                     │
│  [Tri: 🏆 Score]  [📥 Importer]  [✏️ Renommer]  [🗑️ Supprimer]    │
│                                                                     │
│  [◀ Préc.]  [📥 Charger]  [🏆 Meilleur]  [🔄 Refresh]  [Suiv. ▶]  │
│                                                                     │
│                  Page 1/5 | Total: 218 modèles                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 🎯 Sections Expliquées

### 📋 Liste des Modèles (Gauche)

```
┌──────────────────────────────┐
│  ► model_85000ep...          │  ← Modèle sélectionné (bleu foncé)
│    Win: 95%                  │     avec bordure verte
│    15/01 16:45               │
├──────────────────────────────┤
│  ● model_current...          │  ← Modèle actuellement chargé
│    Win: 90%                  │     (fond vert foncé)
│    14/01 12:30               │
├──────────────────────────────┤
│    model_50000ep...          │  ← Modèle normal
│    Win: 85%                  │     (alternance gris clair/foncé)
│    13/01 18:20               │
└──────────────────────────────┘

Indicateurs:
► = Sélectionné
● = Chargé actuellement
  = Non sélectionné
```

### 📊 Détails du Modèle (Droite)

#### Score Composite
```
┌────────────────────────────┐
│   🏆 Score: 85.2/100       │  ← En haut, grand, couleur selon valeur
└────────────────────────────┘
  🟢 Vert  : > 80 (excellent)
  🟡 Jaune : 60-80 (bon)
  🔴 Rouge : < 60 (faible)
```

#### Section MÉTRIQUES
```
─ MÉTRIQUES ─
┌───────────────────────────┐
│ Perf: 85.0         🟢     │  ← Métriques classiques
│ Efficacité: 28.5   🟢     │
│ Robustesse: 1.85   🟢     │
├───────────────────────────┤
│ Sample Eff: 1.73   🟡     │  ← NOUVELLES métriques RL
│ Bellman: 0.1523    🟡     │     (maintenant ici !)
│ RetVar: 0.385      🟡     │
│ Entropy: 0.428     🟡     │
└───────────────────────────┘
```

## 🔘 Boutons et Actions

### Ligne du Haut (Gestion)
```
┌─────────────────┬─────────────┬──────────────┬──────────────┐
│ Tri: 🏆 Score  │ 📥 Importer │ ✏️ Renommer  │ 🗑️ Supprimer │
└─────────────────┴─────────────┴──────────────┴──────────────┘
     ↓ Clic
┌─────────────────┐
│ Tri: ⚡ Sample │  ← Change de critère
└─────────────────┘
     ↓ Clic
┌─────────────────┐
│ Tri: 🎯 Bellman│
└─────────────────┘
     ↓ Clic
┌─────────────────┐
│ Tri: 🏆 Score  │  ← Retour au début
└─────────────────┘
```

### Ligne du Bas (Navigation)
```
┌──────────┬──────────┬──────────┬──────────┬──────────┐
│ ◀ Préc. │ 📥 Charg │ 🏆 Meill │ 🔄 Refre │ Suiv. ▶ │
└──────────┴──────────┴──────────┴──────────┴──────────┘

Actions:
- ◀ Préc.    : Page précédente
- 📥 Charger : Charge le modèle SÉLECTIONNÉ
- 🏆 Meilleur: Charge automatiquement le meilleur composite_score
- 🔄 Refresh : Recharge la liste des modèles
- Suiv. ▶    : Page suivante
```

## 🎨 Code Couleur des Métriques

### Sample Efficiency
```
🟢 Vert  (> 5.0)   : ████████████  Apprend TRÈS vite
🟡 Jaune (2.0-5.0) : ████████░░░░  Apprend efficacement
🔴 Rouge (< 2.0)   : ████░░░░░░░░  Apprend lentement
```

### Bellman Error
```
🟢 Vert  (< 0.1)   : ████████████  Q-table très convergée
🟡 Jaune (0.1-0.3) : ████████░░░░  Convergence acceptable
🔴 Rouge (> 0.3)   : ████░░░░░░░░  Convergence insuffisante
```

### Return Variance
```
🟢 Vert  (< 0.3)   : ████████████  Politique très stable
🟡 Jaune (0.3-0.5) : ████████░░░░  Stabilité acceptable
🔴 Rouge (> 0.5)   : ████░░░░░░░░  Politique instable
```

### Policy Entropy
```
🟢 Vert  (< 0.3)   : ████████████  Très déterministe
🟡 Jaune (0.3-0.7) : ████████░░░░  Équilibre exploration/exploitation
🔴 Rouge (> 0.7)   : ████░░░░░░░░  Trop exploratoire
```

## 🔄 Workflow de Sélection

### Scénario 1: Charger le meilleur modèle global
```
1. [Clic] 🏆 Meilleur
   └─→ Charge automatiquement model_85000ep... (meilleur composite_score)
   
2. Interface met à jour:
   ● model_85000ep...  ← Nouveau modèle actif
   Win: 95%
   
3. Détails affichés à droite
```

### Scénario 2: Chercher le modèle le plus efficace
```
1. [Clic] Tri: 🏆 Score
   └─→ [Clic] Affiche maintenant "Tri: ⚡ Sample Eff"
   
2. Liste retriée par sample_efficiency (décroissant)
   ► q_table.pkl         ← Sample Eff le plus élevé
   Win: 98%
   
3. [Clic sur q_table.pkl] Sélectionne
   
4. [Clic] 📥 Charger
   └─→ Charge q_table.pkl
```

### Scénario 3: Trouver les Q-tables les mieux convergées
```
1. [Clic] Tri: 🏆 Score
   └─→ [Clic] "Tri: ⚡ Sample Eff"
   └─→ [Clic] "Tri: 🎯 Bellman"
   
2. Liste retriée par bellman_error (croissant)
   ► model_XYZ.pkl       ← Bellman le plus petit
   Win: 92%
   
3. Détails → Bellman: 0.0523 🟢
```

## 🎯 Cas d'Usage Typiques

### Pour Jouer Contre un Agent Fort
```
Objectif: Trouver un adversaire difficile

1. [Clic] Tri: 🏆 Score       ← Trier par score global
2. Sélectionner le 1er        ← Meilleur score
3. [Clic] 📥 Charger ou 🏆 Meilleur
4. Aller dans "Jeu" → Jouer

Résultat: Agent avec 95%+ de win rate
```

### Pour Analyser l'Apprentissage
```
Objectif: Comparer efficacité d'apprentissage

1. [Clic] Tri: ⚡ Sample Eff  ← Trier par efficacité
2. Comparer le top 5
   - model_A: Sample Eff 8.5 🟢 (85,000 ep)
   - model_B: Sample Eff 6.2 🟢 (50,000 ep)
   - model_C: Sample Eff 3.1 🟡 (100,000 ep)
   
Interprétation:
- model_A: Excellent, apprend très vite
- model_B: Très bon avec moins d'épisodes
- model_C: Plus lent malgré plus d'entraînement
```

### Pour Vérifier la Convergence
```
Objectif: Trouver les modèles les plus stables

1. [Clic] Tri: 🎯 Bellman     ← Trier par erreur
2. Sélectionner model avec Bellman < 0.1
3. Vérifier aussi:
   - RetVar < 0.3 🟢         ← Politique stable
   - Entropy < 0.3 🟢        ← Déterministe
   
Résultat: Modèle convergé et fiable
```

## 📊 Exemple Complet de Lecture

```
┌─────────────────────────────────────┐
│ 🏆 Score: 85.2/100          🟢      │  Score global excellent
│                                     │
│ ─ PERFORMANCE ─                     │
│ Win: 95.0%                  🟢      │  Très bon taux de victoire
│ Draw: 3.5%                          │  Peu de matchs nuls
│ Loss: 1.5%                  🟢      │  Très peu de défaites
│                                     │
│ ─ MÉTRIQUES ─                       │
│ Perf: 85.0                  🟢      │  Performance excellente
│ Robustesse: 1.85            🟢      │  Résultats stables
│ Sample Eff: 1.73            🟡      │  Apprentissage moyen
│ Bellman: 0.1523             🟡      │  Convergence acceptable
│ RetVar: 0.385               🟡      │  Politique assez stable
│ Entropy: 0.428              🟡      │  Bon équilibre
└─────────────────────────────────────┘

Interprétation:
✅ Excellent joueur (Win 95%)
✅ Résultats fiables (Robustesse 1.85)
⚠️  A pris du temps pour apprendre (Sample Eff 1.73)
⚠️  Convergence acceptable mais pas parfaite (Bellman 0.15)
✅ Bon équilibre exploration/exploitation (Entropy 0.43)

Conclusion: Excellent modèle pour jouer, mais pas le plus efficace
            en termes d'apprentissage. Bon pour une utilisation finale.
```

## 🎓 Conseils d'Utilisation

### Pour Débutants
```
1. Utilisez 🏆 Meilleur pour charger un bon modèle
2. Regardez surtout le Win Rate dans la liste
3. Les couleurs 🟢 = bon, 🔴 = à améliorer
```

### Pour Utilisateurs Avancés
```
1. Explorez les 3 critères de tri
2. Comparez Sample Efficiency vs Performance
3. Analysez Bellman Error pour la convergence
4. Utilisez Return Variance pour la stabilité
```

### Pour Chercheurs/Développeurs
```
1. Examinez toutes les métriques ensemble
2. Corrélation Sample Eff ↔ Total Episodes
3. Balance Bellman Error ↔ Policy Entropy
4. Utilisez display_rl_metrics.py pour analyse détaillée
```

## 🚀 Raccourcis Clavier (à venir)

```
← →    : Navigation page précédente/suivante
L      : Charger le modèle sélectionné
B      : Charger le meilleur modèle
R      : Rafraîchir la liste
S      : Changer de critère de tri
↑ ↓    : Sélectionner modèle précédent/suivant
```

## 🎉 Points Clés à Retenir

1. **Les métriques RL sont maintenant dans MÉTRIQUES** ✅
2. **3 critères de tri disponibles** (Score, Sample Eff, Bellman) ✅
3. **Bouton "Meilleur" = composite_score** ✅
4. **Couleurs indiquent la qualité** (🟢 🟡 🔴) ✅
5. **Liste triée automatiquement** selon le critère choisi ✅

---

*Pour plus de détails techniques, voir [SORT_SYSTEM_GUIDE.md](SORT_SYSTEM_GUIDE.md)*
