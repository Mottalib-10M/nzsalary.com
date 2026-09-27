#!/usr/bin/env bash
# Ping IndexNow (Bing/Yandex) avec toutes les URLs du sitemap après déploiement.
# Usage : scripts/indexnow.sh [https://nettolohn-rechner.ch]
set -euo pipefail
SITE="${1:-https://nettolohn-rechner.ch}"
KEY="c1f0e5f4b7a94d2e9b3c8a7d6e5f4a3b"
URLS=$(curl -s "$SITE/sitemap-0.xml" | grep -oE '<loc>[^<]+</loc>' | sed -E 's#</?loc>##g' | jq -R . | jq -s .)
HOST=$(echo "$SITE" | sed -E 's#https?://##')
curl -s -X POST "https://api.indexnow.org/indexnow" -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"host\":\"$HOST\",\"key\":\"$KEY\",\"keyLocation\":\"$SITE/$KEY.txt\",\"urlList\":$URLS}" -w "\nHTTP %{http_code}\n"
