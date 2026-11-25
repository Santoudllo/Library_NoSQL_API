#!/usr/bin/env sh
set -eu
echo "== Containers =="
docker compose ps
echo "== API health =="
curl -fsS http://localhost:8000/api/v1/health
echo
echo "== Open Library search =="
curl -fsS "http://localhost:8000/api/v1/books/search?q=tolkien&limit=3"
echo
