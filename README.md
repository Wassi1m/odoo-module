# Odoo 18 avec Docker Compose

Environnement Odoo 18 prêt à l'emploi, avec une base PostgreSQL 16, lancé via Docker Compose.

## Stack technique
- Odoo 18
- PostgreSQL 16
- Docker Compose

## Lancement
```bash
mkdir -p odoo/addons
docker compose up -d
```

## Accès local
- Odoo : http://localhost:8069

## Base de données
- Hôte : `odoo-db`
- Utilisateur : `odoo`
- Mot de passe : `odoo`

## Modules personnalisés
Place tes modules dans `./odoo/addons`. Ce dossier est monté dans le conteneur sur `/mnt/extra-addons`.

## Arrêt
```bash
docker compose down
```
