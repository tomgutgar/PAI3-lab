# Parte 2 — Bastionado del navegador

Objetivo: directivas corporativas (fichero de políticas, no ajustes a mano) aplicadas y verificadas.

## Flujo

1. Estado inicial: pruebas de `plan_pruebas.md` con el navegador sin tocar. Capturas.
2. Editar `firefox/policies.json` (y `chromium/policies.json`). Justificar cada directiva en `directivas.md`.
3. `sudo ./desplegar.sh` → copia los ficheros a su ruta del sistema.
4. Verificar en `about:policies` / `chrome://policy`. Captura (es la prueba).
5. Estado final: repetir pruebas. Tabla antes/después.

## Rutas de las políticas (Linux)

- Firefox: `/etc/firefox/policies/policies.json`
- Chromium: `/etc/chromium/policies/managed/policies.json`
- Brave: `/etc/brave/policies/managed/policies.json`

Referencias: https://mozilla.github.io/policy-templates/ · https://chromeenterprise.google/policies/
