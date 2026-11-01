#!/usr/bin/env bash
# Ejecuta Lynis y guarda los logs en evidencias/sistemas/ con fecha y etiqueta.
# Uso: sudo ./run_lynis.sh <antes|despues>
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Ejecuta con sudo."; exit 1; }

ETIQUETA="${1:-antes}"
HOST="$(hostname)"
FECHA="$(date +%Y-%m-%d)"
DEST="$(cd "$(dirname "$0")/.." && pwd)/evidencias/sistemas"
mkdir -p "$DEST"

# Prefiere la copia de git (más actual que la de apt); si no, el lynis del PATH.
if [ -x "$(dirname "$0")/lynis/lynis" ]; then
  LYNIS="$(dirname "$0")/lynis/lynis"
else
  LYNIS="$(command -v lynis)" || { echo "Lynis no instalado (ver README)."; exit 1; }
fi

"$LYNIS" audit system
cp /var/log/lynis.log        "$DEST/lynis-${HOST}-${ETIQUETA}-${FECHA}.log"
cp /var/log/lynis-report.dat "$DEST/report-${HOST}-${ETIQUETA}-${FECHA}.dat"
echo
grep '^hardening_index=' "$DEST/report-${HOST}-${ETIQUETA}-${FECHA}.dat" \
  || echo "hardening_index no encontrado."
echo "Logs guardados en $DEST"
