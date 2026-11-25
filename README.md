# Library NoSQL API — environnement de départ

Projet de départ pour l'évaluation pratique du **8 décembre 2026**. Il met à disposition quatre bases NoSQL, une API FastAPI et une intégration à Open Library.

## Architecture

- **MongoDB** : catalogue bibliographique sous forme de documents.
- **Redis** : cache des recherches Open Library avec expiration TTL.
- **Cassandra** : historique des consultations et événements utilisateurs.
- **Neo4j** : graphe lecteurs-livres-auteurs et recommandations simples.
- **FastAPI** : API REST et documentation Swagger.
- **Open Library** : API publique externe de recherche de livres.

## Prérequis

- Docker Desktop récent avec Docker Compose v2 (ou Docker Engine + Compose).
- Git.
- 8 Go de RAM recommandés. Cassandra et Neo4j sont les services les plus gourmands.
- Connexion Internet pour interroger Open Library.

## Démarrage

Depuis un terminal à l'emplacement où vous souhaitez installer le projet :

```bash
git clone <URL_DU_DEPOT_GITHUB>
cd Library_NoSQL_API
cp .env.example .env
docker compose config
docker compose up -d --build
docker compose ps
```

Sous Windows, les commandes sont à exécuter dans Git Bash. Sous PowerShell, copier `.env.example` vers `.env` avec `Copy-Item .env.example .env`.

Le premier démarrage peut prendre plusieurs minutes, surtout pour Cassandra. Attendre que les quatre bases soient `healthy`, puis que l'API soit `Up`.

## Accès

- Swagger UI : http://localhost:8000/docs
- État des bases : http://localhost:8000/api/v1/health
- Neo4j Browser : http://localhost:7474
- MongoDB : localhost:27017
- Redis : localhost:6379
- Cassandra CQL : localhost:9042

Les identifiants locaux sont dans `.env`. Ne jamais publier le fichier `.env`.

## Scénarios de test rapides

### Recherche Open Library — MongoDB + Redis

```bash
curl "http://localhost:8000/api/v1/books/search?q=tolkien&limit=5"
```

Relancer la même requête : la réponse doit indiquer `source: redis-cache` si le cache n'a pas expiré. Lors d'un cache miss, les livres retournés sont également enregistrés dans MongoDB.

### Catalogue MongoDB

```bash
curl "http://localhost:8000/api/v1/books?limit=10"
```

### Historique Cassandra

```bash
curl -X POST "http://localhost:8000/api/v1/users/student-01/history" \
  -H "Content-Type: application/json" \
  -d '{"book_key":"/works/OL27448W","title":"The Hobbit","action":"view"}'

curl "http://localhost:8000/api/v1/users/student-01/history"
```

### Graphe Neo4j

```bash
curl -X POST "http://localhost:8000/api/v1/graph/users/student-01/interactions" \
  -H "Content-Type: application/json" \
  -d '{"book_key":"/works/OL27448W","title":"The Hobbit","author_name":"J. R. R. Tolkien"}'

curl -X POST "http://localhost:8000/api/v1/graph/users/student-02/interactions" \
  -H "Content-Type: application/json" \
  -d '{"book_key":"/works/OL27448W","title":"The Hobbit","author_name":"J. R. R. Tolkien"}'

curl -X POST "http://localhost:8000/api/v1/graph/users/student-02/interactions" \
  -H "Content-Type: application/json" \
  -d '{"book_key":"/works/OL82563W","title":"The Fellowship of the Ring","author_name":"J. R. R. Tolkien"}'

curl "http://localhost:8000/api/v1/recommendations/student-01"
```

La recommandation Neo4j est volontairement simple : elle propose des livres consultés par des lecteurs qui partagent au moins une consultation avec le lecteur cible.

## Routes de l'API

| Méthode | Route | Utilisation |
|---|---|---|
| GET | `/api/v1/health` | Vérifier les quatre bases |
| GET | `/api/v1/books/search?q=...` | Open Library, cache Redis, persistance MongoDB |
| POST | `/api/v1/books` | Créer / mettre à jour un livre dans MongoDB |
| GET | `/api/v1/books` | Lister les livres MongoDB |
| GET | `/api/v1/books/{book_key}` | Consulter un livre MongoDB |
| POST | `/api/v1/users/{user_id}/history` | Ajouter un événement Cassandra |
| GET | `/api/v1/users/{user_id}/history` | Lire l'historique Cassandra |
| POST | `/api/v1/graph/users/{user_id}/interactions` | Ajouter une interaction Neo4j |
| GET | `/api/v1/recommendations/{user_id}` | Recommandations via Neo4j |

## Commandes de diagnostic

```bash
docker compose ps
docker compose logs --tail=100 api
docker compose logs --tail=100 cassandra
docker compose logs --tail=100 neo4j
```

Connexions en ligne de commande :

```bash
docker compose exec mongodb mongosh -u library_admin -p --authenticationDatabase admin
docker compose exec redis redis-cli -a 'LibraryRedis2026!' ping
docker compose exec cassandra cqlsh
docker compose exec neo4j cypher-shell -u neo4j -p 'LibraryNeo4j2026!'
```

Dans `mongosh` :

```javascript
show dbs
use library
show collections
db.books.countDocuments()
```

Dans `cqlsh` :

```sql
DESCRIBE KEYSPACES;
USE library;
DESCRIBE TABLES;
SELECT * FROM user_history LIMIT 10;
```

Dans `cypher-shell` :

```cypher
MATCH (n) RETURN labels(n), count(*);
MATCH (u:Reader)-[r]->(b:Book) RETURN u, r, b LIMIT 25;
```

## Arrêt et réinitialisation

Arrêter les services sans supprimer les données :

```bash
docker compose stop
```

Supprimer conteneurs et réseau tout en conservant les volumes :

```bash
docker compose down
```

**Réinitialisation destructive** : supprime également les données des quatre bases.

```bash
docker compose down -v
```

Ne lancez cette dernière commande que si vous souhaitez repartir de zéro.

## Important

- Ce dépôt fournit un environnement et un squelette d'API à compléter. Il ne contient pas le sujet d'évaluation ni son corrigé.
- Les mots de passe `.env.example` sont uniquement des identifiants de démonstration locaux.
- Open Library est un service public : limiter les appels et respecter ses règles d'utilisation. Le cache Redis évite de répéter inutilement les mêmes recherches.
- Le premier démarrage de Cassandra peut prendre plusieurs minutes.
- Pour une utilisation pédagogique, éviter de lancer plusieurs fois des recherches identiques trop rapidement.

## Dépannage

- **Un service reste `starting` / `unhealthy`** : consulter `docker compose ps` puis `docker compose logs --tail=150 cassandra` ou `neo4j`.
- **L'API ne démarre pas** : `docker compose logs --tail=200 api`.
- **Port occupé** : vérifier les ports 27017, 6379, 9042, 7474, 7687 et 8000.
- **Open Library indisponible** : vérifier Internet, attendre un peu puis réessayer.
