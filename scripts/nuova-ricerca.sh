#!/usr/bin/env bash
# Apre il cantiere di una nuova ricerca.
#   ./scripts/nuova-ricerca.sh rossi-scurtabo
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Uso: $0 <slug-della-ricerca>" >&2
  echo "Esempio: $0 rossi-scurtabo" >&2
  exit 1
fi

SLUG="$1"
OGGI="$(date +%F)"
DIR="ricerche/$(date +%Y-%m)-${SLUG}"

if [ -d "$DIR" ]; then
  echo "Esiste già: $DIR" >&2
  exit 1
fi

mkdir -p "$DIR/immagini" "$DIR/dati"
sed -e "s|SLUG|$(basename "$DIR")|g" -e "s|DATA|${OGGI}|g" \
    scripts/template.qmd > "$DIR/index.qmd"
: > "$DIR/_revisioni.md"

git checkout -b "ricerca/${SLUG}" >/dev/null 2>&1 || true
git add "$DIR"
git commit -S -m "Apro la ricerca: ${SLUG}" >/dev/null

echo "Cantiere aperto in $DIR"
echo "Ramo: ricerca/${SLUG}"
echo
echo "Ora:  quarto preview   (oppure: make anteprima)"
