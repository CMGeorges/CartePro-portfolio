# Lancer CartePro

Python 3.11 ou 3.12 :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

En développement, SQLite et une clé de session locale sont utilisés par défaut. Ouvrir http://localhost:5000 ; état : `/health`. Les paiements nécessitent vos propres clés Stripe.

Les clients JSON récupèrent d'abord `GET /auth/csrf`, conservent les cookies et envoient `X-CSRFToken` avec le token pour chaque mutation. Après connexion, récupérer un nouveau token. Seul `/api/v1/stripe/webhook` est exempté de CSRF et exige une signature Stripe valide, même en test.

## Docker Compose

Renseigner `SECRET_KEY` et `POSTGRES_PASSWORD` avec des valeurs aléatoires dans `.env`, puis :

```bash
docker compose up --build
```

PostgreSQL est persistant et non exposé au réseau hôte. Le serveur Gunicorn attend la disponibilité de PostgreSQL et écoute sur localhost:5000. La configuration production impose une clé de session. Pour tester la connexion par navigateur, servir via HTTPS : les cookies de session production sont sécurisés.

## Abonnements Stripe

Associer le `stripe_customer_id` de chaque utilisateur au client Stripe créé par votre intégration de souscription. Configurer `STRIPE_WEBHOOK_SECRET`, puis abonner l'endpoint aux événements `customer.subscription.created`, `customer.subscription.updated` et `customer.subscription.deleted`. Pour tester localement :

```bash
stripe listen --forward-to localhost:5000/api/v1/stripe/webhook
```

Utiliser le secret affiché par Stripe CLI. Le webhook relit l'abonnement Stripe courant, évite les doublons et enregistre l'état avec le marqueur d'événement dans une transaction unique. Les erreurs temporaires retournent 502/503 pour provoquer une nouvelle livraison. Un client non associé retourne 503 ; associer le client puis relancer la livraison. Les abonnements annulés retirent l'accès Pro.

La table additive `stripe_webhook_events` est créée au démarrage. Sauvegarder la base avant une mise à jour. Les tests Stripe utilisent des requêtes signées réelles et un fournisseur Stripe simulé ; aucun paiement réel n'est effectué.

```bash
python -m pytest -q
```

Cette correction sécurise la synchronisation des abonnements existants. Le parcours complet de création d'un abonnement, un stockage partagé des limites de requêtes et les migrations versionnées restent à compléter avant une exploitation commerciale à plusieurs workers. Gunicorn est volontairement limité à un worker dans cette configuration.
