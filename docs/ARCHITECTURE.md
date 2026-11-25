# Architecture pédagogique

## Recherche de livres
Client -> FastAPI -> Redis.
- Cache hit : retourner le résultat mémorisé.
- Cache miss : appeler Open Library, enregistrer les livres dans MongoDB, placer le résultat dans Redis avec TTL.

## Historique
Client -> FastAPI -> Cassandra `library.user_history`.
La clé de partition est `user_id`, ce qui permet de lire l'historique d'un utilisateur.

## Graphe
Nœuds : `Reader`, `Book`, `Author`.
Relations : `VIEWED`, `WRITTEN_BY`.
La recommandation est une requête de parcours de graphe basée sur des lecteurs ayant consulté des livres communs.

## Périmètre
Projet conçu pour être cloné et démarré localement avec Docker Compose. Aucun compte Open Library n'est nécessaire.
