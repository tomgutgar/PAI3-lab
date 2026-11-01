#!/usr/bin/env bash
# Ejecuta Lynis y guarda los logs en evidencias/ con fecha y etiqueta (antes/despues).
# Uso: sudo ./run_lynis.sh <etiqueta>
set -euo pipefail

ETIQUETA="${1:-antes}"
HOST="$(hostname)"
FECHA="$(date +%Y-%m-%d)"
DEST="$(dirname "$0")/../evidencias/sistemas"
mkdir -p "$DEST"

# TODO: usar la última versión de Lynis (git clone) en vez de la de apt si resta puntos.
lynis audit system

cp /var/log/lynis.log        "$DEST/lynis-${HOST}-${ETIQUETA}-${FECHA}.log"
cp /var/log/lynis-report.dat "$DEST/report-${HOST}-${ETIQUETA}-${FECHA}.dat"

echo "Hardening index:"
grep 'hardening_index' "$DEST/report-${HOST}-${ETIQUETA}-${FECHA}.dat" || true
