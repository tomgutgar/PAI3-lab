#!/usr/bin/env bash
# Copia las politicas a la ruta del navegador. Ejecutar con sudo.
# Uso: sudo ./desplegar.sh [firefox|chromium|brave]
set -euo pipefail
[ "$(id -u)" -eq 0 ] || { echo "Ejecuta con sudo."; exit 1; }
DIR="$(dirname "$0")"
NAV="${1:-firefox}"

valida() { python3 -m json.tool "$1" >/dev/null || { echo "JSON invalido: $1"; exit 1; }; }

case "$NAV" in
  firefox)
    valida "$DIR/firefox/policies.json"
    install -d /etc/firefox/policies
    cp "$DIR/firefox/policies.json" /etc/firefox/policies/policies.json ;;
  chromium)
    valida "$DIR/chromium/policies.json"
    install -d /etc/chromium/policies/managed
    cp "$DIR/chromium/policies.json" /etc/chromium/policies/managed/policies.json ;;
  brave)
    valida "$DIR/chromium/policies.json"
    install -d /etc/brave/policies/managed
    cp "$DIR/chromium/policies.json" /etc/brave/policies/managed/policies.json ;;
  *) echo "Navegador no soportado: $NAV"; exit 1 ;;
esac
echo "Politicas desplegadas para $NAV. Verifica en about:policies / chrome://policy."
