#!/usr/bin/env bash
# Comprobacion rapida: los JSON de politicas son validos y los scripts no tienen
# errores de sintaxis. Falla (exit != 0) si algo esta mal.
# Uso: ./check.sh
set -euo pipefail
cd "$(dirname "$0")"

echo "== JSON =="
for f in navegador/firefox/policies.json navegador/chromium/policies.json; do
  python3 -m json.tool "$f" >/dev/null && echo "OK  $f"
done

echo "== Bash (bash -n) =="
while IFS= read -r f; do
  bash -n "$f" && echo "OK  $f"
done < <(find . -name '*.sh')

echo "Todo correcto."
