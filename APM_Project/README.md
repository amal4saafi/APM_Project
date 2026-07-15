# APM Project - Guide d'installation rapide (Docker & Django)

Ce projet utilise **Docker** et **Docker Compose** pour simplifier la configuration de l'environnement de développement local avec **Django** et **MariaDB**.

---

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé les outils suivants sur votre machine :

1. **Git** (pour cloner le projet).
2. **Docker Desktop** (assurez-vous qu'il est démarré et que le moteur Docker est actif - icône verte).

---

## 🚀 Étape 1 : Récupérer le projet

Clonez le dépôt Git du projet (remplacez le lien ci-dessous par l'URL de votre dépôt) :
```bash
git clone <URL_DU_DEPOT_GIT>
cd APM-Project
```

---

## 🛠️ Étape 2 : Construire les images Docker

Depuis la racine du projet (là où se trouve le fichier `docker-compose.yml`), exécutez la commande suivante pour télécharger les images nécessaires et construire le conteneur Django :
```bash
docker compose build
```

---

## 🗄️ Étape 3 : Appliquer les migrations de base de données

Une fois la construction terminée, appliquez les migrations Django pour initialiser les tables de la base de données MariaDB :
```bash
docker compose run --rm web python manage.py migrate
```

---

## 🏃‍♂️ Étape 4 : Lancer le projet

Démarrez les services (Base de données + Django) en arrière-plan :
```bash
docker compose up -d
```

---

## 🔑 Étape 4bis : Initialiser les rôles et le compte admin

```bash
docker compose run --rm web python manage.py seed_apm
```
Cela crée deux rôles (**Admin**, **User**) et un compte administrateur :
- **Utilisateur :** `admin`
- **Mot de passe :** `Admin123!`

⚠️ Changez ce mot de passe en production.

---

## 🌍 Étape 5 : Accéder à l'application

Ouvrez votre navigateur et accédez à l'adresse suivante :
- **Django :** [http://localhost:8000](http://localhost:8000)

---

## 🧭 Module Gestion Admin / Utilisateur (app `apm`)

Ce module ajoute :
- **Authentification** avec redirection selon le rôle : les **admins** arrivent sur le dashboard admin, les **utilisateurs standards** sur leur propre dashboard (aucun accès aux pages d'administration).
- **Dashboard admin** : statistiques globales (utilisateurs actifs/désactivés, applications, environnements, rôles) + graphiques (applications par direction métier, utilisateurs par rôle, environnements par type) + derniers logs.
- **Dashboard utilisateur** : ses propres applications et environnements uniquement.
- **Gestion des utilisateurs** (admin) : liste, création, modification, **activer/désactiver** un compte en un clic, **export Excel** (`.xlsx`) et **import Excel** (création/mise à jour en masse).
- **Gestion des rôles** (table `Role`, ajoutée au diagramme ERD) : CRUD complet avec droits (`peut_gerer_users`, `peut_gerer_apps`, `peut_voir_dashboard_admin`).
- **CRUD complet Application** et **CRUD complet Environnement** (réservé à l'admin ; l'utilisateur standard voit ses applications/environnements en lecture seule).

Diagramme ERD mis à jour (avec la table `Role`) : voir `docs/diagramme_ERD_avec_Role.png`.

---

## 🛑 Commandes utiles

- **Arrêter le projet :**
  ```bash
  docker compose down
  ```
- **Voir les logs des conteneurs en temps réel :**
  ```bash
  docker compose logs -f
  ```
- **Accéder au shell de Django :**
  ```bash
  docker compose run --rm web python manage.py shell
  ```
- **Créer un superutilisateur Django :**
  ```bash
  docker compose run --rm web python manage.py createsuperuser
  ```
