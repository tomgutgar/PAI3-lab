#!/usr/bin/env bash
# Copia las políticas a la ruta del navegador. Ejecutar con sudo.
# Uso: sudo ./desplegar.sh [firefox|chromium|brave]
set -euo pipefail
DIR="$(dirname "$0")"
NAV="${1:-firefox}"

case "$NAV" in
  firefox)
    install -d /etc/firefox/policies
    cp "$DIR/firefox/policies.json" /etc/firefox/policies/policies.json ;;
  chromium)
    install -d /etc/chromium/policies/managed
    cp "$DIR/chromium/policies.json" /etc/chromium/policies/managed/policies.json ;;
  brave)
    install -d /etc/brave/policies/managed
    cp "$DIR/chromium/policies.json" /etc/brave/policies/managed/policies.json ;;
  *) echo "Navegador no soportado: $NAV"; exit 1 ;;
esac
echo "Políticas desplegadas para $NAV. Verifica en about:policies / chrome://policy."
