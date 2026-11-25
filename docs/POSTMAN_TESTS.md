# Scénarios de test dans Swagger / Postman

Base URL : `http://localhost:8000/api/v1`

1. `GET /health`
2. `GET /books/search?q=python&limit=5` — appel externe, MongoDB et Redis.
3. Rejouer la même recherche — observer `source=redis-cache`.
4. `GET /books?limit=10`
5. `POST /users/etu01/history` avec `{"book_key":"/works/OL...","title":"Titre du livre","action":"view"}`
6. `GET /users/etu01/history`
7. `POST /graph/users/etu01/interactions` avec `{"book_key":"/works/OL...","title":"Titre","author_name":"Auteur"}`
8. `GET /recommendations/etu01`
