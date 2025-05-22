# 🚀 RocketStatsBot

**RocketStatsBot** est un bot Discord qui génère un résumé automatique des derniers matchs Rocket League d’un joueur. Il affiche des statistiques telles que les victoires, le delta MMR, les buts, et les arrêts.

---

## 📦 Fonctionnalités

- 🧠 Analyse automatique des 5 derniers replays importés.
- 🏅 Calcul des victoires / défaites selon l’équipe du joueur.
- 📈 Estimation du MMR grâce aux données `debug_info`.
- ⚽ Agrégation des buts et arrêts du joueur.
- 📡 Commande Discord `!report` pour afficher les statistiques en direct.

---

## 🛠️ Installation

### Prérequis

- Python 3.11+
- Une base de données SQLite (ou autre moteur SQL compatible avec SQLAlchemy).
- Token Discord Bot
