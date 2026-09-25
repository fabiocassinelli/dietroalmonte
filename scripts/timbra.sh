#!/usr/bin/env bash
# Applica una marca temporale OpenTimestamps ai sorgenti di una ricerca.
#   ./scripts/timbra.sh ricerche/2026-01-rossi-scurtabo
set -euo pipefail

if ! command -v ots >/dev/null 2>&1; then
  echo "Manca il client OpenTimestamps. Installalo con:" >&2
  echo "  pip install opentimestamps-client" >&2
  exit 1
fi

DIR="${1:?Uso: $0 <cartella-della-ricerca>}"
[ -d "$DIR" ] || { echo "Cartella inesistente: $DIR" >&2; exit 1; }

# Marca il sorgente e ogni file di dati. Non marcare i file generati.
mapfile -t FILE < <(find "$DIR" -type f \
  \( -name '*.qmd' -o -name '*.geojson' -o -name '*.dot' -o -name '*.csv' \) \
  ! -name '_*' | sort)

if [ ${#FILE[@]} -eq 0 ]; then
  echo "Nessun file da marcare in $DIR" >&2
  exit 1
fi

for f in "${FILE[@]}"; do
  [ -f "$f.ots" ] && { echo "già marcato: $f"; continue; }
  ots stamp "$f"
  echo "marcato:    $f"
done

echo
echo "Fra qualche ora completa l'ancoraggio con:"
echo "  ots upgrade $DIR/*.ots"
echo "e verifica con:"
echo "  ots verify $DIR/index.qmd.ots"
