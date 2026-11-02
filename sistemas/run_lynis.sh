#!/usr/bin/env bash
# Ejecuta Lynis y guarda los logs en evidencias/sistemas/ con fecha y etiqueta.
# Uso: sudo ./run_lynis.sh <antes|despues>
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Ejecuta con sudo."; exit 1; }

ETIQUETA="${1:-antes}"
HOST="$(hostname)"
FECHA="$(date +%Y-%m-%d)"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$RAIZ/evidencias/sistemas"
mkdir -p "$DEST"

# Prefiere la copia de git (más actual que la de apt): en la raíz del repo, en sistemas/ o en el directorio actual.
LYNIS=""
for d in "$RAIZ/lynis" "$RAIZ/sistemas/lynis" "$PWD"; do
  [ -x "$d/lynis" ] && [ -d "$d/include" ] && { LYNIS="$d/lynis"; break; }
done
[ -n "$LYNIS" ] || LYNIS="$(command -v lynis)" || { echo "Lynis no instalado (ver README)."; exit 1; }

# La copia de git exige ejecutarse desde su carpeta (busca ./include).
(cd "$(dirname "$LYNIS")" && "$LYNIS" audit system)
cp /var/log/lynis.log        "$DEST/lynis-${HOST}-${ETIQUETA}-${FECHA}.log"
cp /var/log/lynis-report.dat "$DEST/report-${HOST}-${ETIQUETA}-${FECHA}.dat"
echo
grep '^hardening_index=' "$DEST/report-${HOST}-${ETIQUETA}-${FECHA}.dat" \
  || echo "hardening_index no encontrado."
echo "Logs guardados en $DEST"
