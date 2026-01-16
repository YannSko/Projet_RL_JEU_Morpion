# 📚 Documentation Complète - Morpion Q-Learning

Index de toute la documentation technique du projet.

---

## 🎯 Guides Principaux

### [FEATURES_GUIDE.md](FEATURES_GUIDE.md)
**Guide complet de toutes les fonctionnalités**
- Modes de jeu détaillés
- Système de tournoi
- AutoML et optimisation
- Mode Coach et explainability
- Interface et raccourcis

### [METRICS_GUIDE.md](METRICS_GUIDE.md)
**Documentation complète des métriques d'évaluation**
- 4 métriques classiques
- 6 métriques RL avancées
- Composite Score et pondération
- Interprétation et seuils
- Exemples de calcul

### [UI_IMPROVEMENTS.md](UI_IMPROVEMENTS.md)
**Design moderne et améliorations UI/UX**
- Palette de couleurs dark mode
- Effets visuels (glow, ombres, dégradés)
- Boutons, cartes, barres de progression
- Typographie et responsive
- Principes de design

---

## 🧠 Métriques & Évaluation

### [METRICS_CLASSIFICATION.md](METRICS_CLASSIFICATION.md)
**Classification détaillée des métriques**
- Catégories : Performance, Efficience, RL, Global
- Formules mathématiques complètes
- Implémentation Python
- Relations entre métriques

### [TRAIN_EVAL_FIXED.md](TRAIN_EVAL_FIXED.md)
**Séparation train/eval et bonnes pratiques ML**
- Pourquoi séparer train et eval
- Post-training evaluation avec ε=0
- Éviter le data leakage
- Protocole d'évaluation rigoureux

### [MULTI_SEED_EVAL.md](MULTI_SEED_EVAL.md)
**Évaluation robuste multi-seed**
- Évaluation avec 3-5 seeds différentes
- Statistiques : moyenne, std, CV
- Interprétation de la robustesse
- Implémentation technique

---

## 🔧 Fonctionnalités Techniques

### [SORT_SYSTEM_GUIDE.md](SORT_SYSTEM_GUIDE.md)
**Système de tri multi-critères**
- Tri par Composite Score
- Tri par Sample Efficiency
- Tri par Bellman Error
- Bouton cyclique dans l'interface

### [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
**Résumé de l'architecture et implémentation**
- Structure du code
- Composants principaux
- Flux de données
- Design patterns utilisés

---

## 📖 Guides Historiques

### [RL_METRICS_v2.md](RL_METRICS_v2.md)
**Version 2 des métriques RL** (archive)
- Évolution des métriques
- Versions antérieures
- Historique des améliorations

### [TRAIN_EVAL_ISSUE.md](TRAIN_EVAL_ISSUE.md)
**Problème initial train/eval** (archive)
- Description du bug original
- Impact sur les résultats
- Solution mise en place

### [FIXES_RECAP.md](FIXES_RECAP.md)
**Récapitulatif des corrections** (archive)
- Bugs corrigés
- Améliorations apportées
- Changelog détaillé

### [VISUAL_GUIDE.md](VISUAL_GUIDE.md)
**Guide visuel de l'interface** (archive)
- Captures d'écran
- Diagrammes
- Wireframes

---

## 📑 Navigation Rapide

### Par Thème

**🎮 Fonctionnalités** → [FEATURES_GUIDE.md](FEATURES_GUIDE.md)

**📊 Métriques** → [METRICS_GUIDE.md](METRICS_GUIDE.md), [METRICS_CLASSIFICATION.md](METRICS_CLASSIFICATION.md)

**🎨 Design** → [UI_IMPROVEMENTS.md](UI_IMPROVEMENTS.md)

**🧪 Évaluation** → [TRAIN_EVAL_FIXED.md](TRAIN_EVAL_FIXED.md), [MULTI_SEED_EVAL.md](MULTI_SEED_EVAL.md)

**🔧 Technique** → [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md), [SORT_SYSTEM_GUIDE.md](SORT_SYSTEM_GUIDE.md)

### Par Question

**"Comment sont calculées les métriques ?"**
→ [METRICS_GUIDE.md](METRICS_GUIDE.md) sections 2-4

**"Pourquoi l'interface est-elle moderne ?"**
→ [UI_IMPROVEMENTS.md](UI_IMPROVEMENTS.md) section Palette & Effets

**"Comment fonctionne le Mode Coach ?"**
→ [FEATURES_GUIDE.md](FEATURES_GUIDE.md) section Mode Coach

**"Comment sont évalués les modèles ?"**
→ [TRAIN_EVAL_FIXED.md](TRAIN_EVAL_FIXED.md) + [MULTI_SEED_EVAL.md](MULTI_SEED_EVAL.md)

**"Quelle est l'architecture du code ?"**
→ [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

---

## 🚀 Pour Commencer

1. **README principal** : [../README.md](../README.md)
2. **Guide des fonctionnalités** : [FEATURES_GUIDE.md](FEATURES_GUIDE.md)
3. **Lancer l'application** : `python run.py` (à la racine)

---

## 📞 Besoin d'Aide ?

- Consultez d'abord le [README principal](../README.md)
- Puis le guide approprié ci-dessus
- Enfin les archives historiques si nécessaire

---

**Bonne lecture ! 📚**
